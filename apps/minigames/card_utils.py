"""Shared card game utilities — percentile-based stat ranking across all Gods."""

from functools import lru_cache

from django.db.models import Max, Min

from apps.gods.models import God


def _percentile_value(raw: int, stat_min: int, stat_max: int) -> int:
    """Map a raw stat to 1-9 based on its percentile position across all gods."""
    if stat_max == stat_min:
        return 5
    return max(1, min(9, 1 + round((raw - stat_min) / (stat_max - stat_min) * 8)))


@lru_cache(maxsize=1)
def _get_stat_ranges() -> dict:
    """Compute global min/max for each base stat across all Gods (cached)."""
    stats = God.objects.aggregate(
        atk_min=Min("base_attack"),
        atk_max=Max("base_attack"),
        def_min=Min("base_defense"),
        def_max=Max("base_defense"),
        spd_min=Min("base_speed"),
        spd_max=Max("base_speed"),
        hp_min=Min("base_hp"),
        hp_max=Max("base_hp"),
    )
    return stats


def compute_card_values(
    base_attack: int, base_defense: int,
    base_speed: int, base_hp: int,
    ranges: dict | None = None,
) -> dict:
    """Compute top/right/bottom/left card values using percentile ranking."""
    if ranges is None:
        ranges = _get_stat_ranges()
    return {
        "top": _percentile_value(base_attack, ranges["atk_min"], ranges["atk_max"]),
        "right": _percentile_value(base_defense, ranges["def_min"], ranges["def_max"]),
        "bottom": _percentile_value(base_speed, ranges["spd_min"], ranges["spd_max"]),
        "left": _percentile_value(base_hp, ranges["hp_min"], ranges["hp_max"]),
    }


def god_to_card(god, ranges: dict | None = None) -> dict:
    """Convert a God (or object with .name, .image_url, .base_*) to a card dict."""
    if ranges is None:
        ranges = _get_stat_ranges()
    return {
        "name": god.name,
        "image_url": god.image_url,
        "values": compute_card_values(
            god.base_attack, god.base_defense, god.base_speed, god.base_hp, ranges
        ),
    }
