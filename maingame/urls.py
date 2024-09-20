from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.index, name="index"),
    # path("build", views.build, name="build"),
    path("buildings/destroy/<int:building_id>", views.destroy_building, name="destroy_building"),
    path("regions/<int:region_id>/build/<int:building_type_id>/amount/<int:amount>", views.build_building, name="build_building"),
    path("regions/<int:region_id>", views.region, name="region"),
    path("regions", views.regions, name="regions"),
    path("army_training/submit", views.submit_training, name="submit_training"),
    path("army_training", views.army_training, name="army_training"),
    path("resources", views.resources, name="resources"),
    path("dispatch_to_all_regions/<int:unit_id>/<int:quantity>", views.dispatch_to_all_regions, name="dispatch_to_all_regions"),
    path("dispatch_to_one_region/<int:region_id>", views.dispatch_to_one_region, name="dispatch_to_one_region"),
    
]