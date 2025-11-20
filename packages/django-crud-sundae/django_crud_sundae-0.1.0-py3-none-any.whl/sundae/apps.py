from django.apps import AppConfig


class SundaeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sundae"
    verbose_name = "Django CRUD Sundae"

    def ready(self):
        """Called when Django starts up"""
        from sundae.plugins.discovery import PluginLoader

        # Auto-discover and register all plugins
        PluginLoader.autodiscover()
