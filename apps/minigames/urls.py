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
]
