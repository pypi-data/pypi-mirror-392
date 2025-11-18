import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class StatusFormat(Enum):
    """Status area formatting styles."""

    COMPACT = "compact"
    DETAILED = "detailed"
    MINIMAL = "minimal"
    BRACKETED = "bracketed"


@dataclass
class BlockConfig:
    """Configuration for a single status block."""

    width_fraction: float  # 0.25, 0.33, 0.5, 0.67, 1.0
    content_provider: Callable[[], List[str]]  # Function that returns status content
    title: str  # Block title/label
    priority: int = 0  # Block priority within view


@dataclass
class StatusViewConfig:
    """Configuration for a complete status view."""

    name: str  # "Session Stats", "Performance", "My Plugin View"
    plugin_source: str  # Plugin that registered this view
    priority: int  # Display order priority
    blocks: List[BlockConfig]  # Block layout configuration


@dataclass
class StatusMetric:
    """Represents a single status metric."""

    key: str
    value: Any
    format_type: str = (
        "default"  # "number", "boolean", "time", "ratio", "percentage"
    )
    color_hint: Optional[str] = None
    priority: int = 0

    def format_value(self) -> str:
        """Format the value based on its type."""
        if self.format_type == "boolean":
            return "Yes" if self.value else "No"
        elif self.format_type == "time":
            if isinstance(self.value, (int, float)):
                return f"{self.value:.1f}s"
            return str(self.value)
        elif self.format_type == "ratio":
            if isinstance(self.value, tuple) and len(self.value) == 2:
                return f"{self.value[0]}/{self.value[1]}"
            return str(self.value)
        elif self.format_type == "percentage":
            if isinstance(self.value, (int, float)):
                return f"{self.value:.1f}%"
            return str(self.value)
        elif self.format_type == "number":
            if isinstance(self.value, int) and self.value >= 1000:
                # Add comma separators for large numbers
                return f"{self.value:,}"
            return str(self.value)
        else:
            return str(self.value)

    def get_display_text(self) -> str:
        """Get formatted display text for this metric."""
        formatted_value = self.format_value()
        return f"{self.key}: {formatted_value}"


class StatusAreaManager:
    """Manages individual status areas and their content."""

    def __init__(self, area_name: str):
        """Initialize status area manager.

        Args:
            area_name: Name of the status area (A, B, C).
        """
        self.area_name = area_name
        self.metrics: Dict[str, StatusMetric] = {}
        self.custom_lines: List[str] = []
        self.format_style = StatusFormat.BRACKETED

    def add_metric(self, metric: StatusMetric) -> None:
        """Add or update a status metric.

        Args:
            metric: StatusMetric to add.
        """
        self.metrics[metric.key] = metric

    def update_metric(self, key: str, value: Any, **kwargs) -> None:
        """Update an existing metric or create a new one.

        Args:
            key: Metric key.
            value: New value.
            **kwargs: Additional metric properties.
        """
        if key in self.metrics:
            self.metrics[key].value = value
            for attr, val in kwargs.items():
                if hasattr(self.metrics[key], attr):
                    setattr(self.metrics[key], attr, val)
        else:
            self.add_metric(StatusMetric(key, value, **kwargs))

    def remove_metric(self, key: str) -> None:
        """Remove a metric from the status area.

        Args:
            key: Metric key to remove.
        """
        self.metrics.pop(key, None)

    def add_custom_line(self, line: str) -> None:
        """Add a custom formatted line to the status area.

        Args:
            line: Custom line text.
        """
        self.custom_lines.append(line)

    def clear_custom_lines(self) -> None:
        """Clear all custom lines."""
        self.custom_lines.clear()

    def get_formatted_lines(self, colorizer_func=None) -> List[str]:
        """Get formatted lines for display.

        Args:
            colorizer_func: Optional function to apply colors to text.

        Returns:
            List of formatted status lines.
        """
        lines = []

        # Add metric lines (sorted by priority)
        sorted_metrics = sorted(
            self.metrics.values(), key=lambda m: m.priority, reverse=True
        )
        for metric in sorted_metrics:
            line = metric.get_display_text()

            # Apply color hints if specified
            if metric.color_hint and colorizer_func:
                line = colorizer_func(line)
            elif colorizer_func:
                line = colorizer_func(line)

            lines.append(line)

        # Add custom lines
        for line in self.custom_lines:
            if colorizer_func:
                line = colorizer_func(line)
            lines.append(line)

        return lines

    def clear(self) -> None:
        """Clear all metrics and custom lines."""
        self.metrics.clear()
        self.custom_lines.clear()


class StatusViewRegistry:
    """Registry for plugin-configurable status views with navigation."""

    def __init__(self, event_bus=None):
        """Initialize status view registry.

        Args:
            event_bus: Event bus for firing status change events.
        """
        self.views: List[StatusViewConfig] = []
        self.current_index = 0
        self.event_bus = event_bus
        logger.info("StatusViewRegistry initialized")

    def register_status_view(
        self, plugin_name: str, config: StatusViewConfig
    ) -> None:
        """Register a new status view from a plugin.

        Args:
            plugin_name: Name of the plugin registering the view.
            config: StatusViewConfig for the new view.
        """
        # Add the view and sort by priority
        self.views.append(config)
        self.views.sort(key=lambda v: v.priority, reverse=True)

        logger.info(
            f"Registered status view '{config.name}' from plugin '{plugin_name}' with priority {config.priority}"
        )

    def cycle_next(self) -> Optional[StatusViewConfig]:
        """Navigate to next status view.

        Returns:
            New current view config, or None if no views.
        """
        if not self.views:
            return None

        self.current_index = (self.current_index + 1) % len(self.views)
        current_view = self.views[self.current_index]

        # Fire status view changed event
        if self.event_bus:
            try:
                # Import here to avoid circular imports
                from ..events.models import EventType, Event

                event = Event(
                    type=EventType.STATUS_VIEW_CHANGED,
                    data={"view_name": current_view.name, "direction": "next"},
                    source="status_view_registry",
                )
                self.event_bus.fire_event(event)
            except Exception as e:
                logger.warning(f"Failed to fire STATUS_VIEW_CHANGED event: {e}")

        logger.debug(f"Cycled to next status view: '{current_view.name}'")
        return current_view

    def cycle_previous(self) -> Optional[StatusViewConfig]:
        """Navigate to previous status view.

        Returns:
            New current view config, or None if no views.
        """
        if not self.views:
            return None

        self.current_index = (self.current_index - 1) % len(self.views)
        current_view = self.views[self.current_index]

        # Fire status view changed event
        if self.event_bus:
            try:
                # Import here to avoid circular imports
                from ..events.models import EventType, Event

                event = Event(
                    type=EventType.STATUS_VIEW_CHANGED,
                    data={
                        "view_name": current_view.name,
                        "direction": "previous",
                    },
                    source="status_view_registry",
                )
                self.event_bus.fire_event(event)
            except Exception as e:
                logger.warning(f"Failed to fire STATUS_VIEW_CHANGED event: {e}")

        logger.debug(f"Cycled to previous status view: '{current_view.name}'")
        return current_view

    def get_current_view(self) -> Optional[StatusViewConfig]:
        """Get the currently active status view.

        Returns:
            Current view config, or None if no views registered.
        """
        if not self.views:
            return None
        return self.views[self.current_index]

    def get_view_count(self) -> int:
        """Get total number of registered views."""
        return len(self.views)

    def get_view_names(self) -> List[str]:
        """Get names of all registered views."""
        return [view.name for view in self.views]


class StatusRenderer:
    """Main status rendering system coordinating multiple areas."""

    def __init__(
        self,
        terminal_width: int = 80,
        status_registry: Optional[StatusViewRegistry] = None,
    ):
        """Initialize status renderer.

        Args:
            terminal_width: Terminal width for layout calculations.
            status_registry: Optional status view registry for block-based rendering.
        """
        self.terminal_width = terminal_width
        self.status_registry = status_registry

        # Create status area managers (legacy compatibility)
        self.areas: Dict[str, StatusAreaManager] = {
            "A": StatusAreaManager("A"),
            "B": StatusAreaManager("B"),
            "C": StatusAreaManager("C"),
        }

        # Rendering configuration
        self.bracket_style = {
            "open": "",
            "close": "",
            "color": "",
        }  # No brackets
        self.spacing = (
            4  # Spacing between columns (increased for clarity without separator)
        )
        self.separator_style = ""  # No separator - clean minimal aesthetic

    def get_area(self, area_name: str) -> Optional[StatusAreaManager]:
        """Get status area manager by name.

        Args:
            area_name: Area name (A, B, or C).

        Returns:
            StatusAreaManager instance or None.
        """
        return self.areas.get(area_name.upper())

    def update_area_content(self, area_name: str, content: List[str]) -> None:
        """Update area content with raw lines (backward compatibility).

        Args:
            area_name: Area name.
            content: List of content lines.
        """
        area = self.get_area(area_name)
        if area:
            area.clear()
            for line in content:
                area.add_custom_line(line)

    def set_terminal_width(self, width: int) -> None:
        """Update terminal width for layout calculations.

        Args:
            width: New terminal width.
        """
        self.terminal_width = width

    def render_horizontal_layout(self, colorizer_func=None) -> List[str]:
        """Render status areas in horizontal (column) layout.

        Args:
            colorizer_func: Optional function to apply colors to text.

        Returns:
            List of formatted status lines.
        """
        # Use block-based rendering if registry is available and has views
        if self.status_registry and self.status_registry.get_view_count() > 0:
            return self._render_block_layout(colorizer_func)

        # Fallback to legacy area-based rendering
        return self._render_legacy_layout(colorizer_func)

    def _render_legacy_layout(self, colorizer_func=None) -> List[str]:
        """Render legacy area-based layout for backwards compatibility.

        Args:
            colorizer_func: Optional function to apply colors to text.

        Returns:
            List of formatted status lines.
        """
        # Get content for all areas
        area_contents = {}
        for name, area in self.areas.items():
            content = area.get_formatted_lines(colorizer_func)
            if content:
                area_contents[name] = content

        if not area_contents:
            return []

        # Use three-column layout for wide terminals
        if self.terminal_width >= 80:
            return self._render_three_column_layout(area_contents, colorizer_func)
        else:
            return self._render_vertical_layout(area_contents, colorizer_func)

    def _render_three_column_layout(
        self, area_contents: Dict[str, List[str]], colorizer_func=None
    ) -> List[str]:
        """Render three-column layout for wide terminals.

        Args:
            area_contents: Dictionary of area contents.
            colorizer_func: Optional colorizer function.

        Returns:
            List of formatted lines.
        """
        lines = []

        # Improved column width calculation
        # Reserve space for brackets [text] and spacing between columns
        brackets_overhead = 4  # 2 brackets + 2 padding spaces per column
        total_spacing = (3 - 1) * self.spacing  # spacing between 3 columns
        available_width = self.terminal_width - total_spacing
        column_width = max(15, (available_width - (3 * brackets_overhead)) // 3)

        # Get content for areas A, B, C in order
        area_names = ["A", "B", "C"]
        area_data = []
        for area_name in area_names:
            content = area_contents.get(area_name, [])
            area_data.append(content)

        # Find maximum lines across all areas
        max_lines = max(len(content) for content in area_data) if area_data else 0

        # Create each row with three columns
        for line_idx in range(max_lines):
            columns = []

            for content in area_data:
                if line_idx < len(content):
                    text = content[line_idx]

                    # Truncate if too long for column (account for brackets)
                    visible_text = self._strip_ansi(text)
                    max_text_width = column_width - 2  # Reserve space for brackets

                    if len(visible_text) > max_text_width:
                        # Smart truncation - preserve important parts
                        if max_text_width > 3:
                            truncated = self._truncate_with_ansi(
                                text, max_text_width - 3
                            )
                            text = truncated + "..."
                        else:
                            text = "..."

                    # Apply bracket formatting
                    bracketed_text = self._apply_brackets(text)
                    columns.append(bracketed_text)
                else:
                    columns.append("")  # Empty column

            # Join columns with improved spacing
            formatted_line = self._join_columns_improved(
                columns, column_width + brackets_overhead
            )

            # Only add line if it has content
            if formatted_line.strip():
                lines.append(formatted_line.rstrip())

        return lines

    def _render_vertical_layout(
        self, area_contents: Dict[str, List[str]], colorizer_func=None
    ) -> List[str]:
        """Render vertical layout for narrow terminals.

        Args:
            area_contents: Dictionary of area contents.
            colorizer_func: Optional colorizer function.

        Returns:
            List of formatted lines.
        """
        lines = []

        # Render each area vertically
        for area_name in ["A", "B", "C"]:
            content = area_contents.get(area_name, [])
            for line in content:
                if line.strip():
                    bracketed_line = self._apply_brackets(line)
                    lines.append(bracketed_line)

        return lines

    def _apply_brackets(self, text: str) -> str:
        """Apply bracket styling to text.

        Args:
            text: Text to apply brackets to.

        Returns:
            Text with brackets applied.
        """
        bracket_color = self.bracket_style["color"]
        reset = "\033[0m"
        open_bracket = self.bracket_style["open"]
        close_bracket = self.bracket_style["close"]

        return f"{bracket_color}{open_bracket}{reset}{text}{bracket_color}{close_bracket}{reset}"

    def _join_columns(self, columns: List[str], column_width: int) -> str:
        """Join columns with proper spacing and alignment (legacy method).

        Args:
            columns: List of column strings.
            column_width: Width of each column.

        Returns:
            Joined line string.
        """
        return self._join_columns_improved(columns, column_width)

    def _join_columns_improved(self, columns: List[str], column_width: int) -> str:
        """Join columns with improved spacing and alignment.

        Args:
            columns: List of column strings.
            column_width: Width of each column (including brackets).

        Returns:
            Joined line string.
        """
        formatted_line = ""

        for i, col in enumerate(columns):
            if col:
                # Add the column content
                formatted_line += col

                # Calculate padding needed
                visible_length = len(self._strip_ansi(col))
                padding = max(0, column_width - visible_length)

                # Add padding only if not the last column
                if i < len(columns) - 1:
                    formatted_line += " " * padding
                    # Add inter-column spacing
                    formatted_line += " " * self.spacing
            else:
                # Empty column - add spacing if not last
                if i < len(columns) - 1:
                    formatted_line += " " * column_width
                    formatted_line += " " * self.spacing

        return formatted_line

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text.

        Args:
            text: Text with potential ANSI codes.

        Returns:
            Text with ANSI codes removed.
        """
        return re.sub(r"\033\[[0-9;]*m", "", text)

    def _truncate_with_ansi(self, text: str, max_length: int) -> str:
        """Truncate text while preserving ANSI codes.

        Args:
            text: Text to truncate.
            max_length: Maximum visible length.

        Returns:
            Truncated text with ANSI codes preserved.
        """
        result = ""
        visible_count = 0
        i = 0

        while i < len(text) and visible_count < max_length:
            # Check for ANSI escape sequence
            if (
                text[i : i + 1] == "\033"
                and i + 1 < len(text)
                and text[i + 1] == "["
            ):
                # Find end of ANSI sequence
                end = i + 2
                while end < len(text) and text[end] not in "mhlABCDEFGHJKSTfimpsuI":
                    end += 1
                if end < len(text):
                    end += 1

                # Add the entire ANSI sequence
                result += text[i:end]
                i = end
            else:
                # Regular character
                result += text[i]
                visible_count += 1
                i += 1

        return result

    def _render_block_layout(self, colorizer_func=None) -> List[str]:
        """Render flexible block-based layout using StatusViewRegistry.

        Args:
            colorizer_func: Optional function to apply colors to text.

        Returns:
            List of formatted status lines.
        """
        if not self.status_registry:
            return []

        current_view = self.status_registry.get_current_view()
        if not current_view:
            return []

        # Get content from all blocks in the current view
        block_contents = []
        for block in current_view.blocks:
            try:
                content = block.content_provider()
                if content:
                    block_contents.append(
                        {
                            "width_fraction": block.width_fraction,
                            "title": block.title,
                            "content": content,
                            "priority": block.priority,
                        }
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to get content from block '{block.title}': {e}"
                )

        if not block_contents:
            return []

        # Sort blocks by priority
        block_contents.sort(key=lambda b: b["priority"], reverse=True)

        # Calculate block layout
        lines = self._calculate_and_render_blocks(block_contents, colorizer_func)

        # Add cycling hint if multiple views are available
        view_count = self.status_registry.get_view_count()
        if view_count > 1:
            current_index = (
                self.status_registry.current_index + 1
            )  # 1-indexed for display
            # Use INFO_CYAN from Neon Minimal palette
            hint = f"\033[38;2;6;182;212m(Opt+, / Opt+. to cycle • View {current_index}/{view_count}: {current_view.name})\033[0m"
            lines.append(hint)

        return lines

    def _calculate_and_render_blocks(
        self, block_contents: List[Dict], colorizer_func=None
    ) -> List[str]:
        """Calculate block layout and render status lines.

        Args:
            block_contents: List of block content dictionaries.
            colorizer_func: Optional colorizer function.

        Returns:
            List of formatted status lines.
        """
        if not block_contents:
            return []

        # For now, implement horizontal layout similar to the legacy system
        # This can be enhanced later for more complex layouts

        # Calculate how many blocks can fit horizontally
        total_width_needed = sum(block["width_fraction"] for block in block_contents)

        if total_width_needed <= 1.0:
            # All blocks fit in one row
            return self._render_single_row_blocks(block_contents, colorizer_func)
        else:
            # Need multiple rows or vertical layout
            return self._render_multi_row_blocks(block_contents, colorizer_func)

    def _render_single_row_blocks(
        self, block_contents: List[Dict], colorizer_func=None
    ) -> List[str]:
        """Render blocks in a single horizontal row.

        Args:
            block_contents: List of block content dictionaries.
            colorizer_func: Optional colorizer function.

        Returns:
            List of formatted status lines.
        """
        lines = []

        # Calculate actual column widths
        total_spacing = (
            (len(block_contents) - 1) * self.spacing
            if len(block_contents) > 1
            else 0
        )
        available_width = self.terminal_width - total_spacing

        column_widths = []
        for block in block_contents:
            width = int(available_width * block["width_fraction"])
            column_widths.append(max(10, width))  # Minimum width of 10

        # Find maximum lines across all blocks
        max_lines = (
            max(len(block["content"]) for block in block_contents)
            if block_contents
            else 0
        )

        # Create each row
        for line_idx in range(max_lines):
            columns = []

            for i, block in enumerate(block_contents):
                if line_idx < len(block["content"]):
                    text = block["content"][line_idx]

                    # Apply colorizer
                    if colorizer_func:
                        text = colorizer_func(text)

                    # Truncate if too long
                    visible_text = self._strip_ansi(text)
                    max_width = column_widths[i]

                    if len(visible_text) > max_width:
                        if max_width > 3:
                            text = (
                                self._truncate_with_ansi(text, max_width - 3) + "..."
                            )
                        else:
                            text = "..."

                    columns.append(text)
                else:
                    columns.append("")  # Empty column

            # Join columns with smart spacing (no separator needed)
            formatted_line = ""
            for i, col in enumerate(columns):
                formatted_line += col

                # Add spacing between columns (not after last)
                if i < len(columns) - 1 and any(
                    columns[i + 1 :]
                ):  # Only add spacing if there are more non-empty columns
                    # Pad current column to its width
                    visible_length = len(self._strip_ansi(col))
                    padding = max(0, column_widths[i] - visible_length)
                    formatted_line += " " * padding
                    # Add clean inter-column spacing
                    formatted_line += " " * self.spacing

            if formatted_line.strip():
                lines.append(formatted_line.rstrip())

        return lines

    def _render_multi_row_blocks(
        self, block_contents: List[Dict], colorizer_func=None
    ) -> List[str]:
        """Render blocks that don't fit in a single row.

        Args:
            block_contents: List of block content dictionaries.
            colorizer_func: Optional colorizer function.

        Returns:
            List of formatted status lines.
        """
        lines = []

        # For now, render each block on its own line(s)
        # This is a simple fallback - can be enhanced later
        for block in block_contents:
            for content_line in block["content"]:
                if colorizer_func:
                    content_line = colorizer_func(content_line)

                # Truncate if too long
                visible_text = self._strip_ansi(content_line)
                if len(visible_text) > self.terminal_width - 3:
                    content_line = (
                        self._truncate_with_ansi(
                            content_line, self.terminal_width - 6
                        )
                        + "..."
                    )

                lines.append(content_line)

        return lines

    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of status rendering state.

        Returns:
            Dictionary with status information.
        """
        summary = {
            "terminal_width": self.terminal_width,
            "areas": {
                name: {
                    "metrics_count": len(area.metrics),
                    "custom_lines_count": len(area.custom_lines),
                    "total_lines": len(area.get_formatted_lines()),
                }
                for name, area in self.areas.items()
            },
            "bracket_style": self.bracket_style,
            "spacing": self.spacing,
            "separator_style": self.separator_style,
        }

        # Add status registry information if available
        if self.status_registry:
            current_view = self.status_registry.get_current_view()
            summary["status_registry"] = {
                "view_count": self.status_registry.get_view_count(),
                "view_names": self.status_registry.get_view_names(),
                "current_view": current_view.name if current_view else None,
                "current_blocks": (len(current_view.blocks) if current_view else 0),
            }

        return summary
