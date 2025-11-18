"""Input/Output subsystem for Kollabor CLI."""

from .input_handler import InputHandler
from .terminal_renderer import TerminalRenderer
from .key_parser import KeyParser, KeyPress, KeyType
from .buffer_manager import BufferManager
from .input_errors import InputErrorHandler, ErrorType, ErrorSeverity
from .visual_effects import VisualEffects, ColorPalette, EffectType
from .terminal_state import TerminalState, TerminalCapabilities, TerminalMode
from .layout import LayoutManager, LayoutArea, ThinkingAnimationManager
from .status_renderer import StatusRenderer, StatusMetric, StatusFormat
from .message_renderer import (
    MessageRenderer,
    ConversationMessage,
    MessageType,
    MessageFormat,
)

__all__ = [
    # Core components
    "InputHandler",
    "TerminalRenderer",
    # Input handling
    "KeyParser",
    "KeyPress",
    "KeyType",
    "BufferManager",
    "InputErrorHandler",
    "ErrorType",
    "ErrorSeverity",
    # Visual effects
    "VisualEffects",
    "ColorPalette",
    "EffectType",
    # Terminal management
    "TerminalState",
    "TerminalCapabilities",
    "TerminalMode",
    # Layout management
    "LayoutManager",
    "LayoutArea",
    "ThinkingAnimationManager",
    # Status rendering
    "StatusRenderer",
    "StatusMetric",
    "StatusFormat",
    # Message rendering
    "MessageRenderer",
    "ConversationMessage",
    "MessageType",
    "MessageFormat",
]
