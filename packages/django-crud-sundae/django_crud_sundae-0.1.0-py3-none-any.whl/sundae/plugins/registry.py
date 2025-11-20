# sundae/plugins/registry.py
from collections import defaultdict, OrderedDict
from typing import Dict, List, Any, Type, Optional
import logging

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Central registry for all plugin functionality"""

    _plugins: Dict[str, 'BasePlugin'] = OrderedDict()
    _hooks: Dict[str, List[tuple]] = defaultdict(list)
    _widget_mappings: Dict[str, Type] = {}
    _view_mixins: List[Type] = []
    _field_renderers: Dict[str, callable] = {}
    _template_overrides: Dict[str, List[str]] = defaultdict(list)
    _initialized = False

    @classmethod
    def register(cls, plugin_name: str, plugin_instance: 'BasePlugin'):
        """
        Register a plugin instance

        Args:
            plugin_name: Unique identifier for the plugin
            plugin_instance: Instance of a plugin class
        """
        if plugin_name in cls._plugins:
            logger.warning(f"Plugin {plugin_name} already registered, overwriting")

        cls._plugins[plugin_name] = plugin_instance
        plugin_instance.name = plugin_name

        # Let plugin register its components
        plugin_instance.register(cls)

        logger.info(f"Registered plugin: {plugin_name} v{plugin_instance.version}")

    @classmethod
    def register_hook(cls, hook_name: str, callback: callable, priority: int = 50):
        """
        Register a callback for a specific hook point

        Args:
            hook_name: Name of the hook (e.g., 'pre_save', 'post_list')
            callback: Function to call at this hook point
            priority: Lower numbers execute first (default 50)
        """
        cls._hooks[hook_name].append((priority, callback))
        cls._hooks[hook_name].sort(key=lambda x: x[0])

    @classmethod
    def register_widget(cls, field_type: str, widget_class: Type):
        """Register a custom widget for a field type"""
        cls._widget_mappings[field_type] = widget_class

    @classmethod
    def register_view_mixin(cls, mixin_class: Type):
        """Register a mixin to be dynamically added to CRUDSundaeView"""
        if mixin_class not in cls._view_mixins:
            cls._view_mixins.append(mixin_class)

    @classmethod
    def register_template_override(cls, template_pattern: str, template_path: str):
        """Register template overrides"""
        cls._template_overrides[template_pattern].append(template_path)

    @classmethod
    def initialize_all(cls):
        """Initialize all registered plugins"""
        if cls._initialized:
            return

        for plugin_name, plugin in cls._plugins.items():
            try:
                plugin.ready()
                logger.info(f"Initialized plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to initialize plugin {plugin_name}: {e}")

        cls._initialized = True

    @classmethod
    def get_hooks(cls, hook_name: str) -> List[callable]:
        """Get all callbacks for a hook, ordered by priority"""
        return [callback for priority, callback in cls._hooks.get(hook_name, [])]

    @classmethod
    def execute_hook(cls, hook_name: str, *args, **kwargs):
        """Execute all callbacks for a hook"""
        results = []
        for callback in cls.get_hooks(hook_name):
            try:
                result = callback(*args, **kwargs)
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error executing hook {hook_name}: {e}")
        return results

    @classmethod
    def get_plugin(cls, plugin_name: str) -> Optional['BasePlugin']:
        """Get a specific plugin by name"""
        return cls._plugins.get(plugin_name)

    @classmethod
    def get_all_plugins(cls) -> Dict[str, 'BasePlugin']:
        """Get all registered plugins"""
        return cls._plugins.copy()

    @classmethod
    def get_field_renderer(cls, field_name: str) -> Optional[callable]:
        """Get a custom field renderer for a specific field"""
        return cls._field_renderers.get(field_name)

    @classmethod
    def register_field_renderer(cls, field_name: str, renderer: callable):
        """Register a custom field renderer"""
        cls._field_renderers[field_name] = renderer

    @classmethod
    def get_view_mixins(cls) -> List[Type]:
        """Get all registered view mixins"""
        return cls._view_mixins.copy()

    @classmethod
    def get_widget_for_field(cls, field_type: str) -> Optional[Type]:
        """Get a custom widget for a field type"""
        return cls._widget_mappings.get(field_type)

    @classmethod
    def get_template_overrides(cls, template_pattern: str) -> List[str]:
        """Get template overrides for a specific pattern"""
        return cls._template_overrides.get(template_pattern, [])