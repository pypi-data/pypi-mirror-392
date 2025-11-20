"""
Base plugin class for Django CRUD Sundae plugins.
"""
from typing import Optional
from abc import ABC


class BasePlugin(ABC):
    """Base class for all Sundae plugins"""

    name: Optional[str] = None
    version: str = "1.0.0"
    description: str = ""
    author: str = ""

    def register(self, registry: 'PluginRegistry'):
        """
        Called during plugin registration.
        Override this to register hooks, widgets, etc.

        Args:
            registry: The PluginRegistry instance
        """
        pass

    def ready(self):
        """
        Called after all plugins are registered.
        Override this for initialization that depends on other plugins.
        """
        pass

    def is_enabled(self):
        """
        Check if this plugin is enabled.

        Returns:
            bool: True if plugin is enabled, False otherwise
        """
        from django.conf import settings
        plugin_config = getattr(settings, 'SUNDAE_PLUGINS', {})
        disabled = plugin_config.get('disabled', [])
        return self.name not in disabled

    def get_config(self):
        """Get plugin configuration from settings"""
        from django.conf import settings
        plugin_config = getattr(settings, 'SUNDAE_PLUGINS', {})
        return plugin_config.get('config', {}).get(self.name, {})
