"""Core URL configuration."""

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("api/health/", views.health_check, name="health_check"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("home/", views.home, name="home"),
    path("inventory/", views.inventory, name="inventory"),
    path("missions/", views.missions, name="missions"),
    path("missions/claim/<int:mission_id>/", views.claim_mission, name="claim_mission"),
    path("missions/claim-all/", views.claim_all_missions, name="claim_all_missions"),
    path("shop/", views.shop, name="shop"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="core:landing"), name="logout"),
    path("redeem/", views.redeem_referral, name="redeem_referral"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("notifications/mark-seen/", views.mark_gift_seen, name="mark_gift_seen"),
]
