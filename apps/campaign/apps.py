"""Campaign app configuration."""

from django.apps import AppConfig


class CampaignConfig(AppConfig):
    """Configuration for the campaign app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.campaign"
    verbose_name = "Campaign"
