"""PvP admin."""

from django.contrib import admin

from .models import PvPBattle, PvPProfile


@admin.register(PvPProfile)
class PvPProfileAdmin(admin.ModelAdmin):
    """Admin for PvP profiles."""

    list_display = [
        "player",
        "rating",
        "rank",
        "battles_played",
        "battles_won",
        "defense_team",
    ]
    list_filter = ["rank"]
    search_fields = ["player__user__username"]
    readonly_fields = ["highest_rating", "battles_played", "battles_won"]


@admin.register(PvPBattle)
class PvPBattleAdmin(admin.ModelAdmin):
    """Admin for PvP battles."""

    list_display = [
        "attacker",
        "defender",
        "winner",
        "attacker_rating_change",
        "defender_rating_change",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["attacker__user__username", "defender__user__username"]
    readonly_fields = [
        "attacker_snapshot",
        "defender_snapshot",
        "battle_log",
        "created_at",
    ]
