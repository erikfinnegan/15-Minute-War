from random import randint
from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit
from django.contrib.auth.models import User
import os

from maingame.game_pieces.initialize import initialize_blessed_order_discoveries

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        print()
        # user = User.objects.get(username="erik")
        # user_settings = UserSettings.objects.get(associated_user=user)

        # pages = 50
        # days = 2

        # for _ in range(6 * 24 * days):
        #     pages *= 1.0018

        # print(pages)


        # total = 0
        # shortest = 99999999999999999
        # longest = 0
        # passed_target = 0
        # attempts = 10000
        # target = 700

        # for _ in range(attempts):
        #     keep_going = True
        #     ticks_it_lasted = 0

        #     while keep_going:
        #         ticks_it_lasted += 1
        #         keep_going = randint(1, 100) <= 99

        #     total += ticks_it_lasted
        #     longest = max(longest, ticks_it_lasted)
        #     shortest = min(shortest, ticks_it_lasted)

        #     if ticks_it_lasted >= target:
        #         passed_target += 1

        # print("average", total/attempts)
        # print("shortest", shortest)
        # print("longest", longest)
        # print("pct passed target", passed_target/attempts)



        # x1 = 0
        # x2 = 0
        # x3 = 0
        # x4 = 0
        # x5 = 0
        # x6 = 0
        # x7 = 0
        # x8 = 0
        # x9 = 0
        # x10 = 0
        # x11 = 0
        # x12 = 0

        # attempts = 10000

        # die1 = 6
        # die2 = 6
        # die3 = 6

        # hightotal = 0
        # midtotal = 0
        # lowtotal = 0

        # results = {}

        # for x in range(max(die1, die2, die3)):
        #     strx = str(x+1)
        #     results[strx] = 0

        # for _ in range(attempts):
        #     roll1 = randint(1, die1)
        #     roll2 = randint(1, die2)
        #     roll3 = randint(1, die3)

        #     rolls = [roll1, roll2, roll3]
        #     rolls.sort(reverse=True)

        #     high = rolls[0]
        #     mid = rolls[1]
        #     low = rolls[2]

        #     hightotal += high
        #     midtotal += mid
        #     lowtotal += low

        #     results[str(mid)] += 1

        # print(hightotal / attempts)
        # print(midtotal / attempts)
        # print(lowtotal / attempts)
        # print()

        # for x in range(die1 + die2 + die3):
        #     strx = str(x+1)
        #     results[strx] = 0

        # for _ in range(attempts):
        #     roll = 0

        #     if die1 > 0:
        #         roll1 = randint(1, die1)
        #         roll += roll1
        #         results[str(roll1)] += 1

        #     if die2 > 0:
        #         roll2 = randint(1, die2)
        #         roll += roll2
        #         results[str(roll2)] += 1

        #     if die3 > 0:
        #         roll3 = randint(1, die3)
        #         roll += roll3
        #         results[str(roll3)] += 1

        #     results[str(roll)] += 1

        # print()
        # print(f"d{die1} + d{die2}")

        # approximator = int(attempts / 100)

        # for key, value in results.items():
        #     output = f"{key}: "

        #     if int(key) < 10:
        #         output += " "

        #     outputter = int(value/approximator) if approximator > 0 else value
        #     for _ in range(outputter):
        #         output += "x"

        #     pct = (value/attempts) * 100

        #     if attempts >= 1000:
        #         output += f" {int(pct)}%"

        #     print(output)
        # print()

        def percentize(x):
            x = x * 100
            return int(x)

        die_a = 8
        die_b = 8
        die_c = 8

        target_number = 11

        attempts = 100000
        complications = 0
        big_complications = 0
        successes = 0

        for _ in range(attempts):
            a = randint(1, die_a)
            b = randint(1, die_b)
            c = randint(1, die_c)

            if a + b + c >= target_number:
                successes += 1

            if c > b or c > a:
                complications += 1

            if c > b and c > a:
                big_complications += 1

        print()
        print()
        print(f"{die_a} {die_b} [{die_c}] -vs- {target_number}")
        print("Success:", percentize(successes/attempts))
        print("Complication:", percentize(complications/attempts))
        print("Big comps::", percentize(big_complications/attempts))
        print()
        print()


