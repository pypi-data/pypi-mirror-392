from sundae.plugins.base import PluginRegistry


def create_pluggable_view(base_view_class):
    """Dynamically create view class with plugin mixins"""
    mixins = PluginRegistry.get_view_mixins()
    bases = tuple(mixins) + (base_view_class,)
    return type('PluggableCRUDSundaeView', bases, {})