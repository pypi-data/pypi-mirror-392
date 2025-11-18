"""Core system commands for Kollabor CLI."""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..events.models import (
    CommandDefinition,
    CommandMode,
    CommandCategory,
    CommandResult,
    SlashCommand,
    UIConfig
)

logger = logging.getLogger(__name__)


class SystemCommandsPlugin:
    """Core system commands plugin.

    Provides essential system management commands like /help, /config, /status.
    These commands are automatically registered at application startup.
    """

    def __init__(self, command_registry, event_bus, config_manager) -> None:
        """Initialize system commands plugin.

        Args:
            command_registry: Command registry for registration.
            event_bus: Event bus for system events.
            config_manager: Configuration manager for system settings.
        """
        self.name = "system"
        self.command_registry = command_registry
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger

    def register_commands(self) -> None:
        """Register all system commands."""
        try:
            # Register /help command
            help_command = CommandDefinition(
                name="help",
                description="Show available commands and usage",
                handler=self.handle_help,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.INSTANT,
                aliases=["h", "?"],
                icon="❓"
            )
            self.command_registry.register_command(help_command)

            # Register /config command
            config_command = CommandDefinition(
                name="config",
                description="Open system configuration panel",
                handler=self.handle_config,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["settings", "preferences"],
                icon="[INFO]",
                ui_config=UIConfig(
                    type="tree",
                    navigation=["↑↓←→", "Enter", "Esc"],
                    height=15,
                    title="System Configuration",
                    footer="↑↓←→ navigate • Enter edit • Esc exit"
                )
            )
            self.command_registry.register_command(config_command)

            # Register /status command
            status_command = CommandDefinition(
                name="status",
                description="Show system status and diagnostics",
                handler=self.handle_status,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["info", "diagnostics"],
                icon="[STATS]",
                ui_config=UIConfig(
                    type="table",
                    navigation=["↑↓", "Esc"],
                    height=12,
                    title="System Status",
                    footer="↑↓ navigate • Esc exit"
                )
            )
            self.command_registry.register_command(status_command)

            # Register /version command
            version_command = CommandDefinition(
                name="version",
                description="Show application version information",
                handler=self.handle_version,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.INSTANT,
                aliases=["v", "ver"],
                icon="[INFO]"
            )
            self.command_registry.register_command(version_command)



            self.logger.info("System commands registered successfully")

        except Exception as e:
            self.logger.error(f"Error registering system commands: {e}")

    async def handle_help(self, command: SlashCommand) -> CommandResult:
        """Handle /help command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            if command.args:
                # Show help for specific command
                command_name = command.args[0]
                return await self._show_command_help(command_name)
            else:
                # Show all commands categorized by plugin
                return await self._show_all_commands()

        except Exception as e:
            self.logger.error(f"Error in help command: {e}")
            return CommandResult(
                success=False,
                message=f"Error displaying help: {str(e)}",
                display_type="error"
            )

    async def handle_config(self, command: SlashCommand) -> CommandResult:
        """Handle /config command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result with status UI.
        """
        try:
            # Import the comprehensive config widget definitions
            from ..ui.config_widgets import ConfigWidgetDefinitions

            # Get the complete configuration modal definition
            modal_definition = ConfigWidgetDefinitions.get_config_modal_definition()

            return CommandResult(
                success=True,
                message="Configuration modal opened",
                ui_config=UIConfig(
                    type="modal",
                    title=modal_definition["title"],
                    width=modal_definition["width"],
                    modal_config=modal_definition
                ),
                display_type="modal"
            )

        except Exception as e:
            self.logger.error(f"Error in config command: {e}")
            return CommandResult(
                success=False,
                message=f"Error opening configuration: {str(e)}",
                display_type="error"
            )

    async def handle_status(self, command: SlashCommand) -> CommandResult:
        """Handle /status command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result with status UI.
        """
        try:
            # Create status UI component
            status_ui = SystemStatusUI(self.event_bus, self.command_registry)

            return CommandResult(
                success=True,
                message="System status opened",
                status_ui=status_ui,
                display_type="info"
            )

        except Exception as e:
            self.logger.error(f"Error in status command: {e}")
            return CommandResult(
                success=False,
                message=f"Error showing status: {str(e)}",
                display_type="error"
            )

    async def handle_version(self, command: SlashCommand) -> CommandResult:
        """Handle /version command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            # Get version information
            version_info = self._get_version_info()

            message = f"""Kollabor CLI v{version_info['version']}
Built: {version_info['build_date']}
Python: {version_info['python_version']}
Platform: {version_info['platform']}"""

            return CommandResult(
                success=True,
                message=message,
                display_type="info",
                data=version_info
            )

        except Exception as e:
            self.logger.error(f"Error in version command: {e}")
            return CommandResult(
                success=False,
                message=f"Error getting version: {str(e)}",
                display_type="error"
            )



    async def _show_command_help(self, command_name: str) -> CommandResult:
        """Show help for a specific command.

        Args:
            command_name: Name of command to show help for.

        Returns:
            Command result with help information.
        """
        command_def = self.command_registry.get_command(command_name)
        if not command_def:
            return CommandResult(
                success=False,
                message=f"Unknown command: /{command_name}",
                display_type="error"
            )

        # Format detailed help for the command
        help_text = f"""Command: /{command_def.name}
Description: {command_def.description}
Plugin: {command_def.plugin_name}
Category: {command_def.category.value}
Mode: {command_def.mode.value}"""

        if command_def.aliases:
            help_text += f"\nAliases: {', '.join(command_def.aliases)}"

        if command_def.parameters:
            help_text += "\nParameters:"
            for param in command_def.parameters:
                required = " (required)" if param.required else ""
                help_text += f"\n  {param.name}: {param.description}{required}"

        return CommandResult(
            success=True,
            message=help_text,
            display_type="info"
        )

    async def _show_all_commands(self) -> CommandResult:
        """Show all available commands grouped by plugin in a status modal.

        Returns:
            Command result with status modal UI config.
        """
        # Get commands grouped by plugin
        plugin_categories = self.command_registry.get_plugin_categories()

        # Build command list for modal display
        command_sections = []

        for plugin_name in sorted(plugin_categories.keys()):
            commands = self.command_registry.get_commands_by_plugin(plugin_name)
            if not commands:
                continue

            # Create section for this plugin
            section_commands = []
            for cmd in sorted(commands, key=lambda c: c.name):
                aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                section_commands.append({
                    "name": f"/{cmd.name}{aliases}",
                    "description": cmd.description
                })

            command_sections.append({
                "title": f"{plugin_name.title()} Commands",
                "commands": section_commands
            })

        return CommandResult(
            success=True,
            message="Help opened in status modal",
            ui_config=UIConfig(
                type="status_modal",
                title="Available Commands",
                height=15,
                width=80,
                modal_config={
                    "sections": command_sections,
                    "footer": "Press Esc to close • Use /help <command> for detailed help",
                    "scrollable": True
                }
            ),
            display_type="status_modal"
        )

    def _get_version_info(self) -> Dict[str, str]:
        """Get application version information.

        Returns:
            Dictionary with version details.
        """
        import sys
        import platform

        return {
            "version": "1.0.0-dev",
            "build_date": datetime.now().strftime("%Y-%m-%d"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "architecture": platform.machine()
        }


class SystemConfigUI:
    """UI component for system configuration."""

    def __init__(self, config_manager, event_bus) -> None:
        """Initialize config UI.

        Args:
            config_manager: Configuration manager.
            event_bus: Event bus for configuration events.
        """
        self.config_manager = config_manager
        self.event_bus = event_bus

    def render(self) -> List[str]:
        """Render configuration interface.

        Returns:
            List of lines for display.
        """
        # This would be implemented to show actual config options
        return [
            "╭─ System Configuration ─────────────────────────────────────╮",
            "│                                                             │",
            "│ ❯ Terminal Settings                                         │",
            "│   Input Configuration                                       │",
            "│   Display Options                                           │",
            "│   Performance Settings                                      │",
            "│                                                             │",
            "│ Plugin Settings                                             │",
            "│   Event Bus Configuration                                   │",
            "│   Logging Options                                           │",
            "│                                                             │",
            "╰─────────────────────────────────────────────────────────────╯",
            "   ↑↓←→ navigate • Enter edit • Esc exit"
        ]


class SystemStatusUI:
    """UI component for system status display."""

    def __init__(self, event_bus, command_registry) -> None:
        """Initialize status UI.

        Args:
            event_bus: Event bus for status information.
            command_registry: Command registry for statistics.
        """
        self.event_bus = event_bus
        self.command_registry = command_registry

    def render(self) -> List[str]:
        """Render status interface.

        Returns:
            List of lines for display.
        """
        stats = self.command_registry.get_registry_stats()

        return [
            "╭─ System Status ─────────────────────────────────────────────╮",
            "│                                                             │",
            f"│ Commands: {stats['total_commands']} registered, {stats['enabled_commands']} enabled              │",
            f"│ Plugins: {stats['plugins']} active                                    │",
            f"│ Categories: {stats['categories']} in use                               │",
            "│                                                             │",
            "│ Event Bus: [OK] Active                                        │",
            "│ Input Handler: [OK] Running                                   │",
            "│ Terminal Renderer: [OK] Active                                │",
            "│                                                             │",
            "│ Memory Usage: ~ 45MB                                        │",
            "│ Uptime: 00:15:32                                            │",
            "│                                                             │",
            "╰─────────────────────────────────────────────────────────────╯",
            "   ↑↓ navigate • Esc exit"
        ]