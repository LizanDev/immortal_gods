"""Gods URL configuration."""

from django.urls import path

from . import views

app_name = "gods"

urlpatterns = [
    path("", views.god_list, name="list"),
    path("<int:god_id>/", views.god_detail, name="detail"),
    path("my/", views.my_gods, name="my_gods"),
    path("<int:god_id>/level-up/", views.level_up_god, name="level_up"),
    path("<int:god_id>/equip/<int:item_id>/", views.equip_item, name="equip_item"),
    path("unequip/<int:item_id>/", views.unequip_item, name="unequip_item"),
    path("<int:god_id>/available-items/<str:item_type>/", views.available_items, name="available_items"),
]
