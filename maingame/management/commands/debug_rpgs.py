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
        attempts = 100000
        print()
        print()

        def percentize(x):
            x = x * 100
            return int(x)

        die_a = 8
        die_b = 8
        die_c = 12

        target_number = 11

        complications = 0
        big_complications = 0
        full_successes = 0
        comp_successes = 0
        bigc_successes = 0
        successes = 0
        failures = 0

        for _ in range(attempts):
            a = randint(1, die_a)
            b = randint(1, die_b)
            c = randint(1, die_c)

            is_complication = False
            is_big_complication = False

            if c > a + b:
                big_complications += 1
                is_big_complication = True
            elif c > b or c > a:
                complications += 1
                is_complication = True

            if a + b + c >= target_number:
                successes += 1

                if is_big_complication:
                    bigc_successes += 1
                elif is_complication:
                    comp_successes += 1
                else:
                    full_successes += 1
            else:
                failures += 1

            

        print()
        print()
        print(f"{die_a} {die_b} [{die_c}] -vs- {target_number}")
        print("Success (full):", percentize(full_successes/attempts))
        print("Success (comp):", percentize(comp_successes/attempts))
        print("Success (big comp):", percentize(bigc_successes/attempts))
        print()
        print("Success:", percentize(successes/attempts))
        print("Failure:", percentize(failures/attempts))
        print()
        print("Complication:", percentize(complications/attempts))
        print("Big comps:", percentize(big_complications/attempts))
        print()
        print()
