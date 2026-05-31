"""Minigames URL configuration."""

from django.urls import path

from . import views

app_name = "minigames"

urlpatterns = [
    path("", views.index, name="index"),
    path("memory/", views.memory_game, name="memory"),
    path("memory/save/", views.memory_save, name="memory_save"),
    path("memory/claim/", views.memory_claim, name="memory_claim"),
    path("wheel/", views.wheel_of_fortune, name="wheel"),
    path("wheel/spin/", views.wheel_spin, name="wheel_spin"),
    path("cards/", views.card_game, name="cards"),
    path("cards/place/", views.card_place, name="card_place"),
    path("cards/claim/", views.card_claim, name="card_claim"),
    path("cards/deck/", views.card_deck, name="card_deck"),
    path(
        "cards/allocate-bonus/", views.card_allocate_bonus, name="card_allocate_bonus"
    ),
]
