from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from maingame.models import Building, BuildingType, Player, Region, Unit, Journey
from maingame.utils import send_journey


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

    context = {
        "buildings_here": buildings_here,
        "building_types": player.building_types_available.all(),
        "region": region,
        "available_plots": 3 - Building.objects.filter(region=region).count(),
        "primary_terrain_available": region.primary_plots_available,
        "secondary_terrain_available": region.secondary_plots_available,
        "marshaled_units": marshaled_units,
        "units_here": units_here,
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
    for _ in range(amount):
        building_type = BuildingType.objects.get(id=building_type_id)
        region = Region.objects.get(id=region_id)
        built_on_ideal_terrain = False

        if building_type.ideal_terrain == region.primary_terrain and region.primary_plots_available:
            built_on_ideal_terrain = True
        elif building_type.ideal_terrain == region.secondary_terrain and region.secondary_plots_available:
            built_on_ideal_terrain = True

        Building.objects.create(
            ruler=Player.objects.get(associated_user=request.user),
            type=building_type,
            region=region,
            built_on_ideal_terrain=built_on_ideal_terrain,
        )

    return redirect(f"/regions/{region_id}")


@login_required
def regions(request):
    player = Player.objects.get(associated_user=request.user)
    regions = Region.objects.filter(ruler=player)

    context = {
        "regions": regions,
    }

    return render(request, "maingame/regions.html", context)


@login_required
def army_training(request):
    show_cant_afford_error = request.GET.get("cant_afford")
    player = Player.objects.get(associated_user=request.user)

    marshaled_units = Unit.objects.filter(ruler=player, quantity_marshaled__gt=0)

    context = {
        "units": Unit.objects.filter(ruler=player),
        "show_cant_afford_error": show_cant_afford_error,
        "marshaled_units": marshaled_units,
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

                if resource in total_cost_dict:
                    total_cost_dict[resource] += total_of_this_resource
                else:
                    total_cost_dict[resource] = total_of_this_resource

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

    # for resource in player.resource_dict:
	# get production, get consumption, calculate net

    context = {
        "placeholder": "test",
    }

    return render(request, "maingame/resources.html", context)


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
    region = Region.objects.get(ruler=player, id=region_id)

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