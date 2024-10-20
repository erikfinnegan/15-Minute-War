import json
import math
import zoneinfo

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from maingame.formatters import create_or_add_to_key
from maingame.models import Building, Player, Unit, Battle, Round, Event, Resource, Faction, Discovery, Spell
from maingame.tick_processors import do_global_tick
from maingame.utils import abandon_player, get_grudge_bonus, initialize_player, prune_buildings, unlock_discovery, update_trade_prices, cast_spell


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
        player = Player.objects.get(associated_user=request.user)
        return redirect("resources")
    except:
        pass

    TIMEZONES_CHOICES = [tz for tz in zoneinfo.available_timezones()]

    context = {
        "factions": Faction.objects.all(),
        "timezones": TIMEZONES_CHOICES,
    }

    return render(request, "maingame/register.html", context)


@login_required
def submit_register(request):
    display_name = request.POST["playerName"]
    faction = Faction.objects.get(name=request.POST["factionChoice"].lower())
    timezone = request.POST["timezone"]

    initialize_player(user=request.user, faction=faction, display_name=display_name, timezone=timezone)

    return redirect("buildings")


@login_required
def buildings(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    primary_resource = Resource.objects.get(ruler=player, name=player.building_primary_resource_name)
    secondary_resource = Resource.objects.get(ruler=player, name=player.building_secondary_resource_name)

    max_affordable = int(min(primary_resource.quantity / player.building_primary_cost, secondary_resource.quantity / player.building_secondary_cost))

    context = {
        "buildings": Building.objects.filter(ruler=player),
        "primary_resource": primary_resource,
        "secondary_resource": secondary_resource,
        "max_buildable": min(player.barren_acres, max_affordable),
    }
    
    return render(request, "maingame/buildings.html", context)


@login_required
def discoveries(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")

    available_discoveries = []

    for discovery_name in player.available_discoveries:
        available_discoveries.append(Discovery.objects.get(name=discovery_name))

    context = {
        "available_discoveries": available_discoveries,
    }
    
    return render(request, "maingame/discoveries.html", context)


@login_required
def submit_discovery(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    discovery_name = request.POST["discovery_name"]
    
    if player.discovery_points < 50:
        messages.error(request, f"Insufficient discovery points")
        return redirect("discoveries")
    elif not Discovery.objects.filter(name=discovery_name).exists():
        messages.error(request, f"That discovery doesn't exist")
        return redirect("discoveries")
    else:
        player.discovery_points -= 50
        unlock_discovery(player, discovery_name)

    return redirect("discoveries")


@login_required
def submit_building(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    primary_resource = Resource.objects.get(ruler=player, name=player.building_primary_resource_name)
    secondary_resource = Resource.objects.get(ruler=player, name=player.building_secondary_resource_name)
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
    elif total_built > player.barren_acres:
        messages.error(request, f"You tried to build {total_built} buildings but only have {player.barren_acres} acres of barren land")
        return redirect("buildings")

    building_succeeded = True

    if total_built * player.building_primary_cost > primary_resource.quantity:
        building_succeeded = False
        messages.error(request, f"This would cost {f'{total_built * player.building_primary_cost:,}'} {primary_resource.icon}. You have {f'{primary_resource.quantity:,}'}.")
    elif total_built * player.building_secondary_cost > secondary_resource.quantity:
        building_succeeded = False
        messages.error(request, f"This would cost {f'{total_built * player.building_secondary_cost:,}'} {secondary_resource.icon}. You have {f'{secondary_resource.quantity:,}'}.")

    if building_succeeded:
        primary_resource.quantity -= total_built * player.building_primary_cost
        primary_resource.save()
        secondary_resource.quantity -= total_built * player.building_secondary_cost
        secondary_resource.save()
        player.save()

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
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    print("sorted units")
    print(player.sorted_units)

    context = {
        # "units": Unit.objects.filter(ruler=player),
        "units": player.sorted_units
    }

    return render(request, "maingame/military.html", context)


@login_required
def submit_training(request):
    try:
        player = Player.objects.get(associated_user=request.user)
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
        players_resource = Resource.objects.get(ruler=player, icon=resource)

        if players_resource.quantity < amount:
            training_succeeded = False
            messages.error(request, f"This would cost {f'{amount:,}'}{resource}. You have {f'{players_resource.quantity:,}'}. You're {f'{amount - players_resource.quantity:,}'} short.")

    if training_succeeded:
        for resource, amount in total_cost_dict.items():
            players_resource = Resource.objects.get(ruler=player, icon=resource)
            players_resource.quantity -= amount
            players_resource.save()

        for key, string_amount in request.POST.items():
            if "train_" in key and string_amount != "":
                unit = Unit.objects.get(ruler=player, id=key[6:])
                amount = int(string_amount)
                unit.training_dict["12"] += amount
                unit.save()

        messages.success(request, f"Training of {total_trained} units successful")
    
    return redirect("military")


@login_required
def submit_release(request):
    try:
        player = Player.objects.get(associated_user=request.user)
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
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    round = Round.objects.first()
    resources_dict = {}
    player_resource_total_dict = {}

    for resource in Resource.objects.filter(ruler=player):
        player_resource_total_dict[resource.icon] = resource.quantity

        resources_dict[resource.icon] = {
            "name": resource.name,
            "produced": player.get_production(resource.name),
            "consumed": player.get_consumption(resource.name),
        }

        resources_dict[resource.icon]["net"] = resources_dict[resource.icon]["produced"] - resources_dict[resource.icon]["consumed"]

    update_trade_prices()
    trade_price_dict = round.trade_price_dict
    trade_price_data = {}

    for resource_name, price in trade_price_dict.items():
        if Resource.objects.filter(ruler=player, name=resource_name).exists():
            trade_price_data[resource_name] = {
                "icon": Resource.objects.get(ruler=player, name=resource_name).icon,
                "price": price,
                "difference": int((price / round.base_price_dict[resource_name]) * 100)
            }

    context = {
        "resources_dict": resources_dict,
        "trade_price_data": trade_price_data,
        "resources_dict_json": json.dumps(resources_dict),
        "player_resources_json": json.dumps(player_resource_total_dict),
        "trade_price_json": json.dumps(trade_price_dict),
        "last_sold_resource_icon": Resource.objects.get(name=player.last_sold_resource_name, ruler=player).icon,
        "last_bought_resource_icon": Resource.objects.get(name=player.last_bought_resource_name, ruler=player).icon,
    }

    return render(request, "maingame/resources.html", context)


@login_required
def trade(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    round = Round.objects.first()
    input_resource_icon = request.POST["inputResource"]
    amount = int(request.POST["resourceAmount"])
    output_resource_icon = request.POST["outputResource"]

    input_resource = Resource.objects.get(ruler=player, icon=input_resource_icon)
    output_resource = Resource.objects.get(ruler=player, icon=output_resource_icon)

    credit = round.trade_price_dict[input_resource.name] * amount
    payout = int(credit / round.trade_price_dict[output_resource.name])

    input_resource.quantity -= amount
    input_resource.save()

    output_resource.quantity += payout
    output_resource.save()

    round.resource_bank_dict[input_resource.name] += amount
    round.resource_bank_dict[output_resource.name] -= payout
    round.save()

    player.last_sold_resource_name = input_resource.name
    player.last_bought_resource_name = output_resource.name
    player.save()

    update_trade_prices()

    messages.success(request, f"Traded {amount:2,} {input_resource} for {payout:2,} {output_resource}")
    return redirect("resources")


@login_required
def upgrades(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    research_resource = Resource.objects.get(ruler=player, name="research")
    buildings = Building.objects.filter(ruler=player)

    context = {
        "buildings": buildings,
        "research_points_available": research_resource.quantity,
    }

    return render(request, "maingame/upgrades.html", context)


@login_required
def upgrade_building(request, building_id):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    building = Building.objects.get(ruler=player, id=building_id)
    research_resource = Resource.objects.get(ruler=player, name="research")

    available_research_points = research_resource.quantity

    if available_research_points < building.upgrade_cost:
        messages.error(request, f"This would cost {f'{building.upgrade_cost:,}'}📜. You have {f'{available_research_points:,}'}. You're {f'{building.upgrade_cost - available_research_points:,}'} short.")
        return redirect("upgrades")

    research_resource.quantity -= building.upgrade_cost
    research_resource.save()
    building.upgrades += 1
    
    if building.amount_produced > 0:
        building.amount_produced += 1
    elif building.defense_multiplier > 0:
        building. defense_multiplier += 1
    
    building.save()
    player.save()

    return redirect("upgrades")


@login_required
def spells(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    spells = Spell.objects.filter(ruler=player)

    context = {
        "spells": spells,
        "mana_quantity": Resource.objects.get(ruler=player, name="mana").quantity,
    }

    return render(request, "maingame/spells.html", context)


@login_required
def submit_spell(request, spell_id):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    spell = Spell.objects.get(id=spell_id)
    mana = Resource.objects.get(ruler=player, name="mana")

    if spell.mana_cost > mana.quantity:
        messages.error(request, f"This would cost {f'{spell.mana_cost:,}'}🔮. You have {f'{mana.quantity:,}'}. You're {f'{spell.mana_cost - mana.quantity:,}'} short.")
        return redirect("spells")
    
    cast_spell(spell)

    return redirect("spells")


@login_required
def run_tick_view(request, quantity):
    for _ in range(quantity):
        do_global_tick()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def protection_tick(request, quantity):
    if quantity <= 96:
        try:
            player = Player.objects.get(associated_user=request.user)
        except:
            return redirect("register")
        
        for _ in range(quantity):
            if player.protection_ticks_remaining > 0:
                player.do_tick()
                player.protection_ticks_remaining -= 1
                player.save()
    else:
        messages.error(request, f"Knock it off")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def battle_report(request, battle_id):
    try:
        player = Player.objects.get(associated_user=request.user)
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
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    displayed_events = []
    
    for event in Event.objects.all().order_by('-id')[:20]:
        displayed_events.append({
            "event": event,
            "involves_player": event.notified_players.filter(id=player.id).count() > 0,
        })

    player.has_unread_events = False
    player.save()

    context = {
        "displayed_events": displayed_events,
        "timezones": TIMEZONES_CHOICES,
    }

    return render(request, "maingame/news.html", context)


@login_required
def set_timezone(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    timezone = request.POST["timezone"]
    player.timezone = timezone
    player.save()

    messages.success(request, f"Time zone updated to {timezone}")
    
    return redirect("news")


@login_required
def overview(request, player_id):
    try:
        my_player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    player = Player.objects.get(id=player_id)

    if player_id != my_player.id and player.protection_ticks_remaining > 0:
        return redirect("world")

    my_units = my_player.sorted_units

    player = Player.objects.get(id=player_id)
    units = player.sorted_units
    buildings = Building.objects.filter(ruler=player, quantity__gte=1)
    resources = Resource.objects.filter(ruler=player, quantity__gte=1)
    learned_discoveries = []

    for discovery in Discovery.objects.all():
        if discovery.name in player.learned_discoveries:
            learned_discoveries.append(discovery)

    if "book_of_grudges" in player.perk_dict and my_player.protection_ticks_remaining == 0 and my_player.id != player_id:
        if str(my_player.id) in player.perk_dict["book_of_grudges"]:
            player.perk_dict["book_of_grudges"][str(my_player.id)]["pages"] += 1
        else:
            player.perk_dict["book_of_grudges"][str(my_player.id)] = {}
            player.perk_dict["book_of_grudges"][str(my_player.id)]["pages"] = 1
            player.perk_dict["book_of_grudges"][str(my_player.id)]["animosity"] = 0
        
        player.save()

    context = {
        "player": player,
        "units": units,
        "buildings": buildings,
        "resources": resources,
        "my_units": my_units,
        "offense_multiplier": my_player.offense_multiplier + get_grudge_bonus(my_player, player),
        "spells": Spell.objects.filter(ruler=player),
        "learned_discoveries": learned_discoveries,
    }

    return render(request, "maingame/overview.html", context)


@login_required
def world(request):
    try:
        my_player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    players = Player.objects.all().order_by('-acres')

    # If you don't have grudge values set for someone, set them now
    if "book_of_grudges" in my_player.perk_dict:
        for player in players:
            if str(player.id) not in my_player.perk_dict["book_of_grudges"]:
                my_player.perk_dict["book_of_grudges"][str(player.id)] = {}
                my_player.perk_dict["book_of_grudges"][str(player.id)]["pages"] = 0
                my_player.perk_dict["book_of_grudges"][str(player.id)]["animosity"] = 0

    context = {
        "players": players,
    }

    return render(request, "maingame/world.html", context)


@login_required
def options(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    return render(request, "maingame/options.html")


@login_required
def submit_options(request):
    try:
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if "abandon" in request.POST and request.POST["confirm_abandon"] == "DELETE ME FOREVER":
        print("ABANDON TIME")
        abandon_player(player)
    
    player.show_tutorials = "show_tutorials" in request.POST
    player.dark_mode = "dark_mode" in request.POST
    player.save()

    return redirect("options")


@login_required
def tutorial(request):
    try:
        my_player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")

    context = {
        "asdf": "asdf",
    }

    return render(request, "maingame/tutorial.html", context)


@login_required
def toggle_tutorials(request):
    try:
        my_player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    my_player.show_tutorials = not my_player.show_tutorials
    my_player.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def submit_invasion(request, player_id):
    try:
        my_player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    target_player = Player.objects.get(id=player_id)
    round = Round.objects.first()

    if target_player.protection_ticks_remaining > 0 or my_player.protection_ticks_remaining > 0 or not round.has_started or round.has_ended:
        messages.error(request, f"Illegal invasion")
        return redirect("overview", player_id=player_id)
    
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
                return redirect("overview", player_id=player_id)

    if total_units_sent < 1:
        messages.error(request, f"Zero units sent")
        return redirect("overview", player_id=player_id)
    
    offense_sent = 0
    
    # Calculate OP
    for unit_details_dict in units_sent_dict.values():
        unit = unit_details_dict["unit"]
        quantity_sent = unit_details_dict["quantity_sent"]
        offense_sent += unit.op * quantity_sent

    offense_sent *= (my_player.offense_multiplier + get_grudge_bonus(my_player, target_player))

    # Determine victor
    if offense_sent >= target_player.defense:
        attacker_victory = True
        target_player.complacency = 0
        target_player.save()

        if "book_of_grudges" in target_player.perk_dict:
            if str(my_player.id) in target_player.perk_dict["book_of_grudges"]:
                target_player.perk_dict["book_of_grudges"][str(my_player.id)]["pages"] += 100
            else:
                target_player.perk_dict["book_of_grudges"][str(my_player.id)] = {}
                target_player.perk_dict["book_of_grudges"][str(my_player.id)]["pages"] = 100
                target_player.perk_dict["book_of_grudges"][str(my_player.id)]["animosity"] = 0
    else:
        attacker_victory = False

    battle_units_sent_dict = {}
    battle_units_defending_dict = {}

    for unit_id, data in units_sent_dict.items():
        battle_units_sent_dict[unit_id] = data["quantity_sent"]

    for unit in Unit.objects.filter(ruler=target_player):
        if unit.quantity_at_home > 0:
            battle_units_defending_dict[str(unit.id)] = unit.quantity_at_home
    
    print(battle_units_defending_dict)

    battle = Battle.objects.create(
        attacker=my_player,
        defender=target_player,
        winner=my_player if attacker_victory else target_player,
        op=offense_sent,
        dp=target_player.defense,
        units_sent_dict=battle_units_sent_dict,
        units_defending_dict=battle_units_defending_dict,
    )

    event = Event.objects.create(
        reference_id=battle.id, 
        reference_type="battle", 
        icon="🗡" if attacker_victory else "🛡"
    )
    event.notified_players.add(my_player)
    event.notified_players.add(target_player)
    target_player.has_unread_events = True
    target_player.save()

    # Determine casualty rates and handle victory triggers
    if attacker_victory:
        offensive_survival = 0.9
        defensive_survival = 0.95
        acres_conquered = int(0.06 * target_player.acres * (target_player.acres / my_player.acres))

        target_player.acres -= acres_conquered
        target_player.save()
        prune_buildings(target_player)

        my_player.incoming_acres_dict["12"] += acres_conquered * 2
        my_player.save()
        
        battle.acres_conquered = acres_conquered
        battle.save()

        # Dwarves erase their grudges for a player once they hit them
        if "book_of_grudges" in my_player.perk_dict and str(target_player.id) in my_player.perk_dict["book_of_grudges"]:
            my_player.perk_dict["book_of_grudges"][str(target_player.id)]["pages"] = 0
            my_player.perk_dict["book_of_grudges"][str(target_player.id)]["animosity"] = 0
            my_player.save()
    else:
        offensive_survival = 0.85

        # If you're not close, then no casualties
        if offense_sent < target_player.defense / 2:
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

        if "🔮" not in unit.upkeep_dict and "🔮" not in unit.cost_dict:
            total_casualties += (quantity_sent - survivors)

        unit.returning_dict["12"] += survivors
        unit.save()

    # Apply defensive casualties
    for unit in Unit.objects.filter(ruler=target_player):
        survivors = math.ceil(unit.quantity_at_home * defensive_survival)

        if "🔮" not in unit.upkeep_dict and "🔮" not in unit.cost_dict:
            total_casualties += (unit.quantity_at_home - survivors)

        unit.quantity_at_home = survivors
        unit.save()

    if attacker_victory and Resource.objects.filter(ruler=my_player, icon="🪦").exists():
        my_bodies = Resource.objects.get(ruler=my_player, icon="🪦")
        my_bodies.quantity += total_casualties
        my_bodies.save()
    elif not attacker_victory and Resource.objects.filter(ruler=target_player, icon="🪦").exists():
        targets_bodies = Resource.objects.get(ruler=target_player, icon="🪦")
        targets_bodies.quantity += total_casualties
        targets_bodies.save()

    return redirect("battle_report", battle_id=battle.id)