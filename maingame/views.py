import json
import math
from random import randint
import random
import zoneinfo

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from maingame.formatters import create_or_add_to_key, get_sludgeling_name
from maingame.models import Artifact, Building, Dominion, Unit, Battle, Round, Event, Resource, Faction, Discovery, Spell, UserSettings, Theme
from maingame.tick_processors import do_global_tick
from maingame.utils.dominion_controls import initialize_dominion, abandon_dominion, delete_dominion
from maingame.utils.give_stuff import create_resource_for_dominion, give_dominion_unit
from maingame.utils.invasion import do_gsf_infiltration, do_invasion, get_op_and_dp_left
from maingame.utils.utils import do_quest, get_acres_conquered, get_grudge_bonus, get_highest_op_quested, round_x_to_nearest_y, unlock_discovery, cast_spell, update_available_discoveries


def index(request):
    context = {
        "testcontext": "Context test successful",
    }

    return render(request, "maingame/index.html", context)


def faction_info(request):
    faction_list = []
    
    for faction in Faction.objects.all():
        faction_list.append({
            "faction": faction,
            "units": Unit.objects.filter(ruler=None, faction=faction),
            "discoveries": Discovery.objects.filter(required_faction_name=faction.name)
        })

    context = {
        "factions": faction_list
    }

    return render(request, "maingame/faction_info.html", context)


@login_required
def register(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        return redirect("buildings")
    except:
        pass

    context = {
        "factions": Faction.objects.all(),
    }

    return render(request, "maingame/register.html", context)


@login_required
def submit_register(request):
    display_name = request.POST["dominionName"]
    faction = Faction.objects.get(name=request.POST["factionChoice"].lower())

    if Dominion.objects.filter(name=display_name).exists():
        messages.error(request, "A dominion with that name already exists")
        return redirect("register")

    initialize_dominion(user=request.user, faction=faction, display_name=display_name)

    return redirect("buildings")


def buildings(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    # primary_resource = Resource.objects.get(ruler=dominion, name=dominion.building_primary_resource_name)
    # secondary_resource = Resource.objects.get(ruler=dominion, name=dominion.building_secondary_resource_name)
    # max_affordable = int(min(primary_resource.quantity / dominion.building_primary_cost, secondary_resource.quantity / dominion.building_secondary_cost))

    resources_dict = {}

    for resource in Resource.objects.filter(ruler=dominion):
        if not resource.name == "corpses":
            resources_dict[resource.name] = {
                "name": resource.name,
                "produced": dominion.get_production(resource.name),
                "consumed": dominion.get_consumption(resource.name),
            }

            resources_dict[resource.name]["net"] = resources_dict[resource.name]["produced"] - resources_dict[resource.name]["consumed"]

    context = {
        "resources_dict": resources_dict,
        "buildings": Building.objects.filter(ruler=dominion),
    }
    
    return render(request, "maingame/buildings.html", context)


def discoveries(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    new_discoveries_message = update_available_discoveries(dominion)
    dominion.save()

    if new_discoveries_message:
        messages.success(request, f"New discoveries unlocked: {new_discoveries_message}")

    available_discoveries = []

    for discovery_name in dominion.available_discoveries:
        available_discoveries.append(Discovery.objects.get(name=discovery_name))

    depth = ""

    if "mining_depth" in dominion.perk_dict:
        mining_depth = dominion.perk_dict["mining_depth"]
        depth = f"{mining_depth:2,} torchbrights"

    future_discoveries = []

    for discovery in Discovery.objects.all():
        if discovery.name not in dominion.available_discoveries and discovery.name not in dominion.learned_discoveries:
            if not discovery.required_faction_name or discovery.required_faction_name == dominion.faction_name:
                and_requirements_left = []
                or_requirements_left = []
                
                if discovery.required_discoveries:                    
                    for requirement_name in discovery.required_discoveries:
                        if requirement_name not in dominion.learned_discoveries:
                            and_requirements_left.append(requirement_name)

                if discovery.required_discoveries_or:
                    for requirement_name in discovery.required_discoveries_or:
                        if requirement_name not in dominion.learned_discoveries:
                            or_requirements_left.append(requirement_name)

                requirement_string = ""

                if len(or_requirements_left) == 1:
                    requirement_string = or_requirements_left[0]
                elif len(or_requirements_left) > 1:
                    requirement_string = f"one of {', '.join(or_requirements_left)}"

                if len(and_requirements_left) == 1:
                    requirement_string = and_requirements_left[0]
                elif len(and_requirements_left) > 1:
                    requirement_string = f"{', '.join(and_requirements_left)}"

                if "mining_depth" in discovery.required_perk_dict:
                    required_depth = discovery.required_perk_dict["mining_depth"]
                    requirement_string += f"mining depth {int(required_depth):2,} torchbrights"

                future_discoveries.append(
                    {
                        "discovery": discovery,
                        "requirement_string": requirement_string,
                    }
                )

    context = {
        "available_discoveries": available_discoveries,
        "future_discoveries": future_discoveries,
        "depth": depth,
    }
    
    return render(request, "maingame/discoveries.html", context)


def submit_discovery(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("discoveries")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("discoveries")
    
    discovery_name = request.POST["discovery_name"]

    if user_settings.tutorial_step < 999 and discovery_name != "Palisades":
        messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
        return redirect("discoveries")
    
    if dominion.discovery_points < 50:
        messages.error(request, f"Insufficient discovery points")
        return redirect("discoveries")
    elif not Discovery.objects.filter(name=discovery_name).exists():
        messages.error(request, f"That discovery doesn't exist")
        return redirect("discoveries")
    elif dominion.faction_name in Discovery.objects.get(name=discovery_name).not_for_factions:
        messages.error(request, f"Your faction doesn't have access to that discovery")
        return redirect("discoveries")
    else:
        dominion.discovery_points -= 50
        new_discoveries_message = unlock_discovery(dominion, discovery_name)
        messages.success(request, f"Discovered {discovery_name}")
        
        if new_discoveries_message:
            messages.success(request, f"New discoveries unlocked: {new_discoveries_message}")

    return redirect("discoveries")


def submit_building(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("buildings")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("buildings")
    
    user_settings = UserSettings.objects.get(associated_user=dominion.associated_user)

    total_new_percent = 0

    for building in Building.objects.filter(ruler=dominion):
        if request.POST.get(f"build_{building.id}") != "":
            string_percent = request.POST.get(f"build_{building.id}")
            total_new_percent += int(string_percent)

            if user_settings.tutorial_step == 1:
                if building.name == "farm" and int(string_percent) != 5:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "quarry" and int(string_percent) != 45:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "lumberyard" and int(string_percent) != 11:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "school" and int(string_percent) != 39:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "tower" and int(string_percent) != 0:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")

    if total_new_percent != 100:
        messages.error(request, f"Building allocation must add up to exactly 100%")
        return redirect("buildings")
    
    for building in Building.objects.filter(ruler=dominion):
        if request.POST.get(f"build_{building.id}") != "":
            string_percent = request.POST.get(f"build_{building.id}")
            building.percent_of_land = int(string_percent)
        else:
            building.percent_of_land = 0

        building.save()

    # for key, string_percent in request.POST.items():
    #     if "build_" in key and string_percent != "":
    #         building = Building.objects.get(id=key[6:])
    #         building.percent_of_land = int(string_percent)
    #         building.save()

    messages.success(request, f"Building allocation successful")
    
    return redirect("buildings")


def military(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    context = {
        "units": dominion.sorted_units
    }

    return render(request, "maingame/military.html", context)


def submit_training(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("military")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("military")
    
    total_trained = 0
    total_cost_dict = {}

    for key, string_amount in request.POST.items():
        # key is like "train_123" where 123 is the ID of the Unit
        if "train_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[6:])

            if user_settings.tutorial_step < 999:
                if user_settings.tutorial_step <= 5:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                if unit.name == "Stoneshield" and int(string_amount) != 500 and user_settings.tutorial_step <= 6:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                elif unit.name == "Hammerer" and int(string_amount) != 720 and user_settings.tutorial_step <= 7:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                elif unit.name == "Palisade" and int(string_amount) != 147 and user_settings.tutorial_step <= 9:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                

            if unit.is_trainable:
                amount = int(string_amount)
                total_trained += amount

                for resource, cost in unit.cost_dict.items():
                    total_of_this_resource = cost * amount
                    total_cost_dict = create_or_add_to_key(total_cost_dict, resource, total_of_this_resource)
            else:
                messages.error(request, f"Knock it off")
                return redirect("military")

    if total_trained < 1:
        messages.error(request, f"Zero units trained")
        return redirect("military")

    training_succeeded = True

    for resource, amount in total_cost_dict.items():
        dominions_resource = Resource.objects.get(ruler=dominion, name=resource)

        if dominions_resource.quantity < amount:
            training_succeeded = False
            messages.error(request, f"This would cost {f'{amount:,}'} {resource}. You have {f'{dominions_resource.quantity:,}'}. You're {f'{amount - dominions_resource.quantity:,}'} short.")

    if training_succeeded:
        for resource, amount in total_cost_dict.items():
            dominions_resource = Resource.objects.get(ruler=dominion, name=resource)
            dominions_resource.quantity -= amount
            dominions_resource.save()

        for key, string_amount in request.POST.items():
            if "train_" in key and string_amount != "":
                unit = Unit.objects.get(ruler=dominion, id=key[6:])
                amount = int(string_amount)

                if "unit_training_time" in dominion.perk_dict:
                    unit_training_time = dominion.perk_dict["unit_training_time"]
                    print("unit_training_time", unit_training_time)
                    unit.training_dict[unit_training_time] += amount
                else:
                    print("else")
                    unit.training_dict["12"] += amount

                unit.save()

        messages.success(request, f"Training of {total_trained} units successful")
    
    return redirect("military")


def submit_release(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("military")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("military")
    
    total_released = 0

    for key, string_amount in request.POST.items():
        # key is like "release_123" where 123 is the ID of the Unit
        if "release_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[8:])
            amount = int(string_amount)

            if total_released > unit.quantity_at_home:
                messages.error(request, f"You can't release more units than you have at home.")
                return redirect("military")

            unit.quantity_at_home = max(0, unit.quantity_at_home - amount)
            unit.save()
            total_released += amount

    if total_released < 1:
        messages.error(request, f"Zero units released")
        return redirect("military")

    messages.success(request, f"{total_released} units released")

    return redirect("military")


def resources(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    round = Round.objects.first()
    resources_dict = {}
    dominion_resource_total_dict = {}

    for resource in Resource.objects.filter(ruler=dominion):
        if not resource.name == "corpses":
            dominion_resource_total_dict[resource.name] = resource.quantity

            # resources_dict[resource.name] = {
            #     "name": resource.name,
            #     "produced": dominion.get_production(resource.name),
            #     "consumed": dominion.get_consumption(resource.name),
            # }

            # resources_dict[resource.name]["net"] = resources_dict[resource.name]["produced"] - resources_dict[resource.name]["consumed"]

    trade_price_dict = round.trade_price_dict
    trade_price_data = {}
    my_tradeable_price_data = {}

    for resource_name, price in trade_price_dict.items():
        trade_price_data[resource_name] = {
            "name": resource_name,
            "price": price,
            "difference": int((price / round.base_price_dict[resource_name]) * 100)
        }

        if Resource.objects.filter(ruler=dominion, name=resource_name).exists():
            my_tradeable_price_data[resource_name] = {
            "name": resource_name,
            "price": price,
            "difference": int((price / round.base_price_dict[resource_name]) * 100)
        }

    context = {
        "resources_dict": resources_dict,
        "trade_price_data": trade_price_data,
        "my_tradeable_price_data": my_tradeable_price_data,
        "resources_dict_json": json.dumps(resources_dict),
        "dominion_resources_json": json.dumps(dominion_resource_total_dict),
        "trade_price_json": json.dumps(trade_price_dict),
        "last_sold_resource_name": dominion.last_sold_resource_name,
        "last_bought_resource_name": dominion.last_bought_resource_name,
    }

    return render(request, "maingame/resources.html", context)


def trade(request):
    messages.error(request, f"Trading has been disabled.")
    return redirect("buildings")

    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("buildings")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("buildings")
    
    try:
        input_resource_name = request.POST["inputResource"]
        amount = int(request.POST["resourceAmount"])
        output_resource_name = request.POST["outputResource"]
    except:
        messages.error(request, f"Please ensure your trade resources are selected properly")
        return redirect("buildings")
    
    round = Round.objects.first()

    if not Resource.objects.filter(ruler=dominion, name=input_resource_name).exists() or not Resource.objects.filter(ruler=dominion, name=output_resource_name).exists():
        messages.error(request, f"You don't have access to that resource")
        return redirect("buildings")
    elif input_resource_name == output_resource_name:
        messages.error(request, f"You can't trade a resource for itself")
        return redirect("buildings")

    untradable_resources = ["corpses", "faith", "mithril"]

    if input_resource_name in untradable_resources or output_resource_name in untradable_resources:
        messages.error(request, f"You can't trade that resource.")
        return redirect("buildings")

    input_resource = Resource.objects.get(ruler=dominion, name=input_resource_name)
    output_resource = Resource.objects.get(ruler=dominion, name=output_resource_name)

    if amount > input_resource.quantity:
        messages.error(request, f"You can't trade more {input_resource_name} than you have")
        return redirect("buildings")

    credit = round.trade_price_dict[input_resource.name] * amount
    payout = int((credit / round.trade_price_dict[output_resource.name]) * 0.9)

    input_resource.quantity -= amount
    input_resource.save()

    output_resource.quantity += payout
    output_resource.save()

    input_total_production = 0
    output_total_production = 0
    dominion_count = 0

    for dominion in Dominion.objects.all():
        input_total_production += dominion.get_production(input_resource_name)
        output_total_production += dominion.get_production(output_resource_name)
        dominion_count += 1

    round.resource_bank_dict[input_resource.name] += min(amount, 24 * int(input_total_production / dominion_count))
    round.resource_bank_dict[output_resource.name] -= min(amount, 24 * int(output_total_production / dominion_count))
    round.save()

    dominion.last_sold_resource_name = input_resource.name
    dominion.last_bought_resource_name = output_resource.name
    dominion.save()

    messages.success(request, f"Traded {amount:2,} {input_resource.name} for {payout:2,} {output_resource.name}")
    return redirect("buildings")


def upgrades(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    research_resource = Resource.objects.get(ruler=dominion, name="research")
    buildings = Building.objects.filter(ruler=dominion)

    context = {
        "buildings": buildings,
        "research_points_available": research_resource.quantity,
    }

    return render(request, "maingame/upgrades.html", context)


def upgrade_building(request, building_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("upgrades")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("upgrades")
    
    building = Building.objects.get(ruler=dominion, id=building_id)
    research_resource = Resource.objects.get(ruler=dominion, name="research")
    available_research_points = research_resource.quantity

    if user_settings.tutorial_step == 4 and building.name != "quarry":
        messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
        return redirect("upgrades")

    if available_research_points < building.upgrade_cost:
        messages.error(request, f"This would cost {f'{building.upgrade_cost:,}'} research. You have {f'{available_research_points:,}'}. You're {f'{building.upgrade_cost - available_research_points:,}'} short.")
        return redirect("upgrades")

    research_resource.quantity -= building.upgrade_cost
    research_resource.save()
    building.upgrades += 1
    
    if building.amount_produced > 0:
        building.amount_produced += 1
    elif building.defense_multiplier > 0:
        building. defense_multiplier += 1
    
    building.save()
    dominion.save()

    return redirect("upgrades")


def spells(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    spells = Spell.objects.filter(ruler=dominion)

    context = {
        "spells": spells,
        "mana_quantity": Resource.objects.get(ruler=dominion, name="mana").quantity,
        "dominions": Dominion.objects.filter(is_abandoned=False).order_by('protection_ticks_remaining', '-acres'),
    }

    return render(request, "maingame/spells.html", context)


def submit_spell(request, spell_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    target_dominion = None
    spell = Spell.objects.get(id=spell_id)
    mana = Resource.objects.get(ruler=dominion, name="mana")
    round = Round.objects.first()

    try:
        dominion_id = request.POST["target_dominion_id"]
        target_dominion = Dominion.objects.get(id=dominion_id)

        if not target_dominion.is_oop or not dominion.is_oop or not round.has_started or round.has_ended or target_dominion.is_abandoned:
            messages.error(request, f"Illegal target")
            return redirect("spells")
    except:
        pass

    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("spells")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("spells")

    if spell.mana_cost > mana.quantity:
        messages.error(request, f"This would cost {f'{spell.mana_cost:,}'} mana. You have {f'{mana.quantity:,}'}. You're {f'{spell.mana_cost - mana.quantity:,}'} short.")
        return redirect("spells")
    
    if spell.cooldown_remaining > 0:
        messages.error(request, f"This spell is still on cooldown.")
        return redirect("spells")
    
    cast_spell(spell, target_dominion)

    messages.success(request, f"Cast {spell.name}")
    return redirect("spells")


def run_tick_view(request, quantity):
    if request.user.username != "test":
        messages.error(request, f"Ticky tick tick")
        return redirect("buildings")

    round = Round.objects.first()
    round.has_started = True
    round.save()

    for _ in range(quantity):
        do_global_tick()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def protection_tick(request, quantity):
    if quantity <= 96:
        try:
            dominion = Dominion.objects.get(associated_user=request.user)
            user_settings = UserSettings.objects.get(associated_user=request.user)
        except:
            return redirect("register")
        
        if user_settings.tutorial_step == 1:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step == 2 and dominion.protection_ticks_remaining - quantity != 71:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step == 3 and quantity != 12:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step == 10 and dominion.protection_ticks_remaining - quantity < 1:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step < 999 and user_settings.tutorial_step not in [1, 2, 3, 5, 10, 11]:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            if user_settings.tutorial_step in [4]:
                return redirect("upgrades")
            elif user_settings.tutorial_step in [6, 7, 10]:
                return redirect("military")
            elif user_settings.tutorial_step in [8]:
                return redirect("discoveries")
            else:
                return redirect("buildings")
        
        print("user_settings.tutorial_step", user_settings.tutorial_step)
        
        if dominion.protection_ticks_remaining - quantity < 12:
            forgot_units = True

            for unit in Unit.objects.filter(ruler=dominion):
                if unit.quantity_at_home + unit.quantity_in_training > 0:
                    forgot_units = False

            if forgot_units:
                messages.error(request, f"You may not leave protection without units and they take 12 ticks to train. You'll want at least a few hundred total defense.")
            else:
                for _ in range(quantity):
                    if dominion.protection_ticks_remaining > 0:
                        dominion.do_tick()
                        dominion.protection_ticks_remaining -= 1
                        dominion.save()
        else:
            for _ in range(quantity):
                if dominion.protection_ticks_remaining > 0:
                    dominion.do_tick()
                    dominion.protection_ticks_remaining -= 1
                    dominion.save()
    else:
        messages.error(request, f"Knock it off")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def protection_restart(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    display_name = dominion.name
    faction = Faction.objects.get(name=dominion.faction_name)

    delete_dominion(dominion)
    initialize_dominion(user=request.user, faction=faction, display_name=display_name)

    return redirect("buildings")


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


def battle_report(request, battle_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    battle = Battle.objects.get(id=battle_id)

    units_sent_dict = {}
    units_defending_dict = {}

    for unit_id, quantity in battle.units_sent_dict.items():
        unit = Unit.objects.get(id=unit_id)
        units_sent_dict[unit.name] = quantity

    for unit_id, quantity in battle.units_defending_dict.items():
        unit = Unit.objects.get(id=unit_id)
        units_defending_dict[unit.name] = quantity

    context = {
        "battle": battle,
        "units_sent_dict": units_sent_dict,
        "units_defending_dict": units_defending_dict,
        "attacker": battle.attacker,
        "defender": battle.defender,
    }

    return render(request, "maingame/battle_report.html", context)


def news(request):
    TIMEZONES_CHOICES = [tz for tz in zoneinfo.available_timezones()]
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    displayed_events = []
    
    for event in Event.objects.all().order_by('-id')[:50]:
        displayed_events.append({
            "event": event,
            "involves_dominion": event.notified_dominions.filter(id=dominion.id).count() > 0,
        })

    dominion.has_unread_events = False
    dominion.save()

    context = {
        "displayed_events": displayed_events,
        "timezones": TIMEZONES_CHOICES,
    }

    return render(request, "maingame/news.html", context)


def overview(request, dominion_id):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominion = Dominion.objects.get(id=dominion_id)

    if dominion_id != my_dominion.id and dominion.protection_ticks_remaining > 0:
        return redirect("world")

    dominion = Dominion.objects.get(id=dominion_id)
    units = dominion.sorted_units
    buildings = Building.objects.filter(ruler=dominion, percent_of_land__gte=1)
    resources = Resource.objects.filter(ruler=dominion)
    learned_discoveries = []

    for discovery in Discovery.objects.all():
        if discovery.name in dominion.learned_discoveries:
            learned_discoveries.append(discovery)

    resources_dict = {}

    for resource in Resource.objects.filter(ruler=dominion):
        # if not resource.name == "corpses":
        resources_dict[resource.name] = {
            "name": resource.name,
            "quantity": resource.quantity,
            "produced": dominion.get_production(resource.name),
            "consumed": dominion.get_consumption(resource.name),
        }

        resources_dict[resource.name]["net"] = resources_dict[resource.name]["produced"] - resources_dict[resource.name]["consumed"]

        dominion.save()

    battles_with_this_dominion = Battle.objects.filter(attacker=dominion) | Battle.objects.filter(defender=dominion)

    context = {
        "dominion": dominion,
        "other_dominions": Dominion.objects.filter(~Q(id=dominion.id), is_abandoned=False, protection_ticks_remaining=0).order_by('protection_ticks_remaining', '-acres'),
        "units": units,
        "buildings": buildings,
        "resources": resources,
        "resources_dict": resources_dict,
        "raw_defense": my_dominion.raw_defense,
        "defense_multiplier": my_dominion.defense_multiplier,
        "minimum_defense_left": my_dominion.acres * 5,
        "spells": Spell.objects.filter(ruler=dominion),
        "learned_discoveries": learned_discoveries,
        "acres_conquered": get_acres_conquered(my_dominion, dominion),
        "battles_with_this_dominion": battles_with_this_dominion.order_by("-timestamp"),
    }

    return render(request, "maingame/overview.html", context)


def world(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominions = Dominion.objects.filter(is_abandoned=False).order_by('protection_ticks_remaining', '-acres')

    my_units = my_dominion.sorted_units

    # If you don't have grudge values set for someone, set them now
    if "book_of_grudges" in my_dominion.perk_dict:
        for dominion in dominions:
            if str(dominion.id) not in my_dominion.perk_dict["book_of_grudges"]:
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)] = {}
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] = 0
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] = 0

    offense_multiplier_dict = {}
    offense_bonus_dict = {}
    current_defense_dict = {}
    land_conquered_dict = {}
    artifact_count_dict = {}
    bonus_steal_op_dict = {}
    lowest_defense_larger_than_you = 99999999999
    lowest_defense_in_game = 99999999999
    largest_with_incoming = my_dominion

    for dominion in dominions:
        if "book_of_grudges" in my_dominion.perk_dict:
            offense_multiplier_dict[str(dominion.id)] = my_dominion.offense_multiplier + get_grudge_bonus(my_dominion, dominion)
        else:
            offense_multiplier_dict[str(dominion.id)] = my_dominion.offense_multiplier

        if "infiltration_dict" in my_dominion.perk_dict and dominion.strid in my_dominion.perk_dict["infiltration_dict"]:
            offense_bonus_dict[dominion.strid] = my_dominion.perk_dict["infiltration_dict"][dominion.strid]
        else:
            offense_bonus_dict[dominion.strid] = 0

        if dominion.protection_ticks_remaining > 0:
            current_defense_dict[str(dominion.id)] = False
        else:
            current_defense_dict[str(dominion.id)] = dominion.defense

        land_conquered_dict[str(dominion.id)] = get_acres_conquered(my_dominion, dominion)
        artifact_count_dict[str(dominion.id)] = dominion.artifact_count

        if dominion.acres >= my_dominion.acres and dominion.is_oop:
            lowest_defense_larger_than_you = min(dominion.defense, lowest_defense_larger_than_you)

        if dominion.is_oop:
            lowest_defense_in_game = min(dominion.defense, lowest_defense_in_game)

        if dominion.acres_with_incoming > largest_with_incoming.acres_with_incoming:
            largest_with_incoming = dominion

    for unit in my_units:
        if "op_bonus_percent_for_stealing_artifacts" in unit.perk_dict:
            bonus_steal_op_dict[str(unit.id)] = unit.perk_dict["op_bonus_percent_for_stealing_artifacts"]

    context = {
        "dominions": dominions,
        "minimum_defense_left": my_dominion.acres * 5,
        "my_units": my_units,
        "base_offense_multiplier": my_dominion.offense_multiplier,
        "offense_multiplier_dict": json.dumps(offense_multiplier_dict),
        "offense_bonus_dict": json.dumps(offense_bonus_dict),
        "current_defense_dict": json.dumps(current_defense_dict),
        "land_conquered_dict": json.dumps(land_conquered_dict),
        "artifact_count_dict": json.dumps(artifact_count_dict),
        "bonus_steal_op_dict": json.dumps(bonus_steal_op_dict),
        "raw_defense": my_dominion.raw_defense,
        "defense_multiplier": my_dominion.defense_multiplier,
        "lowest_defense_larger_than_you": lowest_defense_larger_than_you,
        "lowest_defense_in_game": lowest_defense_in_game,
        "highest_op_quested": get_highest_op_quested(),
        "largest_with_incoming": largest_with_incoming,
    }

    return render(request, "maingame/world.html", context)


def options(request):
    try:
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("index")
    
    TIMEZONES_CHOICES = [tz for tz in zoneinfo.available_timezones()]
    # themes = ["Mustard and blue", "Blood and beige", "It's a boy", "Elesh Norn", "Swampy", "OpenDominion", "ODA"]
    current_theme = user_settings.theme_model

    try:
        my_theme = Theme.objects.get(creator_user_settings_id=user_settings.id)
    except:
        my_theme = Theme.objects.get(name="OpenDominion")

    context = {
        "themes": Theme.objects.all(),
        "my_theme": my_theme,
        "current_theme": current_theme,
        "current_display_name": user_settings.display_name,
        "juicy_target_threshold": user_settings.juicy_target_threshold,
        "timezones": TIMEZONES_CHOICES,
    }
    
    return render(request, "maingame/options.html", context)


def submit_options(request):
    try:
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("index")
    
    user_settings.display_name = request.POST["display_name"]
    user_settings.use_am_pm = "use_am_pm" in request.POST
    user_settings.timezone = request.POST["timezone"]
    user_settings.is_tutorial = "tutorial_mode" in request.POST
    user_settings.hide_zero_resources = "hide_zero_resources" in request.POST
    selected_theme = Theme.objects.get(id=request.POST["theme"])
    user_settings.juicy_target_threshold = request.POST["juicy_target_threshold"]

    header_background = request.POST["header_background"]
    header_text = request.POST["header_text"]
    base_background = request.POST["base_background"]
    base_text = request.POST["base_text"]
    card_background = request.POST["card_background"]
    card_text = request.POST["card_text"]
    input_background = request.POST["input_background"]
    input_text = request.POST["input_text"]

    try:
        my_theme = Theme.objects.get(creator_user_settings_id=user_settings.id)
    except:
        my_theme = Theme.objects.create(
            name=f"{user_settings.display_name}'s Theme",
            creator_user_settings_id=user_settings.id,
            base_background=base_background,
            base_text=base_text,
            header_background=header_background,
            header_text=header_text,
            card_background=card_background,
            card_text=card_text,
            input_background=input_background,
            input_text=input_text,   
        )

    if (
        user_settings.theme_model == selected_theme and
        (
            header_background != selected_theme.header_background or
            header_text != selected_theme.header_text or
            base_background != selected_theme.base_background or
            base_text != selected_theme.base_text or
            card_background != selected_theme.card_background or
            card_text != selected_theme.card_text or
            input_background != selected_theme.input_background or
            input_text != selected_theme.input_text
        )
    ):
        my_theme.header_background = header_background
        my_theme.header_text = header_text
        my_theme.base_background = base_background
        my_theme.base_text = base_text
        my_theme.card_background = card_background
        my_theme.card_text = card_text
        my_theme.input_background = input_background
        my_theme.input_text = input_text
        my_theme.save()
        user_settings.theme_model = my_theme
    else:
        user_settings.theme_model = selected_theme

    user_settings.save()
    messages.success(request, "Options saved")
    return redirect("options")


def abandon(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("overview", dominion.id)
    
    if "abandon" in request.POST and request.POST["confirm_abandon"] == "REALLY DO IT":
        if Round.objects.first().has_started:
            abandon_dominion(dominion)
        else:
            delete_dominion(dominion)

        return redirect("register")

    return redirect("overview", dominion.id)


def tutorial(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")

    context = {
        "asdf": "asdf",
    }

    return render(request, "maingame/tutorial.html", context)


def church_affairs(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if dominion.faction_name not in ["blessed order", "fallen order"]:
        messages.error(request, f"I swear I WILL smite you")
        return redirect("buildings")
    
    if dominion.perk_dict["inquisition_rate"] > 0:
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
    
    dominion.perk_dict["fallen_order"] = False
    dominion.faction_name = "fallen order"
    dominion.save()

    blasphemy = create_resource_for_dominion("blasphemy", dominion)
    faith = Resource.objects.get(ruler=dominion, name="faith")
    heretics = Resource.objects.get(ruler=dominion, name="heretics")

    blasphemy.quantity = faith.quantity
    blasphemy.save()
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

    harbingers.quantity_at_home += martyrs.quantity_total_and_paid
    harbingers.save()
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

    chosen_ones.quantity_at_home -= conversions
    chosen_ones.save()

    anointed_ones.quantity_at_home += conversions
    anointed_ones.save()

    blasphemy.quantity -= conversions * 500
    blasphemy.save()

    dominion.perk_dict["order_cant_attack_ticks_left"] = 13
    dominion.save()

    messages.success(request, "The baptism has begun.")
    return redirect("church_affairs")


def experimentation(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")

    if dominion.faction_name != "sludgeling":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    research_cost = int(dominion.perk_dict["experiment_cost_dict"]["research_per_acre"] * dominion.acres)
    sludge_cost = int(dominion.perk_dict["experiment_cost_dict"]["sludge_per_acre"] * dominion.acres)

    experimental_units = []

    for unit in Unit.objects.filter(ruler=dominion):
        if "sludge" in unit.cost_dict:
            experimental_units.append(unit)

    latest_experiment_unit = Unit.objects.filter(id=dominion.perk_dict["latest_experiment_id"]).first()
    
    context = {
        "research_cost": research_cost,
        "sludge_cost": sludge_cost,
        "allow_new_experiments": dominion.perk_dict["custom_units"] < dominion.perk_dict["max_custom_units"],
        "latest_experiment": dominion.perk_dict["latest_experiment"],
        "latest_experiment_unit": latest_experiment_unit,
        "experimental_units": experimental_units,
        "has_experimental_units": dominion.perk_dict["custom_units"] > 0,
    }
    
    return render(request, "maingame/faction_pages/experimentation.html", context)


def generate_experiment(request):
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
    
    experiment_research_cost = int(dominion.perk_dict["experiment_cost_dict"]["research_per_acre"] * dominion.acres)
    experiment_sludge_cost = int(dominion.perk_dict["experiment_cost_dict"]["sludge_per_acre"] * dominion.acres)

    players_research = Resource.objects.get(ruler=dominion, name="research")
    players_sludge = Resource.objects.get(ruler=dominion, name="sludge")

    if dominion.perk_dict["free_experiments"] == 0:
        if experiment_research_cost > players_research.quantity or experiment_sludge_cost > players_sludge.quantity:
            messages.error(request, f"You can't afford this experiment")
            return redirect("experimentation")
    
    try:
        old_experiment = Unit.objects.get(id=dominion.perk_dict["latest_experiment_id"])
        old_experiment.delete()
    except:
        pass
    
    if dominion.perk_dict["free_experiments"] == 0:
        players_research.quantity -= experiment_research_cost
        players_research.save()

        players_sludge.quantity -= experiment_sludge_cost
        players_sludge.save()
    else:
        dominion.perk_dict["free_experiments"] -= 1
        dominion.save()
    
    past_experiments = dominion.perk_dict["experiments_done"]

    low_gold_cost = False
    low_sludge_cost = False
    low_upkeep = False
    high_op = False
    high_dp = False

    bonus_roll = randint(1,6)
    low_gold_cost = bonus_roll == 1
    low_sludge_cost = bonus_roll == 2
    low_upkeep = bonus_roll == 3
    high_op = bonus_roll == 4
    high_dp = bonus_roll == 5

    if past_experiments >= randint(1, 100):
        second_bonus_roll = randint(1,5)
        low_gold_cost = second_bonus_roll == 1 or low_gold_cost
        low_sludge_cost = second_bonus_roll == 2 or low_sludge_cost
        low_upkeep = second_bonus_roll == 3 or low_upkeep
        high_op = second_bonus_roll == 4 or high_op
        high_dp = second_bonus_roll == 5 or high_dp

    malus_roll = randint(1,6)
    high_gold_cost = malus_roll == 1
    high_sludge_cost = malus_roll == 2
    high_upkeep = malus_roll == 3
    low_op = malus_roll == 4
    low_dp = malus_roll == 5

    if high_gold_cost and low_gold_cost:
        high_gold_cost = False
        low_gold_cost = False

    if high_sludge_cost and low_sludge_cost:
        high_sludge_cost = False
        low_sludge_cost = False

    if high_upkeep and low_upkeep:
        high_upkeep = False
        low_upkeep = False

    if high_op and low_op:
        high_op = False
        low_op = False

    if high_dp and low_dp:
        high_dp = False
        low_dp = False

    min_roll_for_extra_power = 1

    for _ in range(past_experiments):
            min_roll_for_extra_power += (100 - min_roll_for_extra_power) / 75

    min_roll_for_extra_power = int(min_roll_for_extra_power)

    op = randint(1,10)
    extra_op = randint(1,2) == 1

    if extra_op and past_experiments >= 10:
        roll = randint(min_roll_for_extra_power, 100)

        while roll >= 100 and extra_op:
            op += randint(1, 4)
            roll = randint(min_roll_for_extra_power, 100)
            extra_op = randint(1,2) == 1

    dp = randint(1,10)
    extra_dp = randint(1,2) == 1

    if extra_dp and past_experiments >= 10:
        roll = randint(min_roll_for_extra_power, 100)

        while roll >= 100 and extra_dp:
            dp += randint(1, 4)
            roll = randint(min_roll_for_extra_power, 100)
            extra_dp = randint(1,2) == 1

    if high_op:
        op *= 2
    elif low_op:
        op = int(op/2)
    
    if high_dp:
        dp *= 2
    elif low_dp:
        dp = int(dp/2)

    perk_dict = {}
    has_perks = False

    if "Speedlings" in dominion.learned_discoveries and randint(1,100) <= 33:
        perk_dict["returns_in_ticks"] = 8
        has_perks = True
    
    # Toughlings and Cheaplings modify the same perk, so we randomize which order to check in because we're too lazy to do this intelligently
    if randint(1,2) == 1:
        if "Cheaplings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 2
            has_perks = True

        if "Toughlings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 0.5
            has_perks = True
    else:
        if "Toughlings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 0.5
            has_perks = True

        if "Cheaplings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 2
            has_perks = True

    cost_type = random.choice(["gold", "other", "hybrid"])
    cost_basis_power = max(op * 1.3, dp)
    is_offensive_unit = cost_basis_power != dp

    goldunit_gold_cost = (cost_basis_power * 300) - 600
    goldunit_sludge_cost = cost_basis_power * 70 * 1.5
    otherunit_sludge_cost = (cost_basis_power * 6 * 70) - (10 * 70)

    if cost_basis_power < 3:
        goldunit_gold_cost = cost_basis_power * 100
        otherunit_sludge_cost = cost_basis_power * 186

    if cost_type == "gold":
        gold_cost = goldunit_gold_cost
        sludge_cost = goldunit_sludge_cost
    elif cost_type == "other":
        gold_cost = 0
        sludge_cost = otherunit_sludge_cost
    else:
        gold_cost = int(goldunit_gold_cost / 2)
        sludge_cost = int((goldunit_sludge_cost + otherunit_sludge_cost) / 2)

    dont_divide_by_zero = 1 if dp == 0 else dp
    bad_turtle_multiplier = (op / 200) / dont_divide_by_zero

    if op > (dp * 2):
        gold_cost *= 1 - (bad_turtle_multiplier)

    multiplier = randint(1,15)
    high_mult = 1 + (multiplier/100)
    low_mult = 1 - (multiplier/100)

    if high_gold_cost:
        gold_cost = int(gold_cost * high_mult)
    elif low_gold_cost:
        gold_cost = int(gold_cost * low_mult)

    if high_sludge_cost:
        sludge_cost = int(sludge_cost * high_mult)
    elif low_sludge_cost:
        sludge_cost = int(sludge_cost * low_mult)

    if "returns_in_ticks" in perk_dict:
        multiplier_base = randint(10, 20) / 100
        gold_cost *= 1 + multiplier_base
        sludge_cost *= 1 + multiplier_base

    if "casualty_multiplier" in perk_dict:
        casualty_based_multiplier = 1

        if perk_dict["casualty_multiplier"] == 2:
            if is_offensive_unit:
                dp_op_ratio = dp / op
                base_discount = int(randint(40, 50) * (1 - dp_op_ratio))
                casualty_based_multiplier = min((1 - (base_discount / 100)), randint(90, 95))
            else:
                casualty_based_multiplier = randint(90, 95) / 100
        elif perk_dict["casualty_multiplier"] == 0.5:
            if is_offensive_unit:
                casualty_based_multiplier = 1 + randint(20, 30) / 100
            else:
                casualty_based_multiplier = 1 + randint(5, 10) / 100

        gold_cost *= casualty_based_multiplier
        sludge_cost *= casualty_based_multiplier

    # No more cost modifiers after this. It's time to start rounding off.
    if gold_cost > 1000:
        gold_cost = round_x_to_nearest_y(gold_cost, 50)
    else:
        gold_cost = round_x_to_nearest_y(gold_cost, 25)

    if sludge_cost > 1000:
        sludge_cost = round_x_to_nearest_y(sludge_cost, 50)
    else:
        sludge_cost = round_x_to_nearest_y(sludge_cost, 25)

    gold_cost = int(gold_cost)
    sludge_cost = int(sludge_cost)

    if high_upkeep:
        if randint(1,2) == 1:
            upkeep_dict = {
                "gold": 4,
                "food": 1,
            }
        else:
            upkeep_dict = {
                "gold": 3,
                "food": 3,
            }
    elif low_upkeep:
        if randint(1,2) == 1:
            upkeep_dict = {
                "gold": 2,
                "food": 1,
                "sludge": 1,
            }
        else:
            upkeep_dict = {
                "gold": 3,
            }
    else:
        upkeep_dict = {
                "gold": 3,
                "food": 1,
            }
    
    current_names = []

    for unit in Unit.objects.filter(ruler=dominion):
        current_names.append(unit.name)

    name = get_sludgeling_name()

    while name in current_names:
        name = get_sludgeling_name()

    cost_per_op = int(((gold_cost * 1.08) + sludge_cost) / max(op, 1))
    cost_per_dp = int(((gold_cost * 1.08) + sludge_cost) / max(dp, 1))

    op_per_normalized_upkeep = (op * 3) / upkeep_dict["gold"]
    dp_per_normalized_upkeep = (dp * 3) / upkeep_dict["gold"]

    if gold_cost == 0:
        cost_dict = {
            "sludge": sludge_cost,
        }
    else:
        cost_dict = {
            "gold": gold_cost,
            "sludge": sludge_cost,
        }

    timer_template = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
    }

    latest_experiment = Unit.objects.create(
        name=name,
        op=op,
        dp=dp,
        cost_dict=cost_dict,
        upkeep_dict=upkeep_dict,
        perk_dict=perk_dict,
        training_dict=timer_template,
        returning_dict=timer_template,
    )

    dominion.perk_dict["latest_experiment_id"] = latest_experiment.id

    dominion.perk_dict["latest_experiment"] = {
        "should_display": True,
        "name": name,
        "op": op,
        "dp": dp,
        "cost_dict": cost_dict,
        "upkeep_dict": upkeep_dict,
        "perk_dict": perk_dict,
        "has_perks": has_perks,
        "cost_per_op": cost_per_op,
        "cost_per_dp": cost_per_dp,
        "op_per_normalized_upkeep": op_per_normalized_upkeep,
        "dp_per_normalized_upkeep": dp_per_normalized_upkeep,
    }

    dominion.perk_dict["experiments_done"] += 1
    dominion.save()

    return redirect("experimentation")


def approve_experiment(request):
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
    elif dominion.perk_dict["custom_units"] >= dominion.perk_dict["max_custom_units"]:
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    dominion.perk_dict["latest_experiment"]["should_display"] = False
    dominion.perk_dict["custom_units"] += 1
    dominion.save()

    try:
        old_experiment = Unit.objects.get(id=dominion.perk_dict["latest_experiment_id"])
        old_experiment.delete()
    except:
        pass

    unit_data = dominion.perk_dict["latest_experiment"]

    timer_template = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
    }

    Unit.objects.create(
        name=unit_data["name"],
        op=unit_data["op"],
        dp=unit_data["dp"],
        cost_dict=unit_data["cost_dict"],
        upkeep_dict=unit_data["upkeep_dict"],
        perk_dict=unit_data["perk_dict"],
        ruler=dominion,
        training_dict=timer_template,
        returning_dict=timer_template,
    )

    return redirect("experimentation")


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

    gold_refund = 0
    sludge_refund = 0

    if "gold" in unit.cost_dict:
        gold_refund = int(unit.quantity_at_home * unit.cost_dict["gold"] * dominion.perk_dict["recycling_refund"])

    if "sludge" in unit.cost_dict:
        sludge_refund = int(unit.quantity_at_home * unit.cost_dict["sludge"] * dominion.perk_dict["recycling_refund"])
    
    gold = Resource.objects.get(ruler=dominion, name="gold")
    gold.quantity += gold_refund
    gold.save()

    sludge = Resource.objects.get(ruler=dominion, name="sludge")
    sludge.quantity += sludge_refund
    sludge.save()

    messages.success(request, f"Terminated the {unit.name} experiment, regained {gold_refund:2,} gold and {sludge_refund:2,} sludge from recycling {unit.quantity_at_home:2,} units")

    unit.ruler = None
    unit.save()

    dominion.perk_dict["custom_units"] -= 1
    dominion.save()
    
    return redirect("experimentation")


def other_head(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if dominion.faction_name != "biclops":
        messages.error(request, f"You don't have access to this page")
        return redirect("buildings")
    
    return render(request, "maingame/faction_pages/other_head.html")


def submit_other_head(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("other_head")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("other_head")
    
    if dominion.faction_name != "biclops" or "partner_attack_on_sight" not in dominion.perk_dict:
        messages.error(request, f"You don't have access to this page")
        return redirect("buildings")
    
    dominion.perk_dict["partner_attack_on_sight"] = "partner_attack_on_sight" in request.POST
    dominion.save()
    
    messages.success(request, "Scheming with your other head successful")
    return redirect("other_head")


def calculate_op(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominion_id = request.GET.get("target_dominion_id")
    is_infiltration = "do_infiltration" in request.GET

    # Not sure how to get the form-wide hx-trigger to fire on repeated use of the checkbox - it only picks up on the first.

    total_units_sent = 0
    units_sent_dict = {}
    
    # Create a dict of the units sent
    for key, string_amount in request.GET.items():
        # key is like "send_123" where 123 is the ID of the Unit
        if "send_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[5:])
            amount = int(string_amount)

            if amount <= unit.quantity_at_home:
                total_units_sent += amount
                units_sent_dict[str(unit.id)] = {
                    "unit": unit,
                    "quantity_sent": amount,
                }
    
    target_dominion = Dominion.objects.filter(id=dominion_id).first()
    op_sent, dp_left = get_op_and_dp_left(units_sent_dict, my_dominion, target_dominion, is_infiltration)

    larger_enemy_has_lower_defense = False
    left_lowest_defense = True

    for dominion in Dominion.objects.all():
        if dominion.defense < dp_left and dominion.acres > my_dominion.acres:
            larger_enemy_has_lower_defense = True
        
        if dominion.defense < dp_left:
            left_lowest_defense = False

    invalid_invasion = False if is_infiltration else (not target_dominion or op_sent < target_dominion.defense or dp_left < my_dominion.acres * 5)

    context = {
        "op": op_sent,
        "dp": target_dominion.defense if target_dominion else 0,
        "dp_left": dp_left,
        "invalid_invasion": invalid_invasion,
        "larger_enemy_has_lower_defense": larger_enemy_has_lower_defense,
        "left_lowest_defense": left_lowest_defense,
        "is_infiltration": is_infiltration,
    }
        
    return render(request, "maingame/components/op_vs_dp.html", context)


def submit_invasion(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    round = Round.objects.first()
    dominion_id = request.POST["target_dominion_id"]
    this_is_infiltration = "do_infiltration" in request.POST
    
    if round.has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("world")
    
    if round.is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("world")
    
    if not my_dominion.can_attack:
        messages.error(request, f"You can't attack right now")
        return redirect("world")
    
    if dominion_id == "0":
        messages.error(request, f"No target selected")
        return redirect("world")
    
    total_units_sent = 0
    units_sent_dict = {}

    # Create a dict of the units sent
    for key, string_amount in request.POST.items():
        # key is like "send_123" where 123 is the ID of the Unit
        if "send_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[5:])
            amount = int(string_amount)

            if 0 < amount <= unit.quantity_at_home:
                total_units_sent += amount
                units_sent_dict[str(unit.id)] = {
                    "unit": unit,
                    "quantity_sent": amount,
                }
            elif dominion_id == "quest" and "always_dies_on_offense" in unit.perk_dict:
                messages.error(request, f"You can't send units that always die on offense on quests.")
                return redirect("world")
            elif amount == 0:
                pass
            elif amount < 0:
                messages.error(request, f"You can't send negative units.")
                return redirect("world")
            else:
                messages.error(request, f"You can't send more units than you have at home.")
                return redirect("world")

    if total_units_sent < 1:
        messages.error(request, f"Zero units sent")
        return redirect("world")

    target_dominion = Dominion.objects.get(id=dominion_id)
    
    if target_dominion.protection_ticks_remaining > 0 or my_dominion.protection_ticks_remaining > 0 or not round.has_started or round.has_ended or target_dominion.is_abandoned:
        messages.error(request, f"Illegal invasion")
        return redirect("world")

    if this_is_infiltration:
        success, message = do_gsf_infiltration(units_sent_dict, my_dominion, target_dominion)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("world")
    else:
        battle_id, message = do_invasion(units_sent_dict, my_dominion, target_dominion)

        if battle_id == 0:
            messages.error(request, message)
            return redirect("world")

        return redirect("battle_report", battle_id=battle_id)
    
    return redirect("world")