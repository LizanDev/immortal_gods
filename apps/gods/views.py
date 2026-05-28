"""Gods views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.items.models import PlayerItem

from .models import God, PlayerGod


@login_required
def god_list(request):
    """List all available gods."""
    gods = God.objects.all()
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
    gods = profile.gods.select_related("god").prefetch_related("equipped_items__item").all()

    from apps.gods.models import Pantheon
    pantheons = Pantheon.choices

    return render(
        request,
        "gods/my_gods.html",
        {"gods": gods, "profile": profile, "pantheons": pantheons},
    )


@login_required
def level_up_god(request, god_id):
    """Level up a god using gold."""
    pg = get_object_or_404(PlayerGod, pk=god_id, player=request.user.profile)

    if request.method == "POST":
        if pg.level_up_with_gold():
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
def equip_item(request, god_id, item_id):
    """Equip an item to a god via AJAX."""
    pg = get_object_or_404(PlayerGod, pk=god_id, player=request.user.profile)
    pi = get_object_or_404(PlayerItem, pk=item_id, player=request.user.profile)

    if request.method == "POST":
        success = pi.equip(pg)
        if success:
            return JsonResponse({
                "status": "ok",
                "message": f"{pi.item.name} equipped to {pg.god.name}",
            })
        return JsonResponse({
            "status": "error",
            "message": "Slot already occupied. Unequip first.",
        }, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def unequip_item(request, item_id):
    """Unequip an item via AJAX."""
    pi = get_object_or_404(PlayerItem, pk=item_id, player=request.user.profile)

    if request.method == "POST":
        pi.unequip()
        return JsonResponse({
            "status": "ok",
            "message": f"{pi.item.name} unequipped",
        })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
def available_items(request, god_id, item_type):
    """Get available items of a type for a god via AJAX."""
    pg = get_object_or_404(PlayerGod, pk=god_id, player=request.user.profile)

    equipped_ids = set(pg.equipped_items.values_list("id", flat=True))

    available = PlayerItem.objects.filter(
        player=request.user.profile,
        item__item_type=item_type,
    ).exclude(id__in=equipped_ids).select_related("item")

    items = []
    for pi in available:
        items.append({
            "id": pi.id,
            "name": pi.item.name,
            "level": pi.level,
            "atk": pi.item.attack_bonus,
            "def": pi.item.defense_bonus,
            "hp": pi.item.hp_bonus,
            "spd": pi.item.speed_bonus,
            "is_specific": pi.item.belongs_to_god == pg.god.name,
        })

    return JsonResponse({"items": items})
