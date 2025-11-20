# sundae/plugins/mixins.py
from typing import Any, Dict, List, Optional
from sundae.plugins.registry import PluginRegistry

class PluginMixin:
    """Mixin that provides hook execution methods to views"""

    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Execute a plugin hook and return all results.

        Args:
            hook_name: Name of the hook to execute
            *args, **kwargs: Arguments to pass to hook callbacks

        Returns:
            List of results from all hook callbacks
        """
        if not getattr(self, 'enable_plugins', True):
            return []

        if hook_name in getattr(self, 'skip_hooks', []):
            return []

        # Add view context to kwargs
        kwargs['view'] = self
        kwargs['request'] = getattr(self, 'request', None)
        kwargs['model'] = getattr(self, 'model', None)

        return PluginRegistry.execute_hook(hook_name, *args, **kwargs)

    def filter_hook(self, hook_name: str, value: Any, *args, **kwargs) -> Any:
        """
        Execute a filter hook that modifies and returns a value.

        Each hook callback receives the current value and returns a modified version.

        Args:
            hook_name: Name of the hook to execute
            value: Initial value to filter
            *args, **kwargs: Additional arguments for callbacks

        Returns:
            Final filtered value
        """
        if not getattr(self, 'enable_plugins', True):
            return value

        if hook_name in getattr(self, 'skip_hooks', []):
            return value

        kwargs['view'] = self
        kwargs['request'] = getattr(self, 'request', None)

        for callback in PluginRegistry.get_hooks(hook_name):
            try:
                value = callback(value, *args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in filter hook {hook_name}: {e}")

        return value

    def hook_or_default(self, hook_name: str, default: Any, *args, **kwargs) -> Any:
        """
        Execute a hook and return first non-None result, or default if all return None.
        """
        results = self.execute_hook(hook_name, *args, **kwargs)
        for result in results:
            if result is not None:
                return result
        return default