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


# def get_production_dict(player: Player):
#     production_dict = {
#         "🪙": {
#             "produced": 0,
#             "consumed": 0,
#             "net": 0,
#         },
#         "🪨": {
#             "produced": 0,
#             "consumed": 0,
#             "net": 0,
#         },
#         "🪵": {
#             "produced": 0,
#             "consumed": 0,
#             "net": 0,
#         },
#         "🔮": {
#             "produced": 0,
#             "consumed": 0,
#             "net": 0,
#         },
#         "💎": {
#             "produced": 0,
#             "consumed": 0,
#             "net": 0,
#         },
#         "🍞": {
#             "produced": 0,
#             "consumed": 0,
#             "net": 0,
#         },
#     }

#     gold_production = 5000
#     beautiful_terrain = Terrain.objects.get(name="beautiful")

#     for region in Region.objects.filter(ruler=self):
#         if region.primary_terrain == beautiful_terrain:
#             gold_production += 1500
#         elif region.secondary_terrain == beautiful_terrain:
#             gold_production += 1000
#         else:
#             gold_production += 500

#     production_dict["🪙"] = {"produced": gold_production}

#     for building in Building.objects.filter(ruler=self):
#         if building.type.amount_produced > 0:
#             print("Handle building", building)
#             amount_produced = building.type.amount_produced
            
#             if building.built_on_ideal_terrain:
#                 amount_produced *= 2

#             if building.type.resource_produced == "ore":
#                 production_dict["🪨"] = {"produced": amount_produced}
#             elif building.type.resource_produced == "lumber":
#                 production_dict["🪵"] = {"produced": amount_produced}
#             elif building.type.resource_produced == "mana":
#                 production_dict["🔮"] = {"produced": amount_produced}
#             elif building.type.resource_produced == "gems":
#                 production_dict["💎"] = {"produced": amount_produced}
#             elif building.type.resource_produced == "food":
#                 production_dict["🍞"] = {"produced": amount_produced}

#     total_units = 0

#     for unit in Unit.objects.filter(ruler=self):
#         total_units += unit.quantity_marshaled

#     for region in Region.objects.filter(ruler=self):
#         for _, quantity in region.units_here_dict.items():
#             total_units += quantity

#     print()
#     print(production_dict)
#     print()
#     production_dict["🍞"]["consumed"] = total_units / 10

#     for key in production_dict:
#         if hasattr(production_dict[key], "produced") and hasattr(production_dict[key], "consumed"):
#             production_dict[key]["net"] = production_dict[key]["produced"] - production_dict[key]["consumed"]
#         else:
#             production_dict[key]["net"] = production_dict[key]["produced"]