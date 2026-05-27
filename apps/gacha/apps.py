"""Gacha app configuration."""

from django.apps import AppConfig


class GachaConfig(AppConfig):
    """Configuration for the gacha app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.gacha"
    verbose_name = "Gacha"
