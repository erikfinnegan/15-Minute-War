from math import ceil
from random import randint
from django.core.management.base import BaseCommand

from maingame.formatters import get_fast_return_cost_multiplier
from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit, MechModule
from django.contrib.auth.models import User

from maingame.utils.utils_sludgeling import create_random_sludgene
from maingame.utils.utils import generate_unit_cost_dict

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        print()
        
        
        # pages_to_gain = 55

        # for x in range(96*7):
        #     pages_to_gain *= 1.002
            
        #     if x % 96 == 0:
        #         print(x/96, pages_to_gain)
            
        # return_ticks = 5
        # op = 5
        # dp = 5
        # print(get_fast_return_cost_multiplier(return_ticks, op, dp))
        
        
        # attempts = 1000000
        
        # def percentize(x, y=attempts):
        #     x = x / y
        #     x = x * 100
        #     return int(x)
        
        
        
        # sorcs = 99000
        # demons = 0
        # demons_per_sorc_per_tick = 1
        # demon_attrition_mult = 0.98
        
        # for _ in range(100):
        #     demons = int(demons * demon_attrition_mult)
        #     demons += demons_per_sorc_per_tick * sorcs
        #     print(demons)
        
        # print("demons per sorc", demons/sorcs)
        
        
        
        # returned_mult = 0.025
        # mult_add = 0.025
        
        # void_units = attempts
        # home_units = 0
        # ticks = 0
        
        # while void_units > 0:
        #     ticks += 1
        #     units_returned = ceil(returned_mult * void_units)
        #     void_units -= units_returned
        #     home_units += units_returned
        #     returned_mult += mult_add
            
        #     print(f"{ticks}: {percentize(home_units)}")
            
        # print("ticks", ticks)
        
        
        
        
        
        
        # void_units = 10000
        # return_mult_growth = 0.03
        # return_mult = return_mult_growth
        # ticks = 0
        # attacks = 1
        
        # while void_units > 100:
        #     ticks += 1
        #     returned_units = ceil(return_mult * void_units)
        #     void_units -= returned_units
        #     return_mult = min(1, return_mult + return_mult_growth)
            
        #     if void_units < 2000 and void_units > 0:
        #         attacks += 1
        #         void_units += 10000
        #         print(ticks)
            
        # print(ticks)
        # print("attacks", attacks)
        
        
             
        costdict = generate_unit_cost_dict(12, 8, "gold", "mithril", "hybrid", casualty_multiplier=0.5, return_ticks=12, cost_multiplier=1)
        print(costdict)
        
        
        
        
        # total_ticks = 0
        # attempts = 100000
        
        # for _ in range(attempts):
        #     ticks = 0
        #     percent_chance = 2
        #     units_out = True
            
        #     while units_out:
        #         ticks += 1
                
        #         if percent_chance >= randint(1,100):
        #             units_out = False
            
        #         percent_chance += 1
            
        #     total_ticks += ticks
            
        # print(total_ticks/attempts)
            
        
        
        
        
        # def update_return_cost(return_cost, ticks):
        #     mult = 0.7
        #     return min(return_cost - 1, return_cost * mult)
            
        
        # ticks = 0
        # mana_upkeep = 0
        # return_cost = 5000
        # print(f"Upkeep vs Cost")
        
        # while return_cost > mana_upkeep:
        #     ticks += 1
        #     mana_upkeep += 3
        #     return_cost = update_return_cost(return_cost, ticks)
            
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
