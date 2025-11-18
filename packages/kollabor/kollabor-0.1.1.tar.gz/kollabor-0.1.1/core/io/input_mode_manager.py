import logging
from typing import Optional, Callable

from ..events import EventType
from ..events.models import CommandMode
from .key_parser import KeyPress
from .buffer_manager import BufferManager
from ..commands.menu_renderer import CommandMenuRenderer
from ..commands.parser import SlashCommandParser

logger = logging.getLogger(__name__)


class InputModeManager:
    """Handles input mode management and command mode processing.

    This component is responsible for:
    - Mode state management (enter/exit command modes)
    - Command mode keypress handling
    - Menu navigation and command execution coordination
    - Mode transitions and display updates
    """

    def __init__(
        self,
        buffer_manager: BufferManager,
        command_menu_renderer: CommandMenuRenderer,
        slash_parser: SlashCommandParser,
        event_bus,
        renderer,
        config,
    ) -> None:
        """Initialize the input mode manager.

        Args:
            buffer_manager: Buffer manager for text operations.
            command_menu_renderer: Command menu rendering system.
            slash_parser: Slash command parser.
            event_bus: Event bus for emitting input events.
            renderer: Terminal renderer for updating input display.
            config: Configuration manager for input settings.
        """
        self.buffer_manager = buffer_manager
        self.command_menu_renderer = command_menu_renderer
        self.slash_parser = slash_parser
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config

        # Mode state
        self.command_mode = CommandMode.NORMAL
        self.command_menu_active = False
        self.selected_command_index = 0
        self.current_status_modal_config = None

        # Callbacks for delegation back to InputHandler
        self.on_mode_change: Optional[Callable] = None
        self.on_command_execute: Optional[Callable] = None
        self.on_display_update: Optional[Callable] = None
        self.on_event_emit: Optional[Callable] = None
        self.get_available_commands: Optional[Callable] = None
        self.filter_commands: Optional[Callable] = None
        self.execute_command: Optional[Callable] = None

        logger.info("Input mode manager initialized")

    def set_callbacks(
        self,
        on_mode_change: Callable,
        on_command_execute: Callable,
        on_display_update: Callable,
        on_event_emit: Callable,
        get_available_commands: Callable,
        filter_commands: Callable,
        execute_command: Callable,
    ) -> None:
        """Set callbacks for delegation back to InputHandler."""
        self.on_mode_change = on_mode_change
        self.on_command_execute = on_command_execute
        self.on_display_update = on_display_update
        self.on_event_emit = on_event_emit
        self.get_available_commands = get_available_commands
        self.filter_commands = filter_commands
        self.execute_command = execute_command

    # Mode State Management Methods (Phase 2A)
    # =========================================

    async def _enter_command_mode(self) -> None:
        """Enter slash command mode and show command menu."""
        try:
            logger.info("🎯 Entering slash command mode")
            self.command_mode = CommandMode.MENU_POPUP
            self.command_menu_active = True

            # Reset selection to first command
            self.selected_command_index = 0

            # Add the '/' character to buffer for visual feedback
            self.buffer_manager.insert_char("/")

            # Show command menu via renderer
            available_commands = self.get_available_commands()
            self.command_menu_renderer.show_command_menu(available_commands, "")

            # Emit command menu show event
            await self.on_event_emit(
                EventType.COMMAND_MENU_SHOW,
                {"available_commands": available_commands, "filter_text": ""},
                "commands",
            )

            # Update display to show command mode
            await self.on_display_update(force_render=True)

            logger.info("Command menu activated")

        except Exception as e:
            logger.error(f"Error entering command mode: {e}")
            await self._exit_command_mode()

    async def _exit_command_mode(self) -> None:
        """Exit command mode and restore normal input."""
        try:
            import traceback

            logger.info("🚪 Exiting slash command mode")
            logger.info(
                f"🚪 Exit called from: {traceback.format_stack()[-2].strip()}"
            )

            # Hide command menu via renderer
            self.command_menu_renderer.hide_menu()

            # Emit command menu hide event
            if self.command_menu_active:
                await self.on_event_emit(
                    EventType.COMMAND_MENU_HIDE,
                    {"reason": "manual_exit"},
                    "commands",
                )

            self.command_mode = CommandMode.NORMAL
            self.command_menu_active = False

            # Clear command buffer (remove the '/' and any partial command)
            self.buffer_manager.clear()

            # Update display
            await self.on_display_update(force_render=True)

            logger.info("Returned to normal input mode")

        except Exception as e:
            logger.error(f"Error exiting command mode: {e}")

    async def _enter_status_modal_mode(self, ui_config) -> None:
        """Enter status modal mode - modal confined to status area.

        Args:
            ui_config: Status modal configuration.
        """
        try:
            # Set status modal mode
            self.command_mode = CommandMode.STATUS_MODAL
            self.current_status_modal_config = ui_config
            logger.info(f"Entered status modal mode: {ui_config.title}")

            # Unlike full modals, status modals don't take over the screen
            # They just appear in the status area via the renderer
            await self.on_display_update(force_render=True)

        except Exception as e:
            logger.error(f"Error entering status modal mode: {e}")
            await self._exit_command_mode()

    async def _exit_status_modal_mode(self) -> None:
        """Exit status modal mode and return to normal input."""
        try:
            logger.info("Exiting status modal mode...")
            self.command_mode = CommandMode.NORMAL
            self.current_status_modal_config = None
            logger.info("Status modal mode exited successfully")

            # Refresh display to remove the status modal
            await self.on_display_update(force_render=True)
            logger.info("Display updated after status modal exit")

        except Exception as e:
            logger.error(f"Error exiting status modal mode: {e}")
            self.command_mode = CommandMode.NORMAL

    # Command Processing Methods (Phase 2B)
    # =====================================

    async def _handle_menu_popup_keypress(self, key_press: KeyPress) -> bool:
        """Handle KeyPress during menu popup mode with arrow key navigation.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled.
        """
        try:
            # Handle arrow key navigation
            if key_press.name == "ArrowUp":
                await self._navigate_menu("up")
                return True
            elif key_press.name == "ArrowDown":
                await self._navigate_menu("down")
                return True
            elif key_press.name == "Enter":
                await self._execute_selected_command()
                return True
            elif key_press.name == "Escape":
                await self._exit_command_mode()
                return True

            # Handle printable characters (for filtering)
            elif key_press.char and key_press.char.isprintable():
                # Insert character for command filtering (routed from RawInputProcessor)
                self.buffer_manager.insert_char(key_press.char)
                await self._update_command_filter()
                return True

            # Handle backspace/delete
            elif key_press.name in ["Backspace", "Delete"]:
                # If buffer only has '/', exit command mode
                if len(self.buffer_manager.content) <= 1:
                    await self._exit_command_mode()
                    return True
                else:
                    # Remove character and update command filter
                    self.buffer_manager.delete_char()
                    await self._update_command_filter()
                    return True

            # Other keys not handled
            return False

        except Exception as e:
            logger.error(f"Error handling menu popup keypress: {e}")
            await self._exit_command_mode()
            return False

    async def _update_command_filter(self) -> None:
        """Update command menu based on current buffer content."""
        try:
            # Get current input (minus the leading '/')
            current_input = self.buffer_manager.content
            filter_text = (
                current_input[1:] if current_input.startswith("/") else current_input
            )

            # Update menu renderer with filtered commands
            filtered_commands = self.filter_commands(filter_text)

            # Reset selection when filtering
            self.selected_command_index = 0
            self.command_menu_renderer.set_selected_index(
                self.selected_command_index
            )
            self.command_menu_renderer.filter_commands(
                filtered_commands, filter_text
            )

            # Emit filter update event
            await self.on_event_emit(
                EventType.COMMAND_MENU_FILTER,
                {
                    "filter_text": filter_text,
                    "available_commands": self.get_available_commands(),
                    "filtered_commands": filtered_commands,
                },
                "commands",
            )

            # Update display
            await self.on_display_update(force_render=True)

        except Exception as e:
            logger.error(f"Error updating command filter: {e}")

    async def _navigate_menu(self, direction: str) -> None:
        """Navigate the command menu up or down.

        Args:
            direction: "up" or "down"
        """
        try:
            # Get current filtered commands
            current_input = self.buffer_manager.content
            filter_text = (
                current_input[1:] if current_input.startswith("/") else current_input
            )
            filtered_commands = self.filter_commands(filter_text)

            if not filtered_commands:
                return

            # Update selection index
            if direction == "up":
                self.selected_command_index = max(0, self.selected_command_index - 1)
            elif direction == "down":
                self.selected_command_index = min(
                    len(filtered_commands) - 1, self.selected_command_index + 1
                )

            # Update menu renderer with new selection (don't reset selection during navigation)
            self.command_menu_renderer.set_selected_index(
                self.selected_command_index
            )
            self.command_menu_renderer.filter_commands(
                filtered_commands, filter_text, reset_selection=False
            )

            # Note: No need to call _update_display - filter_commands already renders the menu

        except Exception as e:
            logger.error(f"Error navigating menu: {e}")

    async def _execute_selected_command(self) -> None:
        """Execute the currently selected command."""
        try:
            # Get the selected command from the menu
            selected_command = self.command_menu_renderer.get_selected_command()
            if not selected_command:
                logger.warning("No command selected")
                await self._exit_command_mode()
                return

            # Create command string from selected command
            command_string = f"/{selected_command['name']}"

            # Parse the command
            command = self.slash_parser.parse_command(command_string)
            if command:
                logger.info(f"🚀 Executing selected command: {command.name}")

                # Exit command mode first
                await self._exit_command_mode()

                # Execute the command using delegation
                result = await self.execute_command(command)

                # Handle the result
                if result.success:
                    logger.info(f"✅ Command {command.name} completed successfully")

                    # Modal display is handled by event bus trigger, not here
                    if result.message:
                        # Display success message in status area
                        logger.info(f"Command result: {result.message}")
                        # TODO: Display in status area
                else:
                    logger.warning(
                        f"❌ Command {command.name} failed: {result.message}"
                    )
                    # TODO: Display error message in status area
            else:
                logger.warning("Failed to parse selected command")
                await self._exit_command_mode()

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            await self._exit_command_mode()

    # Public Interface Methods
    # =======================

    async def handle_mode_transition(self, new_mode: CommandMode, **kwargs) -> None:
        """Handle transition to a new command mode."""
        if new_mode == CommandMode.MENU_POPUP:
            await self._enter_command_mode()
        elif new_mode == CommandMode.STATUS_MODAL:
            ui_config = kwargs.get("ui_config")
            await self._enter_status_modal_mode(ui_config)
        elif new_mode == CommandMode.NORMAL:
            if self.command_mode == CommandMode.MENU_POPUP:
                await self._exit_command_mode()
            elif self.command_mode == CommandMode.STATUS_MODAL:
                await self._exit_status_modal_mode()

    async def handle_command_mode_keypress(self, key_press: KeyPress) -> bool:
        """Handle keypress while in command mode."""
        if self.command_mode == CommandMode.MENU_POPUP:
            result = await self._handle_menu_popup_keypress(key_press)
            # Notify mode change callback if mode changed
            if hasattr(self, "on_mode_change") and self.on_mode_change:
                await self.on_mode_change(self.command_mode)
            return result
        elif self.command_mode == CommandMode.STATUS_MODAL:
            # For now, delegate status modal handling back to InputHandler
            # This will be refined in future phases
            return False

        return False

    def get_current_mode(self) -> CommandMode:
        """Get the current command mode."""
        return self.command_mode
