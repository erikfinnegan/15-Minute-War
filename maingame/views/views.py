import json
import zoneinfo

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse

from maingame.models import Building, Dominion, MechModule, Unit, Battle, Round, Event, Resource, Faction, Discovery, Spell, UserSettings, Theme
from maingame.utils.invasion import does_x_of_unit_break_defender, get_op_and_dp_left
from maingame.utils.utils import create_unit_dict, get_acres_conquered, update_available_discoveries


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


def buildings(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
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
        if discovery.name not in dominion.available_discoveries and discovery.name not in dominion.learned_discoveries and dominion.faction_name not in discovery.not_for_factions:
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


def military(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    try:
        hammerers = Unit.objects.get(ruler=dominion, name="Hammerer")
        hammerer_count = hammerers.quantity_at_home
    except:
        hammerer_count = 0
    
    context = {
        "units": dominion.sorted_units,
        "hammerer_count": hammerer_count,
    }

    return render(request, "maingame/military.html", context)


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
    }

    return render(request, "maingame/resources.html", context)


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


def battle_report(request, battle_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    battle = Battle.objects.get(id=battle_id)

    context = {
        "battle": battle,
        "units_sent_dict": battle.units_sent_dict,
        "units_defending_dict": battle.units_defending_dict,
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
            
    repeated_discoveries = []
    for discovery in set(dominion.learned_discoveries):
        discovery_name = discovery
        
        if dominion.learned_discoveries.count(discovery_name) > 1:
            discovery_name += f" x{dominion.learned_discoveries.count(discovery_name)}"
            repeated_discoveries.append(discovery_name)
        
    resources_dict = {}

    for resource in Resource.objects.filter(ruler=dominion):
        # if not resource.name == "corpses":
        resources_dict[resource.name] = {
            "name": resource.name,
            "quantity": resource.quantity,
            "produced": dominion.get_production(resource.name),
            "consumed": dominion.get_consumption(resource.name),
            "resource": resource,
        }

        resources_dict[resource.name]["net"] = resources_dict[resource.name]["produced"] - resources_dict[resource.name]["consumed"]

        dominion.save()

    battles_with_this_dominion = Battle.objects.filter(attacker=dominion) | Battle.objects.filter(defender=dominion)
    
    try:
        red_beret = Unit.objects.get(ruler=my_dominion, name="Red Beret")
        show_red_beret_recall = dominion.strid == red_beret.perk_dict["subverted_target_id"]
    except:
        show_red_beret_recall = False

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
        "repeated_discoveries": repeated_discoveries,
        "acres_conquered": get_acres_conquered(my_dominion, dominion),
        "battles_with_this_dominion": battles_with_this_dominion.order_by("-timestamp"),
        "modules": MechModule.objects.filter(ruler=dominion),
        "show_red_beret_recall": show_red_beret_recall,
    }

    return render(request, "maingame/overview.html", context)


def world(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominions = Dominion.objects.filter(is_abandoned=False).order_by('protection_ticks_remaining', '-acres')
    dominion_list = list(dominions)
    
    def sort_dominions(dominion: Dominion):
        if dominion.protection_ticks_remaining > 0:
            return 0
        
        sort_val = dominion.acres * 1000000000
        sort_val += dominion.incoming_acres * 100000
        sort_val += dominion.defense
        return sort_val
        
    dominion_list.sort(key=sort_dominions, reverse=True)
    my_units = my_dominion.sorted_units

    # If you don't have grudge values set for someone, set them now
    if "book_of_grudges" in my_dominion.perk_dict:
        for dominion in dominions:
            if str(dominion.id) not in my_dominion.perk_dict["book_of_grudges"]:
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)] = {}
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] = 0
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] = 0

    land_conquered_dict = {}
    lowest_defense_larger_than_you = 99999999999
    lowest_defense_in_game = 99999999999
    largest_with_incoming = my_dominion

    for dominion in dominions:
        land_conquered_dict[str(dominion.id)] = get_acres_conquered(my_dominion, dominion)

        if dominion.acres >= my_dominion.acres and dominion.is_oop:
            lowest_defense_larger_than_you = min(dominion.defense, lowest_defense_larger_than_you)

        if dominion.is_oop:
            lowest_defense_in_game = min(dominion.defense, lowest_defense_in_game)

        if dominion.acres_with_incoming > largest_with_incoming.acres_with_incoming:
            largest_with_incoming = dominion
            
    plunder_unit_ids = []
    
    if my_dominion.faction_name == "aethertide corsairs":
        for unit in Unit.objects.filter(ruler=my_dominion):
            if unit.name in ["Pirate Crew", "Realitylubber Crew"]:
                plunder_unit_ids.append(unit.id)

    context = {
        "dominions": dominion_list,
        "minimum_defense_left": my_dominion.acres * 5,
        "my_units": my_units,
        "base_offense_multiplier": my_dominion.offense_multiplier,
        "land_conquered_dict": json.dumps(land_conquered_dict),
        "raw_defense": my_dominion.raw_defense,
        "defense_multiplier": my_dominion.defense_multiplier,
        "lowest_defense_larger_than_you": lowest_defense_larger_than_you,
        "lowest_defense_in_game": lowest_defense_in_game,
        "largest_with_incoming": largest_with_incoming,
        "is_debug": False,
        "plunder_unit_ids": plunder_unit_ids,
    }

    return render(request, "maingame/world.html", context)


def world_debug(request):
    ##### DEBUG
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominions = Dominion.objects.filter(is_abandoned=False).order_by('protection_ticks_remaining', '-acres')
    dominion_list = list(dominions)
    
    ##### DEBUG
    
    def sort_dominions(dominion: Dominion):
        if dominion.protection_ticks_remaining > 0:
            return 0
        
        sort_val = dominion.score * (10 ** 100)
        sort_val += dominion.acres * (10 ** 10)
        sort_val += dominion.incoming_acres * (10 ** 5)
        sort_val += dominion.defense
        return sort_val
        
    dominion_list.sort(key=sort_dominions, reverse=True)
    my_units = my_dominion.sorted_units
    
    ##### DEBUG

    # If you don't have grudge values set for someone, set them now
    if "book_of_grudges" in my_dominion.perk_dict:
        for dominion in dominions:
            if str(dominion.id) not in my_dominion.perk_dict["book_of_grudges"]:
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)] = {}
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] = 0
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] = 0

    land_conquered_dict = {}
    lowest_defense_larger_than_you = 99999999999
    lowest_defense_in_game = 99999999999
    largest_with_incoming = my_dominion
    
    ##### DEBUG

    for dominion in dominions:
        land_conquered_dict[str(dominion.id)] = get_acres_conquered(my_dominion, dominion)

        if dominion.acres >= my_dominion.acres and dominion.is_oop:
            lowest_defense_larger_than_you = min(dominion.defense, lowest_defense_larger_than_you)

        if dominion.is_oop:
            lowest_defense_in_game = min(dominion.defense, lowest_defense_in_game)

        if dominion.acres_with_incoming > largest_with_incoming.acres_with_incoming:
            largest_with_incoming = dominion

    ##### DEBUG

    context = {
        "dominions": dominion_list,
        "minimum_defense_left": my_dominion.acres * 5,
        "my_units": my_units,
        "base_offense_multiplier": my_dominion.offense_multiplier,
        "land_conquered_dict": json.dumps(land_conquered_dict),
        "raw_defense": my_dominion.raw_defense,
        "defense_multiplier": my_dominion.defense_multiplier,
        "lowest_defense_larger_than_you": lowest_defense_larger_than_you,
        "lowest_defense_in_game": lowest_defense_in_game,
        "largest_with_incoming": largest_with_incoming,
        "is_debug": True,
    }
    
    ##### DEBUG

    return render(request, "maingame/world.html", context)
    ##### DEBUG


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


def tutorial(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")

    context = {
        "asdf": "asdf",
    }

    return render(request, "maingame/tutorial.html", context)


def calculate_op(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominion_id = request.GET.get("target_dominion_id")
    is_infiltration = "do_infiltration" in request.GET
    is_plunder = "do_plunder" in request.GET

    # Not sure how to get the form-wide hx-trigger to fire on repeated use of the checkbox - it only picks up on the first.

    units_sent_dict, _ = create_unit_dict(request.GET, "send_")
    target_dominion = Dominion.objects.filter(id=dominion_id).first()
    op_sent, dp_left, raw_dp_left = get_op_and_dp_left(units_sent_dict, attacker=my_dominion, defender=target_dominion, is_infiltration=is_infiltration, is_plunder=is_plunder)

    larger_enemy_has_lower_defense = False
    left_lowest_defense = True

    for dominion in Dominion.objects.all():
        if dominion.defense < dp_left and dominion.acres > my_dominion.acres:
            larger_enemy_has_lower_defense = True
        
        if dominion.defense < dp_left:
            left_lowest_defense = False

    invalid_invasion = False if is_infiltration else (not target_dominion or op_sent < target_dominion.defense or dp_left < my_dominion.acres * 5)
    
    # Build the dict that powers the win button. If this is slow, delete this part
    units_needed_to_break_list = []
    if target_dominion:
        for unit in Unit.objects.filter(ruler=my_dominion, op__gt=0):
            unit_sent_entry = units_sent_dict.get(str(unit.id))
            quantity_queued = 0 if unit_sent_entry == None else unit_sent_entry.get("quantity_sent")
            def check(x):
                return does_x_of_unit_break_defender(x, unit, units_sent_dict, attacker=my_dominion, defender=target_dominion, is_plunder=is_plunder)

            if not check(unit.quantity_at_home):
                units_needed_to_break_list.append({
                    "id": unit.id,
                    "quantity_needed": unit.quantity_at_home,
                })
            elif check(quantity_queued):
                units_needed_to_break_list.append({
                    "id": unit.id,
                    "quantity_needed": quantity_queued,
                })
            else:
                mod_op = unit.op * my_dominion.offense_multiplier
                
                if is_plunder:
                    mod_op *= 2
                
                test_quantity = min(unit.quantity_at_home, int((target_dominion.defense - op_sent) / mod_op) + 1 + quantity_queued)
                test_quantity = max(0, test_quantity)
                keep_going = True
                counter = 0

                while keep_going and counter < 1000:
                    counter += 1
                    if check(test_quantity) and not check(test_quantity - 1):
                        keep_going = False
                        units_needed_to_break_list.append({
                            "id": unit.id,
                            "quantity_needed": test_quantity,
                        })
                    elif check(test_quantity):
                        test_quantity -= 1
                    else:
                        test_quantity += 1

    # End win button stuff
    
    try:
        invasion_consequences = target_dominion.invasion_consequences
    except:
        invasion_consequences = ""
        
    try:
        if target_dominion.red_beret_target_id == my_dominion.strid:
            red_beret_op_reduction = target_dominion.perk_dict["infiltration_dict"][my_dominion.strid]
        else:
            red_beret_op_reduction = 0
    except:
        red_beret_op_reduction = 0

    context = {
        "op": op_sent,
        "dp": target_dominion.defense if target_dominion else 0,
        "dp_left": dp_left,
        "raw_dp_left": raw_dp_left,
        "invalid_invasion": invalid_invasion,
        "larger_enemy_has_lower_defense": larger_enemy_has_lower_defense,
        "left_lowest_defense": left_lowest_defense,
        "is_infiltration": is_infiltration,
        "units_needed_to_break_list": units_needed_to_break_list,
        "invasion_consequences": invasion_consequences,
        "red_beret_op_reduction": red_beret_op_reduction,
    }
        
    return render(request, "maingame/components/op_vs_dp.html", context)


def calculate_acres_from_invasion(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    target_id = request.GET.get("target_dominion_id")
    is_plunder = "do_plunder" in request.GET
    acres_gained = 0
    
    try:
        target_dominion = Dominion.objects.get(id=target_id)
        acres_gained = 1 if is_plunder else get_acres_conquered(attacker=my_dominion, target=target_dominion)
    except:
        pass
    
    return HttpResponse(f"{acres_gained}")