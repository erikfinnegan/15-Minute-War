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

    context = {
        "buildings_here": buildings_here,
        "building_types": player.building_types_available.all(),
        "region": region,
        "available_plots": 3 - Building.objects.filter(region=region).count(),
        "primary_terrain_available": region.primary_plots_available,
        "secondary_terrain_available": region.secondary_plots_available,
    }

    return render(request, "maingame/region_details.html", context)


@login_required
def destroy_building(request, building_id):
    building = Building.objects.get(id=building_id)
    region_id = building.region.id
    building.delete()

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

    marshaled_units = Unit.objects.filter(quantity_marshaled__gt=0)

    context = {
        "units": Unit.objects.filter(ruler=player),
        "show_cant_afford_error": show_cant_afford_error,
        "marshaled_units": marshaled_units,
    }

    return render(request, "maingame/army_training.html", context)


@login_required
def submit_training(request):
    player = Player.objects.get(associated_user=request.user)

    gold_cost = 0
    food_cost = 0
    ore_cost = 0
    lumber_cost = 0
    gem_cost = 0
    mana_cost = 0

    total_trained = 0

    for key, value in request.POST.items():
        if "train_" in key and value != "":
            unit = Unit.objects.get(id=key[6:])
            amount = int(value)
            total_trained += amount

            gold_cost += amount * unit.gold_cost
            food_cost += amount * unit.food_cost
            ore_cost += amount * unit.ore_cost
            lumber_cost += amount * unit.lumber_cost
            gem_cost += amount * unit.gem_cost
            mana_cost += amount * unit.mana_cost

    if total_trained < 1:
        messages.error(request, f"Zero units trained")
        return redirect("army_training")

    training_succeeded = True

    if gold_cost > player.gold:
        messages.error(request, f"This would cost {f'{gold_cost:,}'} gold. You have {f'{player.gold:,}'}. You're {f'{gold_cost - player.gold:,}'} short.")
        training_succeeded = False
    
    if mana_cost > player.mana:
        messages.error(request, f"This would cost {f'{mana_cost:,}'} mana. You have {f'{player.mana:,}'}. You're {f'{mana_cost - player.mana:,}'} short.")
        training_succeeded = False

    if ore_cost > player.ore:
        messages.error(request, f"This would cost {f'{ore_cost:,}'} ore. You have {f'{player.ore:,}'}. You're {f'{ore_cost - player.ore:,}'} short.")
        training_succeeded = False

    if gem_cost > player.gems:
        messages.error(request, f"This would cost {f'{gem_cost:,}'} gems. You have {f'{player.gems:,}'}. You're {f'{gem_cost - player.gems:,}'} short.")
        training_succeeded = False

    if food_cost > player.food:
        messages.error(request, f"This would cost {f'{food_cost:,}'} food. You have {f'{player.food:,}'}. You're {f'{food_cost - player.food:,}'} short.")
        training_succeeded = False

    if lumber_cost > player.lumber:
        messages.error(request, f"This would cost {f'{lumber_cost:,}'} lumber. You have {f'{player.lumber:,}'}. You're {f'{lumber_cost - player.lumber:,}'} short.")
        training_succeeded = False

    if training_succeeded:
        player.gold -= gold_cost
        player.food -= food_cost
        player.ore -= ore_cost
        player.lumber -= lumber_cost
        player.gems -= gem_cost
        player.mana -= mana_cost
        player.save()

        total_trained = 0

        for key, value in request.POST.items():
            if "train_" in key and value != "":
                unit = Unit.objects.get(id=key[6:])
                amount = int(value)
                unit.quantity_marshaled += amount
                unit.save()

        messages.success(request, f"Training of {total_trained} units successful")
    
    return redirect("army_training")


@login_required
def dispatch_to_all_regions(request, unit_id, quantity):
    player = Player.objects.get(associated_user=request.user)
    unit = Unit.objects.get(id=unit_id)

    if quantity * player.regions_ruled > unit.quantity_marshaled:
        return redirect("army_training")
    
    for region in Region.objects.filter(ruler=player):
        send_journey(player=player, unit=unit, quantity=quantity, destination=region, origin=None)

    messages.success(request, f"{quantity}x {unit.name} have begun journeys to each region")
    return redirect("army_training")


@login_required
def dispatch_to_one_region(request, unit_id, quantity, origin_id, destination_id):
    player = Player.objects.get(associated_user=request.user)
    unit = Unit.objects.get(id=unit_id)
    origin = Region.objects.get(id=origin_id)
    destination = Region.objects.get(id=destination_id)

    if quantity > unit.quantity_marshaled:
        return redirect("army_training")

    send_journey(player=player, unit=unit, quantity=quantity, destination=destination, origin=origin)

    # return HttpResponseRedirect('army_training'). 
    # And in success function, you can get that parameter: request.GET.get('status', None)

    return redirect("army_training")