"""Gods views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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
    gods = profile.gods.select_related("god").all()
    return render(request, "gods/my_gods.html", {"gods": gods, "profile": profile})


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
