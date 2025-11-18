"""Configuration loading and plugin integration logic."""

import logging
from pathlib import Path
from typing import Any, Dict

from ..utils import deep_merge
from ..utils.error_utils import safe_execute, log_and_continue
from .manager import ConfigManager

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Handles complex configuration loading with plugin integration.
    
    This class manages the coordination between file-based configuration
    and plugin-provided configurations, implementing the complex merging
    logic that was previously in ConfigManager.
    """
    
    def __init__(self, config_manager: ConfigManager, plugin_registry=None):
        """Initialize the config loader.
        
        Args:
            config_manager: Basic config manager for file operations.
            plugin_registry: Optional plugin registry for plugin configs.
        """
        self.config_manager = config_manager
        self.plugin_registry = plugin_registry
        logger.debug("ConfigLoader initialized")
    
    def get_base_config(self) -> Dict[str, Any]:
        """Get the base application configuration with defaults.
        
        Returns:
            Base configuration dictionary with application defaults.
        """
        return {
            "terminal": {
                "render_fps": 20,
                "spinner_frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧"],
                "status_lines": 4,
                "thinking_message_limit": 2,
                "thinking_effect": "shimmer",
                "shimmer_speed": 3,
                "shimmer_wave_width": 4,
                "render_error_delay": 0.1,
                "render_cache_enabled": True
            },
            "input": {
                "ctrl_c_exit": True,
                "backspace_enabled": True,
                "input_buffer_limit": 100000,
                "polling_delay": 0.01,
                "error_delay": 0.1,
                "history_limit": 100,
                "error_threshold": 10,
                "error_window_minutes": 5,
                "max_errors": 100,
                "paste_detection_enabled": True,
                "paste_threshold_ms": 50,
                "paste_min_chars": 3,
                "paste_max_chars": 10000,
                "bracketed_paste_enabled": True
            },
            "logging": {
                "level": "INFO",
                "file": ".kollabor/logs/kollabor.log",
                "format_type": "compact",
                "format": "%(asctime)s - %(levelname)-4s - %(message)-100s - %(filename)s:%(lineno)04d"
            },
            "hooks": {
                "default_timeout": 30,
                "default_retries": 3,
                "default_error_action": "continue"
            },
            "application": {
                "name": "Kollabor CLI",
                "version": "1.0.0",
                "description": "AI Edition"
            },
            "core": {
                "llm": {
                    "api_url": "http://localhost:1234",
                    "model": "qwen/qwen3-4b",
                    "temperature": 0.7,
                    "timeout": 120,
                    "max_history": 90,
                    "save_conversations": True,
                    "conversation_format": "jsonl",
                    "show_status": True,
                    "http_connector_limit": 10,
                    "message_history_limit": 20,
                    "thinking_phase_delay": 0.5,
                    "log_message_truncate": 50,
                    "enable_streaming": False,
                    "processing_delay": 0.1,
                    "thinking_delay": 0.3,
                    "api_poll_delay": 0.01,
                    "terminal_timeout": 30,
                    "mcp_timeout": 60
                }
            },
            "performance": {
                "failure_rate_warning": 0.05,
                "failure_rate_critical": 0.15,
                "degradation_threshold": 0.15
            },
            "plugins": {
                "enhanced_input": {
                    "enabled": True
                },
                "system_commands": {
                    "enabled": True
                },
                "hook_monitoring": {
                    "enabled": False
                },
                "query_enhancer": {
                    "enabled": False
                },
                "workflow_enforcement": {
                    "enabled": False
                },
                "fullscreen": {
                    "enabled": False
                }
            }
        }
    
    def get_plugin_configs(self) -> Dict[str, Any]:
        """Get merged configuration from all plugins.
        
        Returns:
            Merged plugin configurations or empty dict if no plugins.
        """
        if not self.plugin_registry:
            return {}
        
        def get_configs():
            return self.plugin_registry.get_merged_config()
        
        plugin_configs = safe_execute(
            get_configs,
            "getting plugin configurations",
            default={},
            logger_instance=logger
        )
        
        return plugin_configs if isinstance(plugin_configs, dict) else {}
    
    def load_complete_config(self) -> Dict[str, Any]:
        """Load complete configuration including plugins.
        
        This is the main entry point for getting a fully merged configuration
        that includes base defaults, plugin configs, and user overrides.
        
        Returns:
            Complete merged configuration dictionary.
        """
        # Start with base application configuration
        base_config = self.get_base_config()
        
        # Add plugin configurations
        plugin_configs = self.get_plugin_configs()
        if plugin_configs:
            base_config = deep_merge(base_config, plugin_configs)
            logger.debug(f"Merged configurations from plugins")
        
        # Load any existing user configuration
        if self.config_manager.config_path.exists():
            user_config = self.config_manager.load_config_file()
            if user_config:
                # User config takes precedence over defaults and plugins
                base_config = deep_merge(base_config, user_config)
                logger.debug("Merged user configuration")
        
        return base_config
    
    def save_merged_config(self, config: Dict[str, Any]) -> bool:
        """Save the complete merged configuration to file.
        
        Args:
            config: Configuration dictionary to save.
            
        Returns:
            True if save successful, False otherwise.
        """
        return self.config_manager.save_config_file(config)
    
    def update_with_plugins(self) -> bool:
        """Update the configuration file with newly discovered plugins.
        
        This method reloads the complete configuration including any new
        plugin configurations and saves it to the config file.
        
        Returns:
            True if update successful, False otherwise.
        """
        if not self.plugin_registry:
            logger.warning("No plugin registry available for config update")
            return False
        
        try:
            # Load complete config including plugins
            updated_config = self.load_complete_config()
            
            # Save the updated configuration
            success = self.save_merged_config(updated_config)
            
            if success:
                # Update the config manager's in-memory config
                self.config_manager.config = updated_config
                plugin_count = len(self.plugin_registry.list_plugins())
                logger.info(f"Updated config with configurations from {plugin_count} plugins")
            
            return success
            
        except Exception as e:
            log_and_continue(logger, "updating config with plugins", e)
            return False