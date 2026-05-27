"""Items URL configuration."""

from django.urls import path

from . import views

app_name = "items"

urlpatterns = [
    path("", views.item_list, name="list"),
    path("<int:item_id>/", views.item_detail, name="detail"),
    path("my/", views.my_items, name="my_items"),
    path("<int:item_id>/equip/", views.equip_item, name="equip"),
    path("<int:item_id>/unequip/", views.unequip_item, name="unequip"),
    path("<int:item_id>/upgrade/", views.upgrade_item, name="upgrade"),
]
