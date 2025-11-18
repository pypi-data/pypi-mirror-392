"""Raw input processing system for Kollabor CLI - extracted from InputHandler."""

import asyncio
import logging
import select
import sys
import time
from typing import Optional, Dict, Any, Callable

from ..events import EventType
from ..events.models import CommandMode
from .key_parser import KeyParser, KeyPress, KeyType as KeyTypeEnum
from .buffer_manager import BufferManager
from .input_errors import InputErrorHandler, ErrorType, ErrorSeverity

logger = logging.getLogger(__name__)


class RawInputProcessor:
    """Handles raw terminal input processing, key parsing, and buffer management.

    This component is responsible for:
    - Main input loop with select() polling
    - Raw data reading and chunking
    - Escape sequence detection
    - Character parsing and key press handling
    - Display updates and cursor management
    - Paste detection integration
    - Basic event processing (Enter, Escape)
    """

    def __init__(
        self,
        event_bus,
        renderer,
        config,
        buffer_manager: BufferManager,
        key_parser: KeyParser,
        error_handler: InputErrorHandler,
    ) -> None:
        """Initialize the raw input processor.

        Args:
            event_bus: Event bus for emitting input events.
            renderer: Terminal renderer for updating input display.
            config: Configuration manager for input settings.
            buffer_manager: Buffer manager for text operations.
            key_parser: Key parser for handling escape sequences.
            error_handler: Error handler for input errors.
        """
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config
        self.buffer_manager = buffer_manager
        self.key_parser = key_parser
        self.error_handler = error_handler

        # Control flags
        self.running = False
        self.rendering_paused = (
            False  # Flag to pause rendering during special effects
        )

        # Load configurable parameters
        self.polling_delay = config.get("input.polling_delay", 0.01)
        self.error_delay = config.get("input.error_delay", 0.1)

        # Paste detection configuration
        self.paste_detection_enabled = False

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

        # Callbacks for delegation back to InputHandler
        self.on_command_mode_keypress: Optional[Callable] = None
        self.on_prevent_default_check: Optional[Callable] = None
        self.get_command_mode: Optional[Callable] = None
        self.on_status_view_previous: Optional[Callable] = None
        self.on_status_view_next: Optional[Callable] = None

        logger.info("Raw input processor initialized")

    def set_callbacks(
        self,
        on_command_mode_keypress: Callable,
        on_prevent_default_check: Callable,
        get_command_mode: Callable,
        on_status_view_previous: Callable,
        on_status_view_next: Callable,
    ) -> None:
        """Set callbacks for delegation back to InputHandler."""
        self.on_command_mode_keypress = on_command_mode_keypress
        self.on_prevent_default_check = on_prevent_default_check
        self.get_command_mode = get_command_mode
        self.on_status_view_previous = on_status_view_previous
        self.on_status_view_next = on_status_view_next

    async def start_input_loop(self) -> None:
        """Start the input processing loop."""
        self.running = True
        await self._input_loop()

    def stop_input_loop(self) -> None:
        """Stop the input processing loop."""
        self.running = False

    def pause_rendering(self):
        """Pause all UI rendering for special effects."""
        self.rendering_paused = True
        logger.debug("Input rendering paused")

    def resume_rendering(self):
        """Resume normal UI rendering."""
        self.rendering_paused = False
        logger.debug("Input rendering resumed")

    async def _input_loop(self) -> None:
        """Main input processing loop with enhanced error handling."""
        while self.running:
            try:
                # Check for available input
                if select.select([sys.stdin], [], [], self.polling_delay)[0]:
                    # Read ALL available data - keep reading until buffer is empty
                    import os

                    chunk = b""
                    while True:
                        try:
                            more_data = os.read(0, 8192)  # Read in 8KB chunks
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
                        """Check if input is an escape sequence that should bypass paste detection."""
                        if not text:
                            return False
                        # Common escape sequences start with ESC (\x1b)
                        if text.startswith("\x1b"):
                            return True
                        return False

                    # If we got multiple characters, check if it's an escape sequence first
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
                        # Escape sequence - process character by character to allow key parser to handle it
                        logger.debug(
                            f"Processing escape sequence character-by-character: {repr(chunk)}"
                        )
                        for char in chunk:
                            await self._process_character(char)
                    else:
                        # Normal input (single or multi-character) - process each character individually
                        logger.info(
                            f"🔤 Processing normal input character-by-character: {repr(chunk)}"
                        )
                        # await self._process_character(chunk)
                        for char in chunk:
                            await self._process_character(char)
                else:
                    # No input available - check for standalone ESC key
                    esc_key = self.key_parser.check_for_standalone_escape()
                    if esc_key and self.on_command_mode_keypress:
                        logger.info("DETECTED STANDALONE ESC KEY!")
                        # CRITICAL FIX: Route escape to command mode handler if in modal mode
                        command_mode = (
                            self.get_command_mode()
                            if self.get_command_mode
                            else CommandMode.NORMAL
                        )
                        if command_mode == CommandMode.MODAL:
                            await self.on_command_mode_keypress(esc_key)
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

            # NOTE: Slash command detection moved to key press level for proper buffer handling

            # Simple paste detection - skip normal processing if character is part of paste
            if self.paste_detection_enabled:
                paste_handled = await self._simple_paste_detection(
                    char, current_time
                )
                if paste_handled:
                    return  # Character consumed by paste detection, skip normal processing

            # Parse character into structured key press (this handles escape sequences)
            key_press = self.key_parser.parse_char(char)
            if not key_press:
                # For modal mode, add timeout-based standalone escape detection
                command_mode = (
                    self.get_command_mode()
                    if self.get_command_mode
                    else CommandMode.NORMAL
                )
                if (
                    command_mode == CommandMode.MODAL
                    and self.on_command_mode_keypress
                ):
                    # Schedule a delayed check for standalone escape (100ms delay)
                    async def delayed_escape_check():
                        await asyncio.sleep(0.1)
                        standalone_escape = (
                            self.key_parser.check_for_standalone_escape()
                        )
                        if standalone_escape:
                            await self.on_command_mode_keypress(standalone_escape)

                    asyncio.create_task(delayed_escape_check())
                return  # Incomplete escape sequence - wait for more characters

            # Check for slash command mode handling AFTER parsing (so arrow keys work)
            command_mode = (
                self.get_command_mode()
                if self.get_command_mode
                else CommandMode.NORMAL
            )
            if command_mode != CommandMode.NORMAL and self.on_command_mode_keypress:
                logger.info(
                    f"🎯 Processing key '{key_press.name}' in command mode: {command_mode}"
                )
                handled = await self.on_command_mode_keypress(key_press)
                if handled:
                    # CRITICAL FIX: Update display after command mode processing
                    await self._update_display()
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
        if self.on_prevent_default_check:
            return self.on_prevent_default_check(key_result)

        # Fallback implementation
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

            # CRITICAL FIX: Command mode input routing - handle ALL command modes
            command_mode = (
                self.get_command_mode()
                if self.get_command_mode
                else CommandMode.NORMAL
            )
            if command_mode != CommandMode.NORMAL and self.on_command_mode_keypress:
                logger.info(
                    f"🎯 Command mode active ({command_mode}) - routing input to command handler: {key_press.name}"
                )
                handled = await self.on_command_mode_keypress(key_press)
                if handled:
                    # CRITICAL FIX: Update display after command mode processing
                    await self._update_display()
                    return

            # LEGACY: Modal input isolation - kept for backward compatibility
            if command_mode == CommandMode.MODAL and self.on_command_mode_keypress:
                logger.info(
                    f"🎯 Modal mode active - routing ALL input to modal handler: {key_press.name}"
                )
                await self.on_command_mode_keypress(key_press)
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
                if self.on_status_view_previous:
                    await self.on_status_view_previous()

            elif key_press.char == "≥":  # Option+period
                logger.info(
                    "🔑 Option+Period (≥) detected - switching to next status view"
                )
                if self.on_status_view_next:
                    await self.on_status_view_next()

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
                else:
                    # Check for slash command initiation AFTER character is in buffer
                    command_mode = (
                        self.get_command_mode()
                        if self.get_command_mode
                        else CommandMode.NORMAL
                    )
                    if (
                        key_press.char == "/"
                        and len(self.buffer_manager.content) == 1
                        and command_mode == CommandMode.NORMAL
                    ):
                        # Slash was just inserted and buffer only contains slash - enter command mode
                        if self.on_command_mode_keypress:
                            # Create a proper key press for slash
                            await self.on_command_mode_keypress(key_press)
                            # CRITICAL FIX: Update display after slash command initiation
                            await self._update_display()
                            return

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
        if (
            hasattr(self, "_paste_cooldown")
            and self._paste_cooldown > 0
            and (current_time - self._paste_cooldown) < 1.0
        ):
            # Still in cooldown period, skip paste detection
            self._last_char_time = current_time
            return False

        # Check if we have a pending paste buffer that timed out
        if self._paste_buffer and self._last_char_time > 0:
            paste_timeout_ms = getattr(self, "_paste_timeout_ms", 50)
            gap_ms = (current_time - self._last_char_time) * 1000

            if gap_ms > paste_timeout_ms:
                # Buffer timed out, process it
                paste_min_chars = getattr(self, "paste_min_chars", 5)
                if len(self._paste_buffer) >= paste_min_chars:
                    self._process_simple_paste_sync()
                    if not hasattr(self, "_paste_cooldown"):
                        self._paste_cooldown = 0
                    self._paste_cooldown = current_time  # Set cooldown
                else:
                    # Too few chars, process them as individual keystrokes
                    self._flush_paste_buffer_as_keystrokes_sync()
                self._paste_buffer = []

        # Now handle the current character
        if self._last_char_time > 0:
            paste_threshold_ms = getattr(self, "paste_threshold_ms", 20)
            gap_ms = (current_time - self._last_char_time) * 1000

            # If character arrived quickly, start/continue paste buffer
            if gap_ms < paste_threshold_ms:
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

    def get_status(self) -> Dict[str, Any]:
        """Get current raw input processor status for debugging.

        Returns:
            Dictionary containing status information.
        """
        return {
            "running": self.running,
            "rendering_paused": self.rendering_paused,
            "paste_detection_enabled": self.paste_detection_enabled,
            "paste_bucket_size": len(self._paste_bucket),
            "paste_counter": self._paste_counter,
            "parser_state": {
                "in_escape_sequence": self.key_parser._in_escape_sequence,
                "escape_buffer": self.key_parser._escape_buffer,
            },
        }

    async def cleanup(self) -> None:
        """Perform cleanup operations."""
        try:
            # Reset parser state
            self.key_parser._reset_escape_state()

            # Clear paste state
            self._paste_buffer = []
            self._paste_bucket.clear()
            self._current_paste_id = None

            logger.debug("Raw input processor cleanup completed")

        except Exception as e:
            logger.error(f"Error during raw input processor cleanup: {e}")
