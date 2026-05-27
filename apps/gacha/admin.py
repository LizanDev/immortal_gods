"""Gacha admin configuration."""

from django.contrib import admin

from .models import PullHistory


@admin.register(PullHistory)
class PullHistoryAdmin(admin.ModelAdmin):
    """Admin interface for PullHistory model."""

    list_display = ("player", "banner", "pull_type", "god", "item", "created_at")
    list_filter = ("banner", "pull_type")
    date_hierarchy = "created_at"
