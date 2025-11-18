"""Configuration widget definitions for modal UI."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ConfigWidgetDefinitions:
    """Defines which config values get which widgets in the modal."""

    @staticmethod
    def get_available_plugins() -> List[Dict[str, Any]]:
        """Get list of available plugins for configuration.

        Returns:
            List of plugin information dictionaries.
        """
        plugins = []

        # Define known plugins with their descriptions
        known_plugins = {
            "enhanced_input": {
                "name": "Enhanced Input",
                "description": "Bordered input boxes with Unicode characters"
            },
            "system_commands": {
                "name": "System Commands",
                "description": "Core system commands (/help, /config, /status)"
            },
            "hook_monitoring": {
                "name": "Hook Monitoring",
                "description": "Monitor and debug hook system activity"
            },
            "query_enhancer": {
                "name": "Query Enhancer",
                "description": "Enhance and optimize user queries"
            },
            "workflow_enforcement": {
                "name": "Workflow Enforcement",
                "description": "Enforce specific workflow patterns"
            },
            "fullscreen": {
                "name": "Fullscreen Effects",
                "description": "Fullscreen visual effects and animations"
            }
        }

        # Create plugin widgets
        for plugin_id, info in known_plugins.items():
            plugins.append({
                "type": "checkbox",
                "label": info["name"],
                "config_path": f"plugins.{plugin_id}.enabled",
                "help": info["description"]
            })

        return plugins

    @staticmethod
    def get_config_modal_definition() -> Dict[str, Any]:
        """Get the complete modal definition for /config command.

        Returns:
            Dictionary defining the modal layout and widgets.
        """
        # Get plugin widgets
        plugin_widgets = ConfigWidgetDefinitions.get_available_plugins()

        return {
            "title": "System Configuration",
            "footer": "↑↓ navigate • Enter edit • Tab next • Esc cancel • Ctrl+S save",
            "width": 80,  # 80% of screen width
            "height": 20,
            "sections": [
                {
                    "title": "Terminal Settings",
                    "widgets": [
                        {
                            "type": "slider",
                            "label": "Render FPS",
                            "config_path": "terminal.render_fps",
                            "min_value": 1,
                            "max_value": 60,
                            "step": 1,
                            "help": "Terminal refresh rate (1-60 FPS)"
                        },
                        {
                            "type": "slider",
                            "label": "Status Lines",
                            "config_path": "terminal.status_lines",
                            "min_value": 1,
                            "max_value": 10,
                            "step": 1,
                            "help": "Number of status lines to display"
                        },
                        {
                            "type": "dropdown",
                            "label": "Thinking Effect",
                            "config_path": "terminal.thinking_effect",
                            "options": ["shimmer", "pulse", "wave", "none"],
                            "help": "Visual effect for thinking animations"
                        },
                        {
                            "type": "slider",
                            "label": "Shimmer Speed",
                            "config_path": "terminal.shimmer_speed",
                            "min_value": 1,
                            "max_value": 10,
                            "step": 1,
                            "help": "Speed of shimmer animation effect"
                        },
                        {
                            "type": "checkbox",
                            "label": "Enable Render Cache",
                            "config_path": "terminal.render_cache_enabled",
                            "help": "Cache renders to reduce unnecessary terminal I/O when idle"
                        }
                    ]
                },
                {
                    "title": "Input Settings",
                    "widgets": [
                        {
                            "type": "checkbox",
                            "label": "Ctrl+C Exit",
                            "config_path": "input.ctrl_c_exit",
                            "help": "Allow Ctrl+C to exit application"
                        },
                        {
                            "type": "checkbox",
                            "label": "Backspace Enabled",
                            "config_path": "input.backspace_enabled",
                            "help": "Enable backspace key for text editing"
                        },
                        {
                            "type": "slider",
                            "label": "History Limit",
                            "config_path": "input.history_limit",
                            "min_value": 10,
                            "max_value": 1000,
                            "step": 10,
                            "help": "Maximum number of history entries"
                        }
                    ]
                },
                {
                    "title": "LLM Settings",
                    "widgets": [
                        {
                            "type": "text_input",
                            "label": "API URL",
                            "config_path": "core.llm.api_url",
                            "placeholder": "http://localhost:1234",
                            "help": "LLM API endpoint URL"
                        },
                        {
                            "type": "text_input",
                            "label": "Model",
                            "config_path": "core.llm.model",
                            "placeholder": "qwen/qwen3-4b",
                            "help": "LLM model identifier"
                        },
                        {
                            "type": "slider",
                            "label": "Temperature",
                            "config_path": "core.llm.temperature",
                            "min_value": 0.0,
                            "max_value": 2.0,
                            "step": 0.1,
                            "help": "Creativity/randomness of responses (0.0-2.0)"
                        },
                        {
                            "type": "slider",
                            "label": "Max History",
                            "config_path": "core.llm.max_history",
                            "min_value": 10,
                            "max_value": 200,
                            "step": 10,
                            "help": "Maximum conversation history entries"
                        }
                    ]
                },
                {
                    "title": "Application Settings",
                    "widgets": [
                        {
                            "type": "text_input",
                            "label": "Application Name",
                            "config_path": "application.name",
                            "placeholder": "Kollabor CLI",
                            "help": "Display name for the application"
                        },
                        {
                            "type": "text_input",
                            "label": "Version",
                            "config_path": "application.version",
                            "placeholder": "1.0.0",
                            "help": "Current application version"
                        }
                    ]
                },
                {
                    "title": "Plugin Settings",
                    "widgets": plugin_widgets
                }
            ],
            "actions": [
                {
                    "key": "Ctrl+S",
                    "label": "Save",
                    "action": "save",
                    "style": "primary"
                },
                {
                    "key": "Escape",
                    "label": "Cancel",
                    "action": "cancel",
                    "style": "secondary"
                }
            ]
        }

    @staticmethod
    def create_widgets_from_definition(config_service, definition: Dict[str, Any]) -> List[Any]:
        """Create widget instances from modal definition.

        Args:
            config_service: ConfigService for reading current values.
            definition: Modal definition dictionary.

        Returns:
            List of instantiated widgets.
        """
        widgets = []

        try:
            from .widgets.checkbox import CheckboxWidget
            from .widgets.dropdown import DropdownWidget
            from .widgets.text_input import TextInputWidget
            from .widgets.slider import SliderWidget

            widget_classes = {
                "checkbox": CheckboxWidget,
                "dropdown": DropdownWidget,
                "text_input": TextInputWidget,
                "slider": SliderWidget
            }

            for section in definition.get("sections", []):
                for widget_def in section.get("widgets", []):
                    widget_type = widget_def["type"]
                    widget_class = widget_classes.get(widget_type)

                    if not widget_class:
                        logger.error(f"Unknown widget type: {widget_type}")
                        continue

                    # Get current value from config
                    config_path = widget_def["config_path"]
                    current_value = config_service.get(config_path)

                    # Create widget with configuration
                    widget = widget_class(
                        label=widget_def["label"],
                        config_path=config_path,
                        help_text=widget_def.get("help", ""),
                        current_value=current_value,
                        **{k: v for k, v in widget_def.items()
                           if k not in ["type", "label", "config_path", "help"]}
                    )

                    widgets.append(widget)
                    logger.debug(f"Created {widget_type} widget for {config_path}")

        except Exception as e:
            logger.error(f"Error creating widgets from definition: {e}")

        logger.info(f"Created {len(widgets)} widgets from definition")
        return widgets

    @staticmethod
    def get_widget_navigation_info() -> Dict[str, str]:
        """Get navigation key information for modal help.

        Returns:
            Dictionary mapping keys to their descriptions.
        """
        return {
            "↑↓": "Navigate between widgets",
            "←→": "Adjust slider values / Navigate dropdown options",
            "Enter": "Toggle checkbox / Open dropdown / Edit text",
            "Space": "Toggle checkbox",
            "Tab": "Next widget",
            "Shift+Tab": "Previous widget",
            "Ctrl+S": "Save all changes",
            "Escape": "Cancel and exit without saving"
        }