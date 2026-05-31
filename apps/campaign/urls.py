"""Campaign URL configuration."""

from django.urls import path

from . import views

app_name = "campaign"

urlpatterns = [
    path("", views.campaign_list, name="list"),
    path("<int:level_id>/", views.campaign_detail, name="detail"),
    path("<int:level_id>/battle/", views.campaign_battle, name="battle"),
    path(
        "<int:level_id>/resultado/",
        views.campaign_battle_result,
        name="battle_result",
    ),
    path("select-team/<int:team_id>/", views.select_team, name="select_team"),
    path("factions/", views.faction_ladders, name="faction_ladders"),
    path(
        "factions/<int:ladder_id>/",
        views.faction_ladder_detail,
        name="faction_ladder_detail",
    ),
    path(
        "factions/battle/<int:stage_id>/",
        views.faction_battle,
        name="faction_battle",
    ),
]
