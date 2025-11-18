"""Visual effects system for terminal rendering."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict, Any


class EffectType(Enum):
    """Types of visual effects."""

    GRADIENT = "gradient"
    SHIMMER = "shimmer"
    DIM = "dim"
    ANIMATION = "animation"
    COLOR = "color"


@dataclass
class EffectConfig:
    """Configuration for visual effects."""

    effect_type: EffectType
    enabled: bool = True
    intensity: float = 1.0
    speed: int = 3
    width: int = 4
    colors: List[str] = field(default_factory=list)


class ColorPalette:
    """Color palette definitions for various effects."""

    # Standard colors
    RESET = "\033[0m"
    DIM = "\033[2m"
    BRIGHT = "\033[1m"

    # Basic colors
    WHITE = "\033[37m"
    BRIGHT_WHITE = "\033[1;37m"
    BLACK = "\033[30m"

    # Red variants
    DIM_RED = "\033[2;31m"
    RED = "\033[31m"
    BRIGHT_RED = "\033[1;31m"

    # Green variants
    DIM_GREEN = "\033[2;32m"
    GREEN = "\033[32m"
    BRIGHT_GREEN = "\033[1;32m"

    # Yellow variants
    DIM_YELLOW = "\033[2;33m"
    YELLOW = "\033[33m"
    BRIGHT_YELLOW = "\033[1;33m"

    # Blue variants
    DIM_BLUE = "\033[2;34m"
    BLUE = "\033[34m"
    BRIGHT_BLUE = "\033[1;34m"
    NORMAL_BLUE = "\033[94m"

    # Magenta variants
    DIM_MAGENTA = "\033[2;35m"
    MAGENTA = "\033[35m"
    BRIGHT_MAGENTA = "\033[1;35m"

    # Cyan variants
    DIM_CYAN = "\033[2;36m"
    CYAN = "\033[36m"
    BRIGHT_CYAN = "\033[1;36m"

    # Grey variants
    DIM_GREY = "\033[2;37m"
    GREY = "\033[90m"
    BRIGHT_GREY = "\033[1;90m"

    # Extended bright colors (256-color mode)
    BRIGHT_CYAN_256 = "\033[1;96m"
    BRIGHT_BLUE_256 = "\033[1;94m"
    BRIGHT_GREEN_256 = "\033[1;92m"
    BRIGHT_YELLOW_256 = "\033[1;93m"
    BRIGHT_MAGENTA_256 = "\033[1;95m"
    BRIGHT_RED_256 = "\033[1;91m"

    # Neon Minimal Palette - RGB True Color (24-bit)
    # Primary: Lime Green #a3e635
    LIME = "\033[38;2;163;230;53m"
    LIME_LIGHT = "\033[38;2;190;242;100m"
    LIME_DARK = "\033[38;2;132;204;22m"

    # Info: Cyan #06b6d4
    INFO_CYAN = "\033[38;2;6;182;212m"
    INFO_CYAN_LIGHT = "\033[38;2;34;211;238m"
    INFO_CYAN_DARK = "\033[38;2;8;145;178m"

    # Warning: Gold #eab308
    WARNING_GOLD = "\033[38;2;234;179;8m"
    WARNING_GOLD_LIGHT = "\033[38;2;253;224;71m"
    WARNING_GOLD_DARK = "\033[38;2;202;138;4m"

    # Error: Bright Red #ef4444
    ERROR_RED = "\033[38;2;239;68;68m"
    ERROR_RED_LIGHT = "\033[38;2;248;113;113m"
    ERROR_RED_DARK = "\033[38;2;220;38;38m"

    # Muted: Steel #71717a
    MUTED_STEEL = "\033[38;2;113;113;122m"
    DIM_STEEL = "\033[2;38;2;113;113;122m"

    # Grey gradient levels (256-color palette)
    GREY_LEVELS = [255, 254, 253, 252, 251, 250]

    # Dim white gradient levels (bright white to subtle dim white)
    DIM_WHITE_LEVELS = [255, 254, 253, 252, 251, 250]

    # Lime green gradient scheme RGB values for ultra-smooth gradients
    DIM_SCHEME_COLORS = [
        (190, 242, 100),  # Bright lime (#bef264)
        (175, 235, 80),  # Light lime
        (163, 230, 53),  # Primary lime (#a3e635) - hero color!
        (145, 210, 45),  # Medium lime
        (132, 204, 22),  # Darker lime (#84cc16)
        (115, 180, 18),  # Deep lime
        (100, 160, 15),  # Strong lime
        (115, 180, 18),  # Deep lime (return)
        (132, 204, 22),  # Darker lime (return)
        (163, 230, 53),  # Primary lime (return)
        (190, 242, 100),  # Bright lime
    ]


class GradientRenderer:
    """Handles various gradient effects."""

    @staticmethod
    def apply_white_to_grey(text: str) -> str:
        """Apply smooth white-to-grey gradient effect.

        Args:
            text: Text to apply gradient to.

        Returns:
            Text with gradient effect applied.
        """
        if not text or "\033[" in text:
            return text

        result = []
        text_length = len(text)
        grey_levels = ColorPalette.GREY_LEVELS

        for i, char in enumerate(text):
            # Calculate position in gradient (0.0 to 1.0)
            position = i / max(1, text_length - 1)

            # Map to grey level with smooth interpolation
            level_index = position * (len(grey_levels) - 1)
            level_index = min(int(level_index), len(grey_levels) - 1)

            grey_level = grey_levels[level_index]
            color_code = f"\033[38;5;{grey_level}m"
            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)

    @staticmethod
    def apply_dim_white_gradient(text: str) -> str:
        """Apply subtle dim white to dimmer white gradient.

        Args:
            text: Text to apply gradient to.

        Returns:
            Text with dim white gradient applied.
        """
        if not text or "\033[" in text:
            return text

        result = []
        text_length = len(text)
        dim_levels = ColorPalette.DIM_WHITE_LEVELS

        for i, char in enumerate(text):
            # Calculate position in gradient (0.0 to 1.0)
            position = i / max(1, text_length - 1)

            # Map to dim white level with smooth interpolation
            level_index = position * (len(dim_levels) - 1)
            level_index = min(int(level_index), len(dim_levels) - 1)

            dim_level = dim_levels[level_index]
            color_code = f"\033[38;5;{dim_level}m"
            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)

    @staticmethod
    def apply_dim_scheme_gradient(text: str) -> str:
        """Apply ultra-smooth gradient using dim color scheme.

        Args:
            text: Text to apply gradient to.

        Returns:
            Text with dim scheme gradient applied.
        """
        if not text:
            return text

        result = []
        text_length = len(text)
        color_rgb = ColorPalette.DIM_SCHEME_COLORS

        for i, char in enumerate(text):
            position = i / max(1, text_length - 1)
            scaled_pos = position * (len(color_rgb) - 1)
            color_index = int(scaled_pos)
            t = scaled_pos - color_index

            if color_index >= len(color_rgb) - 1:
                r, g, b = color_rgb[-1]
            else:
                curr_rgb = color_rgb[color_index]
                next_rgb = color_rgb[color_index + 1]

                r = curr_rgb[0] + (next_rgb[0] - curr_rgb[0]) * t
                g = curr_rgb[1] + (next_rgb[1] - curr_rgb[1]) * t
                b = curr_rgb[2] + (next_rgb[2] - curr_rgb[2]) * t

            r, g, b = int(r), int(g), int(b)
            color_code = f"\033[38;2;{r};{g};{b}m"
            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)

    @staticmethod
    def apply_custom_gradient(text: str, colors: List[Tuple[int, int, int]]) -> str:
        """Apply custom RGB gradient to text.

        Args:
            text: Text to apply gradient to.
            colors: List of RGB color tuples for gradient stops.

        Returns:
            Text with custom gradient applied.
        """
        if not text or len(colors) < 2:
            return text

        result = []
        text_length = len(text)

        for i, char in enumerate(text):
            position = i / max(1, text_length - 1)
            scaled_pos = position * (len(colors) - 1)
            color_index = int(scaled_pos)
            t = scaled_pos - color_index

            if color_index >= len(colors) - 1:
                r, g, b = colors[-1]
            else:
                curr_rgb = colors[color_index]
                next_rgb = colors[color_index + 1]

                r = curr_rgb[0] + (next_rgb[0] - curr_rgb[0]) * t
                g = curr_rgb[1] + (next_rgb[1] - curr_rgb[1]) * t
                b = curr_rgb[2] + (next_rgb[2] - curr_rgb[2]) * t

            r, g, b = int(r), int(g), int(b)
            color_code = f"\033[38;2;{r};{g};{b}m"
            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)


class ShimmerEffect:
    """Handles shimmer animation effects."""

    def __init__(self, speed: int = 3, wave_width: int = 4):
        """Initialize shimmer effect.

        Args:
            speed: Animation speed (frames between updates).
            wave_width: Width of shimmer wave in characters.
        """
        self.speed = speed
        self.wave_width = wave_width
        self.frame_counter = 0
        self.position = 0

    def configure(self, speed: int, wave_width: int) -> None:
        """Configure shimmer parameters.

        Args:
            speed: Animation speed.
            wave_width: Wave width.
        """
        self.speed = speed
        self.wave_width = wave_width

    def apply_shimmer(self, text: str) -> str:
        """Apply elegant wave shimmer effect to text.

        Args:
            text: Text to apply shimmer to.

        Returns:
            Text with shimmer effect applied.
        """
        if not text:
            return text

        # Update shimmer position
        self.frame_counter = (self.frame_counter + 1) % self.speed
        if self.frame_counter == 0:
            self.position = (self.position + 1) % (len(text) + self.wave_width * 2)

        result = []
        for i, char in enumerate(text):
            distance = abs(i - self.position)

            if distance == 0:
                # Center - bright cyan
                result.append(
                    f"{ColorPalette.BRIGHT_CYAN}{char}{ColorPalette.RESET}"
                )
            elif distance == 1:
                # Adjacent - bright blue
                result.append(
                    f"{ColorPalette.BRIGHT_BLUE}{char}{ColorPalette.RESET}"
                )
            elif distance == 2:
                # Second ring - normal blue
                result.append(
                    f"{ColorPalette.NORMAL_BLUE}{char}{ColorPalette.RESET}"
                )
            elif distance <= self.wave_width:
                # Edge - dim blue
                result.append(f"{ColorPalette.DIM_BLUE}{char}{ColorPalette.RESET}")
            else:
                # Base - darker dim blue
                result.append(f"\033[2;94m{char}{ColorPalette.RESET}")

        return "".join(result)


class StatusColorizer:
    """Handles semantic coloring of status text with ASCII icons."""

    # ASCII icon mapping (no emojis)
    ASCII_ICONS = {
        "checkmark": "√",
        "error": "×",
        "processing": "*",
        "active": "+",
        "inactive": "-",
        "ratio": "::",
        "arrow_right": ">",
        "separator": "|",
        "loading": "...",
        "count": "#",
        "circle_filled": "●",
        "circle_empty": "○",
        "circle_dot": "•",
    }

    @staticmethod
    def get_ascii_icon(icon_type: str) -> str:
        """Get ASCII icon by type.

        Args:
            icon_type: Type of icon to retrieve.

        Returns:
            ASCII character for the icon.
        """
        return StatusColorizer.ASCII_ICONS.get(icon_type, "")

    @staticmethod
    def apply_status_colors(text: str) -> str:
        """Apply semantic colors to status line text with ASCII icons.

        Args:
            text: Status text to colorize.

        Returns:
            Colorized text with ANSI codes and ASCII icons.
        """
        # Replace emoji-style indicators with ASCII equivalents
        text = text.replace(
            "🟢",
            f"{ColorPalette.BRIGHT_GREEN}"
            f"{StatusColorizer.ASCII_ICONS['circle_filled']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "🟡",
            f"{ColorPalette.DIM_YELLOW}"
            f"{StatusColorizer.ASCII_ICONS['circle_filled']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "🔴",
            f"{ColorPalette.DIM_RED}"
            f"{StatusColorizer.ASCII_ICONS['circle_filled']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "✅",
            f"{ColorPalette.BRIGHT_GREEN}"
            f"{StatusColorizer.ASCII_ICONS['checkmark']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "❌",
            f"{ColorPalette.DIM_RED}"
            f"{StatusColorizer.ASCII_ICONS['error']}"
            f"{ColorPalette.RESET}",
        )

        # Number/count highlighting (dim cyan for metrics)
        text = re.sub(
            r"\b(\d{1,3}(?:,\d{3})*)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )

        # ASCII icon patterns
        text = re.sub(
            r"\b(✓)\s*",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET} ",
            text,
        )  # Checkmarks
        text = re.sub(
            r"\b(×)\s*",
            f"{ColorPalette.DIM_RED}\\1{ColorPalette.RESET} ",
            text,
        )  # Errors
        text = re.sub(
            r"\b(\*)\s*",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET} ",
            text,
        )  # Processing
        text = re.sub(
            r"\b(\+)\s*",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET} ",
            text,
        )  # Active
        text = re.sub(
            r"\b(-)\s*",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET} ",
            text,
        )  # Inactive

        # Status indicators
        text = re.sub(
            r"\b(Processing: Yes)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Processing: No)\b",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Ready)\b",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Active)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(On)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Off)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )

        # Queue states
        text = re.sub(
            r"\b(Queue: 0)\b",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Queue: [1-9][0-9]*)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )

        # Time measurements
        text = re.sub(
            r"\b(\d+\.\d+s)\b",
            f"{ColorPalette.DIM_MAGENTA}\\1{ColorPalette.RESET}",
            text,
        )

        # Ratio highlighting (with :: separator)
        text = re.sub(
            r"\b(\d+):(\d+)\b",
            f"{ColorPalette.DIM_BLUE}\\1{ColorPalette.DIM_CYAN}::"
            f"{ColorPalette.DIM_BLUE}\\2{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Enhanced: \d+/\d+)",
            f"{ColorPalette.DIM_BLUE}\\1{ColorPalette.RESET}",
            text,
        )

        # Percentage highlighting
        text = re.sub(
            r"\b(\d+\.\d+%)\b",
            f"{ColorPalette.DIM_MAGENTA}\\1{ColorPalette.RESET}",
            text,
        )

        # Token highlighting
        text = re.sub(
            r"\b(\d+\s*tok)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(\d+K\s*tok)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )

        return text


class BannerRenderer:
    """Handles ASCII banner creation and rendering."""

    KOLLABOR_ASCII2 = [
        "██╗  ██╗ ██████╗ ██╗     ██╗      █████╗ ██████╗  ██████╗ ██████╗ ",
        "██║ ██╔╝██╔═══██╗██║     ██║     ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗",
        "█████╔╝ ██║   ██║██║     ██║     ███████║██████╔╝██║   ██║██████╔╝",
        "██╔═██╗ ██║   ██║██║     ██║     ██╔══██║██╔══██╗██║   ██║██╔══██╗",
        "██║  ██╗╚██████╔╝███████╗███████╗██║  ██║██████╔╝╚██████╔╝██║  ██║",
        "╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝",
    ]

    KOLLABOR_ASCII_v1 = [
        "▒█░▄▀ █▀▀█ █░░ █░░ █▀▀█ █▀▀▄ █▀▀█ █▀▀█   █▀▀█ ▀█▀",
        "▒█▀▄░ █░░█ █░░ █░░ █▄▄█ █▀▀▄ █░░█ █▄▄▀   █▄▄█ ░█░",
        "▒█░▒█ ▀▀▀▀ ▀▀▀ ▀▀▀ ▀░░▀ ▀▀▀░ ▀▀▀▀ ▀░▀▀ ▄ ▀░░▀ ▄█▄",
    ]
    KOLLABOR_ASCII_v2 = [
        "\r ──────────────────────────────────────────────── ",
        "\r █ ▄▀ █▀▀█ █   █   █▀▀█ █▀▀▄ █▀▀█ █▀▀█   █▀▀█ ▀█▀  ",
        "\r █▀▄  █  █ █   █   █▄▄█ █▀▀▄ █  █ █▄▄▀   █▄▄█  █   ",
        "\r ▀  ▀ ▀▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ ▀▀▀  ▀▀▀▀ ▀ ▀▀ ▀ ▀  ▀ ▀▀▀  ",
        "\r ──────────────────────────────────────────────── ",
    ]
    KOLLABOR_ASCII = [
        "\r  ██╗  ██╔════════════════════════════════════════════╗",
        "\r  ██║ ██╔╝                                            ║",
        "\r  █████╔╝ █▀▀█ █   █   █▀▀█ █▀▀▄ █▀▀█ █▀▀█   █▀▀█ ▀█▀ ║",
        "\r  ██╔═██╗ █  █ █   █   █▄▄█ █▀▀▄ █  █ █▄▄▀   █▄▄█  █  ║",
        "\r  ██║  ██╗▀▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ ▀▀▀  ▀▀▀▀ ▀ ▀▀ ▀ ▀  ▀ ▀▀▀ ║",
        "\r  ╚═╝  ╚═╩════════════════════════════════════════════╝",
    ]

    @classmethod
    def create_kollabor_banner(cls, version: str = "v1.0.0") -> str:
        """Create beautiful Kollabor ASCII banner with gradient.

        Args:
            version: Version string to display.

        Returns:
            Formatted banner with gradient colors and version.
        """
        gradient_lines = []
        for i, line in enumerate(cls.KOLLABOR_ASCII):
            gradient_line = GradientRenderer.apply_dim_scheme_gradient(line)

            # Add version to first line
            if i == 0:
                gradient_line += f" {ColorPalette.DIM}{version}{ColorPalette.RESET}"

            gradient_lines.append(gradient_line)

        return f"\n{chr(10).join(gradient_lines)}\n"


class VisualEffects:
    """Main visual effects coordinator."""

    def __init__(self):
        """Initialize visual effects system."""
        self.gradient_renderer = GradientRenderer()
        self.shimmer_effect = ShimmerEffect()
        self.status_colorizer = StatusColorizer()
        self.banner_renderer = BannerRenderer()

        # Effect configurations
        self._effects_config: Dict[str, EffectConfig] = {
            "thinking": EffectConfig(EffectType.SHIMMER, speed=3, width=4),
            "gradient": EffectConfig(EffectType.GRADIENT),
            "status": EffectConfig(EffectType.COLOR),
            "banner": EffectConfig(EffectType.GRADIENT),
        }

    def configure_effect(self, effect_name: str, **kwargs) -> None:
        """Configure a specific effect.

        Args:
            effect_name: Name of effect to configure.
            **kwargs: Configuration parameters.
        """
        if effect_name in self._effects_config:
            config = self._effects_config[effect_name]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        # Special handling for shimmer effect
        if effect_name == "thinking":
            self.shimmer_effect.configure(
                kwargs.get("speed", 3), kwargs.get("width", 4)
            )

    def apply_thinking_effect(self, text: str, effect_type: str = "shimmer") -> str:
        """Apply thinking visualization effect.

        Args:
            text: Text to apply effect to.
            effect_type: Type of effect ("shimmer", "dim", "normal").

        Returns:
            Text with thinking effect applied.
        """
        config = self._effects_config.get("thinking")
        if not config or not config.enabled:
            return text

        if effect_type == "shimmer":
            return self.shimmer_effect.apply_shimmer(text)
        elif effect_type == "dim":
            return f"{ColorPalette.DIM}{text}{ColorPalette.RESET}"
        else:
            return text

    def apply_message_gradient(
        self, text: str, gradient_type: str = "dim_white"
    ) -> str:
        """Apply gradient effect to message text.

        Args:
            text: Text to apply gradient to.
            gradient_type: Type of gradient to apply.

        Returns:
            Text with gradient applied.
        """
        config = self._effects_config.get("gradient")
        if not config or not config.enabled:
            return text

        if gradient_type == "white_to_grey":
            return self.gradient_renderer.apply_white_to_grey(text)
        elif gradient_type == "dim_white":
            return self.gradient_renderer.apply_dim_white_gradient(text)
        elif gradient_type == "dim_scheme":
            return self.gradient_renderer.apply_dim_scheme_gradient(text)
        else:
            return text

    def apply_status_colors(self, text: str) -> str:
        """Apply status colors to text.

        Args:
            text: Text to colorize.

        Returns:
            Colorized text.
        """
        config = self._effects_config.get("status")
        if not config or not config.enabled:
            return text

        return self.status_colorizer.apply_status_colors(text)

    def create_banner(self, version: str = "v1.0.0") -> str:
        """Create application banner.

        Args:
            version: Version string.

        Returns:
            Formatted banner.
        """
        config = self._effects_config.get("banner")
        if not config or not config.enabled:
            return f"KOLLABOR {version}\n"

        return self.banner_renderer.create_kollabor_banner(version)

    def get_effect_stats(self) -> Dict[str, Any]:
        """Get visual effects statistics.

        Returns:
            Dictionary with effect statistics.
        """
        return {
            "shimmer_position": self.shimmer_effect.position,
            "shimmer_frame_counter": self.shimmer_effect.frame_counter,
            "effects_config": {
                name: {
                    "enabled": config.enabled,
                    "type": getattr(config.effect_type, "value", config.effect_type),
                    "intensity": config.intensity,
                }
                for name, config in self._effects_config.items()
            },
        }
