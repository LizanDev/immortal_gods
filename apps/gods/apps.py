"""Gods app configuration."""

from django.apps import AppConfig


class GodsConfig(AppConfig):
    """Configuration for the gods app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gods"
    verbose_name = "Gods"
