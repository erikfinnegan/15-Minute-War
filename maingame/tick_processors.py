from maingame.formatters import create_or_add_to_key
from maingame.models import Player, Region, Round, Unit, Building

# def do_resource_production():
#     for player in Player.objects.all():
#         player.adjust_resource("🪙", player.gold_production)
#         player.adjust_resource("👑", player.influence_production)
        
#         for building in Building.objects.filter(ruler=player):
#             if building.type.amount_produced > 0:
#                 amount_produced = building.type.amount_produced
                
#                 if building.built_on_ideal_terrain:
#                     amount_produced *= 2

#                 player.adjust_resource(building.type.resource_produced, amount_produced)

#         player.save()


# def do_food_consumption():
#     for player in Player.objects.all():
#         consumption = player.get_food_consumption()
#         player.is_starving = consumption > player.resource_dict["🍞"]
#         player.adjust_resource("🍞", (consumption * -1))
#         player.save()        


# def do_journeys():
#     for journey in Journey.objects.all():
#         journey.ticks_to_arrive -= 1
#         journey.save()

#         if journey.ticks_to_arrive == 0:
#             receive_journey(journey)


def check_victory():
    for player in Player.objects.all():
        if player.resource_dict["👑"] >= 1000:
            round = Round.objects.first()
            round.winner = player
            round.has_ended = True
            round.save()


def do_invasion(region: Region):
    ruler_power = {}
    unit_casualties_dict = {}

    for unit_id, quantity in region.units_here_dict.items():
        unit = Unit.objects.get(id=unit_id)

        if unit.ruler == region.ruler:
            create_or_add_to_key(ruler_power, str(unit.ruler.id), (quantity * unit.dp) + 0.01)  # Ties go to defender
        else:
            create_or_add_to_key(ruler_power, str(unit.ruler.id), (quantity * unit.op))

    winner_id = 0
    highest_power = 0
    highest_invader_power = 0

    for ruler_id, power in ruler_power.items():
        if power > highest_power:
            winner_id = ruler_id
            highest_power = power

        if ruler_id != region.ruler.id and power > highest_invader_power:
            highest_invader_power = power

    winner = Player.objects.get(id=winner_id)
    units_here_dict_clone = region.units_here_dict.copy()

    for unit_id, quantity in units_here_dict_clone.items():
        unit = Unit.objects.get(id=unit_id)
        defensive_casualties_for_this_unit = int(0.05 * region.units_here_dict[unit_id])
        offensive_casualties_for_this_unit = int(0.1 * region.units_here_dict[unit_id])

        if unit.ruler == region.ruler and ruler_power[str(unit.ruler.id)] <= 1.25 * highest_invader_power:
            unit_casualties_dict[unit.id] = defensive_casualties_for_this_unit
            region.units_here_dict[unit_id] -= defensive_casualties_for_this_unit
        else:
            unit_casualties_dict[unit.id] = offensive_casualties_for_this_unit
            region.units_here_dict[unit_id] -= offensive_casualties_for_this_unit

        if unit.ruler != winner:
            unit.quantity_marshaled += quantity - defensive_casualties_for_this_unit
            del region.units_here_dict[unit_id]
            unit.save()

    for building in Building.objects.filter(region=region):
        building.ruler = winner
        building.save()

    # unit_casualties_dict: key = unit_id, value = casualties_for_that_unit

    region.ruler = winner
    region.invasion_this_tick = False
    region.save()


def do_global_tick():
    check_victory()

    if Round.objects.first().allow_ticks:
        for player in Player.objects.all():
            if player.protection_ticks_remaining == 0:
                player.do_tick()

    for region in Region.objects.filter(invasion_this_tick=True):
        do_invasion(region)