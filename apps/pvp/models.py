"""PvP models."""

from datetime import date

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
    """Per-player PvP stats and defense configuration."""

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
    defense_team = models.ForeignKey(
        "teams.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    BASE_ATTACKS = 5
    MAX_ATTACKS = 10
    daily_attacks_used = models.PositiveIntegerField(default=0)
    daily_attacks_date = models.DateField(null=True, blank=True)

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

    def _reset_daily_if_needed(self) -> None:
        """Reset daily counter if it's a new day."""
        today = date.today()
        if self.daily_attacks_date != today:
            self.daily_attacks_used = 0
            self.daily_attacks_date = today

    def _completed_missions_today(self) -> int:
        """Count missions completed in the current daily cycle."""
        return self.player.missions.filter(completed=True).count()

    @property
    def attacks_remaining(self) -> int:
        """Calculate remaining daily attacks (base + 1/complete mission, max 10)."""
        self._reset_daily_if_needed()
        max_bonus = self.MAX_ATTACKS - self.BASE_ATTACKS
        bonus = min(self._completed_missions_today(), max_bonus)
        total = min(self.BASE_ATTACKS + bonus, self.MAX_ATTACKS)
        return max(0, total - self.daily_attacks_used)

    @property
    def attacks_max(self) -> int:
        """Calculate max daily attacks for display."""
        self._reset_daily_if_needed()
        max_bonus = self.MAX_ATTACKS - self.BASE_ATTACKS
        bonus = min(self._completed_missions_today(), max_bonus)
        return min(self.BASE_ATTACKS + bonus, self.MAX_ATTACKS)

    def use_attack(self) -> bool:
        """Use one attack attempt. Returns False if none remaining."""
        self._reset_daily_if_needed()
        self.refresh_from_db(fields=["daily_attacks_used", "daily_attacks_date"])
        self._reset_daily_if_needed()
        if self.daily_attacks_used >= self.attacks_max:
            return False
        self.daily_attacks_used += 1
        self.save(update_fields=["daily_attacks_used", "daily_attacks_date"])
        return True

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
        self.save(
            update_fields=[
                "rating",
                "highest_rating",
                "battles_played",
                "battles_won",
                "rank",
            ]
        )


class PvPBattle(models.Model):
    """Record of a PvP battle between two players."""

    attacker = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="pvp_attacks",
    )
    defender = models.ForeignKey(
        "core.PlayerProfile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pvp_defenses",
    )
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
        if self.defender_id:
            assert self.defender is not None
            return (
                f"{self.attacker.user.username} vs {self.defender.user.username}"
                f" ({self.created_at.strftime('%Y-%m-%d')})"
            )
        return f"Battle #{self.pk}"

    @property
    def defender_display(self) -> str:
        """Return display name for the defender."""
        if self.defender_id:
            assert self.defender is not None
            return self.defender.user.username
        return "Desconocido"
