"""Gacha models."""

import random

from django.db import models

from apps.gods.models import ESSENCE_REWARDS, RARITY_PULL_WEIGHTS, God, PlayerGod
from apps.items.models import Item

SINGLE_PULL_COST = 150
MULTI_PULL_COST = 1350
PITY_LIMIT = 50


class Banner(models.TextChoices):
    """Available gacha banners."""

    STANDARD = "standard", "Standard"


class PullType(models.TextChoices):
    """Types of pulls."""

    SINGLE = "single", "Single Pull"
    MULTI = "multi", "Multi Pull (x10)"


class PullHistory(models.Model):
    """Records each gacha pull made by a player."""

    player = models.ForeignKey(
        "core.PlayerProfile", on_delete=models.CASCADE, related_name="pulls"
    )
    banner = models.CharField(max_length=20, choices=Banner.choices)
    pull_type = models.CharField(max_length=10, choices=PullType.choices)
    god = models.ForeignKey(God, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        target = self.god or self.item
        return f"{self.get_pull_type_display()} - {target}"


def roll_rarity() -> str:
    """Roll for rarity based on weighted probabilities."""
    rarities = list(RARITY_PULL_WEIGHTS.keys())
    weights = list(RARITY_PULL_WEIGHTS.values())
    return random.choices(rarities, weights=weights, k=1)[0]


def get_pulls_since_last_high(player) -> int:
    """Count consecutive pulls since last legendary or mythic."""
    last_high = (
        PullHistory.objects.filter(player=player, god__rarity__in=["legendary", "mythic"])
        .order_by("-created_at")
        .first()
    )
    if last_high:
        return PullHistory.objects.filter(player=player, created_at__gt=last_high.created_at).count()
    return PullHistory.objects.filter(player=player).count()


def perform_pull(player, banner: str, pull_type: str) -> list[dict]:
    """Execute a gacha pull and return results."""
    cost = MULTI_PULL_COST if pull_type == PullType.MULTI else SINGLE_PULL_COST
    pulls_count = 10 if pull_type == PullType.MULTI else 1

    if not player.spend_gems(cost):
        return []

    results = []
    pantheon_filter = {}

    if banner != Banner.STANDARD:
        pantheon_filter = {"pantheon": banner}

    for _ in range(pulls_count):
        pulls_since = get_pulls_since_last_high(player)

        if pulls_since >= PITY_LIMIT:
            rarity = random.choices(
                ["legendary", "mythic"], weights=[80, 20], k=1
            )[0]
        else:
            rarity = roll_rarity()

        gods = list(God.objects.filter(rarity=rarity, **pantheon_filter))

        if not gods:
            gods = list(God.objects.filter(rarity=rarity))

        if not gods:
            gods = list(God.objects.filter(**pantheon_filter))

        if not gods:
            gods = list(God.objects.all())

        if gods:
            god = random.choice(gods)
            player_god, created = PlayerGod.objects.get_or_create(
                player=player, god=god
            )

            if not created:
                essence_reward = ESSENCE_REWARDS.get(god.rarity, 1)
                player_god.add_essence(essence_reward)

            PullHistory.objects.create(
                player=player,
                banner=banner,
                pull_type=pull_type,
                god=god,
            )
            results.append(
                {
                    "type": "god",
                    "god": god,
                    "new": created,
                    "duplicate": not created,
                    "essence_reward": ESSENCE_REWARDS.get(god.rarity, 1)
                    if not created
                    else 0,
                }
            )

    return results
