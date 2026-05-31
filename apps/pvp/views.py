"""PvP views."""

import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.battle.utils import (
    calculate_elo_change,
    calculate_team_power,
    make_snapshot,
    resolve_battle,
)
from apps.core.models import track_mission

from .models import PvPBattle, PvPProfile


@login_required
def lobby(request):
    """Main PvP hub showing stats, defense team, and attack button."""
    profile = request.user.profile
    pvp, _ = PvPProfile.objects.get_or_create(player=profile)
    recent_battles = PvPBattle.objects.filter(
        Q(attacker=profile) | Q(defender=profile)
    ).select_related("attacker__user", "defender__user", "winner__user")[:5]
    teams = profile.teams.all()

    return render(
        request,
        "pvp/lobby.html",
        {
            "pvp": pvp,
            "profile": profile,
            "recent_battles": recent_battles,
            "teams": teams,
        },
    )


@login_required
def opponents(request):
    """Return JSON list of available opponents within MMR range."""
    profile = request.user.profile
    pvp, _ = PvPProfile.objects.get_or_create(player=profile)

    rating_min = max(0, pvp.rating - 200)
    rating_max = pvp.rating + 200

    qs = (
        PvPProfile.objects.filter(
            defense_team__isnull=False,
            rating__gte=rating_min,
            rating__lte=rating_max,
        )
        .exclude(player=profile)
        .select_related("player__user", "defense_team")
    )

    data = []
    for opp in qs:
        team = opp.defense_team
        data.append(
            {
                "id": opp.id,
                "username": opp.player.user.username,
                "rating": opp.rating,
                "rank": opp.get_rank_display(),
                "team_name": team.name if team else "",
                "team_power": calculate_team_power(team) if team else 0,
                "god_count": team.god_count() if team else 0,
            }
        )

    return JsonResponse({"opponents": data, "count": len(data)})


@login_required
def find_match(request):
    """Find an opponent and resolve a PvP battle.

    POST with opponent_id to target a specific player.
    POST without opponent_id picks a random opponent.
    """
    if request.method != "POST":
        return redirect("pvp:lobby")

    profile = request.user.profile
    pvp, _ = PvPProfile.objects.get_or_create(player=profile)

    attacker_team_id = request.POST.get("team_id")
    if attacker_team_id:
        attacker_team = profile.teams.filter(id=attacker_team_id).first()
    else:
        attacker_team = profile.teams.first()

    if not attacker_team or attacker_team.god_count() == 0:
        return JsonResponse({"status": "no_team"}, status=400)

    if not pvp.defense_team:
        return JsonResponse({"status": "no_defense"}, status=400)

    if pvp.attacks_remaining <= 0:
        return JsonResponse({"status": "no_attacks"}, status=400)

    rating_min = max(0, pvp.rating - 200)
    rating_max = pvp.rating + 200

    opponent_id = request.POST.get("opponent_id")
    if opponent_id:
        opponent = (
            PvPProfile.objects.filter(
                pk=opponent_id,
                defense_team__isnull=False,
                rating__gte=rating_min,
                rating__lte=rating_max,
            )
            .exclude(player=profile)
            .select_related("player", "defense_team")
            .first()
        )
        if not opponent:
            return JsonResponse({"status": "opponent_unavailable"}, status=410)
    else:
        opponents = list(
            PvPProfile.objects.filter(
                defense_team__isnull=False,
                rating__gte=rating_min,
                rating__lte=rating_max,
            )
            .exclude(player=profile)
            .select_related("player", "defense_team")
        )
        if not opponents:
            return JsonResponse({"status": "no_opponents"}, status=404)
        opponent = random.choice(opponents)

    if not pvp.use_attack():
        return JsonResponse({"status": "no_attacks"}, status=400)

    defender_profile = opponent.player
    defender_team = opponent.defense_team

    attacker_power = calculate_team_power(attacker_team)
    defender_power = calculate_team_power(defender_team) if defender_team else 0

    won, battle_log = resolve_battle(
        attacker_power, defender_power,
        has_ultra_buff=attacker_team.has_ultra_buff(),
    )
    attacker_delta, defender_delta = calculate_elo_change(
        pvp.rating, opponent.rating, won_by_a=won
    )

    battle = PvPBattle.objects.create(
        attacker=profile,
        defender=defender_profile,
        attacker_team=attacker_team,
        defender_team=defender_team,
        attacker_snapshot=make_snapshot(attacker_team),
        defender_snapshot=make_snapshot(defender_team) if defender_team else {},
        winner=profile if won else defender_profile,
        attacker_rating_change=attacker_delta,
        defender_rating_change=defender_delta,
        battle_log=battle_log,
    )

    pvp.record_battle(won=won, rating_change=attacker_delta)

    if won:
        track_mission(profile, "win_battles")

    opponent.record_battle(won=not won, rating_change=defender_delta)

    return JsonResponse(
        {
            "status": "match_found",
            "battle_id": battle.id,
        }
    )


@login_required
def set_defense(request):
    """Set the defense team for PvP."""
    if request.method != "POST":
        return redirect("pvp:lobby")

    profile = request.user.profile
    team_id = request.POST.get("team_id")
    team = profile.teams.filter(id=team_id).first()

    if not team or team.god_count() == 0:
        return JsonResponse({"status": "invalid_team"}, status=400)

    pvp, _ = PvPProfile.objects.get_or_create(player=profile)
    pvp.defense_team = team
    pvp.save(update_fields=["defense_team"])
    return JsonResponse({"status": "ok"})


@login_required
def battle_result(request, battle_id: int):
    """Show the result of a PvP battle."""
    profile = request.user.profile
    battle = get_object_or_404(
        PvPBattle.objects.select_related(
            "attacker__user", "defender__user", "winner__user"
        ),
        pk=battle_id,
    )

    if profile not in (battle.attacker, battle.defender):
        messages.error(request, "No tienes permiso para ver esta batalla.")
        return redirect("pvp:lobby")

    is_attacker = profile == battle.attacker
    won = battle.winner == profile

    enemy_name = (
        battle.defender.user.username
        if battle.defender and battle.defender_id
        else "Desconocido"
    )
    rating_change = (
        battle.attacker_rating_change if is_attacker else battle.defender_rating_change
    )

    return render(
        request,
        "pvp/battle_result.html",
        {
            "battle": battle,
            "won": won,
            "is_attacker": is_attacker,
            "enemy_name": enemy_name,
            "rating_change": rating_change,
            "profile": profile,
        },
    )


@login_required
def ranking(request):
    """Show the PvP ranking leaderboard."""
    top_100 = PvPProfile.objects.select_related("player__user").order_by("-rating")[
        :100
    ]

    profile = request.user.profile
    current_rank = None
    try:
        pvp = profile.pvp
        all_ratings = list(
            PvPProfile.objects.values_list("rating", flat=True).order_by("-rating")
        )
        current_rank = 1
        for r in all_ratings:
            if r > pvp.rating:
                current_rank += 1
            else:
                break
    except PvPProfile.DoesNotExist:
        current_rank = None

    return render(
        request,
        "pvp/ranking.html",
        {
            "top_players": top_100,
            "current_rank": current_rank,
            "profile": profile,
        },
    )


@login_required
def history(request):
    """Show PvP battle history for the current player."""
    profile = request.user.profile
    page = int(request.GET.get("page", 1))
    per_page = 20
    offset = (page - 1) * per_page

    battles = PvPBattle.objects.filter(
        Q(attacker=profile) | Q(defender=profile)
    ).select_related("attacker__user", "defender__user", "winner__user")[
        offset : offset + per_page
    ]

    total = PvPBattle.objects.filter(Q(attacker=profile) | Q(defender=profile)).count()
    total_pages = max(1, (total + per_page - 1) // per_page)

    return render(
        request,
        "pvp/history.html",
        {
            "battles": battles,
            "page": page,
            "total_pages": total_pages,
            "profile": profile,
        },
    )
