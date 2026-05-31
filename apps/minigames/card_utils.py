"""Shared card game utilities — percentile-based stat ranking."""

from django.db.models import Max, Min, QuerySet

from apps.gods.models import God


def _percentile_value(raw: int, stat_min: int, stat_max: int) -> int:
    """Map a raw stat to 1-9 based on its percentile position."""
    if stat_max == stat_min:
        return 5
    return max(1, min(9, 1 + round((raw - stat_min) / (stat_max - stat_min) * 8)))


def _get_stat_ranges(queryset: QuerySet | None = None) -> dict:
    """Compute min/max for each base stat across the given queryset (default: all Gods)."""
    if queryset is None:
        queryset = God.objects.all()
    stats = queryset.aggregate(
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


DIRECTIONS = ("top", "right", "bottom", "left")


def _apply_bonus(val: int, bonuses: dict | None, direction: str) -> int:
    """Add bonus points to a card value, capped at 10."""
    if not bonuses:
        return val
    return min(10, val + bonuses.get(direction, 0))


def compute_card_values(
    base_attack: int,
    base_defense: int,
    base_speed: int,
    base_hp: int,
    ranges: dict | None = None,
    bonuses: dict | None = None,
    queryset: QuerySet | None = None,
) -> dict:
    """Compute top/right/bottom/left card values using percentile ranking + bonus."""
    if ranges is None:
        ranges = _get_stat_ranges(queryset)
    return {
        "top": _apply_bonus(
            _percentile_value(base_attack, ranges["atk_min"], ranges["atk_max"]),
            bonuses,
            "top",
        ),
        "right": _apply_bonus(
            _percentile_value(base_defense, ranges["def_min"], ranges["def_max"]),
            bonuses,
            "right",
        ),
        "bottom": _apply_bonus(
            _percentile_value(base_speed, ranges["spd_min"], ranges["spd_max"]),
            bonuses,
            "bottom",
        ),
        "left": _apply_bonus(
            _percentile_value(base_hp, ranges["hp_min"], ranges["hp_max"]),
            bonuses,
            "left",
        ),
    }


def god_to_card(
    god, ranges: dict | None = None, queryset: QuerySet | None = None
) -> dict:
    """Convert a God to a card dict using percentile ranking."""
    if ranges is None:
        ranges = _get_stat_ranges(queryset)
    return {
        "name": god.name,
        "image_url": god.image_url,
        "values": compute_card_values(
            god.base_attack,
            god.base_defense,
            god.base_speed,
            god.base_hp,
            ranges,
        ),
    }
