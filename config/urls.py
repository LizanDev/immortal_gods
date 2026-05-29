"""URL configuration for game project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("apps.core.urls")),
    path("gods/", include("apps.gods.urls")),
    path("items/", include("apps.items.urls")),
    path("teams/", include("apps.teams.urls")),
    path("gacha/", include("apps.gacha.urls")),
    path("campaign/", include("apps.campaign.urls")),
    path("pvp/", include("apps.pvp.urls")),
]
