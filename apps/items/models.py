"""Items models."""

from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import get_language

if TYPE_CHECKING:
    from apps.gods.models import PlayerGod


class ItemType(models.TextChoices):
    """Types of equipable items."""

    WEAPON = "weapon", "Arma"
    ARMOR = "armor", "Armadura"
    AMULET = "amulet", "Amuleto"


UPGRADE_COSTS = {
    1: 100,
    2: 200,
    3: 350,
    4: 500,
    5: 750,
    6: 1000,
    7: 1500,
    8: 2000,
    9: 3000,
}


class Item(models.Model):
    """Represents an equipable item template."""

    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True)
    description_en = models.TextField(blank=True, default="")
    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    attack_bonus = models.IntegerField(default=0)
    defense_bonus = models.IntegerField(default=0)
    hp_bonus = models.IntegerField(default=0)
    speed_bonus = models.IntegerField(default=0)
    max_level = models.PositiveIntegerField(default=10)
    craft_cost = models.PositiveIntegerField(default=40)
    belongs_to_god = models.CharField(max_length=100, blank=True, default="")
    passive_name = models.CharField(max_length=100, blank=True, default="")
    passive_desc = models.TextField(blank=True, default="")
    passive_atk = models.IntegerField(default=0)
    passive_def = models.IntegerField(default=0)
    passive_hp = models.IntegerField(default=0)
    passive_spd = models.IntegerField(default=0)
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.get_item_type_display()})"

    @property
    def display_name(self) -> str:
        """Return item name in the active language."""
        lang = get_language()
        if lang and lang.startswith("en") and self.name_en:
            return self.name_en
        return self.name

    @property
    def display_description(self) -> str:
        """Return item description in the active language."""
        lang = get_language()
        if lang and lang.startswith("en") and self.description_en:
            return self.description_en
        return self.description

    def get_upgrade_cost(self, current_level: int) -> int:
        """Get gold cost to upgrade from current level."""
        if current_level >= self.max_level:
            return 0
        return UPGRADE_COSTS.get(current_level, current_level * 500)

    def has_passive_for(self, god_name: str) -> bool:
        """Check if this item has a passive for the given god."""
        return self.belongs_to_god == god_name and bool(self.passive_name)


class PlayerItem(models.Model):
    """Represents a player's instance of an item with level."""

    player = models.ForeignKey(
        "core.PlayerProfile", on_delete=models.CASCADE, related_name="items"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="player_instances"
    )
    level = models.PositiveIntegerField(default=1)
    equipped_to = models.ForeignKey(
        "gods.PlayerGod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-level"]

    def __str__(self) -> str:
        status = "equipped" if self.equipped_to else "unequipped"
        return f"{self.item.name} +{self.level} ({status})"

    def equip(self, player_god: "PlayerGod") -> bool:
        """Equip this item to a player god. Returns success status."""
        if self.equipped_to == player_god:
            return True

        if self.equipped_to:
            self.unequip()

        same_type_equipped = self.player.items.filter(
            item__item_type=self.item.item_type,
            equipped_to=player_god,
        ).exists()

        if same_type_equipped:
            return False

        self.equipped_to = player_god
        self.save(update_fields=["equipped_to"])
        return True

    def unequip(self) -> None:
        """Unequip this item from its current god."""
        self.equipped_to = None
        self.save(update_fields=["equipped_to"])

    def upgrade(self, gold_cost: int) -> bool:
        """Upgrade item level if player can afford it."""
        if self.level >= self.item.max_level:
            return False

        self.level += 1
        self.save(update_fields=["level"])
        self.player.spend_gold(gold_cost)
        return True
