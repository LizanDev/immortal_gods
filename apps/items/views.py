"""Items views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.gods.models import PlayerGod
from apps.items.models import Item, PlayerItem


@login_required
def item_list(request):
    """List all available items."""
    items = Item.objects.all()
    return render(request, "items/list.html", {"items": items})


@login_required
def item_detail(request, item_id):
    """Show details for a specific item."""
    item = get_object_or_404(Item, pk=item_id)
    return render(request, "items/detail.html", {"item": item})


@login_required
def my_items(request):
    """Show player's owned items."""
    profile = request.user.profile
    items = profile.items.select_related("item", "equipped_to__god").all()
    equip_gods = profile.gods.select_related("god").all()
    return render(
        request,
        "items/my_items.html",
        {"items": items, "profile": profile, "equip_gods": equip_gods},
    )


@login_required
def equip_item(request, item_id):
    """Equip an item to a player god."""
    player_item = get_object_or_404(PlayerItem, pk=item_id, player=request.user.profile)

    if request.method == "POST":
        god_id = request.POST.get("god_id")
        player_god = get_object_or_404(
            PlayerGod, pk=god_id, player=request.user.profile
        )

        success = player_item.equip(player_god)

        if success:
    return redirect(request.META.get("HTTP_REFERER", "core:inventory") + f"#item-{item_id}")

    gods = PlayerGod.objects.filter(player=request.user.profile)
    return render(
        request,
        "items/equip.html",
        {"player_item": player_item, "gods": gods},
    )


@login_required
def unequip_item(request, item_id):
    """Unequip an item from its current god."""
    player_item = get_object_or_404(PlayerItem, pk=item_id, player=request.user.profile)
    player_item.unequip()
    return redirect(request.META.get("HTTP_REFERER", "core:inventory"))


@login_required
def upgrade_item(request, item_id):
    """Upgrade an item's level."""
    player_item = get_object_or_404(PlayerItem, pk=item_id, player=request.user.profile)

    cost = player_item.item.get_upgrade_cost(player_item.level)

    if cost > 0 and (request.user.is_superuser or request.user.profile.gold >= cost):
        player_item.upgrade(cost)

    return redirect(request.META.get("HTTP_REFERER", "core:inventory"))
