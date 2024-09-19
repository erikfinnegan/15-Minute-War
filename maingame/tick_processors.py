from maingame.models import Player, Region, Building, Terrain, Unit, Journey
from maingame.utils import receive_journey

def do_resource_production():
    beautiful_terrain = Terrain.objects.get(name="beautiful")

    for player in Player.objects.all():
        player.gold += 5000
        
        for region in Region.objects.filter(ruler=player):
            if region.primary_terrain == beautiful_terrain:
                player.gold += 1500
            elif region.secondary_terrain == beautiful_terrain:
                player.gold += 1000
            else:
                player.gold += 500

        for building in Building.objects.filter(ruler=player):
            if building.type.amount_produced > 0:
                amount_produced = building.type.amount_produced
                
                if building.built_on_ideal_terrain:
                    amount_produced *= 2
                
                elif building.type.resource_produced == "ore":
                    player.ore += amount_produced
                elif building.type.resource_produced == "lumber":
                    player.lumber += amount_produced
                elif building.type.resource_produced == "mana":
                    player.mana += amount_produced
                elif building.type.resource_produced == "gems":
                    player.gems += amount_produced
                elif building.type.resource_produced == "food":
                    player.food += amount_produced

        total_units = 0

        for unit in Unit.objects.filter(ruler=player):
            total_units += unit.quantity_marshaled

        # for each ruled region, go through units_here_dict

        player.save()


def do_journeys():
    for journey in Journey.objects.all():
        journey.ticks_to_arrive -= 1
        journey.save()

        if journey.ticks_to_arrive == 0:
            receive_journey(journey)


def do_tick():
    do_resource_production()
    do_journeys()