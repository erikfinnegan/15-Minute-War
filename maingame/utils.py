from random import randint

from maingame.models import Terrain, Unit, BuildingType, Player, Faction, Region, Journey, Building


def assign_faction(player: Player, faction: Faction):
    for unit in Unit.objects.filter(faction_for_which_is_default=faction, ruler=None):
        players_unit = unit
        players_unit.pk = None
        players_unit.ruler = player
        players_unit.save()

        player.adjust_resource("👑", 0)

        for resource in players_unit.cost_dict:
            player.adjust_resource(resource, 0)

    for building_type in faction.starter_building_types.all():
        players_building_type = building_type
        players_building_type.pk = None
        players_building_type.ruler = player
        players_building_type.save()

        if players_building_type.amount_produced > 0:
            player.adjust_resource(players_building_type.resource_produced, 0)

    player.upgrade_cost = faction.base_upgrade_cost
    player.upgrade_exponent = faction.base_upgrade_exponent

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


def marshal_from_location(player: Player, unit: Unit, quantity: int, origin: Region):
    if quantity <= origin.units_here_dict[str(unit.id)] and unit.ruler == player:
        origin.units_here_dict[str(unit.id)] -= quantity
        
        if origin.units_here_dict[str(unit.id)] == 0:
            del origin.units_here_dict[str(unit.id)]

        origin.save()

        unit.quantity_marshaled += quantity
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


def construct_building(player, region_id, building_type_id, amount):
    building_type = BuildingType.objects.get(id=building_type_id)
    region = Region.objects.get(id=region_id)

    if region.ruler == player and building_type.ruler == player:
        for _ in range(amount):
            built_on_ideal_terrain = False

            if building_type.ideal_terrain == region.primary_terrain and region.primary_plots_available:
                built_on_ideal_terrain = True
            elif building_type.ideal_terrain == region.secondary_terrain and region.secondary_plots_available:
                built_on_ideal_terrain = True

            Building.objects.create(
                ruler=player,
                type=building_type,
                region=region,
                built_on_ideal_terrain=built_on_ideal_terrain,
            )


def get_journey_output_dict(player: Player, region: Region):
    journey_dict = {}
    output_dict = {}
    incoming_journeys = Journey.objects.filter(ruler=player, destination=region)
    
    for journey in incoming_journeys:
        journey_dict[journey.unit.name] = {}
        journey_dict[journey.unit.name][str(journey.ticks_to_arrive)] = journey.quantity

        for x in range(1, 13):
            if str(x) not in journey_dict[journey.unit.name]:
                journey_dict[journey.unit.name][str(x)] = "-"

    for unit_name, tick_data in journey_dict.items():
        output_dict[unit_name] = []

        for x in range(1, 13):
            output_dict[unit_name].append(tick_data[str(x)])

    return output_dict