"""Shared card game utilities — rarity-based value generation."""

import random

RARITY_SUMS = {
    "common": 18,
    "rare": 22,
    "epic": 26,
    "legendary": 30,
    "mythic": 34,
}

DIRECTIONS = ("top", "right", "bottom", "left")


def _generate_rarity_values(total_sum: int) -> list[int]:
    """Generate 4 random values (1-9) summing to total_sum."""
    for _ in range(200):
        cuts = sorted(random.sample(range(1, total_sum), 3))
        values = [
            cuts[0],
            cuts[1] - cuts[0],
            cuts[2] - cuts[1],
            total_sum - cuts[2],
        ]
        if all(1 <= v <= 9 for v in values):
            random.shuffle(values)
            return values
    base = total_sum // 4
    rem = total_sum % 4
    values = [base, base, base, base]
    for i in range(rem):
        values[i] += 1
    random.shuffle(values)
    return values


def _apply_bonus(val: int, bonuses: dict[str, int] | None, direction: str) -> int:
    """Add bonus points to a card value, capped at 10."""
    if not bonuses:
        return val
    return min(10, val + bonuses.get(direction, 0))


def rarity_card_values(rarity: str, bonuses: dict | None = None) -> dict:
    """Generate top/right/bottom/left card values based on rarity + bonuses."""
    total = RARITY_SUMS.get(rarity, 18)
    pool = _generate_rarity_values(total)
    values = {}
    for i, d in enumerate(DIRECTIONS):
        v = _apply_bonus(pool[i], bonuses, d)
        values[d] = v
    return values


def god_to_card(god, bonuses: dict | None = None) -> dict:
    """Convert a God to a card dict using rarity-based values."""
    return {
        "name": god.name,
        "image_url": god.image_url,
        "values": rarity_card_values(god.rarity, bonuses),
    }
