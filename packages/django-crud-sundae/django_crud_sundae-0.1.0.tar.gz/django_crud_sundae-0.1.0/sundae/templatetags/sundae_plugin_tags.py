"""
Template tags for Django CRUD Sundae plugin system.
"""
from django import template
from django.utils.safestring import mark_safe
from sundae.plugins.registry import PluginRegistry

register = template.Library()


@register.simple_tag(takes_context=True)
def plugin_hook(context, hook_name, *args, **kwargs):
    """
    Execute a plugin hook in a template.

    Usage:
        {% plugin_hook "before_content" %}
        {% plugin_hook "add_to_form" form=form %}

    Args:
        context: Template context
        hook_name: Name of the hook to execute
        *args, **kwargs: Additional arguments for the hook

    Returns:
        Concatenated HTML output from all hook callbacks
    """
    # Add context to kwargs
    kwargs['context'] = context
    kwargs['request'] = context.get('request')
    kwargs['view'] = context.get('view')
    kwargs['user'] = context.get('user')

    # Execute hook and collect results
    results = PluginRegistry.execute_hook(f'template_{hook_name}', *args, **kwargs)

    # Concatenate all string results
    output = []
    for result in results:
        if result:
            output.append(str(result))

    return mark_safe('\n'.join(output))


@register.simple_tag
def plugin_static_css():
    """
    Include CSS files from all plugins.

    Usage:
        {% plugin_static_css %}

    Returns:
        HTML link tags for all plugin CSS files
    """
    css_files = PluginRegistry.execute_hook('get_css_files')

    output = []
    for file_list in css_files:
        if isinstance(file_list, (list, tuple)):
            for css_file in file_list:
                output.append(f'<link rel="stylesheet" href="{css_file}">')
        elif file_list:
            output.append(f'<link rel="stylesheet" href="{file_list}">')

    return mark_safe('\n'.join(output))


@register.simple_tag
def plugin_static_js():
    """
    Include JavaScript files from all plugins.

    Usage:
        {% plugin_static_js %}

    Returns:
        HTML script tags for all plugin JS files
    """
    js_files = PluginRegistry.execute_hook('get_js_files')

    output = []
    for file_list in js_files:
        if isinstance(file_list, (list, tuple)):
            for js_file in file_list:
                output.append(f'<script src="{js_file}"></script>')
        elif file_list:
            output.append(f'<script src="{file_list}"></script>')

    return mark_safe('\n'.join(output))


@register.filter
def plugin_field_renderer(field, field_name):
    """
    Apply plugin field renderer to a form field.

    Usage:
        {{ form.my_field|plugin_field_renderer:"my_field" }}

    Args:
        field: Form field to render
        field_name: Name of the field

    Returns:
        Custom rendered field or default field rendering
    """
    renderer = PluginRegistry.get_field_renderer(field_name)

    if renderer:
        try:
            return mark_safe(renderer(field))
        except Exception as e:
            # Fall back to default rendering on error
            import logging
            logging.error(f"Error in field renderer for {field_name}: {e}")

    return field


@register.simple_tag(takes_context=True)
def plugin_context_processor(context, processor_name):
    """
    Execute a plugin context processor.

    Usage:
        {% plugin_context_processor "my_processor" as my_data %}

    Args:
        context: Template context
        processor_name: Name of the processor to run

    Returns:
        Processed data from plugin
    """
    results = PluginRegistry.execute_hook(
        f'context_processor_{processor_name}',
        context=context
    )

    # Return first non-None result
    for result in results:
        if result is not None:
            return result

    return None


@register.inclusion_tag('sundae/plugin/widget.html', takes_context=True)
def plugin_widget(context, widget_name, **kwargs):
    """
    Render a plugin-provided widget.

    Usage:
        {% plugin_widget "my_widget" param1="value1" %}

    Args:
        context: Template context
        widget_name: Name of the widget to render
        **kwargs: Additional parameters for the widget

    Returns:
        Rendered widget content
    """
    widget_data = PluginRegistry.execute_hook(
        f'render_widget_{widget_name}',
        context=context,
        **kwargs
    )

    return {
        'widget_name': widget_name,
        'widget_data': widget_data,
        'kwargs': kwargs,
    }


@register.simple_tag
def plugin_enabled(plugin_name):
    """
    Check if a plugin is enabled.

    Usage:
        {% plugin_enabled "my_plugin" as is_enabled %}
        {% if is_enabled %}...{% endif %}

    Args:
        plugin_name: Name of the plugin to check

    Returns:
        True if plugin is enabled, False otherwise
    """
    plugin = PluginRegistry.get_plugin(plugin_name)
    return plugin is not None and plugin.is_enabled()


@register.simple_tag
def plugin_version(plugin_name):
    """
    Get version of a plugin.

    Usage:
        {% plugin_version "my_plugin" %}

    Args:
        plugin_name: Name of the plugin

    Returns:
        Version string or empty string if plugin not found
    """
    plugin = PluginRegistry.get_plugin(plugin_name)
    return plugin.version if plugin else ''


@register.simple_tag
def plugin_list():
    """
    Get list of all enabled plugins.

    Usage:
        {% plugin_list as plugins %}
        {% for plugin in plugins %}...{% endfor %}

    Returns:
        List of plugin instances
    """
    return list(PluginRegistry.get_all_plugins().values())