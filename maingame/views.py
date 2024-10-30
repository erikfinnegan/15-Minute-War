import json
import math
import zoneinfo

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from maingame.formatters import create_or_add_to_key
from maingame.models import Building, Dominion, Unit, Battle, Round, Event, Resource, Faction, Discovery, Spell, UserSettings
from maingame.tick_processors import do_global_tick
from maingame.utils import abandon_dominion, get_grudge_bonus, initialize_dominion, prune_buildings, unlock_discovery, update_trade_prices, cast_spell


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
            "units": Unit.objects.filter(ruler=None, faction=faction)
        })

    context = {
        "factions": faction_list
    }

    return render(request, "maingame/faction_info.html", context)


def register(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        return redirect("resources")
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

    initialize_dominion(user=request.user, faction=faction, display_name=display_name)

    return redirect("buildings")


@login_required
def buildings(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    primary_resource = Resource.objects.get(ruler=dominion, name=dominion.building_primary_resource_name)
    secondary_resource = Resource.objects.get(ruler=dominion, name=dominion.building_secondary_resource_name)

    max_affordable = int(min(primary_resource.quantity / dominion.building_primary_cost, secondary_resource.quantity / dominion.building_secondary_cost))

    context = {
        "buildings": Building.objects.filter(ruler=dominion),
        "primary_resource": primary_resource,
        "secondary_resource": secondary_resource,
        "max_buildable": min(dominion.barren_acres, max_affordable),
    }
    
    return render(request, "maingame/buildings.html", context)


@login_required
def discoveries(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")

    available_discoveries = []

    for discovery_name in dominion.available_discoveries:
        available_discoveries.append(Discovery.objects.get(name=discovery_name))

    context = {
        "available_discoveries": available_discoveries,
    }
    
    return render(request, "maingame/discoveries.html", context)


@login_required
def submit_discovery(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    discovery_name = request.POST["discovery_name"]
    
    if dominion.discovery_points < 50:
        messages.error(request, f"Insufficient discovery points")
        return redirect("discoveries")
    elif not Discovery.objects.filter(name=discovery_name).exists():
        messages.error(request, f"That discovery doesn't exist")
        return redirect("discoveries")
    else:
        dominion.discovery_points -= 50
        unlock_discovery(dominion, discovery_name)

    return redirect("discoveries")


@login_required
def submit_building(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    primary_resource = Resource.objects.get(ruler=dominion, name=dominion.building_primary_resource_name)
    secondary_resource = Resource.objects.get(ruler=dominion, name=dominion.building_secondary_resource_name)
    total_built = 0

    destroy_mode = request.POST["buildOrDestroy"] == "Destroy"

    for key, string_amount in request.POST.items():
        # key is like "build_123" where 123 is the ID of the Building
        if "build_" in key and string_amount != "":
            building = Building.objects.get(id=key[6:])

            if destroy_mode:
                amount = int(string_amount)
                total_built += min(amount, building.quantity)
                building.quantity -= amount
                building.quantity = max(0, building.quantity)
                building.save()
            elif building.is_buildable:
                total_built += int(string_amount)

    if total_built < 1:
        verb = "destroyed" if destroy_mode else "built"
        messages.error(request, f"Zero buildings {verb}")
        return redirect("buildings")
    elif destroy_mode:
        messages.success(request, f"Destruction of {total_built} buildings successful")
        return redirect("buildings")
    elif total_built > dominion.barren_acres:
        messages.error(request, f"You tried to build {total_built} buildings but only have {dominion.barren_acres} acres of barren land")
        return redirect("buildings")

    building_succeeded = True

    if total_built * dominion.building_primary_cost > primary_resource.quantity:
        building_succeeded = False
        messages.error(request, f"This would cost {f'{total_built * dominion.building_primary_cost:,}'} {primary_resource.name}. You have {f'{primary_resource.quantity:,}'}.")
    elif total_built * dominion.building_secondary_cost > secondary_resource.quantity:
        building_succeeded = False
        messages.error(request, f"This would cost {f'{total_built * dominion.building_secondary_cost:,}'} {secondary_resource.name}. You have {f'{secondary_resource.quantity:,}'}.")

    if building_succeeded:
        primary_resource.quantity -= total_built * dominion.building_primary_cost
        primary_resource.save()
        secondary_resource.quantity -= total_built * dominion.building_secondary_cost
        secondary_resource.save()
        dominion.save()

        for key, string_amount in request.POST.items():
            if "build_" in key and string_amount != "":
                building = Building.objects.get(id=key[6:])
                building.quantity += int(string_amount)
                building.save()

        messages.success(request, f"Construction of {total_built} buildings successful")
    
    return redirect("buildings")


@login_required
def military(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    context = {
        # "units": Unit.objects.filter(ruler=dominion),
        "units": dominion.sorted_units
    }

    return render(request, "maingame/military.html", context)


@login_required
def submit_training(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    total_trained = 0
    total_cost_dict = {}

    for key, string_amount in request.POST.items():
        # key is like "train_123" where 123 is the ID of the Unit
        if "train_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[6:])

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
            messages.error(request, f"This would cost {f'{amount:,}'}{resource}. You have {f'{dominions_resource.quantity:,}'}. You're {f'{amount - dominions_resource.quantity:,}'} short.")

    if training_succeeded:
        for resource, amount in total_cost_dict.items():
            dominions_resource = Resource.objects.get(ruler=dominion, name=resource)
            dominions_resource.quantity -= amount
            dominions_resource.save()

        for key, string_amount in request.POST.items():
            if "train_" in key and string_amount != "":
                unit = Unit.objects.get(ruler=dominion, id=key[6:])
                amount = int(string_amount)
                unit.training_dict["12"] += amount
                unit.save()

        messages.success(request, f"Training of {total_trained} units successful")
    
    return redirect("military")


@login_required
def submit_release(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
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


@login_required
def resources(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("options")
    
    round = Round.objects.first()
    resources_dict = {}
    dominion_resource_total_dict = {}

    for resource in Resource.objects.filter(ruler=dominion):
        dominion_resource_total_dict[resource.name] = resource.quantity

        resources_dict[resource.name] = {
            "name": resource.name,
            "produced": dominion.get_production(resource.name),
            "consumed": dominion.get_consumption(resource.name),
        }

        resources_dict[resource.name]["net"] = resources_dict[resource.name]["produced"] - resources_dict[resource.name]["consumed"]

    update_trade_prices()
    trade_price_dict = round.trade_price_dict
    trade_price_data = {}

    for resource_name, price in trade_price_dict.items():
        if Resource.objects.filter(ruler=dominion, name=resource_name).exists():
            trade_price_data[resource_name] = {
                "name": Resource.objects.get(ruler=dominion, name=resource_name).name,
                "price": price,
                "difference": int((price / round.base_price_dict[resource_name]) * 100)
            }

    context = {
        "resources_dict": resources_dict,
        "trade_price_data": trade_price_data,
        "resources_dict_json": json.dumps(resources_dict),
        "dominion_resources_json": json.dumps(dominion_resource_total_dict),
        "trade_price_json": json.dumps(trade_price_dict),
        "last_sold_resource_name": Resource.objects.get(name=dominion.last_sold_resource_name, ruler=dominion).name,
        "last_bought_resource_name": Resource.objects.get(name=dominion.last_bought_resource_name, ruler=dominion).name,
    }

    return render(request, "maingame/resources.html", context)


@login_required
def trade(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    round = Round.objects.first()
    input_resource_name = request.POST["inputResource"]
    amount = int(request.POST["resourceAmount"])
    output_resource_name = request.POST["outputResource"]

    input_resource = Resource.objects.get(ruler=dominion, name=input_resource_name)
    output_resource = Resource.objects.get(ruler=dominion, name=output_resource_name)

    credit = round.trade_price_dict[input_resource.name] * amount
    payout = int(credit / round.trade_price_dict[output_resource.name])

    input_resource.quantity -= amount
    input_resource.save()

    output_resource.quantity += payout
    output_resource.save()

    round.resource_bank_dict[input_resource.name] += amount
    round.resource_bank_dict[output_resource.name] -= payout
    round.save()

    dominion.last_sold_resource_name = input_resource.name
    dominion.last_bought_resource_name = output_resource.name
    dominion.save()

    update_trade_prices()

    messages.success(request, f"Traded {amount:2,} {input_resource} for {payout:2,} {output_resource}")
    return redirect("resources")


@login_required
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


@login_required
def upgrade_building(request, building_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    building = Building.objects.get(ruler=dominion, id=building_id)
    research_resource = Resource.objects.get(ruler=dominion, name="research")

    available_research_points = research_resource.quantity

    if available_research_points < building.upgrade_cost:
        messages.error(request, f"This would cost {f'{building.upgrade_cost:,}'}research. You have {f'{available_research_points:,}'}. You're {f'{building.upgrade_cost - available_research_points:,}'} short.")
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


@login_required
def spells(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    spells = Spell.objects.filter(ruler=dominion)

    context = {
        "spells": spells,
        "mana_quantity": Resource.objects.get(ruler=dominion, name="mana").quantity,
    }

    return render(request, "maingame/spells.html", context)


@login_required
def submit_spell(request, spell_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    spell = Spell.objects.get(id=spell_id)
    mana = Resource.objects.get(ruler=dominion, name="mana")

    if spell.mana_cost > mana.quantity:
        messages.error(request, f"This would cost {f'{spell.mana_cost:,}'}mana. You have {f'{mana.quantity:,}'}. You're {f'{spell.mana_cost - mana.quantity:,}'} short.")
        return redirect("spells")
    
    cast_spell(spell)

    return redirect("spells")


@login_required
def run_tick_view(request, quantity):
    round = Round.objects.first()
    round.has_started = True
    round.save()

    for _ in range(quantity):
        do_global_tick()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def protection_tick(request, quantity):
    if quantity <= 96:
        try:
            dominion = Dominion.objects.get(associated_user=request.user)
        except:
            return redirect("register")
        
        for _ in range(quantity):
            if dominion.protection_ticks_remaining > 0:
                dominion.do_tick()
                dominion.protection_ticks_remaining -= 1
                dominion.save()
    else:
        messages.error(request, f"Knock it off")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
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
    }

    return render(request, "maingame/battle_report.html", context)


@login_required
def news(request):
    TIMEZONES_CHOICES = [tz for tz in zoneinfo.available_timezones()]
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    displayed_events = []
    
    for event in Event.objects.all().order_by('-id')[:20]:
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


@login_required
def overview(request, dominion_id):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominion = Dominion.objects.get(id=dominion_id)

    if dominion_id != my_dominion.id and dominion.protection_ticks_remaining > 0:
        return redirect("world")

    my_units = my_dominion.sorted_units

    dominion = Dominion.objects.get(id=dominion_id)
    units = dominion.sorted_units
    buildings = Building.objects.filter(ruler=dominion, quantity__gte=1)
    resources = Resource.objects.filter(ruler=dominion, quantity__gte=1)
    learned_discoveries = []

    for discovery in Discovery.objects.all():
        if discovery.name in dominion.learned_discoveries:
            learned_discoveries.append(discovery)

    if "book_of_grudges" in dominion.perk_dict and my_dominion.protection_ticks_remaining == 0 and my_dominion.id != dominion_id:
        if str(my_dominion.id) in dominion.perk_dict["book_of_grudges"]:
            dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["pages"] += 1
        else:
            dominion.perk_dict["book_of_grudges"][str(my_dominion.id)] = {}
            dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["pages"] = 1
            dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["animosity"] = 0
        
        dominion.save()

    context = {
        "dominion": dominion,
        "units": units,
        "buildings": buildings,
        "resources": resources,
        "my_units": my_units,
        "offense_multiplier": my_dominion.offense_multiplier + get_grudge_bonus(my_dominion, dominion),
        "spells": Spell.objects.filter(ruler=dominion),
        "learned_discoveries": learned_discoveries,
    }

    return render(request, "maingame/overview.html", context)


@login_required
def world(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    dominions = Dominion.objects.all().order_by('-acres')

    # If you don't have grudge values set for someone, set them now
    if "book_of_grudges" in my_dominion.perk_dict:
        for dominion in dominions:
            if str(dominion.id) not in my_dominion.perk_dict["book_of_grudges"]:
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)] = {}
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] = 0
                my_dominion.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] = 0

    context = {
        "dominions": dominions,
    }

    return render(request, "maingame/world.html", context)


@login_required
def options(request):
    try:
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("index")
    
    TIMEZONES_CHOICES = [tz for tz in zoneinfo.available_timezones()]
    themes = ["Mustard and blue", "Blood and beige", "It's a boy", "Elesh Norn", "Swampy", "OpenDominion", "ODA"]

    context = {
        "themes": themes,
        "current_display_name": user_settings.display_name,
        "timezones": TIMEZONES_CHOICES,
    }
    
    return render(request, "maingame/options.html", context)


@login_required
def submit_options(request):
    try:
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("index")
    
    user_settings.display_name = request.POST["display_name"]
    user_settings.theme = request.POST["theme"]
    user_settings.show_tutorials = "show_tutorials" in request.POST
    user_settings.use_am_pm = "use_am_pm" in request.POST
    user_settings.timezone = request.POST["timezone"]
    user_settings.save()

    return redirect("options")


@login_required
def abandon(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if "abandon" in request.POST and request.POST["confirm_abandon"] == "REALLY DO IT":
        abandon_dominion(dominion)

    return redirect("register")


@login_required
def tutorial(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")

    context = {
        "asdf": "asdf",
    }

    return render(request, "maingame/tutorial.html", context)


@login_required
def submit_invasion(request, dominion_id):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    target_dominion = Dominion.objects.get(id=dominion_id)
    round = Round.objects.first()

    if target_dominion.protection_ticks_remaining > 0 or my_dominion.protection_ticks_remaining > 0 or not round.has_started or round.has_ended:
        messages.error(request, f"Illegal invasion")
        return redirect("overview", dominion_id=dominion_id)
    
    total_units_sent = 0
    units_sent_dict = {}

    # Create a dict of the units sent
    for key, string_amount in request.POST.items():
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
                unit.quantity_at_home -= amount
                unit.save()
            else:
                messages.error(request, f"You can't send more units than you have at home.")
                return redirect("overview", dominion_id=dominion_id)

    if total_units_sent < 1:
        messages.error(request, f"Zero units sent")
        return redirect("overview", dominion_id=dominion_id)
    
    offense_sent = 0
    
    # Calculate OP
    for unit_details_dict in units_sent_dict.values():
        unit = unit_details_dict["unit"]
        quantity_sent = unit_details_dict["quantity_sent"]
        offense_sent += unit.op * quantity_sent

    offense_sent *= (my_dominion.offense_multiplier + get_grudge_bonus(my_dominion, target_dominion))

    # Determine victor
    if offense_sent >= target_dominion.defense:
        attacker_victory = True
        target_dominion.complacency = 0
        target_dominion.save()

        if "book_of_grudges" in target_dominion.perk_dict:
            if str(my_dominion.id) in target_dominion.perk_dict["book_of_grudges"]:
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["pages"] += 100
            else:
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)] = {}
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["pages"] = 100
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["animosity"] = 0
    else:
        attacker_victory = False

    battle_units_sent_dict = {}
    battle_units_defending_dict = {}

    for unit_id, data in units_sent_dict.items():
        battle_units_sent_dict[unit_id] = data["quantity_sent"]

    for unit in Unit.objects.filter(ruler=target_dominion):
        if unit.quantity_at_home > 0:
            battle_units_defending_dict[str(unit.id)] = unit.quantity_at_home
    
    battle = Battle.objects.create(
        attacker=my_dominion,
        defender=target_dominion,
        winner=my_dominion if attacker_victory else target_dominion,
        op=offense_sent,
        dp=target_dominion.defense,
        units_sent_dict=battle_units_sent_dict,
        units_defending_dict=battle_units_defending_dict,
    )

    event = Event.objects.create(
        reference_id=battle.id, 
        reference_type="battle", 
        category="Invasion",
    )
    event.notified_dominions.add(my_dominion)
    event.notified_dominions.add(target_dominion)
    target_dominion.has_unread_events = True
    target_dominion.save()

    # Determine casualty rates and handle victory triggers
    if attacker_victory:
        offensive_survival = 0.9
        defensive_survival = 0.95
        acres_conquered = int(0.06 * target_dominion.acres * (target_dominion.acres / my_dominion.acres))

        target_dominion.acres -= acres_conquered
        target_dominion.save()
        prune_buildings(target_dominion)

        my_dominion.incoming_acres_dict["12"] += acres_conquered * 2
        my_dominion.save()
        
        battle.acres_conquered = acres_conquered
        battle.save()

        # Dwarves erase their grudges for a dominion once they hit them
        if "book_of_grudges" in my_dominion.perk_dict and str(target_dominion.id) in my_dominion.perk_dict["book_of_grudges"]:
            my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["pages"] = 0
            my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["animosity"] = 0
            my_dominion.save()
    else:
        offensive_survival = 0.85

        # If you're not close, then no casualties
        if offense_sent < target_dominion.defense / 2:
            defensive_survival = 1
        else:
            defensive_survival = 0.98

    total_casualties = 0

    # Apply offensive casualties and return the survivors home
    for unit_details_dict in units_sent_dict.values():
        unit = unit_details_dict["unit"]
        quantity_sent = unit_details_dict["quantity_sent"]
        survivors = math.ceil(quantity_sent * offensive_survival)

        if "always_dies_on_offense" in unit.perk_dict:
            survivors = 0

        if "mana" not in unit.upkeep_dict and "mana" not in unit.cost_dict:
            total_casualties += (quantity_sent - survivors)

        unit.returning_dict["12"] += survivors
        unit.save()

    # Apply defensive casualties
    for unit in Unit.objects.filter(ruler=target_dominion):
        survivors = math.ceil(unit.quantity_at_home * defensive_survival)

        if "mana" not in unit.upkeep_dict and "mana" not in unit.cost_dict:
            total_casualties += (unit.quantity_at_home - survivors)

        unit.quantity_at_home = survivors
        unit.save()

    if attacker_victory and Resource.objects.filter(ruler=my_dominion, name="corpses").exists():
        my_bodies = Resource.objects.get(ruler=my_dominion, name="corpses")
        my_bodies.quantity += total_casualties
        my_bodies.save()
        battle.battle_report_notes.append(f"{my_dominion} gained {total_casualties} corpses.")
        battle.save()
    elif not attacker_victory and Resource.objects.filter(ruler=target_dominion, name="corpses").exists():
        targets_bodies = Resource.objects.get(ruler=target_dominion, name="corpses")
        targets_bodies.quantity += total_casualties
        targets_bodies.save()
        battle.battle_report_notes.append(f"{target_dominion} gained {total_casualties} corpses.")
        battle.save()

    return redirect("battle_report", battle_id=battle.id)