from django.shortcuts import redirect
from django.contrib import messages

from maingame.models import Dominion, Faction
from maingame.utils.dominion_controls import initialize_dominion, delete_dominion


def goblin_restart(request, resource):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if resource == "gold":
        messages.error(request, f"Nice try.")
        return redirect("buildings")
    
    display_name = dominion.name
    faction = Faction.objects.get(name=dominion.faction_name)

    delete_dominion(dominion)
    new_dominion = initialize_dominion(user=request.user, faction=faction, display_name=display_name)
    new_dominion.perk_dict["rulers_favorite_resource"] = resource
    new_dominion.save()

    return redirect("buildings")
