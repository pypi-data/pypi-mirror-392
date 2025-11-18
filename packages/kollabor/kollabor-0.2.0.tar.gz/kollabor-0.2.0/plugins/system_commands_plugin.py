"""System commands plugin for core application functionality."""

import logging
from core.commands.system_commands import SystemCommandsPlugin

logger = logging.getLogger(__name__)


class SystemCommandsPluginWrapper:
    """Plugin wrapper for system commands integration.

    Provides the system commands as a plugin that gets loaded
    during application initialization.
    """

    def __init__(self) -> None:
        """Initialize the system commands plugin wrapper."""
        self.name = "system_commands"
        self.version = "1.0.0"
        self.description = "Core system commands (/help, /config, /status, etc.)"
        self.enabled = True
        self.system_commands = None
        self.logger = logger

    async def initialize(self, event_bus, config, **kwargs) -> None:
        """Initialize the plugin and register system commands.

        Args:
            event_bus: Application event bus.
            config: Configuration manager.
            **kwargs: Additional initialization parameters.
        """
        try:
            # Get command registry from input handler if available
            command_registry = kwargs.get('command_registry')
            if not command_registry:
                self.logger.warning("No command registry provided, system commands not registered")
                return

            # Create and initialize system commands
            self.system_commands = SystemCommandsPlugin(
                command_registry=command_registry,
                event_bus=event_bus,
                config_manager=config
            )

            # Register all system commands
            self.system_commands.register_commands()

            self.logger.info("System commands plugin initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing system commands plugin: {e}")
            raise

    async def shutdown(self) -> None:
        """Shutdown the plugin and cleanup resources."""
        try:
            if self.system_commands:
                # Unregister commands would happen here if needed
                self.logger.info("System commands plugin shutdown completed")

        except Exception as e:
            self.logger.error(f"Error shutting down system commands plugin: {e}")

    def get_status_line(self) -> str:
        """Get status line information for the plugin.

        Returns:
            Status line string.
        """
        if self.system_commands:
            return "System commands active"
        return "System commands inactive"

    def register_hooks(self) -> None:
        """Register event hooks for the plugin.

        System commands don't need additional hooks beyond command registration.
        """
        pass