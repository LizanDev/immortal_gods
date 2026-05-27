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

    def recalculate_rank_score(self) -> None:
        """Recalculate rank score based on campaign and faction progress."""
        campaign_score = self.campaign_progress * 100
        faction_score = sum(
            fp.highest_floor * 50 for fp in self.faction_progress.all()
        )
        self.rank_score = campaign_score + faction_score
        self.save(update_fields=["rank_score", "updated_at"])


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
