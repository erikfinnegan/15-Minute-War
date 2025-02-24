from random import randint
from django.core.management.base import BaseCommand

from maingame.formatters import get_fast_return_cost_multiplier
from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit
from django.contrib.auth.models import User

from maingame.utils.utils_sludgeling import create_random_sludgene

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        print()
        
        testdominion = Dominion.objects.get(name="ERIKTEST")
        
        food = Resource.objects.get(name="food", ruler=testdominion)
        food.spend(food.quantity)
        
        
        
        
        
        
        
        
        
        # mult = 10
        
        # def cost_after_x_ticks(cost, ticks):
        #     for _ in range(ticks):
        #         cost *= 0.9281
        #         cost = int(cost)
                
        #     return cost
        
        
        # cost = 5000 * mult
        # ticks = 15
        
        # for _ in range(ticks):
        #     # cost *= 0.94395
        #     cost *= 0.9281
        #     cost = int(cost)
        
        # # Looking for 15000
        # print(f"Cost after {ticks} ticks: {cost}")
        
        # pct_land_towers = cost / ticks / 50 / 5
        # print(pct_land_towers)
        
        
        
        
        # cost = 140000 * mult
        
        # for _ in range(ticks):
        #     # cost *= 0.94395
        #     cost *= 0.9281
        #     cost = int(cost)
        
        # # Looking for 15000
        # print(f"Cost after {ticks} ticks: {cost}")
        
        # pct_land_towers = cost / ticks / 50 / 45
        # print(pct_land_towers)
        
        # # for _ in range(6):
        # #     sludgene = create_random_sludgene(Dominion.objects.get(name="ERIKTEST"))

        # print()
        # print()
        # print()
