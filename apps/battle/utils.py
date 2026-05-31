"""Shared battle logic used by campaign and PvP."""

import random
from collections.abc import Sequence

from apps.gods.models import ULTRA_BUFF_COLOSSUS, ULTRA_BUFF_FIRST_STRIKE
from apps.teams.models import Team, TeamMember


def resolve_battle(
    team_power: int,
    enemy_power: int,
    turns: int = 1,
    has_ultra_buff: bool = False,
) -> tuple[bool, list[dict]]:
    """Resolve a battle between two teams and return (won, battle_log).

    If has_ultra_buff is True, the attacker deals bonus first-strike damage.
    """
    log: list[dict] = []
    attacker_hp = team_power
    defender_hp = enemy_power
    initial_attacker_hp = team_power
    initial_defender_hp = enemy_power
    turn_number = 0

    ratio = team_power / enemy_power if enemy_power > 0 else 1
    if has_ultra_buff:
        ratio += ULTRA_BUFF_COLOSSUS

    if ratio >= 1.0:
        won = True
    elif ratio >= 0.7:
        won = random.random() < (ratio - 0.5)
    else:
        won = False

    first_strike = has_ultra_buff
    while attacker_hp > 0 and defender_hp > 0 and turn_number < 20:
        turn_number += 1
        dmg_mult = 1.0
        is_first_strike = False
        if first_strike:
            dmg_mult += ULTRA_BUFF_FIRST_STRIKE
            first_strike = False
            is_first_strike = True

        atk_roll = random.uniform(0.8, 1.2)
        def_roll = random.uniform(0.8, 1.2)
        atk_dmg = max(1, int(team_power * atk_roll * dmg_mult))
        def_dmg = max(1, int(enemy_power * def_roll))

        is_critical = atk_roll > 1.1 if won else def_roll > 1.0
        atk_quality = (
            "Crítico" if atk_roll > 1.1
            else "Fuerte" if atk_roll > 0.95
            else "Normal"
        )
        def_quality = (
            "Crítico" if def_roll > 1.1
            else "Fuerte" if def_roll > 0.95
            else "Normal"
        )

        if won:
            defender_hp -= atk_dmg
        else:
            attacker_hp -= def_dmg

        defender_hp_clamped = max(0, defender_hp)
        attacker_hp_clamped = max(0, attacker_hp)
        def_pct = (
            (defender_hp_clamped / initial_defender_hp) * 100
            if initial_defender_hp > 0 else 0
        )
        atk_pct = (
            (attacker_hp_clamped / initial_attacker_hp) * 100
            if initial_attacker_hp > 0 else 0
        )

        narrative = _build_turn_narrative(
            turn_number, atk_dmg, def_dmg, atk_pct, def_pct,
            atk_quality, def_quality, is_first_strike, is_critical, won,
        )

        log.append(
            {
                "turn": turn_number,
                "attacker_hp": attacker_hp_clamped,
                "defender_hp": defender_hp_clamped,
                "attacker_hp_pct": round(atk_pct, 1),
                "defender_hp_pct": round(def_pct, 1),
                "attacker_damage": atk_dmg,
                "defender_damage": def_dmg,
                "first_strike": is_first_strike,
                "is_critical": is_critical,
                "atk_quality": atk_quality,
                "def_quality": def_quality,
                "narrative": narrative,
            }
        )

    if won:
        log.append({"result": "victory", "winner": "attacker"})
    else:
        log.append({"result": "defeat", "winner": "defender"})

    return won, log


def _build_turn_narrative(
    turn: int,
    atk_dmg: int,
    def_dmg: int,
    atk_hp_pct: float,
    def_hp_pct: float,
    atk_quality: str,
    def_quality: str,
    first_strike: bool,
    critical: bool,
    winning: bool,
) -> str:
    """Generate a short narrative description of a battle turn in Spanish."""
    parts: list[str] = []

    atk_verbs = {
        "Crítico": [
            "asesta un golpe devastador",
            "descarga todo su poder",
            "golpea con furia divina",
            "desata un ataque arrollador",
        ],
        "Fuerte": [
            "golpea con fuerza",
            "lanza un ataque potente",
            "ataca con determinación",
            "ejecuta un golpe contundente",
        ],
        "Normal": [
            "ataca",
            "lanza un ataque",
            "golpea",
            "arremete contra el enemigo",
        ],
    }
    def_verbs = {
        "Crítico": [
            "contraataca ferozmente",
            "responde con un golpe brutal",
            "devuelve el ataque con saña",
            "contragolpea con violencia",
        ],
        "Fuerte": [
            "responde con violencia",
            "contraataca con potencia",
            "lanza un contrataque fuerte",
            "se defiende y responde con fuerza",
        ],
        "Normal": [
            "contraataca",
            "responde al ataque",
            "devuelve el golpe",
            "contragolpea",
        ],
    }
    first_strike_lines = [
        "¡Tu equipo toma la iniciativa y golpea primero!",
        "¡Ventaja inicial! Tu equipo ataca antes que el enemigo.",
        "¡Tu equipo sorprende al enemigo con un ataque relámpago!",
        "¡Golpe preventivo! Tu equipo no da tregua.",
    ]
    atk_strong_lines = [
        "El enemigo está al borde del colapso.",
        "El enemigo apenas puede mantenerse en pie.",
        "El enemigo se tambalea, un golpe más y caerá.",
        "La derrota del enemigo es inminente.",
    ]
    atk_mid_lines = [
        "El enemigo resiste con dificultad.",
        "El enemigo sigue luchando, pero se nota debilitado.",
        "El enemigo retrocede ante la embestida.",
        "Las defensas enemigas empiezan a ceder.",
    ]
    atk_high_lines = [
        "El enemigo sigue en pie.",
        "El enemigo aguanta el ataque sin problemas.",
        "El enemigo se mantiene firme.",
        "El enemigo no parece inmutarse.",
    ]
    def_strong_lines = [
        "Tu equipo está al límite de sus fuerzas.",
        "Tu equipo apenas puede continuar.",
        "La derrota de tu equipo parece cercana.",
        "Tu equipo lucha por mantenerse consciente.",
    ]
    def_mid_lines = [
        "Tu equipo empieza a flaquear.",
        "Tu equipo comienza a sentir el cansancio.",
        "Tu equipo retrocede ante la presión enemiga.",
        "Las filas de tu equipo se resienten.",
    ]
    def_high_lines = [
        "Tu equipo aguanta el envite.",
        "Tu equipo resiste el ataque con firmeza.",
        "Tu equipo mantiene la formación.",
        "Tu equipo no se rinde.",
    ]
    crit_lines = [
        "⚡ ¡Golpe crítico!",
        "⚡ ¡Impacto devastador!",
        "⚡ ¡Golpe perfecto!",
        "⚡ ¡El ataque encuentra el punto débil!",
    ]
    def_crit_lines = [
        "⚡ ¡El enemigo asesta un crítico!",
        "⚡ ¡Golpe brutal del enemigo!",
        "⚡ ¡El enemigo aprovecha una apertura!",
    ]
    victory_lines = [
        "¡El enemigo ha sido derrotado!",
        "¡El enemigo cae ante el poder de tu equipo!",
        "¡Victoria! El enemigo yace en el suelo.",
        "¡El campo de batalla queda despejado!",
    ]
    defeat_lines = [
        "¡Tu equipo ha caído!",
        "Tu equipo ha sido derrotado...",
        "Tu equipo sucumbe ante el enemigo.",
        "No hay más fuerzas, tu equipo cae.",
    ]

    if first_strike:
        parts.append(random.choice(first_strike_lines))

    if winning:
        verb = random.choice(atk_verbs.get(atk_quality, atk_verbs["Normal"]))
        parts.append(f"Tu equipo {verb} causando {atk_dmg} pts de daño.")
        if def_hp_pct <= 0:
            parts.append(random.choice(victory_lines))
        elif def_hp_pct <= 25:
            parts.append(random.choice(atk_strong_lines))
        elif def_hp_pct <= 50:
            parts.append(random.choice(atk_mid_lines))
        else:
            parts.append(random.choice(atk_high_lines))

        if critical:
            parts.append(random.choice(crit_lines))
    else:
        verb = random.choice(def_verbs.get(def_quality, def_verbs["Normal"]))
        parts.append(f"El enemigo {verb} causando {def_dmg} pts de daño.")
        if atk_hp_pct <= 0:
            parts.append(random.choice(defeat_lines))
        elif atk_hp_pct <= 25:
            parts.append(random.choice(def_strong_lines))
        elif atk_hp_pct <= 50:
            parts.append(random.choice(def_mid_lines))
        else:
            parts.append(random.choice(def_high_lines))

        if critical:
            parts.append(random.choice(def_crit_lines))

    return " ".join(parts)


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
