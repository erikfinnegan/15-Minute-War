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
    path("upgrades", views.upgrades, name="upgrades"),
    path("upgrade_building/<int:building_id>", views.upgrade_building, name="upgrade_building"),
    
    path("military/submit", views.submit_training, name="submit_training"),
    path("military/release", views.submit_release, name="submit_release"),
    path("military", views.military, name="military"),
    
    path("buildings/submit", views.submit_building, name="submit_building"),
    path("buildings", views.buildings, name="buildings"),
    path("resources", views.resources, name="resources"),
    path("run_tick_view/<int:quantity>", views.run_tick_view, name="run_tick_view"),
    path("protection_tick/<int:quantity>", views.protection_tick, name="protection_tick"),
    path("protection_restart", views.protection_restart, name="protection_restart"),
    path("goblin_restart/<str:resource>", views.goblin_restart, name="goblin_restart"),
    path("world", views.world, name="world"),
    path("overview/invade", views.submit_invasion, name="submit_invasion"),
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
    path("calculate_op", views.calculate_op, name="calculate_op"),
    
    path("church_affairs", views.church_affairs, name="church_affairs"),
    path("submit_inquisition", views.submit_inquisition, name="submit_inquisition"),
    path("submit_true_inquisition", views.submit_true_inquisition, name="submit_true_inquisition"),
    path("submit_unholy_baptism", views.submit_unholy_baptism, name="submit_unholy_baptism"),
   
    path("experimentation", views.experimentation, name="experimentation"),
    path("generate_experiment", views.generate_experiment, name="generate_experiment"),
    path("approve_experiment", views.approve_experiment, name="approve_experiment"),
    path("terminate_experiment", views.terminate_experiment, name="terminate_experiment"),
    path("submit_masterpiece", views.submit_masterpiece, name="submit_masterpiece"),
   
    path("other_head", views.other_head, name="other_head"),
    path("submit_other_head", views.submit_other_head, name="submit_other_head"),
    
    path("mech_hangar", views.mech_hangar, name="mech_hangar"),
    path("submit_mech_hangar", views.submit_mech_hangar, name="submit_mech_hangar"),
]