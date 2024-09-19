from random import randint

from maingame.models import Terrain, Unit, BuildingType, Player, Faction, Region, Journey


def get_unit_gold_cost(unit: Unit, discount=0):
    base_value = (unit.dp * 1.2) + (unit.op * 0.8)
    base_gold = 10 * base_value
    scaled_gold = base_gold ** 1.2
    scaled_gold = scaled_gold * ((100-discount)/100)
    rounded_gold = 25 * round(scaled_gold/25)

    return rounded_gold


def generate_random_unit(terrain: Terrain):
    power_level = min(randint(1,4), randint(1,4))

    base_power = 6
    
    for _ in range(power_level):
        base_power *= randint(1, 4)

    op = int(terrain.unit_op_dp_ratio * base_power)
    dp = int((2 - terrain.unit_op_dp_ratio) * base_power)

    new_unit = Unit.objects.create(
        name=f"Testunit{randint(1,10000)}",
        op=op,
        dp=dp,
    )

    return new_unit


def generate_bespoke_unit(name, op, dp, secondary_resource, faction=None):
    unit = Unit.objects.create(name=name, op=op, dp=dp)
    unit.gold_cost = get_unit_gold_cost(unit)

    secondary_building_ticks = unit.gold_cost / 533
    secondary_resource_production_building = BuildingType.objects.get(resource_produced=secondary_resource)
    secondary_cost_amount = secondary_building_ticks * secondary_resource_production_building.amount_produced
    secondary_cost_amount = 5 * round(secondary_cost_amount/5)

    if secondary_resource == "ore":
        unit.ore_cost = secondary_cost_amount
    elif secondary_resource == "food":
        unit.food_cost = secondary_cost_amount
    elif secondary_resource == "gems":
        unit.gem_cost = secondary_cost_amount
    elif secondary_resource == "mana":
        unit.mana_cost = secondary_cost_amount
    elif secondary_resource == "lumber":
        unit.lumber_cost = secondary_cost_amount

    if faction:
        unit.faction_for_which_is_default = faction

    unit.save()

    return unit


def assign_faction(player: Player, faction: Faction):
    player.faction = faction
    
    for unit in Unit.objects.filter(faction_for_which_is_default=faction):
        players_unit = unit
        players_unit.pk = None
        players_unit.ruler = player
        players_unit.save()

    for building_type in faction.starter_building_types.all():
        new_building_type = building_type
        new_building_type.pk = None
        new_building_type.save()
        player.building_types_available.add(new_building_type)

    player.save()

def send_journey(player: Player, unit: Unit, quantity: int, destination: Region, origin: Region=None):
    try:
        journey = Journey.objects.get(ruler=player, unit=unit, destination=destination, origin=origin)
        journey.quantity += quantity
        journey.save()
    except:
        Journey.objects.create(ruler=player, unit=unit, quantity=quantity, destination=destination, origin=origin)
        
    unit.quantity_marshaled -= quantity
    unit.save()
