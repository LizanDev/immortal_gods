"""Core models."""

from django.conf import settings
from django.db import models


class PlayerProfile(models.Model):
    """Stores player resources and progression data."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    gems = models.PositiveIntegerField(default=1350)
    gold = models.PositiveIntegerField(default=5000)
    energy = models.PositiveIntegerField(default=120)
    max_energy = models.PositiveIntegerField(default=120)
    campaign_progress = models.PositiveIntegerField(default=1)
    rank_score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile({self.user.username})"

    def add_gems(self, amount: int) -> None:
        """Add gems to the player's balance."""
        if amount < 0:
            raise ValueError("Cannot add negative gems")
        self.gems += amount
        self.save(update_fields=["gems", "updated_at"])

    def spend_gems(self, amount: int) -> bool:
        """Spend gems if player has enough. Returns success status."""
        if self.user.is_superuser:
            return True
        if self.gems < amount:
            return False
        self.gems -= amount
        self.save(update_fields=["gems", "updated_at"])
        return True

    def spend_gold(self, amount: int) -> bool:
        """Spend gold if player has enough. Returns success status."""
        if self.user.is_superuser:
            return True
        if self.gold < amount:
            return False
        self.gold -= amount
        self.save(update_fields=["gold", "updated_at"])
        return True

    def spend_energy(self, amount: int) -> bool:
        """Spend energy if player has enough. Returns success status."""
        if self.user.is_superuser:
            return True
        if self.energy < amount:
            return False
        self.energy -= amount
        self.save(update_fields=["energy", "updated_at"])
        return True
        if self.gems < amount:
            return False
        self.gems -= amount
        self.save(update_fields=["gems", "updated_at"])
        return True

    def add_gold(self, amount: int) -> None:
        """Add gold to the player's balance."""
        if amount < 0:
            raise ValueError("Cannot add negative gold")
        self.gold += amount
        self.save(update_fields=["gold", "updated_at"])

    def spend_gold(self, amount: int) -> bool:
        """Spend gold if player has enough. Returns success status."""
        if self.user.is_superuser:
            return True
        if self.gold < amount:
            return False
        self.gold -= amount
        self.save(update_fields=["gold", "updated_at"])
        return True

    def spend_energy(self, amount: int) -> bool:
        """Spend energy if player has enough. Returns success status."""
        if self.user.is_superuser:
            return True
        if self.energy < amount:
            return False
        self.energy -= amount
        self.save(update_fields=["energy", "updated_at"])
        return True

    def restore_energy(self, amount: int) -> None:
        """Restore energy up to max."""
        self.energy = min(self.energy + amount, self.max_energy)
        self.save(update_fields=["energy", "updated_at"])

    def add_energy(self, amount: int) -> None:
        """Add energy up to max."""
        self.energy = min(self.energy + amount, self.max_energy)
        self.save(update_fields=["energy", "updated_at"])


class DailyMission(models.Model):
    """Daily missions that reset every 24 hours."""

    MISSION_TYPES = [
        ("daily_login", "Inicio de Sesión"),
        ("first_pull", "Primera Invocación"),
        ("gacha_pulls", "Invocaciones Múltiples"),
        ("win_battles", "Victorias en Batalla"),
        ("level_up_god", "Subir de Nivel"),
        ("ascend_god", "Ascender Dios"),
        ("equip_item", "Equipar Objeto"),
        ("win_campaign", "Completar Campaña"),
    ]

    mission_type = models.CharField(max_length=30, choices=MISSION_TYPES, unique=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    target = models.PositiveIntegerField(default=1)
    energy_reward = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.title} ({self.energy_reward} energía)"


class PlayerMission(models.Model):
    """Tracks player's daily mission progress."""

    player = models.ForeignKey(
        PlayerProfile, on_delete=models.CASCADE, related_name="missions"
    )
    mission = models.ForeignKey(DailyMission, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    claimed = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["player", "mission"]

    def __str__(self) -> str:
        return f"{self.player.user.username} - {self.mission.title}"

    @property
    def progress_percentage(self) -> float:
        """Return progress as percentage."""
        if self.mission.target == 0:
            return 100.0
        return min(100.0, (self.progress / self.mission.target) * 100)

    def add_progress(self, amount: int = 1) -> bool:
        """Add progress and return True if completed."""
        if self.completed:
            return False
        self.progress = min(self.progress + amount, self.mission.target)
        if self.progress >= self.mission.target:
            self.completed = True
        self.save(update_fields=["progress", "completed", "last_updated"])
        return self.completed

    def claim_reward(self) -> int:
        """Claim reward and return energy amount. Returns 0 if already claimed."""
        if self.claimed or not self.completed:
            return 0
        self.claimed = True
        self.save(update_fields=["claimed"])
        return self.mission.energy_reward

    def recalculate_rank_score(self) -> None:
        """Recalculate rank score based on campaign and faction progress."""
        try:
            campaign_score = self.campaign_progress * 100
            faction_score = sum(
                fp.highest_floor * 50 for fp in self.faction_progress.all()
            )
            self.rank_score = campaign_score + faction_score
            self.save(update_fields=["rank_score", "updated_at"])
        except Exception:
            pass  # Fail silently to avoid breaking battles


class ReferralCode(models.Model):
    """One-time use referral codes that grant gems."""

    code = models.CharField(max_length=12, unique=True)
    gems_reward = models.PositiveIntegerField(default=4000)
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="used_referrals",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.code

    @property
    def is_used(self) -> bool:
        return self.used_by is not None


def track_mission(player: "PlayerProfile", mission_type: str, amount: int = 1) -> None:
    """Track mission progress for a player. Called by other apps."""
    try:
        mission = DailyMission.objects.get(mission_type=mission_type, is_active=True)
        pm, _ = PlayerMission.objects.get_or_create(player=player, mission=mission)
        pm.add_progress(amount)
    except DailyMission.DoesNotExist:
        pass
