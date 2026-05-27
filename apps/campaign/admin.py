"""Campaign admin configuration."""

from django.contrib import admin

from .models import (
    CampaignBattle,
    CampaignLevel,
    FactionLadder,
    FactionProgress,
    FactionStage,
)


@admin.register(CampaignLevel)
class CampaignLevelAdmin(admin.ModelAdmin):
    """Admin interface for CampaignLevel model."""

    list_display = ("order", "name", "difficulty", "energy_cost", "is_boss_level")
    list_filter = ("difficulty", "is_boss_level")
    ordering = ("order",)


@admin.register(CampaignBattle)
class CampaignBattleAdmin(admin.ModelAdmin):
    """Admin interface for CampaignBattle model."""

    list_display = ("player", "level", "won", "gold_earned", "created_at")
    list_filter = ("won", "level__difficulty")
    date_hierarchy = "created_at"


class FactionStageInline(admin.TabularInline):
    """Inline for FactionStage within FactionLadder admin."""

    model = FactionStage
    extra = 1
    ordering = ("floor",)


@admin.register(FactionLadder)
class FactionLadderAdmin(admin.ModelAdmin):
    """Admin interface for FactionLadder model."""

    list_display = ("name", "pantheon", "pantheon_label")
    list_filter = ("pantheon",)
    search_fields = ("name", "pantheon")
    inlines = [FactionStageInline]


@admin.register(FactionProgress)
class FactionProgressAdmin(admin.ModelAdmin):
    """Admin interface for FactionProgress model."""

    list_display = ("player", "ladder", "highest_floor", "updated_at")
    list_filter = ("ladder",)
    search_fields = ("player__user__username",)
