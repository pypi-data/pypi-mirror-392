import logging
from typing import Optional, Callable

from ..events import EventType
from ..events.models import CommandMode
from .key_parser import KeyPress

logger = logging.getLogger(__name__)


class ModalInteractionHandler:
    """Handles modal interactions, widget navigation, and fullscreen sessions.

    This component is responsible for:
    - Modal keypress handling and widget interactions
    - Fullscreen session management
    - Modal display coordination and rendering
    - Modal exit and cleanup procedures
    """

    def __init__(self, event_bus, renderer, config) -> None:
        """Initialize the modal interaction handler.

        Args:
            event_bus: Event bus for emitting modal events.
            renderer: Terminal renderer for display updates.
            config: Configuration manager for modal settings.
        """
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config

        # Modal state
        self.command_mode = CommandMode.NORMAL
        self.modal_renderer = None
        self._fullscreen_session_active = False

        # Callbacks for delegation back to InputHandler
        self.on_mode_change: Optional[Callable] = None
        self.on_display_update: Optional[Callable] = None
        self.on_event_emit: Optional[Callable] = None

        logger.info("Modal interaction handler initialized")

    def set_callbacks(
        self,
        on_mode_change: Callable,
        on_display_update: Callable,
        on_event_emit: Callable,
    ) -> None:
        """Set callbacks for delegation back to InputHandler."""
        self.on_mode_change = on_mode_change
        self.on_display_update = on_display_update
        self.on_event_emit = on_event_emit

    # Modal Processing Methods
    # =======================

    async def _handle_modal_keypress(self, key_press: KeyPress) -> bool:
        """Handle KeyPress during modal mode.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled.
        """
        try:
            # CRITICAL FIX: Check if this is a fullscreen plugin session first
            if (
                hasattr(self, "_fullscreen_session_active")
                and self._fullscreen_session_active
            ):
                # SIMPLE SOLUTION: Check for exit keys directly
                if key_press.char in ["q", "\x1b"] or key_press.name == "Escape":
                    # Exit fullscreen mode immediately
                    self._fullscreen_session_active = False
                    self.command_mode = CommandMode.NORMAL
                    await self.on_display_update(force_render=True)
                    return True

                # Route input to fullscreen session through event bus
                await self.on_event_emit(
                    EventType.FULLSCREEN_INPUT,
                    {"key_press": key_press, "source": "input_handler"},
                    "input_handler",
                )
                return True

            # Initialize modal renderer if needed
            if not self.modal_renderer:
                logger.warning(
                    "Modal keypress received but no modal renderer active"
                )
                await self._exit_modal_mode()
                return True

            # Handle navigation and widget interaction
            logger.info(f"🔍 Modal processing key: {key_press.name}")

            nav_handled = self.modal_renderer._handle_widget_navigation(key_press)
            logger.info(f"🎯 Widget navigation handled: {nav_handled}")
            if nav_handled:
                # Re-render modal with updated focus
                await self._refresh_modal_display()
                return True

            input_handled = self.modal_renderer._handle_widget_input(key_press)
            logger.info(f"🎯 Widget input handled: {input_handled}")
            if input_handled:
                # Re-render modal with updated widget state
                await self._refresh_modal_display()
                return True

            if key_press.name == "Escape":
                logger.info("🚪 Processing Escape key for modal exit")
                await self._exit_modal_mode()
                return True
            elif key_press.name == "Enter":
                logger.info(
                    "🔴 ENTER KEY HIJACKED - This should not happen if widget handled it!"
                )
                # Try to save modal changes and exit
                await self._save_and_exit_modal()
                return True

            return True
        except Exception as e:
            logger.error(f"Error handling modal keypress: {e}")
            await self._exit_modal_mode()
            return False

    async def _exit_modal_mode(self) -> None:
        """Exit modal mode using existing patterns."""
        try:
            # CRITICAL FIX: Complete terminal state restoration
            # Clear active area to remove modal artifacts
            self.renderer.clear_active_area()

            # Clear any buffered modal content that might persist
            if hasattr(self.renderer, "message_renderer"):
                if hasattr(self.renderer.message_renderer, "buffer"):
                    self.renderer.message_renderer.buffer.clear_buffer()

            # CRITICAL FIX: Properly close modal with alternate buffer restoration
            if self.modal_renderer:
                # FIRST: Close modal and restore terminal state (alternate buffer)
                _ = self.modal_renderer.close_modal()

                # THEN: Reset modal renderer widgets
                self.modal_renderer.widgets = []
                self.modal_renderer.focused_widget_index = 0
                self.modal_renderer = None

            # Return to normal mode
            self.command_mode = CommandMode.NORMAL

            # Complete display restoration with force refresh
            self.renderer.clear_active_area()
            await self.on_display_update(force_render=True)

            # Ensure cursor is properly positioned
            # Note: cursor management handled by terminal_state

        except Exception as e:
            logger.error(f"Error exiting modal mode: {e}")
            self.command_mode = CommandMode.NORMAL
            self.modal_renderer = None
            # Emergency cleanup
            self.renderer.clear_active_area()

    async def _refresh_modal_display(self) -> None:
        """Refresh modal display after widget interactions."""
        try:
            if self.modal_renderer and hasattr(
                self.modal_renderer, "current_ui_config"
            ):

                # CRITICAL FIX: Force complete display clearing to prevent duplication
                # Clear active area completely before refresh
                self.renderer.clear_active_area()

                # Clear any message buffers that might accumulate content
                if hasattr(self.renderer, "message_renderer"):
                    if hasattr(self.renderer.message_renderer, "buffer"):
                        self.renderer.message_renderer.buffer.clear_buffer()
                    # Also clear any accumulated messages in the renderer
                    if hasattr(self.renderer.message_renderer, "clear_messages"):
                        self.renderer.message_renderer.clear_messages()

                # Re-render the modal with current widget states (preserve widgets!)
                modal_lines = self.modal_renderer._render_modal_box(
                    self.modal_renderer.current_ui_config,
                    preserve_widgets=True,
                )
                # FIXED: Use state_manager.render_modal_content() instead of _render_modal_lines()
                # to avoid re-calling prepare_modal_display() which causes buffer switching
                if self.modal_renderer.state_manager:
                    self.modal_renderer.state_manager.render_modal_content(
                        modal_lines
                    )
                else:
                    # Fallback to old method if state_manager not available
                    await self.modal_renderer._render_modal_lines(modal_lines)
            else:
                pass
        except Exception as e:
            logger.error(f"Error refreshing modal display: {e}")

    async def _save_and_exit_modal(self) -> None:
        """Save modal changes and exit modal mode."""
        try:
            if self.modal_renderer and hasattr(
                self.modal_renderer, "action_handler"
            ):
                # Get widget values and save them using proper action handler interface
                result = await self.modal_renderer.action_handler.handle_action(
                    "save", self.modal_renderer.widgets
                )
                if result.get("success"):
                    pass
                else:
                    logger.warning(
                        f"Failed to save modal changes: {result.get('message', 'Unknown error')}"
                    )

            await self._exit_modal_mode()
        except Exception as e:
            logger.error(f"Error saving and exiting modal: {e}")
            await self._exit_modal_mode()

    # Fullscreen Session Management
    # ============================

    def set_fullscreen_session_active(self, active: bool) -> None:
        """Set fullscreen session state."""
        self._fullscreen_session_active = active

    def is_fullscreen_session_active(self) -> bool:
        """Check if fullscreen session is active."""
        return self._fullscreen_session_active

    # Public Interface Methods
    # =======================

    async def handle_modal_keypress(self, key_press: KeyPress) -> bool:
        """Public interface for modal keypress handling."""
        if self.command_mode == CommandMode.MODAL:
            return await self._handle_modal_keypress(key_press)
        return False

    def get_current_mode(self) -> CommandMode:
        """Get the current command mode."""
        return self.command_mode
