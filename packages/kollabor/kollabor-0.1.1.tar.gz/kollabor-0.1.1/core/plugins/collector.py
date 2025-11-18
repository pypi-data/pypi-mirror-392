"""Plugin status collector for aggregating status information from plugins."""

import logging
from typing import Any, Dict, List

from ..utils.plugin_utils import collect_plugin_status_safely
from ..utils.error_utils import safe_execute

logger = logging.getLogger(__name__)


class PluginStatusCollector:
    """Collects and aggregates status information from plugin instances.
    
    This class is responsible for gathering status lines from all plugins,
    organizing them by display areas, and providing aggregated status data.
    """
    
    def __init__(self):
        """Initialize the plugin status collector."""
        self.last_status_collection: Dict[str, Dict[str, List[str]]] = {}
        self.collection_errors: Dict[str, str] = {}
        logger.info("PluginStatusCollector initialized")
    
    def collect_plugin_status(self, plugin_name: str, plugin_instance: Any) -> Dict[str, List[str]]:
        """Collect status information from a single plugin.
        
        Args:
            plugin_name: Name of the plugin.
            plugin_instance: The plugin instance to collect status from.
            
        Returns:
            Dictionary with areas A, B, C containing lists of status lines.
        """
        plugin_status = collect_plugin_status_safely(plugin_instance, plugin_name)
        
        # Store the status for this plugin
        self.last_status_collection[plugin_name] = plugin_status
        
        # Clear any previous collection errors for this plugin
        if plugin_name in self.collection_errors:
            del self.collection_errors[plugin_name]
        
        return plugin_status
    
    def collect_all_status(self, plugin_instances: Dict[str, Any]) -> Dict[str, List[str]]:
        """Collect status lines from all plugins organized by area.
        
        Args:
            plugin_instances: Dictionary of plugin instances.
            
        Returns:
            Dictionary with areas A, B, C containing aggregated status lines.
        """
        status_areas = {"A": [], "B": [], "C": []}
        
        for plugin_name, plugin_instance in plugin_instances.items():
            plugin_status = self.collect_plugin_status(plugin_name, plugin_instance)
            
            # Merge the status from this plugin into our aggregated status
            for area in ["A", "B", "C"]:
                if area in plugin_status:
                    status_areas[area].extend(plugin_status[area])
        
        #logger.debug(f"Collected status from {len(plugin_instances)} plugins")
        return status_areas
    
    def get_plugin_startup_info(self, plugin_name: str, plugin_class: type, config: Any) -> List[str]:
        """Get startup information for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin.
            plugin_class: The plugin class.
            config: Configuration manager instance.
            
        Returns:
            List of startup info strings, or empty list if no info available.
        """
        def get_startup_info():
            return plugin_class.get_startup_info(config)
        
        result = safe_execute(
            get_startup_info,
            f"getting startup info from plugin {plugin_name}",
            default=[],
            logger_instance=logger
        )
        
        return result if isinstance(result, list) else []
    
    def collect_all_startup_info(self, plugin_classes: Dict[str, type], config: Any) -> Dict[str, List[str]]:
        """Collect startup information from all plugin classes.
        
        Args:
            plugin_classes: Dictionary mapping plugin names to classes.
            config: Configuration manager instance.
            
        Returns:
            Dictionary mapping plugin names to their startup info lists.
        """
        startup_info = {}
        
        for plugin_name, plugin_class in plugin_classes.items():
            info_list = self.get_plugin_startup_info(plugin_name, plugin_class, config)
            if info_list:
                startup_info[plugin_name] = info_list
        
        logger.debug(f"Collected startup info from {len(startup_info)} plugins")
        return startup_info
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the last status collection.
        
        Returns:
            Dictionary with status collection summary.
        """
        total_lines = 0
        areas_summary = {"A": 0, "B": 0, "C": 0}
        
        for plugin_name, status in self.last_status_collection.items():
            for area in ["A", "B", "C"]:
                if area in status:
                    line_count = len(status[area])
                    areas_summary[area] += line_count
                    total_lines += line_count
        
        return {
            "total_plugins": len(self.last_status_collection),
            "total_status_lines": total_lines,
            "lines_per_area": areas_summary,
            "collection_errors": len(self.collection_errors),
            "plugins_with_status": [
                name for name, status in self.last_status_collection.items() 
                if any(status.get(area) for area in ["A", "B", "C"])
            ]
        }
    
    def get_plugin_status_details(self, plugin_name: str) -> Dict[str, Any]:
        """Get detailed status information for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin.
            
        Returns:
            Dictionary with detailed status information for the plugin.
        """
        if plugin_name not in self.last_status_collection:
            return {
                "plugin_name": plugin_name,
                "status_collected": False,
                "error": "No status collection found"
            }
        
        status = self.last_status_collection[plugin_name]
        
        return {
            "plugin_name": plugin_name,
            "status_collected": True,
            "areas": {
                area: {
                    "line_count": len(lines),
                    "lines": lines
                }
                for area, lines in status.items()
            },
            "has_error": plugin_name in self.collection_errors,
            "error": self.collection_errors.get(plugin_name)
        }
    
    def clear_status_history(self) -> None:
        """Clear all stored status collection history."""
        self.last_status_collection.clear()
        self.collection_errors.clear()
        logger.debug("Cleared status collection history")
    
    def get_status_by_area(self, area: str) -> List[str]:
        """Get all status lines for a specific area across all plugins.
        
        Args:
            area: The area to get status for ("A", "B", or "C").
            
        Returns:
            List of status lines for the specified area.
        """
        if area not in ["A", "B", "C"]:
            logger.warning(f"Invalid status area: {area}")
            return []
        
        lines = []
        for plugin_name, status in self.last_status_collection.items():
            if area in status:
                lines.extend(status[area])
        
        return lines
    
    def get_collector_stats(self) -> Dict[str, Any]:
        """Get statistics about the collector's operations.
        
        Returns:
            Dictionary with collector statistics.
        """
        total_collections = len(self.last_status_collection)
        successful_collections = total_collections - len(self.collection_errors)
        
        return {
            "total_collections": total_collections,
            "successful_collections": successful_collections,
            "collection_errors": len(self.collection_errors),
            "plugins_tracked": list(self.last_status_collection.keys()),
            "error_plugins": list(self.collection_errors.keys()),
            "status_summary": self.get_status_summary()
        }