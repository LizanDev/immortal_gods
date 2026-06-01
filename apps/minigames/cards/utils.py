"""Card game utilities — god-to-card conversion."""

from apps.gods.models import God, PlayerGod
from apps.minigames.card_utils import god_to_card


def god_to_player_card(pg: PlayerGod) -> dict:
    """Convert a PlayerGod to a card dict with rarity values and bonuses.

    Args:
        pg: PlayerGod instance with related god loaded.

    Returns:
        Card dict with name, image_url, and values.
    """
    return god_to_card(pg.god, pg.card_bonus)


def god_to_ai_card(god: God) -> dict:
    """Convert a God to a card dict with rarity values.

    Args:
        god: God instance.

    Returns:
        Card dict with name, image_url, and values.
    """
    return god_to_card(god)
