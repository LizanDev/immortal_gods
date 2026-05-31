"""Minigames admin."""

from django.contrib import admin

from .models import CardGameSession, DailyWheelSpin, MemoryGameSession


@admin.register(MemoryGameSession)
class MemoryGameSessionAdmin(admin.ModelAdmin):
    """Admin for memory game sessions."""

    list_display = [
        "player",
        "moves",
        "completed",
        "reward_claimed",
        "reward_gems",
        "played_date",
    ]
    list_filter = ["completed", "played_date"]
    search_fields = ["player__user__username"]


@admin.register(DailyWheelSpin)
class DailyWheelSpinAdmin(admin.ModelAdmin):
    """Admin for wheel spins."""

    list_display = ["player", "reward_type", "reward_amount", "spun_date"]
    list_filter = ["reward_type", "spun_date"]
    search_fields = ["player__user__username"]


@admin.register(CardGameSession)
class CardGameSessionAdmin(admin.ModelAdmin):
    """Admin for card duel sessions."""

    list_display = [
        "player",
        "moves",
        "completed",
        "won",
        "reward_claimed",
        "played_date",
    ]
    list_filter = ["completed", "won", "played_date"]
    search_fields = ["player__user__username"]
