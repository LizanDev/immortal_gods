"""PvP models."""

from django.db import models

PVP_RANKS = [
    ("bronze", "Bronce"),
    ("silver", "Plata"),
    ("gold", "Oro"),
    ("platinum", "Platino"),
    ("diamond", "Diamante"),
    ("mythic", "Mítico"),
]

PVP_RANK_THRESHOLDS: list[tuple[int, str]] = [
    (0, "bronze"),
    (1100, "silver"),
    (1300, "gold"),
    (1500, "platinum"),
    (1800, "diamond"),
    (2200, "mythic"),
]


def rating_to_rank(rating: int) -> str:
    """Convert ELO rating to rank label."""
    rank = "bronze"
    for threshold, label in PVP_RANK_THRESHOLDS:
        if rating >= threshold:
            rank = label
    return rank


RANK_ORDER = {r[0]: i for i, r in enumerate(PVP_RANKS)}


class PvPProfile(models.Model):
    """Per-player PvP stats and queue status."""

    player = models.OneToOneField(
        "core.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="pvp",
    )
    rating = models.IntegerField(default=1000)
    highest_rating = models.IntegerField(default=1000)
    battles_played = models.PositiveIntegerField(default=0)
    battles_won = models.PositiveIntegerField(default=0)
    rank = models.CharField(max_length=20, choices=PVP_RANKS, default="bronze")
    in_queue = models.BooleanField(default=False)
    queued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Perfil PvP"
        verbose_name_plural = "Perfiles PvP"

    def __str__(self) -> str:
        return f"PvP({self.player.user.username}) #{self.rating}"

    @property
    def battles_lost(self) -> int:
        return self.battles_played - self.battles_won

    @property
    def win_rate(self) -> float:
        if self.battles_played == 0:
            return 0.0
        return round(self.battles_won / self.battles_played * 100, 1)

    def update_rank(self) -> None:
        """Re-calculate rank label from current rating."""
        self.rank = rating_to_rank(self.rating)
        if self.rating > self.highest_rating:
            self.highest_rating = self.rating

    def record_battle(self, won: bool, rating_change: int) -> None:
        """Record a battle result and update stats."""
        self.battles_played += 1
        if won:
            self.battles_won += 1
        self.rating += rating_change
        self.update_rank()
        self.in_queue = False
        self.queued_at = None
        self.save(
            update_fields=[
                "rating",
                "highest_rating",
                "battles_played",
                "battles_won",
                "rank",
                "in_queue",
                "queued_at",
            ]
        )


BOT_NAMES = [
    "Ares",
    "Loki",
    "Set",
    "Susanoo",
    "Kukulkan",
    "Morrigan",
    "Hela",
    "Typhon",
]


class PvPBattle(models.Model):
    """Record of a PvP battle between two players."""

    attacker = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="pvp_attacks",
    )
    defender = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pvp_defenses",
    )
    is_bot = models.BooleanField(default=False)
    bot_name = models.CharField(max_length=50, blank=True, default="")
    bot_rating = models.IntegerField(default=1000)
    attacker_team = models.ForeignKey(
        "teams.Team", null=True, on_delete=models.SET_NULL, related_name="+"
    )
    defender_team = models.ForeignKey(
        "teams.Team", null=True, on_delete=models.SET_NULL, related_name="+"
    )
    attacker_snapshot = models.JSONField(default=dict)
    defender_snapshot = models.JSONField(default=dict)
    winner = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.SET_NULL,
        null=True,
        related_name="pvp_wins",
    )
    attacker_rating_change = models.IntegerField(default=0)
    defender_rating_change = models.IntegerField(default=0)
    battle_log = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Batalla PvP"
        verbose_name_plural = "Batallas PvP"

    def __str__(self) -> str:
        if self.is_bot:
            return (
                f"{self.attacker.user.username} vs {self.bot_name} (Bot)"
                f" ({self.created_at.strftime('%Y-%m-%d')})"
            )
        if self.defender:
            return (
                f"{self.attacker.user.username} vs {self.defender.user.username}"
                f" ({self.created_at.strftime('%Y-%m-%d')})"
            )
        return f"Battle #{self.pk}"

    @property
    def defender_display(self) -> str:
        """Return display name for the defender (human or bot)."""
        if self.is_bot:
            return f"🤖 {self.bot_name}"
        if self.defender:
            return self.defender.user.username
        return "Desconocido"
