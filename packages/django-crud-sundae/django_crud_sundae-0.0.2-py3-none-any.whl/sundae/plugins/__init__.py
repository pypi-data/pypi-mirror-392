"""
Django CRUD Sundae Plugin System

This package provides a plugin architecture for extending Django CRUD Sundae functionality.
"""

from sundae.plugins.base import BasePlugin
from sundae.plugins.registry import PluginRegistry
from sundae.plugins.mixins import PluginMixin
from sundae.plugins.discovery import PluginLoader

__all__ = [
    'BasePlugin',
    'PluginRegistry',
    'PluginMixin',
    'PluginLoader',
]
