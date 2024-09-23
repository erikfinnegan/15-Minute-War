from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from maingame.formatters import create_or_add_to_key, get_resource_name
from maingame.models import Building, BuildingType, Player, Region, Unit, Journey, Round
from maingame.tick_processors import do_global_tick
from maingame.utils import construct_building, get_journey_output_dict, marshal_from_location, send_journey


def index(request):
    context = {
        "testcontext": "Context test successful",
    }

    return render(request, "maingame/index.html", context)


@login_required
def region(request, region_id):
    try:
        region = Region.objects.get(id=region_id)
        player = Player.objects.get(associated_user=request.user)
    except:
        return redirect("/regions")
    
    buildings_here = region.buildings_here.all().order_by("type")
    marshaled_units = Unit.objects.filter(ruler=player, quantity_marshaled__gt=0)
    
    units_here = []
    
    class UnitHere:
        def __init__(self, unit, quantity):
            self.unit = unit
            self.quantity = quantity

    for unit_id, quantity in region.units_here_dict.items():
        units_here.append(UnitHere(Unit.objects.get(id=unit_id), quantity))

    output_dict = get_journey_output_dict(player, region)

    context = {
        "is_my_region": region.ruler == player,
        "buildings_here": buildings_here,
        "building_types": BuildingType.objects.filter(ruler=player),
        "region": region,
        "available_plots": 3 - Building.objects.filter(region=region).count(),
        "primary_terrain_available": region.primary_plots_available,
        "secondary_terrain_available": region.secondary_plots_available,
        "marshaled_units": marshaled_units,
        "units_here": units_here,
        "output_dict": output_dict,
    }

    return render(request, "maingame/region_details.html", context)


@login_required
def destroy_building(request, building_id):
    player = Player.objects.get(associated_user=request.user)
    building = Building.objects.get(id=building_id)
    region_id = building.region.id

    if building.ruler == player:
        building.delete()
    else:
        messages.error(request, f"That's not your building")

    return redirect(f"/regions/{region_id}")


@login_required
def build_building(request, region_id, building_type_id, amount):
    player = Player.objects.get(associated_user=request.user)
    construct_building(player, region_id, building_type_id, amount)

    return redirect(f"/regions/{region_id}")


@login_required
def regions(request):
    player = Player.objects.get(associated_user=request.user)
    my_regions = Region.objects.filter(ruler=player)

    class OpponentsRegionsData:
        def __init__(self, ruler, regions):
            self.ruler = ruler
            self.regions = regions

    opponents_regions_data_list = []

    for opponent in Player.objects.filter(~Q(associated_user=request.user)):
        opponents_regions_data_list.append(
            OpponentsRegionsData(opponent, Region.objects.filter(ruler=opponent))
        )

    # for unit_id, quantity in region.units_here_dict.items():
        # units_here.append(UnitHere(Unit.objects.get(id=unit_id), quantity))

    context = {
        "my_regions": my_regions,
        "show_enemy_details": Round.objects.first().has_started,
        "opponents_regions_data_list": opponents_regions_data_list,
    }

    return render(request, "maingame/regions.html", context)


@login_required
def army_training(request):
    show_cant_afford_error = request.GET.get("cant_afford")
    player = Player.objects.get(associated_user=request.user)

    marshaled_units = Unit.objects.filter(ruler=player, quantity_marshaled__gt=0)

    journey_regions = []

    for region in Region.objects.filter(ruler=player):
        if Journey.objects.filter(ruler=player, destination=region).count() > 0:
            journey_regions.append({"region": region, "output_dict": get_journey_output_dict(player, region)})

    context = {
        "units": Unit.objects.filter(ruler=player),
        "show_cant_afford_error": show_cant_afford_error,
        "marshaled_units": marshaled_units,
        "journey_regions": journey_regions,
    }

    return render(request, "maingame/army_training.html", context)


@login_required
def submit_training(request):
    player = Player.objects.get(associated_user=request.user)
    total_trained = 0
    total_cost_dict = {}

    for key, string_amount in request.POST.items():
        # key is like "train_123" where 123 is the ID of the Unit
        if "train_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[6:])
            amount = int(string_amount)
            total_trained += amount

            for resource, cost in unit.cost_dict.items():
                total_of_this_resource = cost * amount
                total_cost_dict = create_or_add_to_key(total_cost_dict, resource, total_of_this_resource)

    if total_trained < 1:
        messages.error(request, f"Zero units trained")
        return redirect("army_training")

    training_succeeded = True

    for resource, amount in total_cost_dict.items():
        if player.resource_dict[resource] < amount:
            training_succeeded = False
            messages.error(request, f"This would cost {f'{amount:,}'}{resource}. You have {f'{player.resource_dict[resource]:,}'}. You're {f'{amount - player.resource_dict[resource]:,}'} short.")

    if training_succeeded:
        for resource, amount in total_cost_dict.items():
            player.resource_dict[resource] -= amount

        player.save()

        for key, string_amount in request.POST.items():
            if "train_" in key and string_amount != "":
                unit = Unit.objects.get(ruler=player, id=key[6:])
                amount = int(string_amount)
                unit.quantity_marshaled += amount
                unit.save()

        messages.success(request, f"Training of {total_trained} units successful")
    
    return redirect("army_training")


@login_required
def resources(request):
    player = Player.objects.get(associated_user=request.user)

    resources_dict = {}

    for resource in player.resource_dict:
        resources_dict[resource] = {
            "name": get_resource_name(resource),
            "produced": player.get_production(resource),
            "consumed": 0,
        }

        if resource == "🍞":
            resources_dict[resource]["consumed"] = player.get_food_consumption()
        
        resources_dict[resource]["net"] = resources_dict[resource]["produced"] - resources_dict[resource]["consumed"]

    context = {
        "resources_dict": resources_dict,
    }

    return render(request, "maingame/resources.html", context)


@login_required
def upgrades(request):
    player = Player.objects.get(associated_user=request.user)
    building_types = BuildingType.objects.filter(ruler=player)

    context = {
        "building_types": building_types,
    }

    return render(request, "maingame/upgrades.html", context)


@login_required
def upgrade_building_type(request, building_type_id):
    player = Player.objects.get(associated_user=request.user)
    building_type = BuildingType.objects.get(ruler=player, id=building_type_id)

    available_research_points = player.resource_dict["📜"]

    if available_research_points < building_type.upgrade_cost:
        messages.error(request, f"This would cost {f'{building_type.upgrade_cost:,}'}📜. You have {f'{available_research_points:,}'}. You're {f'{building_type.upgrade_cost - available_research_points:,}'} short.")
        return redirect("upgrades")

    player.resource_dict["📜"] -= building_type.upgrade_cost
    building_type.upgrades += 1
    
    if building_type.amount_produced > 0:
        building_type.amount_produced += 1
    elif building_type.defense_multiplier > 0:
        building_type. defense_multiplier += 1
    
    building_type.save()
    player.save()

    return redirect("upgrades")


@login_required
def run_tick_view(request):
    do_global_tick()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def protection_tick(request, quantity):
    if quantity < 96:
        player = Player.objects.get(associated_user=request.user)
        
        for _ in range(quantity):
            if player.protection_ticks_remaining > 0:
                player.do_tick()
                player.protection_ticks_remaining -= 1
                player.save()
    else:
        messages.error(request, f"Knock it off")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def dispatch_to_all_regions(request, unit_id, quantity):
    player = Player.objects.get(associated_user=request.user)
    unit = Unit.objects.get(ruler=player, id=unit_id)

    if quantity * player.regions_ruled > unit.quantity_marshaled:
        return redirect("army_training")
    
    for region in Region.objects.filter(ruler=player):
        send_journey(player=player, unit=unit, quantity=quantity, destination=region)

    messages.success(request, f"{quantity}x {unit.name} have begun journeys to each region")
    return redirect("army_training")


@login_required
def dispatch_to_one_region(request, region_id):
    player = Player.objects.get(associated_user=request.user)
    region = Region.objects.get(id=region_id)

    if player.protection_ticks_remaining > 0 and region.ruler != player:
        messages.error(request, "You cannot invade other regions until your protection has ended")

    total_sent = 0

    for key, value in request.POST.items():
        if "send_" in key and value != "":
            unit = Unit.objects.get(id=key[5:])
            amount = int(value)

            if amount > unit.quantity_marshaled:
                messages.error(request, f"Attempted to send {amount}x {unit} but there are only {unit.quantity_marshaled} marshaled")
                return redirect("region", region_id)

            total_sent += amount

    if total_sent < 1:
        messages.error(request, f"Zero units sent")
        return redirect("region", region_id)

    for key, value in request.POST.items():
        if "send_" in key and value != "":
            unit = Unit.objects.get(id=key[5:])
            amount = int(value)
            send_journey(player, unit, amount, region)

    messages.success(request, f"Sending {total_sent} units to {region.name}")
    
    return redirect("region", region_id)


@login_required
def marshal_from_region(request, region_id):
    player = Player.objects.get(associated_user=request.user)
    region = Region.objects.get(ruler=player, id=region_id)

    if region.ruler != player:
        messages.error(request, f"You can only marshal your own units")
        return redirect("region", region_id)

    total_marshaled = 0

    for key, value in request.POST.items():
        if "marshal_" in key and value != "":
            unit = Unit.objects.get(ruler=player, id=key[8:])
            amount = int(value)

            if amount > region.units_here_dict[str(unit.id)]:
                messages.error(request, f"Attempted to marshal {amount}x {unit} but there are only {unit.quantity_marshaled} here")
                return redirect("region", region_id)

            total_marshaled += amount

    if total_marshaled < 1:
        messages.error(request, f"Zero units marshaled")
        return redirect("region", region_id)

    for key, value in request.POST.items():
        if "marshal_" in key and value != "":
            unit = Unit.objects.get(id=key[8:], ruler=player)
            amount = int(value)
            marshal_from_location(player, unit, amount, region)

    messages.success(request, f"Marshaling {total_marshaled} units from {region.name}")
    
    return redirect("region", region_id)