"""PvP views."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.battle.utils import (
    calculate_elo_change,
    calculate_team_power,
    make_snapshot,
    resolve_battle,
)
from apps.core.models import track_mission

from .models import BOT_NAMES, PvPBattle, PvPProfile


@login_required
def lobby(request):
    """Main PvP hub showing player stats, queue status, and find match button."""
    profile = request.user.profile
    pvp, _ = PvPProfile.objects.get_or_create(player=profile)
    recent_battles = PvPBattle.objects.filter(
        Q(attacker=profile) | Q(defender=profile)
    ).select_related("attacker__user", "winner__user")[:5]
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
def find_match(request):
    """Enter the PvP queue or find an immediate opponent."""
    if request.method != "POST":
        return redirect("pvp:lobby")

    profile = request.user.profile
    pvp, _ = PvPProfile.objects.get_or_create(player=profile)

    if pvp.in_queue:
        return JsonResponse({"status": "already_in_queue"}, status=400)

    team = profile.teams.first()
    if not team or team.god_count() == 0:
        return JsonResponse({"status": "no_team"}, status=400)

    # Try to find an opponent
    rating_min = max(0, pvp.rating - 200)
    rating_max = pvp.rating + 200

    opponent = (
        PvPProfile.objects.filter(
            in_queue=True,
            rating__gte=rating_min,
            rating__lte=rating_max,
            player__is_superuser=False,
        )
        .exclude(player=profile)
        .select_related("player")
        .order_by("queued_at")
        .first()
    )

    if opponent:
        # Found match — create battle immediately
        attacker = profile
        defender = opponent.player

        attacker_team = team
        defender_team = opponent.player.teams.first()

        attacker_power = calculate_team_power(attacker_team)
        defender_power = calculate_team_power(defender_team) if defender_team else 0

        won, battle_log = resolve_battle(attacker_power, defender_power)
        attacker_delta, defender_delta = calculate_elo_change(
            pvp.rating, opponent.rating, won_by_a=won
        )

        battle = PvPBattle.objects.create(
            attacker=attacker,
            defender=defender,
            attacker_team=attacker_team,
            defender_team=defender_team,
            attacker_snapshot=make_snapshot(attacker_team),
            defender_snapshot=make_snapshot(defender_team) if defender_team else {},
            winner=attacker if won else defender,
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

    # No human opponent — create bot battle immediately
    import random

    bot_name = random.choice(BOT_NAMES)
    bot_rating = max(800, pvp.rating + random.randint(-100, 100))

    # Generate a bot snapshot with scaled power
    player_power = calculate_team_power(team)
    bot_power = max(50, int(player_power * random.uniform(0.7, 1.3)))

    bot_god_names = ["Soldado", "Arquero", "Mago", "Guerrero", "Cuervo"]
    bot_gods = []
    for i, gname in enumerate(bot_god_names):
        bot_gods.append(
            {
                "id": -(i + 1),
                "name": gname,
                "rarity": "common",
                "role": "warrior",
                "level": max(1, pvp.battles_played // 5 + 1),
                "quality_tier": 1,
                "attack": bot_power // (len(bot_god_names) * 2),
                "defense": bot_power // (len(bot_god_names) * 2),
                "hp": bot_power // len(bot_god_names),
                "speed": 50,
                "image_url": "",
                "tags": [],
            }
        )

    defender_snapshot = {
        "gods": bot_gods,
        "power": bot_power,
        "synergy_mult": 1.0,
    }

    won, battle_log = resolve_battle(player_power, bot_power)
    attacker_delta, defender_delta = calculate_elo_change(
        pvp.rating, bot_rating, won_by_a=won
    )

    battle = PvPBattle.objects.create(
        attacker=profile,
        defender=None,
        is_bot=True,
        bot_name=f"🤖 {bot_name}",
        bot_rating=bot_rating,
        attacker_team=team,
        defender_team=None,
        attacker_snapshot=make_snapshot(team),
        defender_snapshot=defender_snapshot,
        winner=profile if won else None,
        attacker_rating_change=attacker_delta,
        defender_rating_change=defender_delta,
        battle_log=battle_log,
    )

    pvp.record_battle(won=won, rating_change=attacker_delta)

    if won:
        track_mission(profile, "win_battles")

    return JsonResponse(
        {
            "status": "match_found",
            "battle_id": battle.id,
        }
    )


@login_required
def cancel_queue(request):
    """Leave the PvP queue."""
    if request.method != "POST":
        return redirect("pvp:lobby")

    profile = request.user.profile
    PvPProfile.objects.filter(player=profile).update(in_queue=False, queued_at=None)
    return JsonResponse({"status": "cancelled"})


@login_required
def check_match(request):
    """Poll endpoint to check if a match has been found."""
    profile = request.user.profile
    pvp = PvPProfile.objects.filter(player=profile).first()

    if not pvp or not pvp.in_queue:
        return JsonResponse({"status": "not_in_queue"})

    # Look for any recent battle where this player is attacker or defender
    recent_cutoff = timezone.now() - timedelta(seconds=30)
    battle = (
        PvPBattle.objects.filter(
            Q(attacker=profile) | Q(defender=profile),
            created_at__gte=recent_cutoff,
        )
        .order_by("-created_at")
        .first()
    )

    if battle:
        pvp.in_queue = False
        pvp.queued_at = None
        pvp.save(update_fields=["in_queue", "queued_at"])
        return JsonResponse(
            {
                "status": "match_found",
                "battle_id": battle.id,
            }
        )

    # Check if the player has been queued too long (heartbeat)
    if pvp.queued_at and timezone.now() - pvp.queued_at > timedelta(seconds=120):
        pvp.in_queue = False
        pvp.queued_at = None
        pvp.save(update_fields=["in_queue", "queued_at"])
        return JsonResponse({"status": "timeout"})

    return JsonResponse({"status": "waiting"})


@login_required
def battle_result(request, battle_id: int):
    """Show the result of a PvP battle."""
    profile = request.user.profile
    battle = get_object_or_404(
        PvPBattle.objects.select_related(
            "attacker__user", "winner__user"
        ),
        pk=battle_id,
    )

    if battle.defender and profile not in (battle.attacker, battle.defender):
        messages.error(request, "No tienes permiso para ver esta batalla.")
        return redirect("pvp:lobby")
    if not battle.defender and not battle.is_bot and profile != battle.attacker:
        messages.error(request, "No tienes permiso para ver esta batalla.")
        return redirect("pvp:lobby")

    is_attacker = profile == battle.attacker
    won = battle.winner == profile

    enemy_name = battle.defender_display if battle.is_bot else (
        battle.defender.user.username if battle.defender else "Desconocido"
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
        # Find player position
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
    ).select_related("attacker__user", "winner__user")[
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
