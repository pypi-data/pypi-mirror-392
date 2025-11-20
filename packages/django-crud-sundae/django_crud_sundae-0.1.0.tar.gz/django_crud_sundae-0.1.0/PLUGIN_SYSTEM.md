# Django CRUD Sundae Plugin System

## Overview

The Django CRUD Sundae plugin system allows you to extend and customize CRUD functionality without modifying the core library. Plugins can add custom widgets, modify templates, inject JavaScript/CSS, customize form rendering, and more.

## Features

- **Auto-discovery**: Plugins are automatically discovered from installed Django apps
- **Hook-based architecture**: Register callbacks for specific lifecycle events
- **Widget customization**: Add custom form widgets for specific field types
- **Template integration**: Inject content into templates via template tags
- **Configuration**: Per-plugin configuration via Django settings
- **Priority system**: Control execution order of multiple plugins

## Quick Start

### 1. Create a Plugin

Create a file named `sundae_plugin.py` in your Django app:

```python
from sundae.plugins import BasePlugin

class SundaePlugin(BasePlugin):
    """My custom plugin"""

    name = "my_plugin"
    version = "1.0.0"
    description = "My awesome plugin"
    author = "Your Name"

    def register(self, registry):
        """Register hooks and components"""
        # Register a hook callback
        registry.register_hook('pre_save', self.on_save, priority=10)

    def on_save(self, form, **kwargs):
        """Called before saving an object"""
        print(f"About to save: {form.instance}")

    def ready(self):
        """Called after all plugins are loaded"""
        print(f"{self.name} plugin ready!")
```

### 2. Configure Settings

Add plugin configuration to your `settings.py`:

```python
SUNDAE_PLUGINS = {
    'enabled': [
        # Explicitly enable plugins (optional - auto-discovery works by default)
    ],
    'disabled': [
        # Disable specific plugins
    ],
    'config': {
        # Plugin-specific configuration
        'my_plugin': {
            'option1': 'value1',
            'option2': True,
        }
    }
}
```

### 3. Use in Views

Plugins are automatically active for all `CRUDSundaeView` instances:

```python
from sundae.views import CRUDSundaeView
from .models import Article

class ArticleView(CRUDSundaeView):
    model = Article
    enable_plugins = True  # Default is True
```

## Plugin Discovery

Plugins are discovered in three ways:

1. **Auto-discovery**: Any Django app with a `sundae_plugin.py` file
2. **Settings**: Plugins listed in `SUNDAE_PLUGINS['enabled']`
3. **Entry points**: Pip-installable plugins using setuptools entry points

## Available Hooks

### View Lifecycle Hooks

- `pre_save` - Before saving an object (create or update)
- `post_save` - After saving an object
- `pre_create` - Before creating a new object
- `post_create` - After creating a new object
- `pre_update` - Before updating an object
- `post_update` - After updating an object
- `pre_delete` - Before deleting an object
- `post_delete` - After deleting an object

### Template Hooks

- `template_head` - Content to inject in `<head>`
- `template_body_start` - Content at start of `<body>`
- `template_body_end` - Content at end of `<body>`
- `template_before_content` - Before main content
- `template_after_content` - After main content

### Filter Hooks

- `filter_queryset` - Modify the queryset
- `filter_form_class` - Modify the form class
- `filter_form_widgets` - Customize form widgets
- `filter_list_context` - Modify list view context
- `get_template_names` - Override template resolution

### Asset Hooks

- `get_css_files` - Return list of CSS files to include
- `get_js_files` - Return list of JavaScript files to include

## Example Plugins

### Widget Enhancement Plugin

Located in `examples/articles/sundae_plugin_widgets.py`:

```python
from sundae.plugins import BasePlugin

class AdvancedWidgetsPlugin(BasePlugin):
    """Adds date pickers, Select2, and rich text editors"""

    name = "sundae_advanced_widgets"
    version = "1.0.0"

    def register(self, registry):
        registry.register_hook('filter_form_widgets', self.customize_widgets)
        registry.register_hook('get_css_files', self.get_css_files)
        registry.register_hook('get_js_files', self.get_js_files)
```

Features:
- Flatpickr date/time pickers
- Select2 for dropdowns
- Quill rich text editor

### DataTables Plugin

Located in `examples/articles/sundae_plugin_datatables.py`:

```python
from sundae.plugins import BasePlugin

class DataTablesPlugin(BasePlugin):
    """Adds DataTables to list views"""

    name = "sundae_datatables"
    version = "1.0.0"

    def register(self, registry):
        registry.register_hook('filter_list_context', self.add_datatables_config)
        registry.register_hook('get_css_files', self.get_css_files)
        registry.register_hook('get_js_files', self.get_js_files)
```

Features:
- Interactive tables with sorting, filtering, pagination
- Export to CSV, Excel, PDF
- Responsive design

## Template Tags

Use plugin template tags in your templates:

```django
{% load sundae_plugin_tags %}

<!DOCTYPE html>
<html>
<head>
    {% plugin_static_css %}
    {% plugin_hook "template_head" %}
</head>
<body>
    {% plugin_hook "template_body_start" %}

    <div class="content">
        {% plugin_hook "before_content" %}
        <!-- Your content here -->
        {% plugin_hook "after_content" %}
    </div>

    {% plugin_static_js %}
    {% plugin_hook "template_body_end" %}
</body>
</html>
```

## Plugin Methods

### BasePlugin Methods

```python
class MyPlugin(BasePlugin):
    def register(self, registry):
        """Register hooks, widgets, etc."""
        pass

    def ready(self):
        """Called after all plugins are loaded"""
        pass

    def is_enabled(self):
        """Check if plugin is enabled"""
        return True

    def get_config(self):
        """Get plugin configuration from settings"""
        return {}
```

### PluginRegistry Methods

```python
from sundae.plugins import PluginRegistry

# Register a hook
PluginRegistry.register_hook('hook_name', callback_function, priority=50)

# Register a widget
PluginRegistry.register_widget('DateField', MyDateWidget)

# Get all plugins
plugins = PluginRegistry.get_all_plugins()

# Execute a hook
results = PluginRegistry.execute_hook('hook_name', arg1, arg2, kwarg1=value)
```

## Configuration

### Plugin-Specific Configuration

Each plugin can access its configuration:

```python
class MyPlugin(BasePlugin):
    def register(self, registry):
        config = self.get_config()
        if config.get('enable_feature', True):
            registry.register_hook('hook_name', self.my_callback)
```

### Global Settings

```python
SUNDAE_PLUGINS = {
    'enabled': [
        'myapp.plugins.MyPlugin',  # Explicit plugin path
    ],
    'disabled': [
        'unwanted_plugin',  # Disable by name
    ],
    'config': {
        'my_plugin': {
            'enable_feature': True,
            'api_key': 'secret',
            'options': ['opt1', 'opt2'],
        }
    }
}
```

## Testing Plugins

Test plugin loading:

```python
python manage.py shell

>>> from sundae.plugins.registry import PluginRegistry
>>> plugins = PluginRegistry.get_all_plugins()
>>> for name, plugin in plugins.items():
...     print(f"{name}: {plugin.version}")
```

## Architecture

```
sundae/
├── plugins/
│   ├── __init__.py           # Package exports
│   ├── base.py               # BasePlugin class
│   ├── registry.py           # PluginRegistry
│   ├── discovery.py          # Plugin auto-discovery
│   ├── mixins.py             # PluginMixin for views
│   └── loader.py             # Plugin loading utilities
├── templatetags/
│   └── sundae_plugin_tags.py # Template tags
└── views.py                   # CRUDSundaeView with PluginMixin
```

## Best Practices

1. **Naming**: Use descriptive plugin names (e.g., `sundae_datatables`)
2. **Versioning**: Follow semantic versioning
3. **Configuration**: Make features configurable via settings
4. **Documentation**: Document hooks and configuration options
5. **Error Handling**: Gracefully handle errors in hook callbacks
6. **Priority**: Use priority to control execution order (lower = earlier)
7. **Dependencies**: Document any external dependencies (JS/CSS libraries)

## Troubleshooting

### Plugin Not Loading

1. Check plugin is in `sundae_plugin.py`
2. Verify app is in `INSTALLED_APPS`
3. Check not in `SUNDAE_PLUGINS['disabled']`
4. Look for errors in Django logs

### Hooks Not Executing

1. Ensure `enable_plugins = True` on view
2. Check hook name spelling
3. Verify plugin registered the hook
4. Check `skip_hooks` list on view

### Import Errors

1. Ensure plugin dependencies are installed
2. Check Python path
3. Verify imports in `sundae_plugin.py`

## Examples

See the `examples/articles/` directory for working examples:

- `sundae_plugin.py` - Main plugin registration
- `sundae_plugin_widgets.py` - Advanced widgets
- `sundae_plugin_datatables.py` - DataTables integration

## Contributing

When creating plugins for distribution:

1. Create a separate package
2. Use setuptools entry points for auto-discovery
3. Document configuration options
4. Include example usage
5. Test with multiple Django versions

## License

The plugin system is part of Django CRUD Sundae and uses the same MIT license.
