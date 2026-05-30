"""URL configuration for game project."""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path, reverse

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("apps.core.urls")),
    path("gods/", include("apps.gods.urls")),
    path(
        "items/",
        lambda r: HttpResponseRedirect(reverse("core:inventory")),
        name="items_redirect",
    ),
    path("items/<path:path>/", lambda r, path: HttpResponseRedirect(reverse("core:inventory"))),
    path("teams/", include("apps.teams.urls")),
    path("gacha/", include("apps.gacha.urls")),
    path("campaign/", include("apps.campaign.urls")),
    path("pvp/", include("apps.pvp.urls")),
    path("minigames/", include("apps.minigames.urls")),
]
