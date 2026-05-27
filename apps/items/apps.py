"""Items app configuration."""

from django.apps import AppConfig


class ItemsConfig(AppConfig):
    """Configuration for the items app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.items"
    verbose_name = "Items"
