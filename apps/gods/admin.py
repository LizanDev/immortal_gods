"""Gods admin configuration."""

from django.contrib import admin

from .models import God, GodSynergyTag, PlayerGod


class GodSynergyTagInline(admin.TabularInline):
    """Inline admin for synergy tags."""

    model = GodSynergyTag
    extra = 2


@admin.register(God)
class GodAdmin(admin.ModelAdmin):
    """Admin interface for God model."""

    inlines = [GodSynergyTagInline]
    list_display = ("name", "pantheon", "role", "rarity")
    list_filter = ("pantheon", "role", "rarity")
    search_fields = ("name",)


@admin.register(GodSynergyTag)
class GodSynergyTagAdmin(admin.ModelAdmin):
    """Admin interface for GodSynergyTag."""

    list_display = ("god", "tag")
    list_filter = ("tag",)
    search_fields = ("god__name", "tag")


@admin.register(PlayerGod)
class PlayerGodAdmin(admin.ModelAdmin):
    """Admin interface for PlayerGod model."""

    list_display = ("god", "player", "level")
    list_filter = ("level",)
