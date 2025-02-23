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
        
        
        for _ in range(6):
            sludgene = create_random_sludgene(Dominion.objects.get(name="ERIKTEST"))
        
        # base_cost = 1000
        
        # def get_faster_cost(faster):
        #     return get_fast_return_cost_multiplier(12 - faster)
        #     # cost = base_cost
        #     # expo = 1.02 + (faster/300)
            
        #     # for _ in range(faster):
        #     #     cost *= expo
                
        #     # return int(cost)/base_cost
        
        # op = 3
        # dp = 10
        # print(f"{op}/{dp}")
        
        # for x in range(12):
        #     # new_cost = get_faster_cost(x) - 1
        #     mult = get_fast_return_cost_multiplier(12 - x, op, dp)
        #     padnum = str(x).ljust(2, " ")
        #     print(f"{padnum} faster = x{mult}")
            
        
        # total_rate = 0
        # attempts = 100000
        # targets = 0
        # lowest = 1
        # highest = 0
        
        # for _ in range(attempts):
        #     rate = 1
            
        #     roll = randint(-1, 1)
        #     rate += roll * 0.25
            
        #     roll = randint(-1, 1)
        #     rate += roll * 0.25
            
        #     roll = randint(-1, 1)
        #     rate += roll * 0.15
            
        #     roll = randint(-1, 1)
        #     rate += roll * 0.10
            
        #     rate = round(rate, 2)
            
        #     total_rate += rate
            
        #     if rate == 0.25:
        #         targets += 1
                
        #     if rate < lowest:
        #         lowest = rate
                
        #     if rate > highest:
        #         highest = rate
            
        # print(total_rate/attempts)
        # print(targets/attempts)
        # print(highest)

        print()
        print()
        print()
