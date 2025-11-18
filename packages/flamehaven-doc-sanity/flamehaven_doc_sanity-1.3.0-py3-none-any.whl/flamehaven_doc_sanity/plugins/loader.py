"""Plugin loader for discovering and loading plugins."""

import importlib
import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

from flamehaven_doc_sanity.plugins.base import Plugin
from flamehaven_doc_sanity.plugins.registry import PluginRegistry, get_global_registry

logger = logging.getLogger(__name__)


class PluginLoader:
    """Discovers and loads plugins from filesystem.

    The loader can:
    - Discover plugins in specified directories
    - Load plugins from Python modules
    - Hot-reload plugins (reload without restarting)
    - Load plugin configurations from YAML
    """

    def __init__(self, registry: Optional[PluginRegistry] = None):
        """Initialize plugin loader.

        Args:
            registry: Plugin registry to use (default: global registry)
        """
        self.registry = registry or get_global_registry()
        self._loaded_modules: Dict[str, Any] = {}

    def discover_plugins(self, plugin_dir: Path) -> List[Type[Plugin]]:
        """Discover plugin classes in a directory.

        Args:
            plugin_dir: Directory to search for plugins

        Returns:
            List of discovered plugin classes
        """
        if not plugin_dir.exists():
            logger.warning(f"Plugin directory does not exist: {plugin_dir}")
            return []

        discovered = []

        # Find all .py files in plugin directory
        for py_file in plugin_dir.glob("**/*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                plugin_classes = self._load_module_plugins(py_file)
                discovered.extend(plugin_classes)
            except Exception as e:
                logger.error(f"Failed to load plugins from {py_file}: {e}")

        logger.info(f"Discovered {len(discovered)} plugin(s) in {plugin_dir}")
        return discovered

    def _load_module_plugins(self, module_path: Path) -> List[Type[Plugin]]:
        """Load plugin classes from a Python module.

        Args:
            module_path: Path to Python module

        Returns:
            List of plugin classes found in module
        """
        # Generate module name from path
        module_name = f"flamehaven_plugins.{module_path.stem}"

        # Load module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load module spec for {module_path}")
            return []

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        self._loaded_modules[str(module_path)] = module

        # Find all Plugin subclasses in module
        plugin_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if it's a Plugin subclass (but not Plugin itself)
            if issubclass(obj, Plugin) and obj is not Plugin:
                # Skip abstract base classes
                if not inspect.isabstract(obj):
                    plugin_classes.append(obj)
                    logger.debug(f"Found plugin class: {obj.__name__} in {module_path}")

        return plugin_classes

    def load_plugin(
        self, plugin_class: Type[Plugin], config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Load a plugin class into the registry.

        Args:
            plugin_class: Plugin class to instantiate and load
            config: Plugin configuration

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Instantiate plugin
            plugin = plugin_class(config=config)

            # Register with registry
            return self.registry.register(plugin)

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_class.__name__}: {e}")
            return False

    def load_plugins_from_directory(
        self, plugin_dir: Path, config_file: Optional[Path] = None
    ) -> int:
        """Discover and load all plugins from a directory.

        Args:
            plugin_dir: Directory containing plugins
            config_file: Optional YAML config file with plugin configurations

        Returns:
            Number of plugins successfully loaded
        """
        # Load configurations if provided
        configs = {}
        if config_file and config_file.exists():
            with open(config_file, "r") as f:
                configs = yaml.safe_load(f) or {}

        # Discover plugins
        plugin_classes = self.discover_plugins(plugin_dir)

        # Load each plugin
        loaded_count = 0
        for plugin_class in plugin_classes:
            plugin_name = plugin_class.__name__
            plugin_config = configs.get(plugin_name, {})

            if self.load_plugin(plugin_class, plugin_config):
                loaded_count += 1

        logger.info(
            f"Loaded {loaded_count}/{len(plugin_classes)} plugins from {plugin_dir}"
        )
        return loaded_count

    def reload_plugin(self, plugin_name: str) -> bool:
        """Hot-reload a plugin.

        Unregisters the plugin, reloads its module, and re-registers it.

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            True if reload successful, False otherwise
        """
        # Get current plugin
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin:
            logger.error(f"Plugin {plugin_name} not found in registry")
            return False

        try:
            # Get module path
            module = inspect.getmodule(plugin.__class__)
            if not module:
                logger.error(f"Could not find module for plugin {plugin_name}")
                return False

            module_path = module.__file__
            if not module_path:
                logger.error(f"Could not find module path for plugin {plugin_name}")
                return False

            # Save current config
            current_config = plugin.config

            # Unregister plugin
            self.registry.unregister(plugin_name)

            # Reload module
            importlib.reload(module)

            # Reload plugins from module
            plugin_classes = self._load_module_plugins(Path(module_path))

            # Find and re-register the plugin
            for plugin_class in plugin_classes:
                if plugin_class.__name__ == plugin.__class__.__name__:
                    if self.load_plugin(plugin_class, current_config):
                        logger.info(f"Successfully reloaded plugin: {plugin_name}")
                        return True

            logger.error(f"Could not find plugin class after reload: {plugin_name}")
            return False

        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return False

    def unload_all(self) -> None:
        """Unload all plugins from the registry."""
        self.registry.clear()
        logger.info("Unloaded all plugins")


def create_plugin_loader(registry: Optional[PluginRegistry] = None) -> PluginLoader:
    """Create a new plugin loader instance.

    Args:
        registry: Plugin registry to use (default: global registry)

    Returns:
        PluginLoader instance
    """
    return PluginLoader(registry=registry)
