from random import randint
import random

from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

from maingame.formatters import get_sludgeling_name
from maingame.models import Dominion, Unit, Round, Resource, Sludgene
from maingame.utils.utils import create_unit_dict, round_x_to_nearest_y
from maingame.utils.utils_sludgeling import breed_sludgenes, create_magnum_goopus, create_unit_from_sludgene


def experimentation(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    try:
        masterpieces_available = dominion.perk_dict["masterpieces_to_create"]
    except:
        return redirect("world")

    if dominion.faction_name != "sludgeling":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    # research_cost = int(dominion.perk_dict["experiment_cost_dict"]["research_per_acre"] * dominion.acres)
    # sludge_cost = int(dominion.perk_dict["experiment_cost_dict"]["sludge_per_acre"] * dominion.acres)

    experimental_units = []

    for unit in Unit.objects.filter(ruler=dominion):
        if "sludge" in unit.cost_dict:
            experimental_units.append(unit)

    # latest_experiment_unit = Unit.objects.filter(id=dominion.perk_dict["latest_experiment_id"]).first()
    preselect_last_parents = request.GET.get('preselect_last_parents', False)
    
    context = {
        # "research_cost": research_cost,
        # "sludge_cost": sludge_cost,
        "allow_new_experiments": dominion.perk_dict["custom_units"] < dominion.perk_dict["max_custom_units"],
        # "latest_experiment": dominion.perk_dict["latest_experiment"],
        # "latest_experiment_unit": latest_experiment_unit,
        "experimental_units": experimental_units,
        "has_experimental_units": len(experimental_units) > 0,
        # "units": dominion.sorted_units,
        "masterpieces_available": masterpieces_available,
        "sludgenes": Sludgene.objects.filter(ruler=dominion).order_by("-is_favorite"),
        "splices": dominion.perk_dict.get("splices"),
        "preselect_last_parents": preselect_last_parents,
    }
    
    return render(request, "maingame/faction_pages/experimentation.html", context)


def terminate_experiment(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("experimentation")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("experimentation")

    if dominion.faction_name != "sludgeling":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    unit = Unit.objects.get(id=request.POST["experiment_to_terminate"])

    if unit.quantity_returning > 0:
        messages.error(request, f"Can't terminate experiments while units are returning")
        return redirect("experimentation")
    elif unit.quantity_in_training > 0:
        messages.error(request, f"Can't terminate experiments while units are in training")
        return redirect("experimentation")

    goop_refund = 0
    sludge_refund = 0

    if "goop" in unit.cost_dict:
        goop_refund = int(unit.quantity_at_home * unit.cost_dict["goop"] * dominion.perk_dict["recycling_refund"])

    if "sludge" in unit.cost_dict:
        sludge_refund = int(unit.quantity_at_home * unit.cost_dict["sludge"] * dominion.perk_dict["recycling_refund"])
    
    goop = Resource.objects.get(ruler=dominion, name="goop")
    goop.gain(goop_refund)

    sludge = Resource.objects.get(ruler=dominion, name="sludge")
    sludge.gain(sludge_refund)

    messages.success(request, f"Terminated the {unit.name} experiment, regained {goop_refund:2,} goop and {sludge_refund:2,} sludge from recycling {unit.quantity_at_home:2,} units")

    # Deleting it breaks battle reports
    # unit.ruler = None
    # unit.save()
    unit.delete()

    dominion.perk_dict["custom_units"] -= 1
    dominion.save()
    
    return redirect("experimentation")


def submit_masterpiece(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("experimentation")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("experimentation")
    
    try:
        masterpieces_available = dominion.perk_dict["masterpieces_to_create"]
    except:
        return redirect("world")
    
    if masterpieces_available < 1:
        messages.error(request, f"Don't be greedy")
        return redirect("experimentation")

    unit_dict, _ = create_unit_dict(request.POST, "combine_")
    
    if not unit_dict:
        messages.error(request, f"You didn't pick any units to combine. Re-read how this thing works.")
        return redirect("experimentation")
    

    is_encore = False

    for unit in Unit.objects.filter(ruler=dominion):
        if "is_more_glorious" in unit.perk_dict:
            messages.error(request, f"Don't be greedy")
            return redirect("experimentation")
        elif "is_glorious" in unit.perk_dict:
            is_encore = True

    create_magnum_goopus(dominion, unit_dict, is_encore)

    messages.success(request, f"Behold your masterpiece!")
    return redirect("military")


def submit_sludgenes(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("experimentation")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("experimentation")
    
    selected_sludgenes = []
    action = request.POST.get("action")
    preselect_last_parents = False
    
    for key in request.POST:
        # key is like "breed_123" where 123 is the ID of the Unit
        if "breed_" in key:
            breed_id = key[6:]
            selected_sludgenes.append(Sludgene.objects.get(id=breed_id))
    
    if action == "splice":
        if dominion.perk_dict.get("splices") < 1:
            messages.error(request, f"No splicing opportunities left")
            return redirect("experimentation")
            
        if len(selected_sludgenes) == 2:
            father = selected_sludgenes[0]
            mother = selected_sludgenes[1]
            
            if father.cost_type == mother.cost_type:
                child = breed_sludgenes(father, mother)
                dominion.perk_dict["splices"] -= 1
                dominion.perk_dict["last_father_id"] = father.id
                dominion.perk_dict["last_mother_id"] = mother.id
                preselect_last_parents = True
                dominion.save()
                messages.success(request, f"Created {child.name} ({child.op}/{child.dp}) - {child.perk_text} (discount: {child.discount_percent}%)")
            else:
                messages.error(request, f"Those sludgenes are from different sludgenotypes")
        else:
            messages.error(request, f"Splicing requires exactly two sludgenes")
    elif action == "spawn":
        if dominion.perk_dict["custom_units"] >= dominion.perk_dict["max_custom_units"]:
            messages.error(request, f"No custom unit slots left")
            return redirect("experimentation")
        elif len(selected_sludgenes) == 1:
            sludgene = selected_sludgenes[0]
            
            for existing_unit in Unit.objects.filter(ruler=dominion):
                if existing_unit.perk_dict.get("sludgene_sequence") == sludgene.name:
                    messages.error(request, f"Sludgene sequence already used by {existing_unit.name}")
                    return redirect("experimentation")
            
            unit = create_unit_from_sludgene(sludgene)
            unit.perk_dict["sludgene_sequence"] = sludgene.name
            unit.save()
            messages.success(request, f"Created {unit.name} from sludgene sequence {sludgene.name}")
            dominion.perk_dict["custom_units"] += 1
            dominion.save()
            return redirect("military")
        else:
            messages.error(request, f"Spawning requires exactly one sludgene")
    elif action == "delete":
        messages.success(request, f"Sludgenes deleted")
        for sludgene in selected_sludgenes:
            sludgene.delete()
    elif action == "favorites":
        messages.success(request, f"Favorites updated")
        for sludgene in selected_sludgenes:
            sludgene.is_favorite = not sludgene.is_favorite
            sludgene.save()
    else:
        messages.error(request, f"No action selected")
    
    if preselect_last_parents:
        url = reverse("experimentation")  # Use the name of your URL pattern
        redirect_url = f"{url}?preselect_last_parents=true"
        return redirect(redirect_url)
        
    return redirect(f"experimentation")