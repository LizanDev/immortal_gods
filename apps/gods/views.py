"""Gods views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.models import track_mission
from apps.items.models import PlayerItem

from .models import God, PlayerGod


@login_required
def god_list(request):
    """List all available gods."""
    gods = God.objects.all()

    MAX_LEVEL = 100
    MAX_QUALITY = 5
    Q_MULT = 1.0 + (MAX_QUALITY - 1) * 0.15

    for g in gods:
        g.max_attack = int(g.base_attack * Q_MULT * (1 + MAX_LEVEL * 0.1))
        g.max_defense = int(g.base_defense * Q_MULT * (1 + MAX_LEVEL * 0.1))
        g.max_hp = int(g.base_hp * Q_MULT * (1 + MAX_LEVEL * 0.1))
        g.max_speed = int(g.base_speed * Q_MULT * (1 + MAX_LEVEL * 0.02))

    return render(request, "gods/list.html", {"gods": gods})


@login_required
def god_detail(request, god_id):
    """Show details for a specific god."""
    god = get_object_or_404(God, pk=god_id)
    return render(request, "gods/detail.html", {"god": god})


@login_required
def my_gods(request):
    """Show player's owned gods."""
    profile = request.user.profile
    gods = (
        profile.gods.select_related("god")
        .prefetch_related("equipped_items__item")
        .all()
    )

    from apps.gods.models import Pantheon

    pantheons = Pantheon.choices

    pantheon_counts = {}
    for pg in gods:
        p = pg.god.pantheon
        pantheon_counts[p] = pantheon_counts.get(p, 0) + 1

    return render(
        request,
        "gods/my_gods.html",
        {
            "gods": gods,
            "profile": profile,
            "pantheons": pantheons,
            "pantheon_counts": pantheon_counts,
        },
    )


@login_required
def level_up_god(request, god_id):
    """Level up a god using gold."""
    pg = get_object_or_404(PlayerGod, pk=god_id, player=request.user.profile)

    if request.method == "POST":
        if pg.level_up_with_gold():
            track_mission(request.user.profile, "level_up_god")
            messages.success(
                request,
                f"{pg.god.name} leveled up to Lv.{pg.level}!",
            )
        else:
            messages.error(
                request,
                f"Not enough gold. Need {pg.gold_upgrade_cost} ",
            )

    return redirect("core:inventory")


@login_required
def ascend_god(request, god_id):
    """Ascend a god using essence."""
    pg = get_object_or_404(PlayerGod, pk=god_id, player=request.user.profile)

    if request.method == "POST":
        if pg.ascend():
            track_mission(request.user.profile, "ascend_god")
            messages.success(
                request,
                f"{pg.god.name} ascended to Tier {pg.quality_tier}!",
            )
        else:
            if pg.quality_tier >= 5:
                messages.error(request, f"{pg.god.name} is already at max tier!")
            else:
                messages.error(
                    request,
                    f"Not enough essence. Need {pg.ascension_cost}, have {pg.essence}",
                )

    return redirect("core:inventory")


@login_required
def equip_item(request, god_id, item_id):
    """Equip an item to a god via AJAX."""
    pg = get_object_or_404(PlayerGod, pk=god_id, player=request.user.profile)
    pi = get_object_or_404(PlayerItem, pk=item_id, player=request.user.profile)

    if request.method == "POST":
        success = pi.equip(pg)
        if success:
            track_mission(request.user.profile, "equip_item")
            return JsonResponse(
                {
                    "status": "ok",
                    "message": f"{pi.item.name} equipped to {pg.god.name}",
                }
            )
        return JsonResponse(
            {
                "status": "error",
                "message": "Slot already occupied. Unequip first.",
            },
            status=400,
        )

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def unequip_item(request, item_id):
    """Unequip an item via AJAX."""
    pi = get_object_or_404(PlayerItem, pk=item_id, player=request.user.profile)

    if request.method == "POST":
        pi.unequip()
        return JsonResponse(
            {
                "status": "ok",
                "message": f"{pi.item.name} unequipped",
            }
        )

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def available_items(request, god_id, item_type):
    """Get available items of a type for a god via AJAX."""
    pg = get_object_or_404(PlayerGod, pk=god_id, player=request.user.profile)

    equipped_ids = set(pg.equipped_items.values_list("id", flat=True))

    available = (
        PlayerItem.objects.filter(
            player=request.user.profile,
            item__item_type=item_type,
        )
        .exclude(id__in=equipped_ids)
        .select_related("item")
    )

    items = []
    for pi in available:
        items.append(
            {
                "id": pi.id,
                "name": pi.item.name,
                "level": pi.level,
                "atk": pi.item.attack_bonus,
                "def": pi.item.defense_bonus,
                "hp": pi.item.hp_bonus,
                "spd": pi.item.speed_bonus,
                "is_specific": pi.item.belongs_to_god == pg.god.name,
            }
        )

    return JsonResponse({"items": items})


@login_required
def god_detail_json(request, pg_id):
    """Return JSON with full PlayerGod details for the hero modal."""
    pg = get_object_or_404(
        PlayerGod.objects.select_related("god").prefetch_related("equipped_items__item"),
        pk=pg_id,
        player=request.user.profile,
    )
    skills = pg.skills
    equipment = []
    for eq in pg._equipment_list():
        equipment.append(
            {
                "name": eq.item.name,
                "type": eq.item.item_type,
                "level": eq.level,
                "atk": eq.item.attack_bonus,
                "def": eq.item.defense_bonus,
                "hp": eq.item.hp_bonus,
                "spd": eq.item.speed_bonus,
                "passive_name": eq.item.passive_name,
                "passive_desc": eq.item.passive_desc,
                "passive_atk": eq.item.passive_atk * eq.level,
                "passive_def": eq.item.passive_def * eq.level,
                "passive_hp": eq.item.passive_hp * eq.level,
                "passive_spd": eq.item.passive_spd * eq.level,
                "has_passive": eq.item.has_passive_for(pg.god.name),
            }
        )

    tags = list(pg.god.synergy_tags.values_list("tag", flat=True))

    return JsonResponse(
        {
            "id": pg.id,
            "name": pg.god.name,
            "pantheon": pg.god.get_pantheon_display(),
            "role": pg.god.get_role_display(),
            "rarity": pg.god.get_rarity_display(),
            "rarity_value": pg.god.rarity,
            "description": pg.god.description,
            "image_url": pg.god.image_url,
            "level": pg.level,
            "quality_roman": pg.quality_roman,
            "quality_tier": pg.quality_tier,
            "essence": pg.essence,
            "total_attack": pg.total_attack,
            "total_defense": pg.total_defense,
            "total_hp": pg.total_hp,
            "total_speed": pg.total_speed,
            "skills": skills,
            "equipment": equipment,
            "synergy_tags": tags,
        }
    )
