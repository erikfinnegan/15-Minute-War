from random import randint
from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit
from django.contrib.auth.models import User
import os

from maingame.static_init import initialize_blessed_order_discoveries

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        print()
        # user = User.objects.get(username="erik")
        # user_settings = UserSettings.objects.get(associated_user=user)

        # bonus = 6
        # target = 17
        # attempts = 100000

        # crits = 0
        # hits = 0
        # misses = 0

        # for _ in range(attempts):
        #     d6 = randint(1,6)
        #     d8 = randint(1,8)
        #     d10 = randint(1,10)

        #     sum = d6 + d8 + d10 + bonus

        #     if sum < target:
        #         misses += 1
        #     elif d6 == d8 or d6 == d10 or d8 == d10:
        #         crits += 1
        #     else:
        #         hits += 1

        # print(f"DC {target} with +{bonus} bonus")


        quantity_dice = 10
        extra_hits_to_crit = 1
        die_size = 6
        attempts = 100000

        crits = 0
        hits = 0
        misses = 0
        streak6 = 0
        streak5 = 0
        streak4 = 0
        streak3 = 0
        streak2 = 0
        dice_to_roll = 2 if quantity_dice == 0 else quantity_dice

        for _ in range(attempts):
            rolls = []

            for _ in range(dice_to_roll):
                rolls.append(randint(1,die_size))

            if quantity_dice == 0:
                rolls.sort()
            else:
                rolls.sort(reverse=True)
                
            if 1 in rolls and 2 in rolls and 3 in rolls and 4 in rolls and 5 in rolls and 6 in rolls:
                streak6 += 1
            
            if 1 in rolls and 2 in rolls and 3 in rolls and 4 in rolls and 5 in rolls:
                streak5 += 1
            
            if 1 in rolls and 2 in rolls and 3 in rolls and 4 in rolls:
                streak4 += 1
            
            if 1 in rolls and 2 in rolls and 3 in rolls:
                streak3 += 1
            
            if 1 in rolls and 2 in rolls:
                streak2 += 1

            result = rolls[0]
            crit_check = rolls[extra_hits_to_crit]

            if crit_check == 6:
                crits += 1
            elif result == 6:
                hits += 1
            else:
                misses += 1
        
        print(f"{quantity_dice}d{die_size}")
        





        # bonus = 10
        # die_size = 20
        # attempts = 1000000

        # crits = 0
        # hits = 0
        # misses = 0

        # for _ in range(attempts):
        #     result = randint(1,die_size) + randint(1,die_size) + bonus

        #     if result >= 31:
        #         crits += 1
        #     elif result >= 21:
        #         hits += 1
        #     else:
        #         misses += 1
        #
        # print(f"2d{die_size} + {bonus}")
       
        print()
        print(f"Crit: {int(crits/attempts * 100)}%")
        print(f"Hits: {int(hits/attempts * 100)}%")
        print(f"Miss: {int(misses/attempts * 100)}%")
        print()
        print(f"6: {int(streak6/attempts * 100)}%")
        print(f"5: {int(streak5/attempts * 100)}%")
        print(f"4: {int(streak4/attempts * 100)}%")
        print(f"3: {int(streak3/attempts * 100)}%")
        print(f"2: {int(streak2/attempts * 100)}%")
        print()