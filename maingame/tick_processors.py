from maingame.models import Player, Region, Building, Terrain, Unit, Journey
from maingame.utils import receive_journey

def do_resource_production():
    beautiful_terrain = Terrain.objects.get(name="beautiful")

    for player in Player.objects.all():
        player.adjust_resource("🪙", 5000)
        
        for region in Region.objects.filter(ruler=player):
            if region.primary_terrain == beautiful_terrain:
                player.adjust_resource("🪙", 850)
            elif region.secondary_terrain == beautiful_terrain:
                player.adjust_resource("🪙", 650)
            else:
                player.adjust_resource("🪙", 500)

        for building in Building.objects.filter(ruler=player):
            if building.type.amount_produced > 0:
                amount_produced = building.type.amount_produced
                
                if building.built_on_ideal_terrain:
                    amount_produced *= 2

                player.adjust_resource(building.type.resource_produced, amount_produced)

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