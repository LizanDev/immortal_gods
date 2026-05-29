"""Shared battle logic used by campaign and PvP."""

import random
from collections.abc import Sequence

from apps.teams.models import Team, TeamMember


def resolve_battle(
    team_power: int,
    enemy_power: int,
    turns: int = 1,
) -> tuple[bool, list[dict]]:
    """Resolve a battle between two teams and return (won, battle_log).

    battle_log contains step-by-step entries for replay.
    """
    log: list[dict] = []
    attacker_hp = team_power
    defender_hp = enemy_power
    turn_number = 0

    ratio = team_power / enemy_power if enemy_power > 0 else 1

    if ratio >= 1.0:
        won = True
    elif ratio >= 0.7:
        won = random.random() < (ratio - 0.5)
    else:
        won = False

    while attacker_hp > 0 and defender_hp > 0 and turn_number < 20:
        turn_number += 1
        atk_dmg = max(1, int(team_power * random.uniform(0.8, 1.2)))
        def_dmg = max(1, int(enemy_power * random.uniform(0.8, 1.2)))

        if won:
            defender_hp -= atk_dmg
        else:
            attacker_hp -= def_dmg

        log.append(
            {
                "turn": turn_number,
                "attacker_hp": max(0, attacker_hp),
                "defender_hp": max(0, defender_hp),
                "attacker_damage": atk_dmg,
                "defender_damage": def_dmg,
            }
        )

    if won:
        log.append({"result": "victory", "winner": "attacker"})
    else:
        log.append({"result": "defeat", "winner": "defender"})

    return won, log


def calculate_team_power(team: Team) -> int:
    """Calculate total team power including class and synergy multipliers."""
    members = team.members.select_related("god__god").all()
    base_power = 0
    for member in members:
        if member.god:
            base_power += member.god.total_attack + member.god.total_defense
    class_mult = team.get_class_advantage_multiplier()
    synergy_mult = team.get_synergy_multiplier()
    return int(base_power * class_mult * synergy_mult)


def calculate_team_power_raw(members: Sequence[TeamMember]) -> int:
    """Calculate power from a sequence of TeamMember objects."""
    class_mult = _calculate_class_mult_from_members(members)
    synergy_mult = _calculate_synergy_mult_from_members(members)
    base_power = 0
    for m in members:
        if m.god:
            base_power += m.god.total_attack + m.god.total_defense
    return int(base_power * class_mult * synergy_mult)


def calculate_elo_change(
    rating_a: int, rating_b: int, won_by_a: bool
) -> tuple[int, int]:
    """Calculate ELO rating changes for both players. Returns (delta_a, delta_b)."""
    expected_a = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    expected_b = 1.0 - expected_a
    score_a = 1.0 if won_by_a else 0.0
    score_b = 0.0 if won_by_a else 1.0
    k = 32
    delta_a = int(k * (score_a - expected_a))
    delta_b = int(k * (score_b - expected_b))
    return delta_a, delta_b


def make_snapshot(team: Team) -> dict:
    """Create a frozen snapshot of a team's gods and stats for PvP."""
    members = team.members.select_related("god__god").all()
    snapshot = []
    for member in members:
        if not member.god:
            continue
        pg = member.god
        god = pg.god
        tags = list(god.synergy_tags.values_list("tag", flat=True))
        snapshot.append(
            {
                "id": pg.id,
                "name": god.name,
                "rarity": god.rarity,
                "role": god.role,
                "level": pg.level,
                "quality_tier": pg.quality_tier,
                "attack": pg.total_attack,
                "defense": pg.total_defense,
                "hp": pg.total_hp,
                "speed": pg.total_speed,
                "image_url": god.image_url,
                "tags": tags,
            }
        )
    return {
        "gods": snapshot,
        "power": calculate_team_power(team),
        "synergy_mult": team.get_synergy_multiplier(),
    }


def _calculate_class_mult_from_members(members: Sequence[TeamMember]) -> float:
    """Calculate class advantage multiplier from a list of members."""
    from apps.gods.models import CLASS_ADVANTAGE_BONUS, CLASS_ADVANTAGES

    if not members:
        return 1.0
    role_counts: dict[str, int] = {}
    for m in members:
        if m.god and m.god.god:
            role = m.god.god.role
            role_counts[role] = role_counts.get(role, 0) + 1
    bonus = 0.0
    for role, count in role_counts.items():
        countered_role = CLASS_ADVANTAGES.get(role)
        if countered_role and countered_role in role_counts:
            bonus += count * CLASS_ADVANTAGE_BONUS
    return 1.0 + min(bonus, 0.5)


def _calculate_synergy_mult_from_members(members: Sequence[TeamMember]) -> float:
    """Calculate synergy multiplier from a list of members."""
    from collections import defaultdict

    from apps.gods.models import SYNERGY_BONUSES, GodSynergyTag

    god_ids = [m.god.god_id for m in members if m.god]
    if not god_ids:
        return 1.0
    tag_counts: dict[str, int] = defaultdict(int)
    for tag in GodSynergyTag.objects.filter(god_id__in=god_ids).values_list(
        "tag", flat=True
    ):
        tag_counts[tag] += 1
    active = {t: c for t, c in tag_counts.items() if c >= 2}
    if not active:
        return 1.0
    max_bonus = 0.0
    thresholds = sorted(SYNERGY_BONUSES.keys(), reverse=True)
    for count in active.values():
        for threshold in thresholds:
            if count >= threshold:
                max_bonus = max(max_bonus, SYNERGY_BONUSES[threshold]["stat_bonus_pct"])
                break
    return 1.0 + max_bonus
