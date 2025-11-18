"""Django app configuration for Djvurn Rbac."""

from django.apps import AppConfig


class RbacConfig(AppConfig):
    """Configuration for Djvurn Rbac."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "djvurn_rbac"
    verbose_name = "Djvurn Rbac"

    def ready(self):
        """Import signals when app is ready."""
        # Import signals here to ensure they're registered
        # from . import signals  # noqa
        pass
