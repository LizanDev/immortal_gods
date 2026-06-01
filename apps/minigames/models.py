"""Minigames models."""

from datetime import date

from django.db import models


class MemoryGameSession(models.Model):
    """Tracks a memory game session and its reward status."""

    player = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="memory_games",
    )
    pairs_total = models.PositiveIntegerField(default=8)
    moves = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    reward_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    played_date = models.DateField(default=date.today)

    class Meta:
        verbose_name = "Juego de Memoria"
        verbose_name_plural = "Juegos de Memoria"

    def __str__(self) -> str:
        status = "✓" if self.completed else "..."
        return f"Memoria({self.player.user.username}) {self.moves} movs {status}"

    @property
    def reward_gems(self) -> int:
        if not self.completed:
            return 0
        if self.moves <= 12:
            return 30
        if self.moves <= 16:
            return 20
        if self.moves <= 20:
            return 10
        return 5

    def claim_reward(self) -> int:
        if self.reward_claimed or not self.completed:
            return 0
        self.reward_claimed = True
        self.save(update_fields=["reward_claimed"])
        self.player.add_gems(self.reward_gems)
        return self.reward_gems


class CardGameSession(models.Model):
    """Tracks a card duel (Triple Triad-style) session."""

    player = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="card_games",
    )
    played_date = models.DateField(default=date.today)
    board_state = models.JSONField(default=list)
    player_hand = models.JSONField(default=list)
    ai_hand = models.JSONField(default=list)
    current_turn = models.CharField(max_length=10, default="player")
    moves = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    won = models.BooleanField(null=True)
    reward_claimed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Duelo de Cartas"
        verbose_name_plural = "Duelos de Cartas"

    def __str__(self) -> str:
        return f"Cartas({self.player.user.username}) movs={self.moves}"

    @property
    def reward_gems(self) -> int:
        if not self.completed:
            return 0
        return 10 if self.won else 3

    @property
    def reward_fragments(self) -> int:
        if not self.completed or not self.won:
            return 0
        base = 3
        try:
            win_streak = self.player.card_games.filter(
                completed=True, won=True
            ).count()
            if win_streak > 0 and win_streak % 5 == 0:
                return base + 6
        except Exception:
            pass
        return base

    def claim_reward(self) -> dict:
        if self.reward_claimed or not self.completed:
            return {"gems": 0, "fragments": 0}
        self.reward_claimed = True
        self.save(update_fields=["reward_claimed"])
        self.player.add_gems(self.reward_gems)

        fragment_amount = 0
        if self.won:
            fragment_amount = self.reward_fragments
            self.player.add_fragments(fragment_amount)

        return {
            "gems": self.reward_gems,
            "fragments": fragment_amount,
        }


class DailyWheelSpin(models.Model):
    """Tracks the daily wheel of fortune spin."""

    REWARD_TYPES = [
        ("gems", "Gemas"),
        ("gold", "Oro"),
        ("nothing", "Nada"),
    ]

    player = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="wheel_spins",
    )
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    reward_amount = models.PositiveIntegerField(default=0)
    spun_date = models.DateField(default=date.today)
    spun_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Giro de Rueda"
        verbose_name_plural = "Giros de Rueda"

    def __str__(self) -> str:
        if self.reward_type == "nothing":
            return f"Rueda({self.player.user.username}) — Nada"
        return (
            f"Rueda({self.player.user.username})"
            f" +{self.reward_amount} {self.reward_type}"
        )
