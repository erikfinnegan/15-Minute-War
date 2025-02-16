import math

from django.shortcuts import render, redirect
from django.contrib import messages

from maingame.models import Dominion, Unit, Round, Resource
from maingame.utils.give_stuff import create_resource_for_dominion, give_dominion_unit


def church_affairs(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if dominion.faction_name not in ["blessed order", "fallen order"]:
        messages.error(request, f"I swear I WILL smite you")
        return redirect("buildings")
    
    if "inquisition_rate" in dominion.perk_dict and dominion.perk_dict["inquisition_rate"] > 0:
        heretics_per_tick = -1 * dominion.perk_dict["inquisition_rate"]
    else:
        heretics_per_tick = dominion.get_production("heretics")

    try:
        heretics = Resource.objects.get(ruler=dominion, name="heretics").quantity
    except:
        heretics = 0

    context = {
        "fallen_order": "fallen_order" in dominion.perk_dict,
        "do_true_inquisition": "fallen_order" in dominion.perk_dict and dominion.perk_dict["fallen_order"] == True,
        "order_cant_attack_ticks_left": dominion.perk_dict["order_cant_attack_ticks_left"],
        "heretics_per_tick": heretics_per_tick,
        "heretics": heretics,
    }
    
    return render(request, "maingame/faction_pages/church_affairs.html", context)


def submit_inquisition(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("church_affairs")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("church_affairs")
    
    dominion.perk_dict["inquisition_rate"] = math.ceil(Resource.objects.get(ruler=dominion, name="heretics").quantity / 24)
    dominion.perk_dict["order_cant_attack_ticks_left"] = 24
    dominion.save()

    messages.success(request, "The inquisition has begun.")
    return redirect("church_affairs")


def submit_true_inquisition(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("church_affairs")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("church_affairs")
    
    if "fallen_order" not in dominion.perk_dict:
        messages.error(request, f"You have much left to learn before you walk this path.")
        return redirect("church_affairs")
    
    if "faith_per_power_died" in dominion.perk_dict:
        del dominion.perk_dict["faith_per_power_died"]

    if "heretics_per_hundred_acres_per_tick" in dominion.perk_dict:
        del dominion.perk_dict["heretics_per_hundred_acres_per_tick"]

    if "inquisition_rate" in dominion.perk_dict:
        del dominion.perk_dict["inquisition_rate"]

    if "martyr_cost" in dominion.perk_dict:
        del dominion.perk_dict["martyr_cost"]

    if "corruption" in dominion.perk_dict:
        del dominion.perk_dict["corruption"]

    dominion.perk_dict["fallen_order"] = False
    dominion.faction_name = "fallen order"
    dominion.save()

    if "Penitent Engines" in dominion.learned_discoveries:
        engines = Unit.objects.get(ruler=dominion, name="Penitent Engine")
        del engines.upkeep_dict["faith"]
        engines.upkeep_dict["blasphemy"] = 1
        engines.perk_dict["casualty_multiplier"] = 0.25
        engines.name = "Demon Engine"
        engines.cost_dict = {}
        engines.is_trainable = False
        engines.save()

    if "Cathedral Titans" in dominion.learned_discoveries:
        titans = Unit.objects.get(ruler=dominion, name="Cathedral Titan")
        del titans.upkeep_dict["faith"]
        titans.upkeep_dict["gold"] = 20
        titans.name = "Oubliette Titan"
        del titans.perk_dict["casualty_multiplier"]
        titans.perk_dict["immortal"] = True
        titans.perk_dict["blasphemy_per_tick"] = 10
        titans.save()

    if "Living Saints" in dominion.learned_discoveries:
        saints = Unit.objects.get(ruler=dominion, name="Living Saint")
        del saints.upkeep_dict["faith"]
        saints.upkeep_dict["blasphemy"] = 1
        saints.name="Great Heretic"
        saints.perk_dict["immortal"] = True
        saints.save()

    blasphemy = create_resource_for_dominion("blasphemy", dominion)
    faith = Resource.objects.get(ruler=dominion, name="faith")
    heretics = Resource.objects.get(ruler=dominion, name="heretics")

    blasphemy.gain(faith.quantity)
    faith.delete()
    heretics.delete()

    brothers = Unit.objects.get(ruler=dominion, name="Blessed Brother")
    brothers.dp = -2
    brothers.perk_dict = {"immortal": True}
    brothers.upkeep_dict = {}
    brothers.is_trainable = False
    brothers.save()

    harbingers = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Harbinger"))
    give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Grisly Altar"))
    give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Chosen One"))
    martyrs = Unit.objects.get(ruler=dominion, name="Blessed Martyr")

    harbingers.gain(martyrs.quantity_total_and_paid)
    martyrs.delete()

    messages.success(request, "There's no going back now.")
    return redirect("church_affairs")


def submit_unholy_baptism(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("church_affairs")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("church_affairs")
    
    if "fallen_order" not in dominion.perk_dict:
        messages.error(request, f"You have much left to learn before you walk this path.")
        return redirect("church_affairs")
    
    try:
        anointed_ones = Unit.objects.get(ruler=dominion, name="Anointed One")
    except:
        anointed_ones = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Anointed One"))

    chosen_ones = Unit.objects.get(ruler=dominion, name="Chosen One")
    
    blasphemy = Resource.objects.get(ruler=dominion, name="blasphemy")
    conversion_max_blasphemy = int(blasphemy.quantity / 500)
    conversion_max_units = chosen_ones.quantity_at_home
    conversions = min(conversion_max_blasphemy, conversion_max_units)
    
    chosen_ones.lose(conversions)
    anointed_ones.gain(conversions)
    blasphemy.spend(conversions * 500)

    dominion.perk_dict["order_cant_attack_ticks_left"] = 13
    dominion.save()

    messages.success(request, "The baptism has begun.")
    return redirect("church_affairs")
