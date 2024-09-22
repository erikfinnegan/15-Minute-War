from maingame.models import Player, Building, Journey
from maingame.utils import receive_journey

def do_resource_production():
    for player in Player.objects.all():
        player.adjust_resource("🪙", player.gold_production)
        
        for building in Building.objects.filter(ruler=player):
            if building.type.amount_produced > 0:
                amount_produced = building.type.amount_produced
                
                if building.built_on_ideal_terrain:
                    amount_produced *= 2

                player.adjust_resource(building.type.resource_produced, amount_produced)

        player.save()


def do_food_consumption():
    for player in Player.objects.all():
        consumption = player.get_food_consumption()
        player.is_starving = consumption > player.resource_dict["🍞"]
        player.adjust_resource("🍞", (consumption * -1))
        player.save()        


def do_journeys():
    for journey in Journey.objects.all():
        journey.ticks_to_arrive -= 1
        journey.save()

        if journey.ticks_to_arrive == 0:
            receive_journey(journey)


def check_victory():
    for player in Player.objects.all():
        if player.resource_dict["👑"] >= 1000:
            print("They win!")


def do_tick():
    check_victory()
    do_resource_production()
    do_food_consumption()
    do_journeys()