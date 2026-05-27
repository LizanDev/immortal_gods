"""Gacha URL configuration."""

from django.urls import path

from . import views

app_name = "gacha"

urlpatterns = [
    path("", views.gacha_pull, name="pull"),
]
