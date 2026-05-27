"""Core URL configuration."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("inventory/", views.inventory, name="inventory"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="core:landing"), name="logout"),
    path("redeem/", views.redeem_referral, name="redeem_referral"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]
