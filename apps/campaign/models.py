"""Campaign models."""

from django.db import models


class Difficulty(models.TextChoices):
    """Campaign difficulty levels."""

    EASY = "easy", "Easy"
    NORMAL = "normal", "Normal"
    HARD = "hard", "Hard"
    HELL = "hell", "Hell"


class CampaignLevel(models.Model):
    """Represents a campaign stage."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
    order = models.PositiveIntegerField(unique=True)
    gold_reward = models.PositiveIntegerField(default=200)
    gems_reward = models.PositiveIntegerField(default=10)
    exp_reward = models.PositiveIntegerField(default=50)
    required_power = models.PositiveIntegerField(default=500)
    is_boss_level = models.BooleanField(default=False)
    enemy_team_data = models.JSONField(
        default=list,
        blank=True,
        help_text="List of enemy god configurations for this level",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        boss_tag = " [BOSS]" if self.is_boss_level else ""
        return f"Level {self.order}: {self.name}{boss_tag}"


class CampaignBattle(models.Model):
    """Records a player's battle in the campaign."""

    player = models.ForeignKey(
        "core.PlayerProfile", on_delete=models.CASCADE, related_name="battles"
    )
    level = models.ForeignKey(
        CampaignLevel, on_delete=models.CASCADE, related_name="battles"
    )
    team = models.ForeignKey(
        "teams.Team", on_delete=models.SET_NULL, null=True, related_name="battles"
    )
    won = models.BooleanField()
    turns = models.PositiveIntegerField(default=1)
    gold_earned = models.PositiveIntegerField(default=0)
    gems_earned = models.PositiveIntegerField(default=0)
    exp_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        result = "Victory" if self.won else "Defeat"
        return f"{self.level} - {result}"


class FactionLadder(models.Model):
    """Permanent faction-restricted challenge ladder."""

    pantheon = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#4a9eff")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def pantheon_label(self) -> str:
        from apps.gods.models import Pantheon

        if self.pantheon in Pantheon.values:
            return Pantheon(self.pantheon).label
        return self.pantheon


class FactionStage(models.Model):
    """A floor in a faction ladder."""

    ladder = models.ForeignKey(
        FactionLadder, on_delete=models.CASCADE, related_name="stages"
    )
    floor = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    required_power = models.PositiveIntegerField(default=500)
    is_boss = models.BooleanField(default=False)

    class Meta:
        ordering = ["ladder", "floor"]
        unique_together = ["ladder", "floor"]

    def __str__(self) -> str:
        return f"Floor {self.floor}: {self.name}"


class FactionProgress(models.Model):
    """Tracks player progress in a faction ladder."""

    player = models.ForeignKey(
        "core.PlayerProfile", on_delete=models.CASCADE, related_name="faction_progress"
    )
    ladder = models.ForeignKey(
        FactionLadder, on_delete=models.CASCADE, related_name="progress"
    )
    highest_floor = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["player", "ladder"]
        ordering = ["-highest_floor"]

    def __str__(self) -> str:
        return f"{self.player.user.username} - {self.ladder.name} (Floor {self.highest_floor})"
