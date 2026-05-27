"""Gods admin configuration."""

from django.contrib import admin

from .models import God, PlayerGod


@admin.register(God)
class GodAdmin(admin.ModelAdmin):
    """Admin interface for God model."""

    list_display = ("name", "pantheon", "role", "rarity")
    list_filter = ("pantheon", "role", "rarity")
    search_fields = ("name",)


@admin.register(PlayerGod)
class PlayerGodAdmin(admin.ModelAdmin):
    """Admin interface for PlayerGod model."""

    list_display = ("god", "player", "level")
    list_filter = ("level",)
