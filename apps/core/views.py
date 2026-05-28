"""Core views."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.campaign.models import FactionLadder, FactionProgress
from apps.core.models import DailyMission, PlayerMission, PlayerProfile, ReferralCode


@login_required
def home(request):
    """Home page view."""
    profile = request.user.profile
    god_count = profile.gods.count()
    team_count = profile.teams.count()

    ladders = FactionLadder.objects.all()
    ladder_data = []
    for ladder in ladders:
        prog, _ = FactionProgress.objects.get_or_create(
            player=profile, ladder=ladder
        )
        ladder_data.append({"ladder": ladder, "progress": prog})

    return render(
        request,
        "core/home.html",
        {
            "profile": profile,
            "god_count": god_count,
            "team_count": team_count,
            "ladder_data": ladder_data,
        },
    )


@login_required
def inventory(request):
    """Show player's inventory of gods and items."""
    profile = request.user.profile
    gods = profile.gods.select_related("god").all()
    items = profile.items.select_related("item").all()
    return render(
        request,
        "core/inventory.html",
        {
            "profile": profile,
            "gods": gods,
            "items": items,
            "equip_gods": gods,
        },
    )


def landing(request):
    """Redirect to login page."""
    return redirect("core:login")


def register(request):
    """Register a new player."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        from django.contrib.auth.models import User

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if not username or not password:
            messages.error(request, "Username and password are required")
            return render(request, "core/register.html")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return render(request, "core/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "core/register.html")

        user = User.objects.create_user(username=username, password=password)
        referral_code = request.POST.get("referral_code", "").strip().upper()
        if referral_code:
            try:
                ref = ReferralCode.objects.get(code=referral_code, used_by__isnull=True)
                ref.used_by = user
                ref.save(update_fields=["used_by", "used_at"])
                user.profile.add_gems(ref.gems_reward)
                messages.success(
                    request, f"Referral code applied! +{ref.gems_reward} gems"
                )
            except ReferralCode.DoesNotExist:
                messages.error(request, "Invalid or already used referral code")
        login(request, user)
        return redirect("core:home")

    return render(request, "core/register.html")


@login_required
def redeem_referral(request):
    """Redeem a referral code for gems."""
    if request.method == "POST":
        code = request.POST.get("referral_code", "").strip().upper()
        if not code:
            messages.error(request, "Please enter a referral code")
            return redirect("core:inventory")

        try:
            ref = ReferralCode.objects.get(code=code, used_by__isnull=True)
            ref.used_by = request.user
            ref.save(update_fields=["used_by", "used_at"])
            request.user.profile.add_gems(ref.gems_reward)
            messages.success(request, f"Code redeemed! +{ref.gems_reward} gems")
        except ReferralCode.DoesNotExist:
            messages.error(request, "Invalid or already used referral code")

    return redirect("core:inventory")


@login_required
def leaderboard(request):
    """Show player ranking leaderboard."""
    top_players = PlayerProfile.objects.select_related("user").order_by("-rank_score")[:50]
    user_rank = None
    user_position = None
    for i, p in enumerate(top_players, 1):
        if p.user_id == request.user.id:
            user_rank = p.rank_score
            user_position = i
            break
    if user_position is None:
        user_position = PlayerProfile.objects.filter(rank_score__gt=request.user.profile.rank_score).count() + 1
    return render(
        request,
        "core/leaderboard.html",
        {
            "top_players": top_players,
            "user_position": user_position,
            "user_rank": user_rank,
        },
    )


@login_required
def missions(request):
    """Show daily missions and allow claiming rewards."""
    profile = request.user.profile

    track_mission(profile, "daily_login")

    active_missions = DailyMission.objects.filter(is_active=True)

    player_missions = []
    for mission in active_missions:
        pm, created = PlayerMission.objects.get_or_create(
            player=profile, mission=mission
        )
        player_missions.append(pm)

    total_energy_claimable = sum(
        pm.mission.energy_reward for pm in player_missions if pm.completed and not pm.claimed
    )

    return render(
        request,
        "core/missions.html",
        {
            "profile": profile,
            "player_missions": player_missions,
            "total_energy_claimable": total_energy_claimable,
        },
    )


@login_required
def claim_mission(request, mission_id):
    """Claim reward for a completed mission."""
    if request.method == "POST":
        profile = request.user.profile
        try:
            pm = PlayerMission.objects.get(
                player=profile, mission_id=mission_id
            )
            if pm.completed and not pm.claimed:
                energy = pm.claim_reward()
                profile.add_energy(energy)
                messages.success(
                    request, f"¡Recompensa reclamada! +{energy} energía"
                )
            else:
                messages.error(request, "Esta misión no está lista para reclamar")
        except PlayerMission.DoesNotExist:
            messages.error(request, "Misión no encontrada")

    return redirect("core:missions")


def track_mission(player, mission_type: str, amount: int = 1):
    """Track mission progress for a player. Called by other apps."""
    try:
        mission = DailyMission.objects.get(mission_type=mission_type, is_active=True)
        pm, _ = PlayerMission.objects.get_or_create(player=player, mission=mission)
        pm.add_progress(amount)
    except DailyMission.DoesNotExist:
        pass
