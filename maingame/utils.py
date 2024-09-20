from random import randint

from maingame.models import Terrain, Unit, BuildingType, Player, Faction, Region, Journey, Building


def assign_faction(player: Player, faction: Faction):
    player.faction = faction
    
    for unit in Unit.objects.filter(faction_for_which_is_default=faction):
        players_unit = unit
        players_unit.pk = None
        players_unit.ruler = player
        players_unit.save()

        for resource in players_unit.cost_dict:
            player.adjust_resource(resource, 0)

    for building_type in faction.starter_building_types.all():
        new_building_type = building_type
        new_building_type.pk = None
        new_building_type.save()
        player.building_types_available.add(new_building_type)

        if new_building_type.amount_produced > 0:
            player.adjust_resource(new_building_type.resource_produced, 0)

    player.save()


def send_journey(player: Player, unit: Unit, quantity: int, destination: Region):
    try:
        journey = Journey.objects.get(ruler=player, unit=unit, destination=destination, ticks_to_arrive=12)
        journey.quantity += quantity
        journey.save()
    except:
        Journey.objects.create(ruler=player, unit=unit, quantity=quantity, destination=destination)
        
    unit.quantity_marshaled -= quantity
    unit.save()


def receive_journey(journey: Journey):
    region = journey.destination
    unit = journey.unit
    unit_id_str = str(unit.id)
    quantity = journey.quantity

    if unit_id_str in region.units_here_dict.keys():
        region.units_here_dict[unit_id_str] += quantity
    else:
        region.units_here_dict[unit_id_str] = quantity

    region.save()
    journey.delete()


def get_journey_output_dict(player: Player, region: Region):
    journey_dict = {}
    output_dict = {}
    incoming_journeys = Journey.objects.filter(ruler=player, destination=region)
    
    for journey in incoming_journeys:
        journey_dict[journey.unit.name] = {}
        journey_dict[journey.unit.name][str(journey.ticks_to_arrive)] = journey.quantity

        for x in range(1, 12):
            if str(x) not in journey_dict[journey.unit.name]:
                journey_dict[journey.unit.name][str(x)] = "-"

    for unit_name, tick_data in journey_dict.items():
        output_dict[unit_name] = []

        for x in range(1, 13):
            output_dict[unit_name].append(tick_data[str(x)])

    return output_dict