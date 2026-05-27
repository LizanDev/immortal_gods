"""Gacha views."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.gacha.models import (
    MULTI_PULL_COST,
    SINGLE_PULL_COST,
    Banner,
    PullType,
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

        return render(
            request,
            "gacha/results.html",
            {"results": results, "profile": profile},
        )

    history = profile.pulls.select_related("god", "item")[:20]
    return render(
        request,
        "gacha/pull.html",
        {
            "profile": profile,
            "history": history,
            "banners": Banner.choices,
            "SINGLE_PULL_COST": SINGLE_PULL_COST,
            "MULTI_PULL_COST": MULTI_PULL_COST,
        },
    )
