# sundae/plugins/discovery.py
import importlib
import logging
from django.apps import apps
from django.conf import settings
from sundae.plugins.registry import PluginRegistry

logger = logging.getLogger(__name__)

class PluginLoader:
    @classmethod
    def autodiscover(cls):
        """
        Auto-discover plugins in three ways:
        1. From SUNDAE_PLUGINS setting
        2. From installed apps with sundae_plugin.py
        3. From entry points (for pip-installed plugins)
        """
        # Method 1: Load from settings
        cls._load_from_settings()

        # Method 2: Auto-discover from installed apps
        cls._discover_from_apps()

        # Method 3: Load from setuptools entry points
        cls._load_from_entry_points()

        # Initialize all registered plugins
        PluginRegistry.initialize_all()

    @classmethod
    def _load_from_settings(cls):
        """Load plugins explicitly defined in settings"""
        plugin_config = getattr(settings, 'SUNDAE_PLUGINS', {})
        enabled_plugins = plugin_config.get('enabled', [])

        for plugin_name in enabled_plugins:
            try:
                if '.' in plugin_name:
                    # Full module path provided
                    module = importlib.import_module(plugin_name)
                else:
                    # Try common patterns
                    for pattern in [f'{plugin_name}.sundae_plugin',
                                    f'sundae_{plugin_name}',
                                    plugin_name]:
                        try:
                            module = importlib.import_module(pattern)
                            break
                        except ImportError:
                            continue

                cls._register_plugin_from_module(module, plugin_name)

            except ImportError as e:
                logger.warning(f"Could not load plugin {plugin_name}: {e}")

    @classmethod
    def _discover_from_apps(cls):
        """Auto-discover plugins from Django apps"""
        for app_config in apps.get_app_configs():
            # Skip if explicitly disabled
            if cls._is_plugin_disabled(app_config.name):
                continue

            try:
                # Look for sundae_plugin.py in the app
                module = importlib.import_module(f'{app_config.name}.sundae_plugin')
                cls._register_plugin_from_module(module, app_config.name)
                logger.info(f"Discovered Sundae plugin in {app_config.name}")

            except ImportError:
                # No sundae_plugin.py found, that's okay
                pass

    @classmethod
    def _load_from_entry_points(cls):
        """Load plugins installed via pip using setuptools entry points"""
        try:
            from importlib.metadata import entry_points

            # Look for plugins registered under 'sundae.plugins' entry point
            discovered = entry_points(group='sundae.plugins')

            for entry_point in discovered:
                if cls._is_plugin_disabled(entry_point.name):
                    continue

                try:
                    plugin_class = entry_point.load()
                    plugin = plugin_class()
                    PluginRegistry.register(entry_point.name, plugin)
                    logger.info(f"Loaded plugin from entry point: {entry_point.name}")

                except Exception as e:
                    logger.error(f"Failed to load entry point {entry_point.name}: {e}")

        except ImportError:
            # importlib.metadata not available (Python < 3.8)
            pass

    @classmethod
    def _register_plugin_from_module(cls, module, plugin_name):
        """Register a plugin from a Python module"""
        # Look for a SundaePlugin class
        if hasattr(module, 'SundaePlugin'):
            plugin_class = module.SundaePlugin
            plugin = plugin_class()
            PluginRegistry.register(plugin_name, plugin)

        # Also look for a register() function (Django admin style)
        elif hasattr(module, 'register'):
            module.register(PluginRegistry)

    @classmethod
    def _is_plugin_disabled(cls, plugin_name):
        """Check if a plugin is explicitly disabled in settings"""
        plugin_config = getattr(settings, 'SUNDAE_PLUGINS', {})
        disabled = plugin_config.get('disabled', [])
        return plugin_name in disabled