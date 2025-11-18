"""Message coordination system for preventing race conditions.

This coordinator solves the fundamental race condition where multiple
message writing systems interfere with each other, causing messages
to be overwritten or cleared unexpectedly.
"""

import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)


class MessageDisplayCoordinator:
    """Coordinates message display to prevent interference between systems.

    Key Features:
    - Atomic message sequences (all messages display together)
    - Unified state management (prevents clearing conflicts)
    - Proper ordering (system messages before responses)
    - Protection from interference (no race conditions)
    """

    def __init__(self, terminal_renderer):
        """Initialize message display coordinator.

        Args:
            terminal_renderer: TerminalRenderer instance for display
        """
        self.terminal_renderer = terminal_renderer
        self.message_queue: List[Tuple[str, str, Dict[str, Any]]] = []
        self.is_displaying = False

        logger.debug("MessageDisplayCoordinator initialized")

    def queue_message(self, message_type: str, content: str, **kwargs) -> None:
        """Queue a message for coordinated display.

        Args:
            message_type: Type of message ("system", "assistant", "user", "error")
            content: Message content to display
            **kwargs: Additional arguments for message formatting
        """
        self.message_queue.append((message_type, content, kwargs))
        logger.debug(f"Queued {message_type} message: {content[:50]}...")

    def display_single_message(
        self, message_type: str, content: str, **kwargs
    ) -> None:
        """Display a single message immediately through coordination.

        This method provides a coordinated way for plugins and other systems
        to display individual messages without bypassing the coordination system.

        Args:
            message_type: Type of message ("system", "assistant", "user", "error")
            content: Message content to display
            **kwargs: Additional arguments for message formatting
        """
        self.display_message_sequence([(message_type, content, kwargs)])

    def display_queued_messages(self) -> None:
        """Display all queued messages in proper atomic sequence.

        This method ensures all queued messages display together
        without interference from other systems.
        """
        if self.is_displaying or not self.message_queue:
            return

        logger.debug(f"Displaying {len(self.message_queue)} queued messages")

        # Enter atomic display mode
        self.is_displaying = True
        self.terminal_renderer.writing_messages = True

        # Clear active area once before all messages
        self.terminal_renderer.clear_active_area()

        try:
            # Display all messages in sequence
            for message_type, content, kwargs in self.message_queue:
                self._display_single_message(message_type, content, kwargs)

            # Add blank line for visual separation
            self.terminal_renderer.message_renderer.write_message(
                "", apply_gradient=False
            )

        finally:
            # Exit atomic display mode
            self.terminal_renderer.writing_messages = False
            self.message_queue.clear()
            self.is_displaying = False
            logger.debug("Completed atomic message display")

    def display_message_sequence(
        self, messages: List[Tuple[str, str, Dict[str, Any]]]
    ) -> None:
        """Display a sequence of messages atomically.

        This is the primary method for coordinated message display.
        All messages in the sequence will display together without
        interference from other systems.

        Args:
            messages: List of (message_type, content, kwargs) tuples

        Example:
            coordinator.display_message_sequence([
                ("system", "Thought for 2.1 seconds", {}),
                ("assistant", "Hello! How can I help you?", {})
            ])
        """
        # Queue all messages
        for message_type, content, kwargs in messages:
            self.queue_message(message_type, content, **kwargs)

        # Display them atomically
        self.display_queued_messages()

    def _display_single_message(
        self, message_type: str, content: str, kwargs: Dict[str, Any]
    ) -> None:
        """Display a single message using the appropriate method.

        Args:
            message_type: Type of message to display
            content: Message content
            kwargs: Additional formatting arguments
        """
        try:
            if message_type == "system":
                # System messages use DIMMED format as per CLAUDE.md spec
                from .message_renderer import MessageType, MessageFormat

                self.terminal_renderer.message_renderer.conversation_renderer.write_message(
                    content,
                    message_type=MessageType.SYSTEM,  # No ∴ prefix for system messages
                    format_style=MessageFormat.DIMMED,  # Professional dimmed formatting
                    **kwargs,
                )
            elif message_type == "assistant":
                # Use MessageFormat.GRADIENT for assistant messages
                from .message_renderer import MessageType, MessageFormat

                format_style = (
                    MessageFormat.GRADIENT
                    if kwargs.get("apply_gradient", True)
                    else MessageFormat.PLAIN
                )
                self.terminal_renderer.message_renderer.conversation_renderer.write_message(
                    content,
                    message_type=MessageType.ASSISTANT,
                    format_style=format_style,
                    **kwargs,
                )
            elif message_type == "user":
                self.terminal_renderer.message_renderer.write_user_message(
                    content, **kwargs
                )
            elif message_type == "error":
                # For error messages, use MessageType.ERROR for proper red color, no ∴ prefix
                from .message_renderer import MessageType, MessageFormat

                self.terminal_renderer.message_renderer.conversation_renderer.write_message(
                    content,
                    message_type=MessageType.ERROR,
                    format_style=MessageFormat.HIGHLIGHTED,  # Uses red color from _format_highlighted
                    **kwargs,
                )
            else:
                logger.warning(f"Unknown message type: {message_type}")
                # Fallback to regular message
                self.terminal_renderer.message_renderer.write_message(
                    content, apply_gradient=False
                )

        except Exception as e:
            logger.error(f"Error displaying {message_type} message: {e}")
            # Fallback display to prevent total failure
            try:
                print(f"[{message_type.upper()}] {content}")
            except Exception:
                logger.error(
                    "Critical: Failed to display message even with fallback"
                )

    def clear_queue(self) -> None:
        """Clear all queued messages without displaying them."""
        self.message_queue.clear()
        logger.debug("Cleared message queue")

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status for debugging.

        Returns:
            Dictionary with queue information
        """
        return {
            "queue_length": len(self.message_queue),
            "is_displaying": self.is_displaying,
            "queued_types": [msg[0] for msg in self.message_queue],
        }
