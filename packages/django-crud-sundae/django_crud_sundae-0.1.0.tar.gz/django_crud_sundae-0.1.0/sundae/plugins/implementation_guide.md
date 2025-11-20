# Django CRUD Sundae Plugin System - Implementation Guide

## 📦 Complete File List

This document lists all the files that need to be added or updated to implement the plugin system in Django CRUD Sundae.

---

## 🗂️ Directory Structure

```
sundae/
├── __init__.py (existing)
├── apps.py (UPDATE)
├── views.py (UPDATE - major changes)
├── plugins/  (NEW DIRECTORY)
│   ├── __init__.py
│   ├── base.py
│   ├── registry.py
│   ├── discovery.py
│   └── mixins.py
├── templates/
│   └── sundae/
│       ├── base.html (UPDATE)
│       └── plugin/  (NEW DIRECTORY)
│           └── widget.html
└── templatetags/
    ├── __init__.py (existing)
    ├── sundae_tags.py (existing)
    └── sundae_plugin_tags.py (NEW)
```

---

## 📄 Files to Add/Update

### 1. **apps.py** (UPDATE)
- **Location:** `sundae/apps.py`
- **Purpose:** Initialize plugin system on Django startup
- **File:** `apps.py`

### 2. **Plugin System Core** (NEW)
All files in `sundae/plugins/`:

- **`__init__.py`** - Package initialization
- **`base.py`** - BasePlugin class
- **`registry.py`** - Plugin registry
- **`discovery.py`** - Plugin discovery and loading
- **`mixins.py`** - PluginMixin for views

### 3. **views.py** (MAJOR UPDATE)
- **Location:** `sundae/views.py`
- **Purpose:** Add plugin hooks throughout view lifecycle
- **Changes:** 
  - Import plugin components
  - Inherit from PluginMixin
  - Add hooks to all major methods
- **Note:** This is a large update - recommend backing up original first

### 4. **Templates** (UPDATE/NEW)
- **`templates/sundae/base.html`** - Add plugin hook tags
- **`templates/sundae/plugin/widget.html`** - New widget template

### 5. **Template Tags** (NEW)
- **`templatetags/sundae_plugin_tags.py`** - Plugin template tags

---

## 📝 Implementation Steps

### Step 1: Create Plugin Directory
```bash
mkdir -p sundae/plugins
```

### Step 2: Copy Plugin Core Files
Copy all files from `/plugins/` directory:
- `__init__.py`
- `base.py`
- `registry.py`
- `discovery.py`
- `mixins.py`

### Step 3: Update apps.py
Replace existing `sundae/apps.py` with the updated version.

### Step 4: Add Template Tags
Copy `sundae_plugin_tags.py` to `sundae/templatetags/`

### Step 5: Update base.html
Add plugin hooks to your base template:
```django
{% load sundae_plugin_tags %}
<!-- At various points in template: -->
{% plugin_hook "hook_name" %}
{% plugin_static_css %}
{% plugin_static_js %}
```

### Step 6: Update views.py
This is the most complex change. The updated views.py includes:
- Import of plugin components
- Inheritance from PluginMixin
- Hook execution throughout all methods

**Key changes to views.py:**
```python
# Add to imports
from sundae.plugins.registry import PluginRegistry
from sundae.plugins.mixins import PluginMixin

# Update class definition
class CRUDSundaeView(PluginMixin, View):
    # ... rest of class
    
    # Add attribute
    enable_plugins: bool = True
    skip_hooks: List[str] = []
```

### Step 7: Configure Settings
Add to your Django settings.py:
```python
SUNDAE_PLUGINS = {
    'enabled': [],  # List of enabled plugins
    'disabled': [],  # List of disabled plugins
    'config': {}  # Plugin-specific configuration
}
```

---

## 🧪 Testing the Implementation

### 1. Create a Test Plugin
Create `myapp/sundae_plugin.py`:
```python
from sundae.plugins import BasePlugin

class SundaePlugin(BasePlugin):
    name = "test_plugin"
    version = "1.0.0"
    
    def register(self, registry):
        registry.register_hook('pre_save', self.on_save)
        
    def on_save(self, view, form, **kwargs):
        print(f"Saving: {form.instance}")
```

### 2. Verify Plugin Discovery
```python
python manage.py shell
>>> from sundae.plugins.registry import PluginRegistry
>>> plugins = PluginRegistry.get_all_plugins()
>>> print(plugins)
```

### 3. Check Hook Execution
Monitor logs while performing CRUD operations to see hook execution.

---

## 📦 Example Plugins Included

### 1. DataTables Plugin
- **File:** `example_datatables_plugin.py`
- **Features:** Adds DataTables to list views

### 2. Advanced Widgets Plugin
- **File:** `example_widgets_plugin.py`
- **Features:** Date pickers, Select2, rich text editors

---

## ⚠️ Important Notes

1. **Backup First:** Always backup your original files before updating
2. **Test Thoroughly:** Test all CRUD operations after implementation
3. **Gradual Implementation:** Consider implementing in a test environment first
4. **Hook Documentation:** Document any custom hooks you add
5. **Plugin Isolation:** Ensure plugins can't break core functionality

---

## 🔄 Migration Path

If you have existing custom code in your CRUDSundaeView subclasses:

1. **Keep existing code:** Your current customizations will continue to work
2. **Gradual migration:** Move customizations to plugins over time
3. **Mix approaches:** Use both inheritance and plugins as needed

---

## 📚 Additional Resources

- **Plugin Development Guide:** See `PLUGIN_SYSTEM_README.md`
- **Example Plugins:** See `example_*.py` files
- **Hook Reference:** Complete list of hooks in documentation

---

## 🐛 Troubleshooting

### Plugin Not Loading
- Check `SUNDAE_PLUGINS` settings
- Verify `sundae_plugin.py` exists in app
- Check logs for loading errors

### Hooks Not Executing
- Ensure `enable_plugins = True` on view
- Check hook name spelling
- Verify plugin is registered

### Import Errors
- Ensure all plugin files are in correct location
- Check Python path configuration
- Verify Django app is in INSTALLED_APPS

---

## ✅ Validation Checklist

- [ ] Plugin directory created
- [ ] All plugin core files copied
- [ ] apps.py updated
- [ ] Template tags added
- [ ] base.html updated with hooks
- [ ] views.py updated with PluginMixin
- [ ] Settings configured
- [ ] Test plugin created
- [ ] Plugin discovery verified
- [ ] Hook execution tested
- [ ] All CRUD operations working

---

## 📞 Support

For questions or issues with the plugin system:
1. Check the comprehensive plugin documentation
2. Review example plugins for patterns
3. Enable debug logging for detailed information
4. Test with minimal plugin first

---

This implementation guide provides all the necessary files and steps to add a robust plugin system to Django CRUD Sundae.