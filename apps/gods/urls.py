"""Gods URL configuration."""

from django.urls import path

from . import views

app_name = "gods"

urlpatterns = [
    path("", views.god_list, name="list"),
    path("<int:god_id>/", views.god_detail, name="detail"),
    path("my/", views.my_gods, name="my_gods"),
    path("<int:god_id>/level-up/", views.level_up_god, name="level_up"),
]
