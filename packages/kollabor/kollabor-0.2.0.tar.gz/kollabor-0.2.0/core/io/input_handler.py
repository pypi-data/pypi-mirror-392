"""Input handling system for Kollabor CLI."""

import asyncio
import logging
import select
import sys
import time
from typing import Dict, Any, List

from ..events import EventType
from ..events.models import CommandMode
from ..commands.parser import SlashCommandParser
from ..commands.registry import SlashCommandRegistry
from ..commands.executor import SlashCommandExecutor
from ..commands.menu_renderer import CommandMenuRenderer
from .key_parser import KeyParser, KeyPress, KeyType as KeyTypeEnum
from .buffer_manager import BufferManager
from .input_errors import InputErrorHandler, ErrorType, ErrorSeverity

logger = logging.getLogger(__name__)


class InputHandler:
    """Advanced terminal input handler with comprehensive key support.

    Features:
    - Extended key sequence support (arrow keys, function keys)
    - Robust buffer management with validation
    - Advanced error handling and recovery
    - Command history navigation
    - Cursor positioning and editing
    """

    def __init__(self, event_bus, renderer, config) -> None:
        """Initialize the input handler.

        Args:
            event_bus: Event bus for emitting input events.
            renderer: Terminal renderer for updating input display.
            config: Configuration manager for input settings.
        """
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config
        self.running = False
        self.rendering_paused = (
            False  # Flag to pause rendering during special effects
        )

        # Load configurable parameters
        self.polling_delay = config.get("input.polling_delay", 0.01)
        self.error_delay = config.get("input.error_delay", 0.1)
        buffer_limit = config.get(
            "input.input_buffer_limit", 100000
        )  # 100KB limit - wide open!
        history_limit = config.get("input.history_limit", 100)

        # NOTE: Paste detection has TWO systems:
        # 1. PRIMARY (ALWAYS ON): Large chunk detection (>10 chars)
        #    creates "[Pasted #N ...]" placeholders
        #    - Located in _input_loop() around line 181
        #    - Triggers automatically when terminal sends big chunks
        #    - This is what users see when they paste
        # 2. SECONDARY (DISABLED): Character-by-character timing fallback
        #    - Located in _process_character() around line 265
        #    - Alternative detection method for edge cases
        #    - Currently disabled via this flag
        self.paste_detection_enabled = False  # Only disables SECONDARY system

        # Initialize components
        self.key_parser = KeyParser()
        self.buffer_manager = BufferManager(buffer_limit, history_limit)

        # Initialize slash command system
        self.command_mode = CommandMode.NORMAL
        self.slash_parser = SlashCommandParser()
        self.command_registry = SlashCommandRegistry()
        self.command_executor = SlashCommandExecutor(self.command_registry)
        self.command_menu_renderer = CommandMenuRenderer(self.renderer)
        self.command_menu_active = False
        self.selected_command_index = 0

        # Initialize modal renderer for modal command mode
        self.modal_renderer = None  # Will be initialized when needed

        # Initialize status modal state
        self.current_status_modal_config = None
        self.error_handler = InputErrorHandler(
            {
                "error_threshold": config.get("input.error_threshold", 10),
                "error_window_minutes": config.get("input.error_window_minutes", 5),
                "max_errors": config.get("input.max_errors", 100),
            }
        )

        # State tracking
        self._last_cursor_pos = 0

        # Simple paste detection state
        self._paste_buffer = []
        self._last_char_time = 0
        # GENIUS PASTE SYSTEM - immediate synchronous storage
        self._paste_bucket = {}  # {paste_id: actual_content}
        self._paste_counter = 0  # Counter for paste numbering
        self._current_paste_id = None  # Currently building paste ID
        self._last_paste_time = 0  # Last chunk timestamp

        logger.info("Input handler initialized with enhanced capabilities")

    async def start(self) -> None:
        """Start the input handling loop."""
        self.running = True
        self.renderer.enter_raw_mode()

        # No bracketed paste - your terminal doesn't support it

        # Check if raw mode worked
        if (
            getattr(
                self.renderer.terminal_state.current_mode,
                "value",
                self.renderer.terminal_state.current_mode,
            )
            != "raw"
        ):
            logger.warning("Raw mode failed - using fallback ESC detection")

        # Register for COMMAND_MENU_RENDER events
        # to provide command menu display
        logger.info("About to register COMMAND_MENU_RENDER hook")
        await self._register_command_menu_render_hook()

        # Register for modal trigger events
        logger.info("About to register modal trigger hook")
        await self._register_modal_trigger_hook()

        # Register for status modal trigger events
        logger.info("About to register status modal trigger hook")
        await self._register_status_modal_trigger_hook()

        # Register for status modal render events
        logger.info("About to register status modal render hook")
        await self._register_status_modal_render_hook()

        # Register for command output display events
        logger.info("About to register command output display hook")
        await self._register_command_output_display_hook()

        logger.info("All hook registrations completed")

        logger.info("Input handler started")
        await self._input_loop()

    async def stop(self) -> None:
        """Stop the input handling loop with cleanup."""
        self.running = False

        # No bracketed paste to disable

        await self.cleanup()
        self.renderer.exit_raw_mode()
        logger.info("Input handler stopped")

    async def _input_loop(self) -> None:
        """Main input processing loop with enhanced error handling."""
        while self.running:
            try:
                # Check for available input
                if select.select([sys.stdin], [], [], self.polling_delay)[0]:
                    # Read ALL available data - keep reading until
                    # buffer is empty
                    import os

                    chunk = b""
                    while True:
                        try:
                            # Read in 8KB chunks
                            more_data = os.read(0, 8192)
                            if not more_data:
                                break
                            chunk += more_data
                            # Check if more data is immediately available
                            if not select.select([sys.stdin], [], [], 0.001)[0]:
                                break  # No more data waiting
                        except OSError:
                            break  # No more data available

                    if not chunk:
                        continue

                    # Decode the complete chunk
                    chunk = chunk.decode("utf-8", errors="ignore")

                    # Raw input processed successfully

                    # Check if this is an escape sequence (arrow keys, etc.)
                    def is_escape_sequence(text: str) -> bool:
                        """Check if input is an escape sequence
                        that should bypass paste detection."""
                        if not text:
                            return False
                        # Common escape sequences start with ESC (\x1b)
                        if text.startswith("\x1b"):
                            return True
                        return False

                    # PRIMARY PASTE DETECTION:
                    # Large chunk detection (ALWAYS ACTIVE)
                    # When user pastes, terminal sends all chars
                    # in one/few chunks
                    # This creates "[Pasted #N X lines, Y chars]" placeholders
                    if len(chunk) > 10 and not is_escape_sequence(chunk):

                        import time

                        current_time = time.time()

                        # Check if this continues the current paste (within 100ms)
                        if (
                            self._current_paste_id
                            and self._last_paste_time > 0
                            and (current_time - self._last_paste_time) < 0.1
                        ):

                            # Merge with existing paste
                            self._paste_bucket[self._current_paste_id] += chunk
                            self._last_paste_time = current_time

                            # Update the placeholder to show new size
                            await self._update_paste_placeholder()
                        else:
                            # New paste - store immediately
                            self._paste_counter += 1
                            self._current_paste_id = f"PASTE_{self._paste_counter}"
                            self._paste_bucket[self._current_paste_id] = chunk
                            self._last_paste_time = current_time

                            # Create placeholder immediately
                            await self._create_paste_placeholder(
                                self._current_paste_id
                            )
                    elif is_escape_sequence(chunk):
                        # Escape sequence - process character by character
                        # to allow key parser to handle it
                        logger.debug(
                            f"Processing escape sequence "
                            f"character-by-character: {repr(chunk)}"
                        )
                        for char in chunk:
                            await self._process_character(char)
                    else:
                        # Normal input (single or multi-character)
                        # process each character individually
                        logger.info(
                            f"🔤 Processing normal input "
                            f"character-by-character: {repr(chunk)}"
                        )
                        # await self._process_character(chunk)
                        for char in chunk:
                            await self._process_character(char)
                else:
                    # No input available - check for standalone ESC key
                    esc_key = self.key_parser.check_for_standalone_escape()
                    if esc_key:
                        logger.info("DETECTED STANDALONE ESC KEY!")
                        # CRITICAL FIX: Route escape to command mode handler
                        # if in modal mode
                        if self.command_mode == CommandMode.MODAL:
                            await self._handle_command_mode_keypress(esc_key)
                        else:
                            await self._handle_key_press(esc_key)

                await asyncio.sleep(self.polling_delay)

            except KeyboardInterrupt:
                logger.info("Ctrl+C received")
                raise
            except OSError as e:
                await self.error_handler.handle_error(
                    ErrorType.IO_ERROR,
                    f"I/O error in input loop: {e}",
                    ErrorSeverity.HIGH,
                    {"buffer_manager": self.buffer_manager},
                )
                await asyncio.sleep(self.error_delay)
            except Exception as e:
                await self.error_handler.handle_error(
                    ErrorType.SYSTEM_ERROR,
                    f"Unexpected error in input loop: {e}",
                    ErrorSeverity.MEDIUM,
                    {"buffer_manager": self.buffer_manager},
                )
                await asyncio.sleep(self.error_delay)

    async def _process_character(self, char: str) -> None:
        """Process a single character input.

        Args:
            char: Character received from terminal.
        """
        try:
            current_time = time.time()

            # Check for slash command initiation
            # (before parsing for immediate response)
            if (
                char == "/"
                and self.buffer_manager.is_empty
                and self.command_mode == CommandMode.NORMAL
            ):
                await self._enter_command_mode()
                return

            # SECONDARY PASTE DETECTION:
            # Character-by-character timing (DISABLED)
            # This is a fallback system - primary chunk detection
            # above handles most cases
            if self.paste_detection_enabled:
                # Currently False - secondary system disabled
                paste_handled = await self._simple_paste_detection(
                    char, current_time
                )
                if paste_handled:
                    # Character consumed by paste detection,
                    # skip normal processing
                    return

            # Parse character into structured key press
            # (this handles escape sequences)
            key_press = self.key_parser.parse_char(char)
            if not key_press:
                # For modal mode, add timeout-based
                # standalone escape detection
                if self.command_mode == CommandMode.MODAL:
                    # Schedule delayed check for standalone escape
                    # (100ms delay)
                    async def delayed_escape_check():
                        await asyncio.sleep(0.1)
                        standalone_escape = (
                            self.key_parser.check_for_standalone_escape()
                        )
                        if standalone_escape:
                            await self._handle_command_mode_keypress(
                                standalone_escape
                            )

                    asyncio.create_task(delayed_escape_check())
                # Incomplete escape sequence - wait for more characters
                return

            # Check for slash command mode handling AFTER parsing
            # (so arrow keys work)
            if self.command_mode != CommandMode.NORMAL:
                logger.info(
                    f"🎯 Processing key '{key_press.name}' "
                    f"in command mode: {self.command_mode}"
                )
                handled = await self._handle_command_mode_keypress(key_press)
                if handled:
                    return

            # Emit key press event for plugins
            key_result = await self.event_bus.emit_with_hooks(
                EventType.KEY_PRESS,
                {
                    "key": key_press.name,
                    "char_code": key_press.code,
                    "key_type": key_press.type.value,
                    "modifiers": key_press.modifiers,
                },
                "input",
            )

            # Check if any plugin handled this key
            prevent_default = self._check_prevent_default(key_result)

            # Process key if not prevented by plugins
            if not prevent_default:
                await self._handle_key_press(key_press)

            # Update renderer
            await self._update_display()

        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.PARSING_ERROR,
                f"Error processing character: {e}",
                ErrorSeverity.MEDIUM,
                {"char": repr(char), "buffer_manager": self.buffer_manager},
            )

    def _check_prevent_default(self, key_result: Dict[str, Any]) -> bool:
        """Check if plugins want to prevent default key handling.

        Args:
            key_result: Result from key press event.

        Returns:
            True if default handling should be prevented.
        """
        if "main" in key_result:
            for hook_result in key_result["main"].values():
                if isinstance(hook_result, dict) and hook_result.get(
                    "prevent_default"
                ):
                    return True
        return False

    async def _handle_key_press(self, key_press: KeyPress) -> None:
        """Handle a parsed key press.

        Args:
            key_press: Parsed key press event.
        """
        # Process key press
        try:
            # Log all key presses for debugging
            logger.info(
                f"🔍 Key press: name='{key_press.name}', "
                f"char='{key_press.char}', code={key_press.code}, "
                f"type={key_press.type}, "
                f"modifiers={getattr(key_press, 'modifiers', None)}"
            )

            # CRITICAL FIX: Modal input isolation
            # capture ALL input when in modal mode
            if self.command_mode == CommandMode.MODAL:
                logger.info(
                    f"🎯 Modal mode active - routing ALL input "
                    f"to modal handler: {key_press.name}"
                )
                await self._handle_command_mode_keypress(key_press)
                return

            # Handle control keys
            if self.key_parser.is_control_key(key_press, "Ctrl+C"):
                logger.info("Ctrl+C received")
                raise KeyboardInterrupt

            elif self.key_parser.is_control_key(key_press, "Enter"):
                await self._handle_enter()

            elif self.key_parser.is_control_key(key_press, "Backspace"):
                self.buffer_manager.delete_char()

            elif key_press.name == "Escape":
                await self._handle_escape()

            elif key_press.name == "Delete":
                self.buffer_manager.delete_forward()

            # Handle arrow keys for cursor movement and history
            elif key_press.name == "ArrowLeft":
                moved = self.buffer_manager.move_cursor("left")
                if moved:
                    logger.debug(
                        f"Arrow Left: cursor moved to position {self.buffer_manager.cursor_position}"
                    )
                    await self._update_display(force_render=True)

            elif key_press.name == "ArrowRight":
                moved = self.buffer_manager.move_cursor("right")
                if moved:
                    logger.debug(
                        f"Arrow Right: cursor moved to position {self.buffer_manager.cursor_position}"
                    )
                    await self._update_display(force_render=True)

            elif key_press.name == "ArrowUp":
                self.buffer_manager.navigate_history("up")
                await self._update_display(force_render=True)

            elif key_press.name == "ArrowDown":
                self.buffer_manager.navigate_history("down")
                await self._update_display(force_render=True)

            # Handle Home/End keys
            elif key_press.name == "Home":
                self.buffer_manager.move_to_start()
                await self._update_display(force_render=True)

            elif key_press.name == "End":
                self.buffer_manager.move_to_end()
                await self._update_display(force_render=True)

            # Handle Option+comma/period keys for status view navigation
            elif key_press.char == "≤":  # Option+comma
                logger.info(
                    "🔑 Option+Comma (≤) detected - switching to previous status view"
                )
                await self._handle_status_view_previous()

            elif key_press.char == "≥":  # Option+period
                logger.info(
                    "🔑 Option+Period (≥) detected - switching to next status view"
                )
                await self._handle_status_view_next()

            # Handle Cmd key combinations (mapped to Ctrl sequences on macOS)
            elif self.key_parser.is_control_key(key_press, "Ctrl+A"):
                logger.info("🔑 Ctrl+A (Cmd+Left) - moving cursor to start")
                self.buffer_manager.move_to_start()
                await self._update_display(force_render=True)

            elif self.key_parser.is_control_key(key_press, "Ctrl+E"):
                logger.info("🔑 Ctrl+E (Cmd+Right) - moving cursor to end")
                self.buffer_manager.move_to_end()
                await self._update_display(force_render=True)

            elif self.key_parser.is_control_key(key_press, "Ctrl+U"):
                logger.info("🔑 Ctrl+U (Cmd+Backspace) - clearing line")
                self.buffer_manager.clear()
                await self._update_display(force_render=True)

            # Handle printable characters
            elif self.key_parser.is_printable_char(key_press):
                # Normal character processing
                success = self.buffer_manager.insert_char(key_press.char)
                if not success:
                    await self.error_handler.handle_error(
                        ErrorType.BUFFER_ERROR,
                        "Failed to insert character - buffer limit reached",
                        ErrorSeverity.LOW,
                        {
                            "char": key_press.char,
                            "buffer_manager": self.buffer_manager,
                        },
                    )

            # Handle other special keys (F1-F12, etc.)
            elif key_press.type == KeyTypeEnum.EXTENDED:
                logger.debug(f"Extended key pressed: {key_press.name}")
                # Could emit special events for function keys, etc.

        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling key press: {e}",
                ErrorSeverity.MEDIUM,
                {
                    "key_press": key_press,
                    "buffer_manager": self.buffer_manager,
                },
            )

    async def _update_display(self, force_render: bool = False) -> None:
        """Update the terminal display with current buffer state."""
        try:
            # Skip rendering if paused (during special effects like Matrix)
            if self.rendering_paused and not force_render:
                return

            buffer_content, cursor_pos = self.buffer_manager.get_display_info()

            # Update renderer with buffer content and cursor position
            self.renderer.input_buffer = buffer_content
            self.renderer.cursor_position = cursor_pos

            # Force immediate rendering if requested (needed for paste operations)
            if force_render:
                try:
                    if hasattr(
                        self.renderer, "render_active_area"
                    ) and asyncio.iscoroutinefunction(
                        self.renderer.render_active_area
                    ):
                        await self.renderer.render_active_area()
                    elif hasattr(
                        self.renderer, "render_input"
                    ) and asyncio.iscoroutinefunction(self.renderer.render_input):
                        await self.renderer.render_input()
                    elif hasattr(self.renderer, "render_active_area"):
                        self.renderer.render_active_area()
                    elif hasattr(self.renderer, "render_input"):
                        self.renderer.render_input()
                except Exception as e:
                    logger.debug(f"Force render failed: {e}")
                    # Continue without forced render

            # Only update cursor if position changed
            if cursor_pos != self._last_cursor_pos:
                # Could implement cursor positioning in renderer
                self._last_cursor_pos = cursor_pos

        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.SYSTEM_ERROR,
                f"Error updating display: {e}",
                ErrorSeverity.LOW,
                {"buffer_manager": self.buffer_manager},
            )

    def pause_rendering(self):
        """Pause all UI rendering for special effects."""
        self.rendering_paused = True
        logger.debug("Input rendering paused")

    def resume_rendering(self):
        """Resume normal UI rendering."""
        self.rendering_paused = False
        logger.debug("Input rendering resumed")

    async def _handle_enter(self) -> None:
        """Handle Enter key press with enhanced validation."""
        try:
            if self.buffer_manager.is_empty:
                return

            # Validate input before processing
            validation_errors = self.buffer_manager.validate_content()
            if validation_errors:
                for error in validation_errors:
                    logger.warning(f"Input validation warning: {error}")

            # Get message and clear buffer
            message = self.buffer_manager.get_content_and_clear()

            # GENIUS PASTE BUCKET: Immediate expansion - no waiting needed!
            logger.debug(f"GENIUS SUBMIT: Original message: '{message}'")
            logger.debug(
                f"GENIUS SUBMIT: Paste bucket contains: {list(self._paste_bucket.keys())}"
            )

            expanded_message = self._expand_paste_placeholders(message)
            logger.debug(
                f"GENIUS SUBMIT: Final expanded: '{expanded_message[:100]}...' ({len(expanded_message)} chars)"
            )

            # Add to history (with expanded content)
            self.buffer_manager.add_to_history(expanded_message)

            # Update renderer
            self.renderer.input_buffer = ""
            self.renderer.clear_active_area()

            # Emit user input event (with expanded content!)
            await self.event_bus.emit_with_hooks(
                EventType.USER_INPUT,
                {
                    "message": expanded_message,
                    "validation_errors": validation_errors,
                },
                "user",
            )

            logger.debug(
                f"Processed user input: {message[:100]}..."
                if len(message) > 100
                else f"Processed user input: {message}"
            )

        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling Enter key: {e}",
                ErrorSeverity.HIGH,
                {"buffer_manager": self.buffer_manager},
            )

    async def _handle_escape(self) -> None:
        """Handle Escape key press for request cancellation."""
        try:
            logger.info("_handle_escape called - emitting CANCEL_REQUEST event")

            # Emit cancellation event
            result = await self.event_bus.emit_with_hooks(
                EventType.CANCEL_REQUEST,
                {"reason": "user_escape", "source": "input_handler"},
                "input",
            )

            logger.info(
                f"ESC key pressed - cancellation request sent, result: {result}"
            )

        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling Escape key: {e}",
                ErrorSeverity.MEDIUM,
                {"buffer_manager": self.buffer_manager},
            )

    async def _handle_status_view_previous(self) -> None:
        """Handle comma key press for previous status view."""
        try:
            logger.info("Attempting to switch to previous status view")
            # Check if renderer has a status registry
            if (
                hasattr(self.renderer, "status_renderer")
                and self.renderer.status_renderer
            ):
                status_renderer = self.renderer.status_renderer
                logger.info(
                    f"[OK] Found status_renderer: {type(status_renderer).__name__}"
                )
                if (
                    hasattr(status_renderer, "status_registry")
                    and status_renderer.status_registry
                ):
                    registry = status_renderer.status_registry
                    logger.info(
                        f"[OK] Found status_registry with {len(registry.views)} views"
                    )
                    if hasattr(registry, "cycle_previous"):
                        previous_view = registry.cycle_previous()
                        if previous_view:
                            logger.info(
                                f"[OK] Switched to previous status view: '{previous_view.name}'"
                            )
                        else:
                            logger.info("No status views available to cycle to")
                    else:
                        logger.info("cycle_previous method not found in registry")
                else:
                    logger.info("No status registry available for view cycling")
            else:
                logger.info("No status renderer available for view cycling")

        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling status view previous: {e}",
                ErrorSeverity.LOW,
                {"key": "Ctrl+ArrowLeft"},
            )

    async def _handle_status_view_next(self) -> None:
        """Handle Ctrl+Right arrow key press for next status view."""
        try:
            # Check if renderer has a status registry
            if (
                hasattr(self.renderer, "status_renderer")
                and self.renderer.status_renderer
            ):
                status_renderer = self.renderer.status_renderer
                if (
                    hasattr(status_renderer, "status_registry")
                    and status_renderer.status_registry
                ):
                    next_view = status_renderer.status_registry.cycle_next()
                    if next_view:
                        logger.debug(
                            f"Switched to next status view: '{next_view.name}'"
                        )
                    else:
                        logger.debug("No status views available to cycle to")
                else:
                    logger.debug("No status registry available for view cycling")
            else:
                logger.debug("No status renderer available for view cycling")

        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling status view next: {e}",
                ErrorSeverity.LOW,
                {"key": "Ctrl+ArrowRight"},
            )

    def get_status(self) -> Dict[str, Any]:
        """Get current input handler status for debugging.

        Returns:
            Dictionary containing status information.
        """
        buffer_stats = self.buffer_manager.get_stats()
        error_stats = self.error_handler.get_error_stats()

        return {
            "running": self.running,
            "buffer": buffer_stats,
            "errors": error_stats,
            "parser_state": {
                "in_escape_sequence": self.key_parser._in_escape_sequence,
                "escape_buffer": self.key_parser._escape_buffer,
            },
        }

    async def cleanup(self) -> None:
        """Perform cleanup operations."""
        try:
            # Clear old errors
            cleared_errors = self.error_handler.clear_old_errors()
            if cleared_errors > 0:
                logger.info(f"Cleaned up {cleared_errors} old errors")

            # Reset parser state
            self.key_parser._reset_escape_state()

            logger.debug("Input handler cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _expand_paste_placeholders(self, message: str) -> str:
        """Expand paste placeholders with actual content from paste bucket.

        Your brilliant idea: Replace [⚡ Pasted #N ...] with actual pasted content!
        """
        logger.debug(f"PASTE DEBUG: Expanding message: '{message}'")
        logger.debug(
            f"PASTE DEBUG: Paste bucket contains: {list(self._paste_bucket.keys())}"
        )

        expanded = message

        # Find and replace each paste placeholder
        import re

        for paste_id, content in self._paste_bucket.items():
            # Extract paste number from paste_id (PASTE_1 -> 1)
            paste_num = paste_id.split("_")[1]

            # Pattern to match: [Pasted #N X lines, Y chars]
            pattern = rf"\[Pasted #{paste_num} \d+ lines?, \d+ chars\]"

            logger.debug(f"PASTE DEBUG: Looking for pattern: {pattern}")
            logger.debug(
                f"PASTE DEBUG: Will replace with content: '{content[:50]}...'"
            )

            # Replace with actual content
            matches = re.findall(pattern, expanded)
            logger.debug(f"PASTE DEBUG: Found {len(matches)} matches")

            expanded = re.sub(pattern, content, expanded)

        logger.debug(f"PASTE DEBUG: Final expanded message: '{expanded[:100]}...'")
        logger.info(
            f"Paste expansion: {len(self._paste_bucket)} placeholders expanded"
        )

        # Clear paste bucket after expansion (one-time use)
        self._paste_bucket.clear()

        return expanded

    async def _create_paste_placeholder(self, paste_id: str) -> None:
        """Create placeholder for paste - GENIUS IMMEDIATE VERSION."""
        content = self._paste_bucket[paste_id]

        # Create elegant placeholder for user to see
        line_count = content.count("\n") + 1 if "\n" in content else 1
        char_count = len(content)
        paste_num = paste_id.split("_")[1]  # Extract number from PASTE_1
        placeholder = f"[Pasted #{paste_num} {line_count} lines, {char_count} chars]"

        # Insert placeholder into buffer (what user sees)
        for char in placeholder:
            self.buffer_manager.insert_char(char)

        logger.info(
            f"GENIUS: Created placeholder for {char_count} chars as {paste_id}"
        )

        # Update display once at the end
        await self._update_display(force_render=True)

    async def _update_paste_placeholder(self) -> None:
        """Update existing placeholder when paste grows - GENIUS VERSION."""
        # For now, just log - updating existing placeholder is complex
        # The merge approach usually works fast enough that this isn't needed
        content = self._paste_bucket[self._current_paste_id]
        logger.info(
            f"GENIUS: Updated {self._current_paste_id} to {len(content)} chars"
        )

    async def _simple_paste_detection(self, char: str, current_time: float) -> bool:
        """Simple, reliable paste detection using timing only.

        Returns:
            True if character was consumed by paste detection, False otherwise.
        """
        # Check cooldown to prevent overlapping paste detections
        if self._paste_cooldown > 0 and (current_time - self._paste_cooldown) < 1.0:
            # Still in cooldown period, skip paste detection
            self._last_char_time = current_time
            return False

        # Check if we have a pending paste buffer that timed out
        if self._paste_buffer and self._last_char_time > 0:
            gap_ms = (current_time - self._last_char_time) * 1000

            if gap_ms > self._paste_timeout_ms:
                # Buffer timed out, process it
                if len(self._paste_buffer) >= self.paste_min_chars:
                    self._process_simple_paste_sync()
                    self._paste_cooldown = current_time  # Set cooldown
                else:
                    # Too few chars, process them as individual keystrokes
                    self._flush_paste_buffer_as_keystrokes_sync()
                self._paste_buffer = []

        # Now handle the current character
        if self._last_char_time > 0:
            gap_ms = (current_time - self._last_char_time) * 1000

            # If character arrived quickly, start/continue paste buffer
            if gap_ms < self.paste_threshold_ms:
                self._paste_buffer.append(char)
                self._last_char_time = current_time
                return True  # Character consumed by paste buffer

        # Character not part of paste, process normally
        self._last_char_time = current_time
        return False

    def _flush_paste_buffer_as_keystrokes_sync(self) -> None:
        """Process paste buffer contents as individual keystrokes (sync version)."""
        logger.debug(
            f"Flushing {len(self._paste_buffer)} chars as individual keystrokes"
        )

        # Just add characters to buffer without async processing
        for char in self._paste_buffer:
            if char.isprintable() or char in [" ", "\t"]:
                self.buffer_manager.insert_char(char)

    def _process_simple_paste_sync(self) -> None:
        """Process detected paste content (sync version with inline indicator)."""
        if not self._paste_buffer:
            return

        # Get the content and clean any terminal markers
        content = "".join(self._paste_buffer)

        # Clean bracketed paste markers if present
        if content.startswith("[200~"):
            content = content[5:]
        if content.endswith("01~"):
            content = content[:-3]
        elif content.endswith("[201~"):
            content = content[:-6]

        # Count lines
        line_count = content.count("\n") + 1
        char_count = len(content)

        # Increment paste counter
        self._paste_counter += 1

        # Create inline paste indicator exactly as user requested
        indicator = f"[⚡ Pasted #{self._paste_counter} {line_count} lines]"

        # Insert the indicator into the buffer at current position
        try:
            for char in indicator:
                self.buffer_manager.insert_char(char)
            logger.info(
                f"Paste #{self._paste_counter}: {char_count} chars, {line_count} lines"
            )
        except Exception as e:
            logger.error(f"Paste processing error: {e}")

        # Clear paste buffer
        self._paste_buffer = []

    async def _flush_paste_buffer_as_keystrokes(self) -> None:
        """Process paste buffer contents as individual keystrokes."""
        self._flush_paste_buffer_as_keystrokes_sync()

    async def _process_simple_paste(self) -> None:
        """Process detected paste content."""
        self._process_simple_paste_sync()
        await self._update_display(force_render=True)

    # ==================== COMMAND MENU RENDER HOOK ====================

    async def _register_command_menu_render_hook(self) -> None:
        """Register hook to provide command menu content for COMMAND_MENU_RENDER events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority

                hook = Hook(
                    name="command_menu_render",
                    plugin_name="input_handler",
                    event_type=EventType.COMMAND_MENU_RENDER,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_command_menu_render,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info(
                        "Successfully registered COMMAND_MENU_RENDER hook for command menu display"
                    )
                else:
                    logger.error("Failed to register COMMAND_MENU_RENDER hook")
        except Exception as e:
            logger.error(f"Failed to register COMMAND_MENU_RENDER hook: {e}")

    async def _handle_command_menu_render(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle COMMAND_MENU_RENDER events to provide command menu content.

        Args:
            event_data: Event data containing render request info.

        Returns:
            Dictionary with menu_lines if command mode is active.
        """
        try:
            # Only provide command menu if we're in menu popup mode
            if (
                self.command_mode == CommandMode.MENU_POPUP
                and self.command_menu_active
                and hasattr(self.command_menu_renderer, "current_menu_lines")
                and self.command_menu_renderer.current_menu_lines
            ):

                return {"menu_lines": self.command_menu_renderer.current_menu_lines}

            # No command menu to display
            return {}

        except Exception as e:
            logger.error(f"Error in COMMAND_MENU_RENDER handler: {e}")
            return {}

    async def _register_modal_trigger_hook(self) -> None:
        """Register hook to handle modal trigger events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority, EventType

                hook = Hook(
                    name="modal_trigger",
                    plugin_name="input_handler",
                    event_type=EventType.MODAL_TRIGGER,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_modal_trigger,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info("Successfully registered MODAL_TRIGGER hook")
                else:
                    logger.error("Failed to register MODAL_TRIGGER hook")
        except Exception as e:
            logger.error(f"Failed to register MODAL_TRIGGER hook: {e}")

    async def _register_status_modal_trigger_hook(self) -> None:
        """Register hook to handle status modal trigger events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority, EventType

                hook = Hook(
                    name="status_modal_trigger",
                    plugin_name="input_handler",
                    event_type=EventType.STATUS_MODAL_TRIGGER,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_status_modal_trigger,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info("Successfully registered STATUS_MODAL_TRIGGER hook")
                else:
                    logger.error("Failed to register STATUS_MODAL_TRIGGER hook")
        except Exception as e:
            logger.error(f"Failed to register STATUS_MODAL_TRIGGER hook: {e}")

    async def _register_status_modal_render_hook(self) -> None:
        """Register hook to handle status modal render events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority, EventType

                hook = Hook(
                    name="status_modal_render",
                    plugin_name="input_handler",
                    event_type=EventType.STATUS_MODAL_RENDER,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_status_modal_render,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info("Successfully registered STATUS_MODAL_RENDER hook")
                else:
                    logger.error("Failed to register STATUS_MODAL_RENDER hook")
        except Exception as e:
            logger.error(f"Failed to register STATUS_MODAL_RENDER hook: {e}")

    async def _register_command_output_display_hook(self) -> None:
        """Register hook to handle command output display events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority, EventType

                hook = Hook(
                    name="command_output_display",
                    plugin_name="input_handler",
                    event_type=EventType.COMMAND_OUTPUT_DISPLAY,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_command_output_display,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info(
                        "Successfully registered COMMAND_OUTPUT_DISPLAY hook"
                    )
                else:
                    logger.error("Failed to register COMMAND_OUTPUT_DISPLAY hook")
        except Exception as e:
            logger.error(f"Failed to register COMMAND_OUTPUT_DISPLAY hook: {e}")

        # Register pause/resume rendering hooks
        await self._register_pause_rendering_hook()
        await self._register_resume_rendering_hook()

        # Register modal hide hook for Matrix effect cleanup
        await self._register_modal_hide_hook()

    async def _register_pause_rendering_hook(self) -> None:
        """Register hook for pause rendering events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority, EventType

                hook = Hook(
                    name="pause_rendering",
                    plugin_name="input_handler",
                    event_type=EventType.PAUSE_RENDERING,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_pause_rendering,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info("Successfully registered PAUSE_RENDERING hook")
                else:
                    logger.error("Failed to register PAUSE_RENDERING hook")
        except Exception as e:
            logger.error(f"Error registering PAUSE_RENDERING hook: {e}")

    async def _register_resume_rendering_hook(self) -> None:
        """Register hook for resume rendering events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority, EventType

                hook = Hook(
                    name="resume_rendering",
                    plugin_name="input_handler",
                    event_type=EventType.RESUME_RENDERING,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_resume_rendering,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info("Successfully registered RESUME_RENDERING hook")
                else:
                    logger.error("Failed to register RESUME_RENDERING hook")
        except Exception as e:
            logger.error(f"Error registering RESUME_RENDERING hook: {e}")

    async def _handle_pause_rendering(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle pause rendering event."""
        logger.info("🛑 PAUSE_RENDERING event received - pausing input rendering")
        self.rendering_paused = True
        return {"status": "paused"}

    async def _handle_resume_rendering(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle resume rendering event."""
        logger.info("▶️ RESUME_RENDERING event received - resuming input rendering")
        self.rendering_paused = False
        # Force a refresh when resuming
        await self._update_display(force_render=True)
        return {"status": "resumed"}

    async def _register_modal_hide_hook(self) -> None:
        """Register hook for modal hide events."""
        try:
            if self.event_bus:
                from ..events.models import Hook, HookPriority, EventType

                hook = Hook(
                    name="modal_hide",
                    plugin_name="input_handler",
                    event_type=EventType.MODAL_HIDE,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_modal_hide,
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    logger.info("Successfully registered MODAL_HIDE hook")
                else:
                    logger.error("Failed to register MODAL_HIDE hook")
        except Exception as e:
            logger.error(f"Error registering MODAL_HIDE hook: {e}")

    async def _handle_modal_hide(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle modal hide event to exit modal mode."""
        logger.info("🔄 MODAL_HIDE event received - exiting modal mode")
        try:
            from ..events.models import CommandMode

            # CRITICAL FIX: Clear input area before restoring (like config modal does)
            self.renderer.clear_active_area()
            self.renderer.writing_messages = False

            self.command_mode = CommandMode.NORMAL
            # CRITICAL FIX: Clear fullscreen session flag when exiting modal
            if hasattr(self, "_fullscreen_session_active"):
                self._fullscreen_session_active = False
                logger.info("🔄 Fullscreen session marked as inactive")
            logger.info("🔄 Command mode reset to NORMAL after modal hide")

            # Force refresh of display when exiting modal mode
            await self._update_display(force_render=True)
            return {"success": True, "modal_deactivated": True}
        except Exception as e:
            logger.error(f"Error handling modal hide: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_command_output_display(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle command output display events.

        Args:
            event_data: Event data containing command output information.
            context: Hook execution context.

        Returns:
            Dictionary with display result.
        """
        try:
            message = event_data.get("message", "")
            display_type = event_data.get("display_type", "info")
            _ = event_data.get("success", True)

            if message:
                # Format message based on display type
                if display_type == "error":
                    formatted_message = f"❌ {message}"
                elif display_type == "warning":
                    formatted_message = f"⚠️  {message}"
                elif display_type == "success":
                    formatted_message = f"✅ {message}"
                else:  # info or default
                    formatted_message = f"ℹ️  {message}"

                # CRITICAL FIX: Prevent input bar duplication during command output
                # Set writing_messages flag to prevent input rendering conflicts
                self.renderer.writing_messages = True

                # Clear the active input area first
                self.renderer.clear_active_area()

                # CRITICAL FIX: Use write_hook_message to avoid ∴ prefix on command output
                self.renderer.write_hook_message(
                    formatted_message,
                    display_type=display_type,
                    source="command",
                )

                # Reset the writing flag to allow input rendering again
                self.renderer.writing_messages = False

                # Force a display update to ensure message appears
                await self._update_display(force_render=True)

                logger.info(f"Command output displayed: {display_type}")

            return {
                "success": True,
                "action": "command_output_displayed",
                "display_type": display_type,
            }

        except Exception as e:
            logger.error(f"Error handling command output display: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_modal_trigger(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle modal trigger events to show modals.

        Args:
            event_data: Event data containing modal configuration.

        Returns:
            Dictionary with modal result.
        """
        try:
            # Check if this is a Matrix effect trigger
            if event_data.get("matrix_effect"):
                logger.info(
                    "🎯 Matrix effect modal trigger received - setting modal mode for complete terminal control"
                )
                # Set modal mode directly for Matrix effect (no UI config needed)
                from ..events.models import CommandMode

                self.command_mode = CommandMode.MODAL
                logger.info("🎯 Command mode set to MODAL for Matrix effect")
                return {
                    "success": True,
                    "modal_activated": True,
                    "matrix_mode": True,
                }

            # Check if this is a full-screen plugin trigger
            if event_data.get("fullscreen_plugin"):
                plugin_name = event_data.get("plugin_name", "unknown")
                logger.info(
                    f"🎯 Full-screen plugin modal trigger received: {plugin_name}"
                )

                # CRITICAL FIX: Clear input area before fullscreen mode (like config modal does)
                self.renderer.writing_messages = True
                self.renderer.clear_active_area()

                # Set modal mode for full-screen plugin (no UI config needed)
                from ..events.models import CommandMode

                self.command_mode = CommandMode.MODAL
                # CRITICAL FIX: Mark fullscreen session as active for input routing
                self._fullscreen_session_active = True
                logger.info(
                    f"🎯 Command mode set to MODAL for full-screen plugin: {plugin_name}"
                )
                logger.info(
                    "🎯 Fullscreen session marked as active for input routing"
                )
                return {
                    "success": True,
                    "modal_activated": True,
                    "fullscreen_plugin": True,
                    "plugin_name": plugin_name,
                }

            # Standard modal with UI config
            ui_config = event_data.get("ui_config")
            if ui_config:
                logger.info(f"🎯 Modal trigger received: {ui_config.title}")
                await self._enter_modal_mode(ui_config)
                return {"success": True, "modal_activated": True}
            else:
                logger.warning("Modal trigger received without ui_config")
                return {"success": False, "error": "Missing ui_config"}

        except Exception as e:
            logger.error(f"Error handling modal trigger: {e}")
            return {"success": False, "error": str(e)}

    # ==================== SLASH COMMAND SYSTEM ====================

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
            available_commands = self._get_available_commands()
            self.command_menu_renderer.show_command_menu(available_commands, "")

            # Emit command menu show event
            await self.event_bus.emit_with_hooks(
                EventType.COMMAND_MENU_SHOW,
                {"available_commands": available_commands, "filter_text": ""},
                "commands",
            )

            # Update display to show command mode
            await self._update_display(force_render=True)

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
                await self.event_bus.emit_with_hooks(
                    EventType.COMMAND_MENU_HIDE,
                    {"reason": "manual_exit"},
                    "commands",
                )

            self.command_mode = CommandMode.NORMAL
            self.command_menu_active = False

            # Clear command buffer (remove the '/' and any partial command)
            self.buffer_manager.clear()

            # Update display
            await self._update_display(force_render=True)

            logger.info("Returned to normal input mode")

        except Exception as e:
            logger.error(f"Error exiting command mode: {e}")

    async def _handle_command_mode_keypress(self, key_press: KeyPress) -> bool:
        """Handle KeyPress while in command mode (supports arrow keys).

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled, False to fall through to normal processing.
        """
        try:
            if self.command_mode == CommandMode.MENU_POPUP:
                return await self._handle_menu_popup_keypress(key_press)
            elif self.command_mode == CommandMode.STATUS_TAKEOVER:
                return await self._handle_status_takeover_keypress(key_press)
            elif self.command_mode == CommandMode.MODAL:
                return await self._handle_modal_keypress(key_press)
            elif self.command_mode == CommandMode.STATUS_MODAL:
                return await self._handle_status_modal_keypress(key_press)
            else:
                # Unknown command mode, exit to normal
                await self._exit_command_mode()
                return False

        except Exception as e:
            logger.error(f"Error handling command mode keypress: {e}")
            await self._exit_command_mode()
            return False

    async def _handle_command_mode_input(self, char: str) -> bool:
        """Handle input while in command mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled, False to fall through to normal processing.
        """
        try:
            if self.command_mode == CommandMode.MENU_POPUP:
                return await self._handle_menu_popup_input(char)
            elif self.command_mode == CommandMode.STATUS_TAKEOVER:
                return await self._handle_status_takeover_input(char)
            elif self.command_mode == CommandMode.STATUS_MODAL:
                return await self._handle_status_modal_input(char)
            else:
                # Unknown command mode, exit to normal
                await self._exit_command_mode()
                return False

        except Exception as e:
            logger.error(f"Error handling command mode input: {e}")
            await self._exit_command_mode()
            return False

    async def _handle_menu_popup_input(self, char: str) -> bool:
        """Handle input during menu popup mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled.
        """
        # Handle special keys first
        if ord(char) == 27:  # Escape key
            await self._exit_command_mode()
            return True
        elif ord(char) == 13:  # Enter key
            await self._execute_selected_command()
            return True
        elif ord(char) == 8 or ord(char) == 127:  # Backspace or Delete
            # If buffer only has '/', exit command mode
            if len(self.buffer_manager.content) <= 1:
                await self._exit_command_mode()
                return True
            else:
                # Remove character and update command filter
                self.buffer_manager.delete_char()
                await self._update_command_filter()
                return True

        # Handle printable characters (add to command filter)
        if char.isprintable():
            self.buffer_manager.insert_char(char)
            await self._update_command_filter()
            return True

        # Let other keys fall through for now
        return False

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

    async def _handle_status_takeover_input(self, char: str) -> bool:
        """Handle input during status area takeover mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled.
        """
        # For now, just handle Escape to exit
        if ord(char) == 27:  # Escape key
            await self._exit_command_mode()
            return True

        # TODO: Implement status area navigation
        return True

    async def _handle_status_takeover_keypress(self, key_press: KeyPress) -> bool:
        """Handle KeyPress during status area takeover mode.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled.
        """
        # For now, just handle Escape to exit
        if key_press.name == "Escape":
            await self._exit_command_mode()
            return True

        # TODO: Implement status area navigation
        return True

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
                    from ..events.models import CommandMode

                    self.command_mode = CommandMode.NORMAL
                    await self._update_display(force_render=True)
                    return True

                # Route input to fullscreen session through event bus
                from ..events.models import EventType

                await self.event_bus.emit_with_hooks(
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

    async def _enter_modal_mode(self, ui_config):
        """Enter modal mode and show modal renderer.

        Args:
            ui_config: Modal configuration.
        """
        try:
            # Import modal renderer here to avoid circular imports
            from ..ui.modal_renderer import ModalRenderer

            # Create modal renderer instance with proper config service
            self.modal_renderer = ModalRenderer(
                terminal_renderer=self.renderer,
                visual_effects=getattr(self.renderer, "visual_effects", None),
                config_service=self.config,  # Use config as config service
            )

            # CRITICAL FIX: Clear input area before modal to prevent duplication
            self.renderer.writing_messages = True
            self.renderer.clear_active_area()

            # Set modal mode FIRST
            self.command_mode = CommandMode.MODAL
            logger.info(f"🎯 Command mode set to: {self.command_mode}")

            # Show the modal with alternate buffer
            logger.info(
                "🔧 DIRECT: About to call show_modal - this should trigger alternate buffer"
            )
            await self.modal_renderer.show_modal(ui_config)

            # Reset writing flag (modal will handle its own rendering from here)
            self.renderer.writing_messages = False

            logger.info("🎯 Entered modal mode with persistent input loop")

        except Exception as e:
            logger.error(f"Error entering modal mode: {e}")
            self.command_mode = CommandMode.NORMAL

    async def _refresh_modal_display(self):
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

    async def _save_and_exit_modal(self):
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

    async def _exit_modal_mode(self):
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
            await self._update_display(force_render=True)

            # Ensure cursor is properly positioned
            # Note: cursor management handled by terminal_state

        except Exception as e:
            logger.error(f"Error exiting modal mode: {e}")
            self.command_mode = CommandMode.NORMAL
            self.modal_renderer = None
            # Emergency cleanup
            self.renderer.clear_active_area()

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
            filtered_commands = self._filter_commands(filter_text)

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

    async def _update_command_filter(self) -> None:
        """Update command menu based on current buffer content."""
        try:
            # Get current input (minus the leading '/')
            current_input = self.buffer_manager.content
            filter_text = (
                current_input[1:] if current_input.startswith("/") else current_input
            )

            # Update menu renderer with filtered commands
            filtered_commands = self._filter_commands(filter_text)

            # Reset selection when filtering
            self.selected_command_index = 0
            self.command_menu_renderer.set_selected_index(
                self.selected_command_index
            )
            self.command_menu_renderer.filter_commands(
                filtered_commands, filter_text
            )

            # Emit filter update event
            await self.event_bus.emit_with_hooks(
                EventType.COMMAND_MENU_FILTER,
                {
                    "filter_text": filter_text,
                    "available_commands": self._get_available_commands(),
                    "filtered_commands": filtered_commands,
                },
                "commands",
            )

            # Update display
            await self._update_display(force_render=True)

        except Exception as e:
            logger.error(f"Error updating command filter: {e}")

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

                # Execute the command
                result = await self.command_executor.execute_command(
                    command, self.event_bus
                )

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

    def _get_available_commands(self) -> List[Dict[str, Any]]:
        """Get list of available commands for menu display.

        Returns:
            List of command dictionaries for menu rendering.
        """
        commands = []
        command_defs = self.command_registry.list_commands()

        for cmd_def in command_defs:
            commands.append(
                {
                    "name": cmd_def.name,
                    "description": cmd_def.description,
                    "aliases": cmd_def.aliases,
                    "category": cmd_def.category.value,
                    "plugin": cmd_def.plugin_name,
                    "icon": cmd_def.icon,
                }
            )

        return commands

    def _filter_commands(self, filter_text: str) -> List[Dict[str, Any]]:
        """Filter commands based on input text.

        Args:
            filter_text: Text to filter commands by.

        Returns:
            List of filtered command dictionaries.
        """
        if not filter_text:
            return self._get_available_commands()

        # Use registry search functionality
        matching_defs = self.command_registry.search_commands(filter_text)

        filtered_commands = []
        for cmd_def in matching_defs:
            filtered_commands.append(
                {
                    "name": cmd_def.name,
                    "description": cmd_def.description,
                    "aliases": cmd_def.aliases,
                    "category": cmd_def.category.value,
                    "plugin": cmd_def.plugin_name,
                    "icon": cmd_def.icon,
                }
            )

        return filtered_commands

    # ==================== STATUS MODAL METHODS ====================

    async def _handle_status_modal_trigger(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle status modal trigger events to show status modals.

        Args:
            event_data: Event data containing modal configuration.
            context: Hook execution context.

        Returns:
            Dictionary with status modal result.
        """
        try:
            ui_config = event_data.get("ui_config")
            if ui_config:
                logger.info(f"Status modal trigger received: {ui_config.title}")
                logger.info(f"Status modal trigger UI config type: {ui_config.type}")
                await self._enter_status_modal_mode(ui_config)
                return {"success": True, "status_modal_activated": True}
            else:
                logger.warning("Status modal trigger received without ui_config")
                return {"success": False, "error": "Missing ui_config"}
        except Exception as e:
            logger.error(f"Error handling status modal trigger: {e}")
            return {"success": False, "error": str(e)}

    async def _enter_status_modal_mode(self, ui_config):
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
            await self._update_display(force_render=True)

        except Exception as e:
            logger.error(f"Error entering status modal mode: {e}")
            await self._exit_command_mode()

    async def _handle_status_modal_keypress(self, key_press: KeyPress) -> bool:
        """Handle keypress during status modal mode.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled, False otherwise.
        """
        try:
            logger.info(
                f"Status modal received key: name='{key_press.name}', char='{key_press.char}', code={key_press.code}"
            )

            if key_press.name == "Escape":
                logger.info("Escape key detected, closing status modal")
                await self._exit_status_modal_mode()
                return True
            elif key_press.name == "Enter":
                logger.info("Enter key detected, closing status modal")
                await self._exit_status_modal_mode()
                return True
            elif key_press.char and ord(key_press.char) == 3:  # Ctrl+C
                logger.info("Ctrl+C detected, closing status modal")
                await self._exit_status_modal_mode()
                return True
            else:
                logger.info(f"Unhandled key in status modal: {key_press.name}")
                return True

        except Exception as e:
            logger.error(f"Error handling status modal keypress: {e}")
            await self._exit_status_modal_mode()
            return False

    async def _handle_status_modal_input(self, char: str) -> bool:
        """Handle input during status modal mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled, False otherwise.
        """
        try:
            # For now, ignore character input in status modals
            # Could add search/filter functionality later
            return True
        except Exception as e:
            logger.error(f"Error handling status modal input: {e}")
            await self._exit_status_modal_mode()
            return False

    async def _exit_status_modal_mode(self):
        """Exit status modal mode and return to normal input."""
        try:
            logger.info("Exiting status modal mode...")
            self.command_mode = CommandMode.NORMAL
            self.current_status_modal_config = None
            logger.info("Status modal mode exited successfully")

            # Refresh display to remove the status modal
            await self._update_display(force_render=True)
            logger.info("Display updated after status modal exit")

        except Exception as e:
            logger.error(f"Error exiting status modal mode: {e}")
            self.command_mode = CommandMode.NORMAL

    async def _handle_status_modal_render(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle status modal render events to provide modal display lines.

        Args:
            event_data: Event data containing render request.
            context: Hook execution context.

        Returns:
            Dictionary with status modal lines if active.
        """
        try:
            if (
                self.command_mode == CommandMode.STATUS_MODAL
                and self.current_status_modal_config
            ):

                # Generate status modal display lines
                modal_lines = self._generate_status_modal_lines(
                    self.current_status_modal_config
                )

                return {"success": True, "status_modal_lines": modal_lines}
            else:
                return {"success": True, "status_modal_lines": []}

        except Exception as e:
            logger.error(f"Error handling status modal render: {e}")
            return {"success": False, "status_modal_lines": []}

    def _generate_status_modal_lines(self, ui_config) -> List[str]:
        """Generate formatted lines for status modal display using visual effects.

        Args:
            ui_config: UI configuration for the status modal.

        Returns:
            List of formatted lines for display.
        """
        try:
            # Get dynamic terminal width
            terminal_width = getattr(self.renderer.terminal_state, "width", 80)
            # Reserve space for borders and padding (│ content │ = 4 chars total)
            content_width = terminal_width - 6  # Leave 6 for borders/padding
            max_line_length = content_width - 4  # Additional safety margin

            content_lines = []

            # Modal content based on config (no duplicate headers)
            modal_config = ui_config.modal_config or {}

            if "sections" in modal_config:
                for section in modal_config["sections"]:
                    # Skip section title since it's redundant with modal title
                    # Display commands directly
                    commands = section.get("commands", [])
                    for cmd in commands:
                        name = cmd.get("name", "")
                        description = cmd.get("description", "")

                        # Format command line with better alignment, using dynamic width
                        cmd_line = f"{name:<28} {description}"
                        if len(cmd_line) > max_line_length:
                            cmd_line = cmd_line[: max_line_length - 3] + "..."

                        content_lines.append(cmd_line)

            # Add spacing before footer
            content_lines.append("")

            # Modal footer with special styling marker
            footer = modal_config.get(
                "footer",
                "Press Esc to close • Use /help <command> for detailed help",
            )
            content_lines.append(f"__FOOTER__{footer}")

            # Clean content lines for box rendering (no ANSI codes)
            clean_content = []
            for line in content_lines:
                if line.startswith("__FOOTER__"):
                    footer_text = line.replace("__FOOTER__", "")
                    clean_content.append(footer_text)
                else:
                    clean_content.append(line)

            # Use BoxRenderer from enhanced input plugin if available
            try:
                from ..plugins.enhanced_input.box_renderer import BoxRenderer
                from ..plugins.enhanced_input.box_styles import (
                    BoxStyleRegistry,
                )
                from ..plugins.enhanced_input.color_engine import ColorEngine
                from ..plugins.enhanced_input.geometry import (
                    GeometryCalculator,
                )
                from ..plugins.enhanced_input.text_processor import (
                    TextProcessor,
                )

                # Initialize components
                style_registry = BoxStyleRegistry()
                color_engine = ColorEngine()
                geometry = GeometryCalculator()
                text_processor = TextProcessor()
                box_renderer = BoxRenderer(
                    style_registry, color_engine, geometry, text_processor
                )

                # Render with clean rounded style first, using dynamic width
                bordered_lines = box_renderer.render_box(
                    clean_content, content_width, "rounded"
                )

                # Add title to top border
                title = ui_config.title or "Status Modal"
                if bordered_lines:
                    _ = bordered_lines[0]
                    # Create title border: ╭─ Title ─────...─╮
                    title_text = f"─ {title} "
                    remaining_width = max(
                        0, content_width - 2 - len(title_text)
                    )  # content_width - 2 border chars - title length
                    titled_border = f"╭{title_text}{'─' * remaining_width}╮"
                    bordered_lines[0] = titled_border

                # Apply styling to content lines after border rendering
                styled_lines = []
                for i, line in enumerate(bordered_lines):
                    if i == 0 or i == len(bordered_lines) - 1:
                        # Border lines - keep as is
                        styled_lines.append(line)
                    elif line.strip() and "│" in line:
                        # Content lines with borders
                        if any(
                            footer in line for footer in ["Press Esc", "Use /help"]
                        ):
                            # Footer line - apply cyan
                            styled_line = line.replace("│", "│\033[2;36m", 1)
                            styled_line = styled_line.replace("│", "\033[0m│", -1)
                            styled_lines.append(styled_line)
                        elif line.strip() != "│" + " " * 76 + "│":  # Not empty line
                            # Command line - apply dim
                            styled_line = line.replace("│", "│\033[2m", 1)
                            styled_line = styled_line.replace("│", "\033[0m│", -1)
                            styled_lines.append(styled_line)
                        else:
                            # Empty line
                            styled_lines.append(line)
                    else:
                        styled_lines.append(line)

                return styled_lines

            except ImportError:
                # Fallback to simple manual borders if enhanced input not available
                return self._create_simple_bordered_content(clean_content)

        except Exception as e:
            logger.error(f"Error generating status modal lines: {e}")
            return [f"Error displaying status modal: {e}"]

    def _create_simple_bordered_content(self, content_lines: List[str]) -> List[str]:
        """Create simple bordered content as fallback.

        Args:
            content_lines: Content lines to border.

        Returns:
            Lines with simple borders.
        """
        # Get dynamic terminal width
        terminal_width = getattr(self.renderer.terminal_state, "width", 80)
        # Reserve space for borders and padding
        width = terminal_width - 6  # Leave 6 for borders/padding
        lines = []

        # Simple top border
        lines.append("╭" + "─" * (width + 2) + "╮")

        # Content with side borders
        for line in content_lines:
            padded_line = f"{line:<{width}}"
            lines.append(f"│ {padded_line} │")

        # Simple bottom border
        lines.append("╰" + "─" * (width + 2) + "╯")

        return lines
