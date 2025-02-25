from random import randint
from django.core.management.base import BaseCommand

from maingame.formatters import get_fast_return_cost_multiplier
from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit, MechModule
from django.contrib.auth.models import User

from maingame.utils.utils_sludgeling import create_random_sludgene

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        print()
        
        for module in MechModule.objects.all():
            module.zone == "hangar"
            module.save()
        
        # ticks = 0
        # mana_upkeep = 0
        # return_cost = 200
        # print(f"Upkeep vs Cost")
        
        # while return_cost > mana_upkeep:
        #     ticks += 1
        #     mana_upkeep += 3
        #     return_cost *= 0.85
            
        #     print(f"{ticks}: {mana_upkeep} vs {return_cost}")
            
        
        
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
        
        # for _ in range(6):
        #     sludgene = create_random_sludgene(Dominion.objects.get(name="ERIKTEST"))

        # print()
        # print()
        # print()
