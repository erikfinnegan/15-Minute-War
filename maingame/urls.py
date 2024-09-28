from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.index, name="index"),
    path("join", views.join, name="join"),
    path("buildings/destroy/<int:building_id>", views.destroy_building, name="destroy_building"),
    path("regions/<int:region_id>/build/<int:building_type_id>/amount/<int:amount>", views.build_building, name="build_building"),
    path("regions/<int:region_id>", views.region, name="region"),
    path("regions", views.regions, name="regions"),
    path("news", views.news, name="news"),
    path("set_timezone", views.set_timezone, name="set_timezone"),
    path("upgrades", views.upgrades, name="upgrades"),
    path("upgrade_building_type/<int:building_type_id>", views.upgrade_building_type, name="upgrade_building_type"),
    path("legions/submit", views.submit_training, name="submit_training"),
    path("legions", views.legions, name="legions"),
    path("resources", views.resources, name="resources"),
    path("dispatch_to_all_regions/<int:unit_id>/<int:quantity>", views.dispatch_to_all_regions, name="dispatch_to_all_regions"),
    path("dispatch_to_one_region/<int:region_id>", views.dispatch_to_one_region, name="dispatch_to_one_region"),
    path("marshal_from_region/<int:region_id>", views.marshal_from_region, name="marshal_from_region"),
    path("run_tick_view/<int:quantity>", views.run_tick_view, name="run_tick_view"),
    path("protection_tick/<int:quantity>", views.protection_tick, name="protection_tick"),
]