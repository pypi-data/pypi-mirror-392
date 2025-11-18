"""Modal renderer using existing visual effects infrastructure."""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional

from ..events.models import UIConfig
from ..io.visual_effects import ColorPalette, GradientRenderer
from ..io.key_parser import KeyPress
from .widgets import BaseWidget, CheckboxWidget, DropdownWidget, TextInputWidget, SliderWidget
from .config_merger import ConfigMerger
from .modal_actions import ModalActionHandler
from .modal_overlay_renderer import ModalOverlayRenderer
from .modal_state_manager import ModalStateManager, ModalLayout, ModalDisplayMode

logger = logging.getLogger(__name__)


class ModalRenderer:
    """Modal overlay renderer using existing visual effects system."""

    def __init__(self, terminal_renderer, visual_effects, config_service=None):
        """Initialize modal renderer with existing infrastructure.

        Args:
            terminal_renderer: Terminal renderer for output.
            visual_effects: Visual effects system for styling.
            config_service: ConfigService for config persistence.
        """
        self.terminal_renderer = terminal_renderer
        self.visual_effects = visual_effects
        self.gradient_renderer = GradientRenderer()
        self.config_service = config_service

        # NEW: Initialize overlay rendering system for proper modal display
        if terminal_renderer and hasattr(terminal_renderer, 'terminal_state'):
            self.overlay_renderer = ModalOverlayRenderer(terminal_renderer.terminal_state)
            self.state_manager = ModalStateManager(terminal_renderer.terminal_state)
        else:
            # Fallback for testing or when terminal_renderer is not available
            self.overlay_renderer = None
            self.state_manager = None

        # Widget management
        self.widgets: List[BaseWidget] = []
        self.focused_widget_index = 0

        # Action handling
        self.action_handler = ModalActionHandler(config_service) if config_service else None

    async def show_modal(self, ui_config: UIConfig) -> Dict[str, Any]:
        """Show modal overlay using TRUE overlay system.

        Args:
            ui_config: Modal configuration.

        Returns:
            Modal interaction result.
        """
        try:
            # FIXED: Use overlay system instead of chat pipeline clearing
            # No more clear_active_area() - that only clears display, not buffers

            # Render modal using existing visual effects (content generation)
            modal_lines = self._render_modal_box(ui_config)

            # Use overlay rendering instead of animation that routes through chat
            await self._render_modal_lines(modal_lines)

            return await self._handle_modal_input(ui_config)
        except Exception as e:
            logger.error(f"Error showing modal: {e}")
            # Ensure proper cleanup on error
            self.state_manager.restore_terminal_state()
            return {"success": False, "error": str(e)}

    def refresh_modal_display(self) -> bool:
        """Refresh modal display without accumulation using overlay system.

        This method refreshes the current modal content without any
        interaction with conversation buffers or message systems.

        Returns:
            True if refresh was successful.
        """
        try:
            # Use state manager to refresh display without chat pipeline
            if self.state_manager:
                return self.state_manager.refresh_modal_display()
            else:
                logger.warning("State manager not available - fallback refresh")
                return True
        except Exception as e:
            logger.error(f"Error refreshing modal display: {e}")
            return False

    def close_modal(self) -> bool:
        """Close modal and restore terminal state.

        Returns:
            True if modal was closed successfully.
        """
        try:
            # Use state manager to properly restore terminal state
            if self.state_manager:
                return self.state_manager.restore_terminal_state()
            else:
                logger.warning("State manager not available - fallback close")
                return True
        except Exception as e:
            logger.error(f"Error closing modal: {e}")
            return False

    def _render_modal_box(self, ui_config: UIConfig, preserve_widgets: bool = False) -> List[str]:
        """Render modal box using existing ColorPalette.

        Args:
            ui_config: Modal configuration.
            preserve_widgets: If True, preserve existing widget states instead of recreating.

        Returns:
            List of rendered modal lines.
        """
        # Use existing ColorPalette for styling
        border_color = ColorPalette.GREY
        title_color = ColorPalette.WHITE
        footer_color = ColorPalette.GREY
        # Use dynamic terminal width instead of hardcoded values
        terminal_width = getattr(self.terminal_renderer.terminal_state, 'width', 80) if self.terminal_renderer else 80
        width = min(int(ui_config.width or terminal_width), terminal_width)
        title = ui_config.title or "Modal"

        lines = []

        # Top border with colored title embedded
        title_separators = "─"
        remaining_width = max(0, width - 2 - len(title) - 2)  # -2 for separators
        left_padding = remaining_width // 2
        right_padding = remaining_width - left_padding
        title_border = f"╭{'─' * left_padding}{title_separators}{title_color}{title}{ColorPalette.RESET}{border_color}{title_separators}{'─' * right_padding}╮"
        lines.append(f"{border_color}{title_border}{ColorPalette.RESET}")

        # Content area
        # Use actual width for content rendering
        actual_content_width = width - 2  # Remove padding from width for content
        content_lines = self._render_modal_content(ui_config.modal_config or {}, actual_content_width + 2, preserve_widgets)
        lines.extend(content_lines)

        # Bottom border with footer embedded
        footer = "enter to select • esc to close"
        footer_remaining = max(0, width - 2 - len(footer))
        footer_left = footer_remaining // 2
        footer_right = footer_remaining - footer_left
        footer_border = f"╰{'─' * footer_left}{footer_color}{footer}{'─' * footer_right}╯"
        lines.append(f"{border_color}{footer_border}{ColorPalette.RESET}")

        return lines

    def _render_modal_content(self, modal_config: dict, width: int, preserve_widgets: bool = False) -> List[str]:
        """Render modal content with interactive widgets.

        Args:
            modal_config: Modal configuration dict.
            width: Modal width.
            preserve_widgets: If True, preserve existing widget states instead of recreating.

        Returns:
            List of content lines with rendered widgets.
        """
        lines = []
        border_color = ColorPalette.GREY

        # CRITICAL FIX: Always recreate widgets to prevent stale state
        # Create or preserve widgets based on mode
        if not preserve_widgets:
            # Clear any existing widgets to prevent accumulation
            self.widgets = []
            self.focused_widget_index = 0
            # Create fresh widgets for clean display
            self.widgets = self._create_widgets(modal_config)
            if self.widgets:
                self.widgets[0].set_focus(True)
        else:
            pass


        # Render sections with widgets
        widget_index = 0
        sections = modal_config.get("sections", [])

        for section in sections:
            section_title = section.get("title", "Section")

            # Create section header (no bold)
            title_text = f"  {section_title}"
            title_line = f"│{title_text.ljust(width-2)}│"
            lines.append(f"{border_color}{title_line}{ColorPalette.RESET}")

            # Empty line after title
            #lines.append(f"{border_color}│{' ' * (width-2)}│{ColorPalette.RESET}")

            # Render widgets in this section
            section_widgets = section.get("widgets", [])
            if section_widgets:
                for widget_config in section_widgets:
                    if widget_index < len(self.widgets):
                        widget = self.widgets[widget_index]
                        widget_lines = widget.render()

                        # Add each widget line with proper modal formatting
                        for widget_line in widget_lines:
                            # Clean widget line and add modal padding
                            clean_line = widget_line.strip()
                            if clean_line.startswith("  "):  # Remove widget's default padding
                                clean_line = clean_line[2:]

                            # Add modal padding and border with ANSI-aware padding
                            padded_line = f"  {clean_line}"
                            modal_line = f"│{self._pad_line_with_ansi(padded_line, width-2)}│"
                            lines.append(f"{border_color}{modal_line}{ColorPalette.RESET}")

                        widget_index += 1
            else:
                # Fallback to static content if no widgets
                section_content = section.get("content", "Interactive widgets enabled")
                content_text = f"    {section_content}"
                content_line = f"│{self._pad_line_with_ansi(content_text, width-2)}│"
                lines.append(f"{border_color}{content_line}{ColorPalette.RESET}")

            # Empty line after section
            #lines.append(f"{border_color}│{' ' * (width-2)}│{ColorPalette.RESET}")

        return lines

    async def _animate_entrance(self, lines: List[str]):
        """Render modal cleanly without stacking animation.

        Args:
            lines: Modal lines to render.
        """
        try:
            # Single clean render without animation to prevent stacking
            await self._render_modal_lines(lines)
        except Exception as e:
            logger.error(f"Error rendering modal: {e}")
            # Single fallback render only
            await self._render_modal_lines(lines)

    async def _render_modal_lines(self, lines: List[str]):
        """Render modal lines using TRUE overlay system (no chat pipeline).

        Args:
            lines: Lines to render.
        """
        try:
            # FIXED: Use overlay rendering system instead of chat pipeline
            # This completely bypasses write_message() and conversation buffers

            # Create modal layout configuration
            content_width = max(len(line) for line in lines) if lines else 80
            # Constrain to terminal width, leaving space for borders
            terminal_width = getattr(self.terminal_renderer.terminal_state, 'width', 80) if self.terminal_renderer else 80
            width = min(content_width + 4, terminal_width - 2)  # Add padding but leave space for borders
            height = len(lines)
            layout = ModalLayout(
                width=width,
                height=height + 2,         # Add border space
                center_horizontal=True,
                center_vertical=True,
                padding=2,
                border_style="box"
            )

            # Prepare modal display with state isolation
            if self.state_manager:
                prepare_result = self.state_manager.prepare_modal_display(layout, ModalDisplayMode.OVERLAY)
                if not prepare_result:
                    logger.error("Failed to prepare modal display")
                    return

                # Render modal content using direct terminal output (bypassing chat)
                render_result = self.state_manager.render_modal_content(lines)
                if not render_result:
                    logger.error("Failed to render modal content")
                    return

                logger.info(f"Modal rendered via overlay system: {len(lines)} lines")
            else:
                # Fallback to basic display for testing
                logger.warning("Modal overlay system not available - using fallback display")
                for line in lines:
                    print(line)

        except Exception as e:
            logger.error(f"Error rendering modal via overlay system: {e}")
            # Ensure state is cleaned up on error
            if self.state_manager:
                self.state_manager.restore_terminal_state()

    def _create_widgets(self, modal_config: dict) -> List[BaseWidget]:
        """Create widgets from modal configuration.

        Args:
            modal_config: Modal configuration dictionary.

        Returns:
            List of instantiated widgets.
        """

        widgets = []
        sections = modal_config.get("sections", [])


        for section_idx, section in enumerate(sections):
            section_widgets = section.get("widgets", [])

            for widget_idx, widget_config in enumerate(section_widgets):
                try:
                    widget = self._create_widget(widget_config)
                    widgets.append(widget)
                except Exception as e:
                    logger.error(f"FAILED to create widget {widget_idx} in section {section_idx}: {e}")
                    logger.error(f"Widget config that failed: {widget_config}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")

        return widgets

    def _create_widget(self, config: dict) -> BaseWidget:
        """Create a single widget from configuration.

        Args:
            config: Widget configuration dictionary.

        Returns:
            Instantiated widget.

        Raises:
            ValueError: If widget type is unknown.
        """

        try:
            widget_type = config["type"]
        except KeyError as e:
            logger.error(f"Widget config missing 'type' field: {e}")
            raise ValueError(f"Widget config missing required 'type' field: {config}")

        config_path = config.get("config_path", "core.ui.unknown")

        # Get current value from config service if available
        current_value = None
        if self.config_service:
            current_value = self.config_service.get(config_path)
        else:
            pass

        # Create widget config with current value
        widget_config = config.copy()
        if current_value is not None:
            widget_config["current_value"] = current_value


        try:
            if widget_type == "checkbox":
                widget = CheckboxWidget(widget_config, config_path, self.config_service)
                return widget
            elif widget_type == "dropdown":
                widget = DropdownWidget(widget_config, config_path, self.config_service)
                return widget
            elif widget_type == "text_input":
                widget = TextInputWidget(widget_config, config_path, self.config_service)
                return widget
            elif widget_type == "slider":
                widget = SliderWidget(widget_config, config_path, self.config_service)
                return widget
            else:
                error_msg = f"Unknown widget type: {widget_type}"
                logger.error(f"{error_msg}")
                raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"FATAL: Widget constructor failed for type '{widget_type}': {e}")
            logger.error(f"Widget config that caused failure: {widget_config}")
            import traceback
            logger.error(f"Full constructor traceback: {traceback.format_exc()}")
            raise

    def _handle_widget_navigation(self, key_press: KeyPress) -> bool:
        """Handle widget focus navigation.

        Args:
            key_press: Key press event.

        Returns:
            True if navigation was handled.
        """
        if not self.widgets:
            return False

        # CRITICAL FIX: Check if focused widget is expanded before handling navigation
        # If a dropdown is expanded, let it handle its own ArrowDown/ArrowUp
        focused_widget = self.widgets[self.focused_widget_index]
        if hasattr(focused_widget, '_expanded') and focused_widget._expanded:
            # Widget is expanded - don't intercept arrow keys
            if key_press.name in ["ArrowDown", "ArrowUp"]:
                return False  # Let widget handle its own navigation

        if key_press.name == "Tab" or key_press.name == "ArrowDown":
            # Move to next widget
            self.widgets[self.focused_widget_index].set_focus(False)
            self.focused_widget_index = (self.focused_widget_index + 1) % len(self.widgets)
            self.widgets[self.focused_widget_index].set_focus(True)
            return True

        elif key_press.name == "ArrowUp":
            # Move to previous widget
            self.widgets[self.focused_widget_index].set_focus(False)
            self.focused_widget_index = (self.focused_widget_index - 1) % len(self.widgets)
            self.widgets[self.focused_widget_index].set_focus(True)
            return True

        return False

    def _handle_widget_input(self, key_press: KeyPress) -> bool:
        """Route input to focused widget.

        Args:
            key_press: Key press event.

        Returns:
            True if input was handled by a widget.
        """

        if not self.widgets or self.focused_widget_index >= len(self.widgets):
            return False

        focused_widget = self.widgets[self.focused_widget_index]

        result = focused_widget.handle_input(key_press)
        return result

    def _get_widget_values(self) -> Dict[str, Any]:
        """Get all widget values for saving.

        Returns:
            Dictionary mapping config paths to values.
        """
        values = {}
        for widget in self.widgets:
            if widget.has_pending_changes():
                values[widget.config_path] = widget.get_pending_value()
        return values

    def _reset_widget_focus(self):
        """Reset widget focus to first widget."""
        if self.widgets:
            for widget in self.widgets:
                widget.set_focus(False)
            self.focused_widget_index = 0
            self.widgets[0].set_focus(True)

    def _create_gradient_header(self, title: str) -> str:
        """Create a gradient header text with bold white and cyan-blue gradient.

        Args:
            title: Section title text.

        Returns:
            Formatted title with gradient effect.
        """
        if not title:
            return ""

        # Make section headers slightly brighter than normal text
        return f"{ColorPalette.BRIGHT}{title}{ColorPalette.RESET}"

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text.

        Args:
            text: Text with potential ANSI codes.

        Returns:
            Text with ANSI codes removed.
        """
        return re.sub(r'\033\[[0-9;]*m', '', text)

    def _pad_line_with_ansi(self, line: str, target_width: int) -> str:
        """Pad line to target width, accounting for ANSI escape codes.

        Args:
            line: Line that may contain ANSI codes.
            target_width: Target visible width.

        Returns:
            Line padded to target visible width.
        """
        visible_length = len(self._strip_ansi(line))
        padding_needed = max(0, target_width - visible_length)
        return line + ' ' * padding_needed

    async def _handle_modal_input(self, ui_config: UIConfig) -> Dict[str, Any]:
        """Handle modal input with persistent event loop for widget interaction.

        Args:
            ui_config: Modal configuration.

        Returns:
            Modal completion result when user exits.
        """
        # Store ui_config for refresh operations
        self.current_ui_config = ui_config

        # Modal is now active and waiting for input
        # Input handling happens through input_handler._handle_modal_keypress()
        # which calls our widget methods and refreshes display


        # The modal stays open until input_handler calls one of:
        # - _exit_modal_mode() (Escape key)
        # - _save_and_exit_modal() (Enter key or save action)

        # This method completes when the modal is closed externally
        # Return success with widget information
        return {
            "success": True,
            "action": "modal_interactive",
            "widgets_enabled": True,
            "widget_count": len(self.widgets),
            "widgets_created": [w.__class__.__name__ for w in self.widgets]
        }