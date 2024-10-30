from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.index, name="index"),
    path("register/submit", views.submit_register, name="submit_register"),
    path("register", views.register, name="register"),
    path("news", views.news, name="news"),
    path("set_timezone", views.set_timezone, name="set_timezone"),
    path("upgrades", views.upgrades, name="upgrades"),
    path("upgrade_building/<int:building_id>", views.upgrade_building, name="upgrade_building"),
    path("military/submit", views.submit_training, name="submit_training"),
    path("military/release", views.submit_release, name="submit_release"),
    path("military", views.military, name="military"),
    path("buildings/submit", views.submit_building, name="submit_building"),
    path("buildings", views.buildings, name="buildings"),
    path("resources", views.resources, name="resources"),
    path("trade/submit", views.trade, name="trade"),
    path("run_tick_view/<int:quantity>", views.run_tick_view, name="run_tick_view"),
    path("protection_tick/<int:quantity>", views.protection_tick, name="protection_tick"),
    path("world", views.world, name="world"),
    path("overview/<int:dominion_id>/invade", views.submit_invasion, name="submit_invasion"),
    path("overview/<int:dominion_id>", views.overview, name="overview"),
    path("discoveries/submit", views.submit_discovery, name="submit_discovery"),
    path("discoveries", views.discoveries, name="discoveries"),
    path("spells", views.spells, name="spells"),
    path("spells/<int:spell_id>", views.submit_spell, name="submit_spell"),
    path("tutorial", views.tutorial, name="tutorial"),
    path("battle_report/<int:battle_id>", views.battle_report, name="battle_report"),
    path("faction_info", views.faction_info, name="faction_info"),
    path("options", views.options, name="options"),
    path("submit_options", views.submit_options, name="submit_options"),
    path("abandon", views.abandon, name="abandon"),
]