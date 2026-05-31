"""Campaign views."""

import random
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.battle.utils import calculate_team_power, resolve_battle
from apps.campaign.models import (
    CampaignBattle,
    CampaignLevel,
    FactionLadder,
    FactionProgress,
    FactionStage,
)
from apps.core.models import track_mission
from apps.items.models import Item, PlayerItem

ITEM_DROP_CHANCE = {
    "easy": 0.05,
    "normal": 0.10,
    "hard": 0.15,
    "hell": 0.25,
}

ENEMY_POOL = [
    {"name": "Soldado Esqueleto", "role": "Tank", "base_atk": 95, "base_def": 145},
    {"name": "Arquero Fantasma", "role": "Archer", "base_atk": 130, "base_def": 85},
    {"name": "Mago Oscuro", "role": "Mage", "base_atk": 145, "base_def": 75},
    {"name": "Lobo de Sombra", "role": "Assassin", "base_atk": 155, "base_def": 65},
    {"name": "Gólem de Piedra", "role": "Tank", "base_atk": 85, "base_def": 170},
    {"name": "Harpía", "role": "Archer", "base_atk": 120, "base_def": 80},
    {"name": "Quimera", "role": "Mage", "base_atk": 140, "base_def": 95},
    {"name": "Minotauro", "role": "Tank", "base_atk": 110, "base_def": 155},
    {"name": "Súcubo", "role": "Assassin", "base_atk": 145, "base_def": 80},
    {"name": "Centauro", "role": "Archer", "base_atk": 135, "base_def": 95},
    {"name": "Gorgona", "role": "Support", "base_atk": 95, "base_def": 120},
    {"name": "Hidra", "role": "Mage", "base_atk": 155, "base_def": 105},
    {"name": "Cerbero", "role": "Tank", "base_atk": 120, "base_def": 165},
    {"name": "Pegaso Oscuro", "role": "Support", "base_atk": 105, "base_def": 110},
    {"name": "Dragón Menor", "role": "Mage", "base_atk": 165, "base_def": 100},
    {"name": "Titán", "role": "Tank", "base_atk": 130, "base_def": 185},
]

BOSS_POOL = [
    {"name": "Rey Momia", "role": "Tank", "base_atk": 160, "base_def": 220},
    {"name": "Sacerdote de Seth", "role": "Mage", "base_atk": 200, "base_def": 130},
    {"name": "Hefesto Enfurecido", "role": "Tank", "base_atk": 170, "base_def": 240},
    {"name": "Hades Renacido", "role": "Assassin", "base_atk": 210, "base_def": 140},
    {"name": "Thor de las Tormentas", "role": "Tank", "base_atk": 180, "base_def": 210},
    {"name": "Emperador de Jade", "role": "Mage", "base_atk": 230, "base_def": 150},
    {"name": "Dragón Celestial", "role": "Mage", "base_atk": 240, "base_def": 160},
    {"name": "Eclipse Viviente", "role": "Assassin", "base_atk": 260, "base_def": 170},
    {"name": "Vacío Absoluto", "role": "Mage", "base_atk": 280, "base_def": 190},
]

QUALITY_ROMAN = {"easy": "I", "normal": "II", "hard": "III", "hell": "IV"}
QUALITY_MULT = {"easy": 1.00, "normal": 1.15, "hard": 1.30, "hell": 1.45}
LEVEL_SCALING = {
    "easy": {"num_enemies": 3, "diff_pct": 0.70},
    "normal": {"num_enemies": 3, "diff_pct": 0.85},
    "hard": {"num_enemies": 4, "diff_pct": 1.00},
    "hell": {"num_enemies": 4, "diff_pct": 1.20},
}


def _build_enemy_team(level: CampaignLevel) -> list[dict]:
    """Build enemy team data for a level (fallback if not pre-seeded)."""
    config = LEVEL_SCALING.get(level.difficulty, LEVEL_SCALING["easy"])
    num = 5 if level.is_boss_level else config["num_enemies"]
    quality = QUALITY_MULT.get(level.difficulty, 1.0)
    diff_pct = config["diff_pct"]
    pool = BOSS_POOL if level.is_boss_level else ENEMY_POOL
    display_level = level.order * 2
    level_mult = 1.0 + (display_level * 0.1)

    enemies = []
    for i in range(num):
        tpl = pool[i % len(pool)]
        atk = int(tpl["base_atk"] * quality * level_mult * diff_pct)
        def_ = int(tpl["base_def"] * quality * level_mult * diff_pct)
        enemies.append(
            {
                "name": tpl["name"],
                "role": tpl["role"],
                "attack": atk,
                "defense": def_,
                "level": display_level,
                "quality_roman": QUALITY_ROMAN.get(level.difficulty, "I"),
            }
        )
    return enemies


@login_required
def campaign_list(request):
    """Show all campaign levels with progress."""
    profile = request.user.profile
    levels = CampaignLevel.objects.all()
    teams = profile.teams.prefetch_related("members__god").all()

    selected_team_id = request.session.get("campaign_team_id")
    selected_team = None
    team_power = 0

    for team in teams:
        power = sum(
            member.god.total_attack + member.god.total_defense
            for member in team.members.all()
        )
        synergy_mult = team.get_synergy_multiplier()
        class_mult = team.get_class_advantage_multiplier()
        team.power = int(power * class_mult * synergy_mult)
        team.synergy_mult = synergy_mult
        if str(team.id) == str(selected_team_id):
            selected_team = team
            team_power = team.power

    if not selected_team and teams:
        selected_team = teams[0]
        team_power = selected_team.power
        request.session["campaign_team_id"] = selected_team.id

    for level in levels:
        if not level.enemy_team_data:
            level.enemy_team_data = _build_enemy_team(level)

    return render(
        request,
        "campaign/list.html",
        {
            "profile": profile,
            "levels": levels,
            "teams": teams,
            "selected_team": selected_team,
            "team_power": team_power,
            "max_visible": profile.campaign_progress + 1,
        },
    )


@login_required
def campaign_detail(request, level_id):
    """Show campaign level detail with teams, rewards, and battle history."""
    profile = request.user.profile
    level = get_object_or_404(CampaignLevel, pk=level_id)

    if level.order > profile.campaign_progress and not request.user.is_superuser:
        return render(
            request,
            "campaign/locked.html",
            {"level": level, "profile": profile},
        )

    team_id = request.session.get("campaign_team_id")
    team = profile.teams.filter(id=team_id).first()
    if not team:
        team = profile.teams.first()

    latest_battle = CampaignBattle.objects.filter(player=profile, level=level).first()

    next_level = CampaignLevel.objects.filter(order=level.order + 1).first()

    if not level.enemy_team_data:
        level.enemy_team_data = _build_enemy_team(level)

    return render(
        request,
        "campaign/detail.html",
        {
            "level": level,
            "profile": profile,
            "team": team,
            "latest_battle": latest_battle,
            "next_level": next_level,
        },
    )


@login_required
def campaign_battle(request, level_id):
    """Execute a battle for a campaign level (POST only)."""
    if request.method != "POST":
        return redirect("campaign:detail", level_id=level_id)

    try:
        profile = request.user.profile
        level = get_object_or_404(CampaignLevel, pk=level_id)

        if level.order > profile.campaign_progress and not request.user.is_superuser:
            return render(
                request,
                "campaign/locked.html",
                {"level": level, "profile": profile},
            )

        recent_battle = CampaignBattle.objects.filter(
            player=profile,
            level=level,
            created_at__gte=timezone.now() - timedelta(seconds=3),
        ).first()
        if recent_battle:
            return redirect("campaign:battle_result", level_id=level_id)

        team_id = request.session.get("campaign_team_id")
        team = profile.teams.filter(id=team_id).first()
        if not team or team.god_count() == 0:
            team = profile.teams.first()
            if team:
                request.session["campaign_team_id"] = team.id

        if not team or team.god_count() == 0:
            return redirect("teams:list")

        team_power = calculate_team_power(team)
        enemy_power = level.required_power if level.required_power > 0 else 1
        won, battle_log = resolve_battle(
            team_power=team_power,
            enemy_power=enemy_power,
            has_ultra_buff=team.has_ultra_buff(),
        )

        gold_var = random.randint(0, int(level.gold_reward * 0.2))
        gems_var = random.randint(0, max(1, int(level.gems_reward * 0.3)))

        gold_earned = level.gold_reward + gold_var
        gems_earned = level.gems_reward + gems_var

        dropped_item = None
        if won:
            profile.add_gold(gold_earned)
            profile.add_gems(gems_earned)
            track_mission(profile, "win_battles")
            track_mission(profile, "win_campaign")

            if level.order == profile.campaign_progress:
                profile.campaign_progress = level.order + 1
                profile.save(update_fields=["campaign_progress"])
                profile.recalculate_rank_score()

            drop_chance = ITEM_DROP_CHANCE.get(level.difficulty, 0.05)
            if random.random() < drop_chance:
                all_items = list(Item.objects.all())
                if all_items:
                    item = random.choice(all_items)
                    PlayerItem.objects.create(player=profile, item=item)
                    dropped_item = item

        actual_turns = len([e for e in battle_log if "turn" in e])
        CampaignBattle.objects.create(
            player=profile,
            level=level,
            team=team,
            won=won,
            turns=actual_turns,
            gold_earned=gold_earned if won else 0,
            gems_earned=gems_earned if won else 0,
            log_json=battle_log,
        )

        request.session["_battle_dropped_item_id"] = (
            dropped_item.id if dropped_item else None
        )

        return redirect("campaign:battle_result", level_id=level_id)
    except Exception as e:
        messages.error(request, f"Error en la batalla: {str(e)}")
        return redirect("campaign:list")


@login_required
def campaign_battle_result(request, level_id):
    """Show the most recent battle result for a level (GET only)."""
    profile = request.user.profile
    level = get_object_or_404(CampaignLevel, pk=level_id)

    battle = (
        CampaignBattle.objects.filter(player=profile, level=level)
        .select_related("team", "level")
        .first()
    )

    if not battle:
        return redirect("campaign:detail", level_id=level_id)

    if not battle.level.enemy_team_data:
        battle.level.enemy_team_data = _build_enemy_team(battle.level)

    dropped_item_id = request.session.pop("_battle_dropped_item_id", None)
    dropped_item = None
    if dropped_item_id:
        dropped_item = Item.objects.filter(id=dropped_item_id).first()

    next_level = None
    if battle.won:
        next_level = CampaignLevel.objects.filter(order=level.order + 1).first()

    return render(
        request,
        "campaign/result.html",
        {
            "battle": battle,
            "won": battle.won,
            "profile": profile,
            "dropped_item": dropped_item,
            "next_level": next_level,
        },
    )


@login_required
def select_team(request, team_id):
    """Set the active team for campaign battles."""
    team = request.user.profile.teams.filter(id=team_id).first()
    if team:
        request.session["campaign_team_id"] = team.id
    return redirect("campaign:list")


@login_required
def faction_ladders(request):
    """Show all faction ladders."""
    ladders = FactionLadder.objects.all()
    ladder_data = []
    for ladder in ladders:
        prog, _ = FactionProgress.objects.get_or_create(
            player=request.user.profile, ladder=ladder
        )
        ladder_data.append({"ladder": ladder, "progress": prog})
    return render(
        request,
        "campaign/faction_ladders.html",
        {"ladder_data": ladder_data},
    )


@login_required
def faction_ladder_detail(request, ladder_id):
    """Show a faction ladder with floors."""
    ladder = get_object_or_404(FactionLadder, pk=ladder_id)
    stages = ladder.stages.all().order_by("floor")
    progress, _ = FactionProgress.objects.get_or_create(
        player=request.user.profile, ladder=ladder
    )

    team_id = request.session.get("campaign_team_id")
    team = request.user.profile.teams.filter(id=team_id).first()
    if not team:
        team = request.user.profile.teams.first()

    faction_gods = []
    team_power = 0
    if team:
        for member in team.members.all():
            if member.god.god.pantheon == ladder.pantheon:
                faction_gods.append(member.god)
                team_power += member.god.total_attack + member.god.total_defense

    next_floor = progress.highest_floor + 1

    return render(
        request,
        "campaign/faction_ladder_detail.html",
        {
            "ladder": ladder,
            "stages": stages,
            "progress": progress,
            "available_gods": faction_gods,
            "next_floor": next_floor,
            "team_power": team_power,
            "team": team,
        },
    )


@login_required
def faction_battle(request, stage_id):
    """Battle a faction ladder stage."""
    try:
        stage = get_object_or_404(FactionStage, pk=stage_id)
        ladder = stage.ladder
        profile = request.user.profile

        progress, _ = FactionProgress.objects.get_or_create(
            player=profile, ladder=ladder
        )

        if stage.floor > progress.highest_floor + 1:
            messages.error(request, "Completa los pisos anteriores primero.")
            return redirect("campaign:faction_ladder_detail", ladder_id=ladder.id)

        team_id = request.session.get("campaign_team_id")
        team = profile.teams.filter(id=team_id).first()
        if not team:
            team = profile.teams.first()

        if not team or team.god_count() == 0:
            messages.error(request, "Crea un equipo primero.")
            return redirect("teams:list")

        faction_gods = []
        for member in team.members.select_related("god__god").all():
            if member.god and member.god.god.pantheon == ladder.pantheon:
                faction_gods.append(member.god)

        if not faction_gods:
            messages.error(
                request,
                f"Tu equipo no tiene dioses {ladder.pantheon_label}.",
            )
            return redirect("campaign:faction_ladder_detail", ladder_id=ladder.id)

        team_power = sum(god.total_attack + god.total_defense for god in faction_gods)
        synergy_multiplier = team.get_synergy_multiplier()
        team_power = int(team_power * synergy_multiplier)

        power_ratio = (
            team_power / stage.required_power if stage.required_power > 0 else 1
        )

        if power_ratio >= 1.0:
            won = True
        elif power_ratio >= 0.7:
            won = random.random() < (power_ratio - 0.5)
        else:
            won = False

        if won and stage.floor > progress.highest_floor:
            progress.highest_floor = stage.floor
            progress.save(update_fields=["highest_floor"])
            profile.recalculate_rank_score()

        next_stage = None
        if won:
            next_stage = FactionStage.objects.filter(
                ladder=ladder, floor=stage.floor + 1
            ).first()

        return render(
            request,
            "campaign/faction_battle_result.html",
            {
                "ladder": ladder,
                "stage": stage,
                "won": won,
                "progress": progress,
                "next_stage": next_stage,
            },
        )
    except Exception as e:
        messages.error(request, f"Error en la batalla: {str(e)}")
        return redirect("campaign:faction_ladders")
