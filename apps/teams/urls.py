"""Teams URL configuration."""

from django.urls import path

from . import views

app_name = "teams"

urlpatterns = [
    path("", views.team_list, name="list"),
    path("<int:team_id>/", views.team_detail, name="detail"),
    path("create/", views.team_create, name="create"),
    path("<int:team_id>/add/", views.team_add_member, name="add_member"),
    path(
        "<int:team_id>/remove/<int:member_id>/",
        views.team_remove_member,
        name="remove_member",
    ),
    path("<int:team_id>/delete/", views.team_delete, name="delete"),
]
