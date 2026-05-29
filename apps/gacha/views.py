"""Gacha views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.core.models import track_mission
from apps.gacha.models import (
    MULTI_PULL_COST,
    SINGLE_PULL_COST,
    Banner,
    PullHistory,
    PullType,
    perform_pull,
)

PITY_THRESHOLD = 50


@login_required
def gacha_pull(request):
    """Handle gacha pull logic."""
    profile = request.user.profile

    if request.method == "POST":
        banner = request.POST.get("banner", Banner.STANDARD)
        pull_type = request.POST.get("pull_type", PullType.SINGLE)

        results = perform_pull(profile, banner, pull_type)

        if not results:
            return render(
                request,
                "gacha/insufficient_gems.html",
                {"profile": profile},
            )

        if pull_type == PullType.SINGLE:
            track_mission(profile, "first_pull")
        track_mission(profile, "gacha_pulls", len(results))

        return render(
            request,
            "gacha/results.html",
            {"results": results, "profile": profile},
        )

    history = profile.pulls.select_related("god", "item")[:20]

    last_high = (
        PullHistory.objects.filter(
            player=profile, god__rarity__in=["legendary", "mythic"]
        )
        .order_by("-created_at")
        .first()
    )
    if last_high:
        pulls_since = PullHistory.objects.filter(
            player=profile, created_at__gt=last_high.created_at
        ).count()
    else:
        pulls_since = profile.pulls.count()

    return render(
        request,
        "gacha/pull.html",
        {
            "profile": profile,
            "history": history,
            "SINGLE_PULL_COST": SINGLE_PULL_COST,
            "MULTI_PULL_COST": MULTI_PULL_COST,
            "pulls_since_legendary": pulls_since,
            "pity_threshold": PITY_THRESHOLD,
            "pity_percent": min(100, int((pulls_since / PITY_THRESHOLD) * 100)),
        },
    )
