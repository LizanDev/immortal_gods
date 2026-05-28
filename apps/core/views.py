"""Core views."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.urls import reverse

from apps.campaign.models import FactionLadder, FactionProgress
from apps.core.models import DailyMission, PlayerMission, PlayerProfile, ReferralCode, track_mission
from apps.gods.models import ASCENSION_COSTS, ESSENCE_REWARDS
from apps.items.models import Item, ItemType, PlayerItem


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
    """Landing page for non-authenticated users."""
    if request.user.is_authenticated:
        return redirect("core:home")
    return render(request, "core/landing.html")


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
                from django.db import transaction
                with transaction.atomic():
                    ref = ReferralCode.objects.select_for_update().get(
                        code=referral_code, used_by__isnull=True
                    )
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
@require_POST
def redeem_referral(request):
    """Redeem a referral code for gems."""
    if request.method == "POST":
        code = request.POST.get("referral_code", "").strip().upper()
        if not code:
            messages.error(request, "Please enter a referral code")
            return redirect("core:inventory")

        try:
            from django.db import transaction
            with transaction.atomic():
                ref = ReferralCode.objects.select_for_update().get(
                    code=code, used_by__isnull=True
                )
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

    try:
        track_mission(profile, "daily_login")
    except Exception:
        pass  # Ignore errors if missions table is empty

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
@require_POST
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


@login_required
@require_POST
def claim_all_missions(request):
    """Claim all completed mission rewards at once."""
    if request.method == "POST":
        profile = request.user.profile
        total_energy = 0
        claimed_count = 0

        for pm in PlayerMission.objects.filter(
            player=profile, completed=True, claimed=False
        ):
            energy = pm.claim_reward()
            total_energy += energy
            claimed_count += 1

        if claimed_count > 0:
            profile.add_energy(total_energy)
            messages.success(
                request, f"¡{claimed_count} misiones reclamadas! +{total_energy} energía"
            )
        else:
            messages.info(request, "No hay misiones para reclamar")

    return redirect("core:missions")


SHOP_ITEMS = [
    {
        "id": "essence_small",
        "name": "Esencia Menor",
        "desc": "+10 Esencia",
        "cost": 100,
        "type": "essence",
        "amount": 10,
        "icon": "💎",
        "rarity": "common",
    },
    {
        "id": "essence_medium",
        "name": "Esencia Media",
        "desc": "+30 Esencia",
        "cost": 250,
        "type": "essence",
        "amount": 30,
        "icon": "💎",
        "rarity": "rare",
    },
    {
        "id": "essence_large",
        "name": "Esencia Mayor",
        "desc": "+100 Esencia",
        "cost": 800,
        "type": "essence",
        "amount": 100,
        "icon": "💎",
        "rarity": "epic",
    },
    {
        "id": "essence_mega",
        "name": "Esencia Legendaria",
        "desc": "+300 Esencia",
        "cost": 2000,
        "type": "essence",
        "amount": 300,
        "icon": "💎",
        "rarity": "legendary",
    },
    {
        "id": "weapon_pack",
        "name": "Pack de Arma",
        "desc": "Arma aleatoria",
        "cost": 150,
        "type": "item",
        "item_type": ItemType.WEAPON,
        "icon": "⚔️",
        "rarity": "rare",
    },
    {
        "id": "armor_pack",
        "name": "Pack de Armadura",
        "desc": "Armadura aleatoria",
        "cost": 150,
        "type": "item",
        "item_type": ItemType.ARMOR,
        "icon": "🛡️",
        "rarity": "rare",
    },
    {
        "id": "amulet_pack",
        "name": "Pack de Amuleto",
        "desc": "Amuleto aleatorio",
        "cost": 150,
        "type": "item",
        "item_type": ItemType.AMULET,
        "icon": "📿",
        "rarity": "rare",
    },
    {
        "id": "energy_pack",
        "name": "Pack de Energía",
        "desc": "+50 Energía",
        "cost": 100,
        "type": "energy",
        "amount": 50,
        "icon": "⚡",
        "rarity": "common",
    },
]


@login_required
def shop(request):
    """Show shop with items purchasable with gems."""
    profile = request.user.profile

    if request.method == "POST":
        shop_id = request.POST.get("shop_id")
        item = next((i for i in SHOP_ITEMS if i["id"] == shop_id), None)

        if not item:
            messages.error(request, "Producto no encontrado")
            return redirect("core:shop")

        if profile.gems < item["cost"]:
            messages.error(request, f"Gemas insuficientes. Necesitas {item['cost']}")
            return redirect("core:shop")

        profile.spend_gems(item["cost"])

        if item["type"] == "essence":
            god_id = request.POST.get("god_id")
            if god_id:
                target_god = profile.gods.filter(id=god_id).first()
            else:
                target_god = profile.gods.first()

            if target_god:
                target_god.add_essence(item["amount"])
                messages.success(
                    request, f"¡Compra exitosa! +{item['amount']} esencia para {target_god.god.name}"
                )
            else:
                profile.gems += item["cost"]
                profile.save(update_fields=["gems"])
                messages.error(request, "Necesitas al menos un dios para comprar esencia")
                return redirect("core:shop")

        elif item["type"] == "item":
            templates = Item.objects.filter(item_type=item["item_type"])
            if templates.exists():
                import random
                template = random.choice(list(templates))
                PlayerItem.objects.create(player=profile, item=template)
                messages.success(
                    request, f"¡Compra exitosa! Obtuviste {template.name}"
                )
            else:
                profile.gems += item["cost"]
                profile.save(update_fields=["gems"])
                messages.error(request, "No hay items disponibles en este momento")
                return redirect("core:shop")

        elif item["type"] == "energy":
            profile.restore_energy(item["amount"])
            messages.success(request, f"¡Compra exitosa! +{item['amount']} energía")

        return redirect("core:shop")

    return render(
        request,
        "core/shop.html",
        {
            "profile": profile,
            "shop_items": SHOP_ITEMS,
        },
    )


def robots_txt(request):
    """Serve robots.txt for search engines."""
    return render(request, "core/robots.txt", content_type="text/plain")


def sitemap(request):
    """Generate XML sitemap for search engines."""
    from apps.gods.models import God

    urls = [
        {"loc": request.build_absolute_uri(reverse("core:landing")), "priority": "1.0", "changefreq": "daily"},
        {"loc": request.build_absolute_uri(reverse("core:login")), "priority": "0.9", "changefreq": "daily"},
        {"loc": request.build_absolute_uri(reverse("core:register")), "priority": "0.9", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri(reverse("gods:list")), "priority": "0.8", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri(reverse("items:list")), "priority": "0.7", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri(reverse("campaign:list")), "priority": "0.7", "changefreq": "weekly"},
        {"loc": request.build_absolute_uri(reverse("teams:list")), "priority": "0.6", "changefreq": "weekly"},
    ]

    gods = God.objects.all()
    for god in gods:
        urls.append({
            "loc": request.build_absolute_uri(reverse("gods:detail", args=[god.id])),
            "priority": "0.6",
            "changefreq": "monthly",
        })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += "  <url>\n"
        xml += f"    <loc>{url['loc']}</loc>\n"
        xml += f"    <changefreq>{url['changefreq']}</changefreq>\n"
        xml += f"    <priority>{url['priority']}</priority>\n"
        xml += "  </url>\n"
    xml += "</urlset>"

    return HttpResponse(xml, content_type="application/xml")
