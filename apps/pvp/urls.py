"""PvP URL configuration."""

from django.urls import path

from . import views

app_name = "pvp"

urlpatterns = [
    path("", views.lobby, name="lobby"),
    path("find-match/", views.find_match, name="find_match"),
    path("cancel-queue/", views.cancel_queue, name="cancel_queue"),
    path("check-match/", views.check_match, name="check_match"),
    path("battle/<int:battle_id>/", views.battle_result, name="battle_result"),
    path("ranking/", views.ranking, name="ranking"),
    path("history/", views.history, name="history"),
]
