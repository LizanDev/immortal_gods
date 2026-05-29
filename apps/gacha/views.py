"""Gacha views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.core.models import track_mission
from apps.gacha.models import (
    MULTI_PULL_COST,
    PITY_LIMIT,
    SINGLE_PULL_COST,
    Banner,
    PullType,
    get_pulls_since_last_high,
    perform_pull,
)


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

        pulls_since = get_pulls_since_last_high(profile)

        return render(
            request,
            "gacha/results.html",
            {
                "results": results,
                "profile": profile,
                "pulls_since_legendary": pulls_since,
                "pity_threshold": PITY_LIMIT,
                "pity_percent": min(100, int((pulls_since / PITY_LIMIT) * 100)),
            },
        )

    history = profile.pulls.select_related("god", "item")[:20]

    pulls_since = get_pulls_since_last_high(profile)

    return render(
        request,
        "gacha/pull.html",
        {
            "profile": profile,
            "history": history,
            "SINGLE_PULL_COST": SINGLE_PULL_COST,
            "MULTI_PULL_COST": MULTI_PULL_COST,
            "pulls_since_legendary": pulls_since,
            "pity_threshold": PITY_LIMIT,
            "pity_percent": min(100, int((pulls_since / PITY_LIMIT) * 100)),
        },
    )
