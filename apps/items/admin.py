"""Items admin configuration."""

from django.contrib import admin

from .models import Item, PlayerItem


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin interface for Item model."""

    list_display = ("name", "item_type", "max_level")
    list_filter = ("item_type",)
    search_fields = ("name",)


@admin.register(PlayerItem)
class PlayerItemAdmin(admin.ModelAdmin):
    """Admin interface for PlayerItem model."""

    list_display = ("player", "item", "level", "equipped_to")
    list_filter = ("level",)
