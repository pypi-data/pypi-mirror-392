"""Plugin registry for managing and discovering plugins."""

import logging
from typing import Dict, List, Optional, Type

from flamehaven_doc_sanity.plugins.base import (
    FormatterPlugin,
    GovernancePlugin,
    Plugin,
    PluginMetadata,
    PluginType,
    ReporterPlugin,
    ValidatorPlugin,
)

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for managing plugins.

    The registry provides plugin discovery, registration, and retrieval.
    It maintains a collection of loaded plugins organized by type.
    """

    def __init__(self):
        """Initialize plugin registry."""
        self._plugins: Dict[str, Plugin] = {}
        self._plugins_by_type: Dict[PluginType, Dict[str, Plugin]] = {
            PluginType.VALIDATOR: {},
            PluginType.FORMATTER: {},
            PluginType.REPORTER: {},
            PluginType.GOVERNANCE: {},
        }

    def register(self, plugin: Plugin) -> bool:
        """Register a plugin.

        Args:
            plugin: Plugin instance to register

        Returns:
            True if registration successful, False otherwise
        """
        try:
            metadata = plugin.get_metadata()

            # Check if plugin already registered
            if metadata.name in self._plugins:
                logger.warning(f"Plugin {metadata.name} already registered. Skipping.")
                return False

            # Initialize plugin
            if not plugin.initialize():
                logger.error(f"Failed to initialize plugin {metadata.name}")
                return False

            # Register plugin
            self._plugins[metadata.name] = plugin
            self._plugins_by_type[metadata.plugin_type][metadata.name] = plugin

            logger.info(
                f"Registered plugin: {metadata.name} v{metadata.version} "
                f"(type: {metadata.plugin_type.value})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False

    def unregister(self, plugin_name: str) -> bool:
        """Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if unregistration successful, False otherwise
        """
        if plugin_name not in self._plugins:
            logger.warning(f"Plugin {plugin_name} not found in registry")
            return False

        try:
            plugin = self._plugins[plugin_name]
            metadata = plugin.get_metadata()

            # Cleanup plugin
            plugin.cleanup()

            # Remove from registry
            del self._plugins[plugin_name]
            del self._plugins_by_type[metadata.plugin_type][plugin_name]

            logger.info(f"Unregistered plugin: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister plugin {plugin_name}: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a plugin by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> Dict[str, Plugin]:
        """Get all plugins of a specific type.

        Args:
            plugin_type: Type of plugins to retrieve

        Returns:
            Dictionary of plugin name -> plugin instance
        """
        return self._plugins_by_type.get(plugin_type, {}).copy()

    def get_all_plugins(self) -> Dict[str, Plugin]:
        """Get all registered plugins.

        Returns:
            Dictionary of plugin name -> plugin instance
        """
        return self._plugins.copy()

    def get_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get metadata for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            PluginMetadata or None if plugin not found
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            return plugin.get_metadata()
        return None

    def list_plugins(self) -> List[Dict[str, str]]:
        """List all registered plugins with basic info.

        Returns:
            List of plugin info dictionaries
        """
        result = []
        for plugin in self._plugins.values():
            metadata = plugin.get_metadata()
            result.append(
                {
                    "name": metadata.name,
                    "version": metadata.version,
                    "type": metadata.plugin_type.value,
                    "author": metadata.author,
                    "enabled": plugin.is_enabled(),
                }
            )
        return result

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin.

        Args:
            plugin_name: Name of plugin to enable

        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enable()
            logger.info(f"Enabled plugin: {plugin_name}")
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin.

        Args:
            plugin_name: Name of plugin to disable

        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.disable()
            logger.info(f"Disabled plugin: {plugin_name}")
            return True
        return False

    def clear(self) -> None:
        """Clear all plugins from registry.

        Cleanup all plugins before removing them.
        """
        for plugin_name in list(self._plugins.keys()):
            self.unregister(plugin_name)

    def get_validator_plugins(self) -> Dict[str, ValidatorPlugin]:
        """Get all validator plugins.

        Returns:
            Dictionary of validator plugins
        """
        return self.get_plugins_by_type(PluginType.VALIDATOR)

    def get_formatter_plugins(self) -> Dict[str, FormatterPlugin]:
        """Get all formatter plugins.

        Returns:
            Dictionary of formatter plugins
        """
        return self.get_plugins_by_type(PluginType.FORMATTER)

    def get_reporter_plugins(self) -> Dict[str, ReporterPlugin]:
        """Get all reporter plugins.

        Returns:
            Dictionary of reporter plugins
        """
        return self.get_plugins_by_type(PluginType.REPORTER)

    def get_governance_plugins(self) -> Dict[str, GovernancePlugin]:
        """Get all governance plugins.

        Returns:
            Dictionary of governance plugins
        """
        return self.get_plugins_by_type(PluginType.GOVERNANCE)


# Global plugin registry instance
_global_registry: Optional[PluginRegistry] = None


def get_global_registry() -> PluginRegistry:
    """Get the global plugin registry instance.

    Returns:
        Global PluginRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
    return _global_registry
