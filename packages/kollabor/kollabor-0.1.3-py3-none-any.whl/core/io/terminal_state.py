"""Terminal state management for rendering system."""

import logging
import os
import shutil
import signal
import sys
import termios
import time
import tty
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict


logger = logging.getLogger(__name__)


class TerminalMode(Enum):
    """Terminal operating modes."""

    NORMAL = "normal"
    RAW = "raw"
    COOKED = "cooked"


@dataclass
class TerminalCapabilities:
    """Terminal capability detection results."""

    has_color: bool = False
    has_256_color: bool = False
    has_truecolor: bool = False
    width: int = 80
    height: int = 24
    cursor_support: bool = True
    mouse_support: bool = False

    @property
    def color_level(self) -> str:
        """Get the color support level description."""
        if self.has_truecolor:
            return "truecolor"
        elif self.has_256_color:
            return "256color"
        elif self.has_color:
            return "basic"
        else:
            return "monochrome"


class TerminalDetector:
    """Detects terminal capabilities and features."""

    @staticmethod
    def detect_capabilities() -> TerminalCapabilities:
        """Detect terminal capabilities.

        Returns:
            Terminal capabilities information.
        """
        caps = TerminalCapabilities()

        # Detect terminal size
        try:
            size = shutil.get_terminal_size()
            caps.width = size.columns
            caps.height = size.lines
        except Exception as e:
            logger.debug(f"Could not get terminal size: {e}")
            caps.width = 80
            caps.height = 24

        # Detect color support from environment variables
        term = os.environ.get("TERM", "").lower()
        colorterm = os.environ.get("COLORTERM", "").lower()

        # Basic color detection
        caps.has_color = (
            "color" in term
            or "xterm" in term
            or "screen" in term
            or "tmux" in term
            or sys.stdout.isatty()
        )

        # 256 color detection
        caps.has_256_color = (
            "256" in term
            or "256color" in colorterm
            or term in ["xterm-256color", "screen-256color"]
        )

        # True color (24-bit) detection
        caps.has_truecolor = (
            colorterm in ["truecolor", "24bit"]
            or "truecolor" in term
            or os.environ.get("TERM_PROGRAM") in ["iTerm.app", "vscode"]
        )

        # Cursor support (assume yes unless proven otherwise)
        caps.cursor_support = sys.stdout.isatty()

        logger.debug(
            f"Detected terminal capabilities: {caps.color_level} color, "
            f"{caps.width}x{caps.height}"
        )
        return caps


class TerminalState:
    """Manages terminal state, mode, and low-level operations."""

    def __init__(self):
        """Initialize terminal state manager."""
        self.current_mode = TerminalMode.NORMAL
        self.original_termios: Optional[Any] = None
        self.is_terminal = False
        self.capabilities = TerminalCapabilities()

        # State tracking
        self._cursor_hidden = False
        self._last_size = (0, 0)
        self._resize_occurred = False  # Track if terminal resize happened
        self._last_resize_time = 0  # Track when last resize signal arrived
        self._resize_debounce_delay = 0.2  # Wait 200ms for resize to settle

        # Initialize terminal state
        self._initialize_terminal()

        # Set up SIGWINCH handler for terminal resize detection
        self._setup_resize_handler()

    def _initialize_terminal(self) -> None:
        """Initialize terminal and detect capabilities."""
        # Save original terminal settings
        try:
            if sys.stdin.isatty():
                self.original_termios = termios.tcgetattr(sys.stdin)
                self.is_terminal = True
                logger.info("Terminal mode detected and settings saved")
            else:
                logger.info("Non-terminal mode detected")
                self.is_terminal = False
        except Exception as e:
            logger.warning(f"Could not save terminal settings: {e}")
            self.is_terminal = False
            self.original_termios = None

        # Detect terminal capabilities
        self.capabilities = TerminalDetector.detect_capabilities()

    def _setup_resize_handler(self) -> None:
        """Set up SIGWINCH signal handler for terminal resize detection."""
        try:

            def handle_resize(signum, frame):
                """Handle SIGWINCH signal (terminal resize) with debouncing."""
                current_time = time.time()
                self._last_resize_time = current_time
                logger.debug(f"Terminal resize signal received at {current_time}")

            signal.signal(signal.SIGWINCH, handle_resize)
            logger.debug("SIGWINCH handler registered successfully")
        except Exception as e:
            logger.warning(f"Could not set up resize handler: {e}")

    def check_and_clear_resize_flag(self) -> bool:
        """Check if resize occurred and clear the flag (with debouncing).

        Returns:
            True if resize occurred and settled, False otherwise.
        """
        current_time = time.time()

        # Check if resize signal was received
        if self._last_resize_time > 0:
            # Check if enough time has passed since last resize signal (debouncing)
            time_since_resize = current_time - self._last_resize_time

            if time_since_resize >= self._resize_debounce_delay:
                # Resize has settled - return True and reset
                logger.debug(f"Resize settled after {time_since_resize:.3f}s")
                self._last_resize_time = 0
                return True
            else:
                # Still within debounce window - resize not settled yet
                logger.debug(
                    f"Resize in progress, waiting... ({time_since_resize:.3f}s elapsed)"
                )
                return False

        return False

    def enter_raw_mode(self) -> bool:
        """Enter raw terminal mode for character-by-character input.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_terminal or self.current_mode == TerminalMode.RAW:
            return False

        try:
            tty.setraw(sys.stdin.fileno())
            self.current_mode = TerminalMode.RAW
            logger.debug("Entered raw terminal mode")
            return True
        except Exception as e:
            logger.error(f"Failed to enter raw mode: {e}")
            return False

    def exit_raw_mode(self) -> bool:
        """Exit raw terminal mode and restore normal settings.

        Returns:
            True if successful, False otherwise.
        """
        if not self.is_terminal or not self.original_termios:
            return False

        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.original_termios)
            self.current_mode = TerminalMode.NORMAL
            logger.debug("Exited raw terminal mode")
            return True
        except Exception as e:
            logger.error(f"Failed to exit raw mode: {e}")
            return False

    def write_raw(self, text: str) -> bool:
        """Write text directly to terminal using low-level operations.

        Args:
            text: Text to write.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.is_terminal:
                os.write(sys.stdout.fileno(), text.encode("utf-8"))
            else:
                sys.stdout.write(text)
                sys.stdout.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to write to terminal: {e}")
            return False

    def hide_cursor(self) -> bool:
        """Hide the terminal cursor.

        Returns:
            True if successful, False otherwise.
        """
        if self._cursor_hidden or not self.capabilities.cursor_support:
            return True

        success = self.write_raw("\033[?25l")
        if success:
            self._cursor_hidden = True
            logger.debug("Cursor hidden")
        return success

    def show_cursor(self) -> bool:
        """Show the terminal cursor.

        Returns:
            True if successful, False otherwise.
        """
        if not self._cursor_hidden or not self.capabilities.cursor_support:
            return True

        success = self.write_raw("\033[?25h")
        if success:
            self._cursor_hidden = False
            logger.debug("Cursor shown")
        return success

    def clear_line(self) -> bool:
        """Clear the current line.

        Returns:
            True if successful, False otherwise.
        """
        return self.write_raw("\r\033[2K")

    def move_cursor_up(self, lines: int = 1) -> bool:
        """Move cursor up by specified number of lines.

        Args:
            lines: Number of lines to move up.

        Returns:
            True if successful, False otherwise.
        """
        if lines <= 0:
            return True
        return self.write_raw(f"\033[{lines}A")

    def move_cursor_down(self, lines: int = 1) -> bool:
        """Move cursor down by specified number of lines.

        Args:
            lines: Number of lines to move down.

        Returns:
            True if successful, False otherwise.
        """
        if lines <= 0:
            return True
        return self.write_raw(f"\033[{lines}B")

    def move_cursor_to_column(self, column: int) -> bool:
        """Move cursor to specified column.

        Args:
            column: Column number (1-based).

        Returns:
            True if successful, False otherwise.
        """
        if column <= 0:
            column = 1
        return self.write_raw(f"\033[{column}G")

    def save_cursor_position(self) -> bool:
        """Save current cursor position.

        Returns:
            True if successful, False otherwise.
        """
        return self.write_raw("\033[s")

    def restore_cursor_position(self) -> bool:
        """Restore previously saved cursor position.

        Returns:
            True if successful, False otherwise.
        """
        return self.write_raw("\033[u")

    def clear_screen_from_cursor(self) -> bool:
        """Clear screen from cursor position to end.

        Returns:
            True if successful, False otherwise.
        """
        return self.write_raw("\033[0J")

    def update_size(self) -> bool:
        """Update terminal size information.

        Returns:
            True if size changed, False otherwise.
        """
        try:
            size = shutil.get_terminal_size()
            new_size = (size.columns, size.lines)

            if new_size != self._last_size:
                self.capabilities.width = size.columns
                self.capabilities.height = size.lines
                self._last_size = new_size
                logger.debug(f"Terminal size updated: {size.columns}x{size.lines}")
                return True
        except Exception as e:
            logger.debug(f"Could not update terminal size: {e}")

        return False

    def get_size(self) -> tuple[int, int]:
        """Get current terminal size.

        Returns:
            Tuple of (width, height).
        """
        return (self.capabilities.width, self.capabilities.height)

    def supports_color(self, color_type: str = "basic") -> bool:
        """Check if terminal supports specified color type.

        Args:
            color_type: Color type to check ("basic", "256", "truecolor").

        Returns:
            True if color type is supported.
        """
        if color_type == "truecolor":
            return self.capabilities.has_truecolor
        elif color_type == "256":
            return self.capabilities.has_256_color
        elif color_type == "basic":
            return self.capabilities.has_color
        else:
            return False

    def cleanup(self) -> None:
        """Cleanup terminal state and restore settings."""
        try:
            # Show cursor if hidden
            if self._cursor_hidden:
                self.show_cursor()

            # Exit raw mode if active
            if self.current_mode == TerminalMode.RAW:
                self.exit_raw_mode()

            logger.debug("Terminal state cleanup completed")
        except Exception as e:
            logger.error(f"Error during terminal cleanup: {e}")

    def get_cursor_position(self) -> tuple[int, int]:
        """Query current cursor position from terminal.

        Returns:
            Tuple of (row, col) position, or (0, 0) if query fails.
        """
        try:
            # Send cursor position query
            sys.stdout.write("\033[6n")
            sys.stdout.flush()

            # Read response (should be \033[row;colR)
            response = ""
            while True:
                char = sys.stdin.read(1)
                response += char
                if char == "R":
                    break
                if len(response) > 20:  # Safety limit
                    break

            # Parse response: \033[row;colR
            if response.startswith("\033[") and response.endswith("R"):
                coords = response[2:-1]  # Remove \033[ and R
                if ";" in coords:
                    row, col = coords.split(";")
                    return (int(row), int(col))

            logger.warning(
                f"Failed to parse cursor position response: {repr(response)}"
            )
            return (0, 0)

        except Exception as e:
            logger.error(f"Error querying cursor position: {e}")
            return (0, 0)

    def get_status(self) -> Dict[str, Any]:
        """Get terminal state status information.

        Returns:
            Dictionary with terminal status information.
        """
        return {
            "mode": getattr(self.current_mode, "value", self.current_mode),
            "is_terminal": self.is_terminal,
            "cursor_hidden": self._cursor_hidden,
            "capabilities": {
                "color_level": self.capabilities.color_level,
                "width": self.capabilities.width,
                "height": self.capabilities.height,
                "cursor_support": self.capabilities.cursor_support,
                "mouse_support": self.capabilities.mouse_support,
            },
            "last_size": self._last_size,
        }
