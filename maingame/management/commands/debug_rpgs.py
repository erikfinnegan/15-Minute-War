from random import choice, randint
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


        def percentize(x, y=attempts):
            x = x / y
            x = x * 100
            return int(x)


        def pbta():
            bonus = 3

            full = 0
            standard = 0
            success = 0
            fail = 0

            for _ in range(attempts):
                roll = randint(1,6) + randint(1,6) + bonus
                
                if roll >= 10:
                    full += 1
                    success += 1
                elif roll >= 7:
                    standard += 1
                    success += 1
                else:
                    fail += 1

            print("full:", percentize(full))
            print("standard:", percentize(standard))
            print("success:", percentize(success))

        
        def genesys():
            boosts = 0
            abilities = 1
            proficiencies = 2

            setbacks = 1
            difficulties = 3
            challenges = 0

            boost = [
                {
                    "number": 1,
                    "success": 0,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 2,
                    "success": 0,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 3,
                    "success": 1,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 4,
                    "success": 1,
                    "advantage": 1,
                    "triumph": 0,
                },
                {
                    "number": 5,
                    "success": 0,
                    "advantage": 2,
                    "triumph": 0,
                },
                {
                    "number": 6,
                    "success": 0,
                    "advantage": 1,
                    "triumph": 0,
                },
            ]

            ability = [
                {
                    "number": 1,
                    "success": 0,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 2,
                    "success": 1,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 3,
                    "success": 1,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 4,
                    "success": 2,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 5,
                    "success": 0,
                    "advantage": 1,
                    "triumph": 0,
                },
                {
                    "number": 6,
                    "success": 1,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 7,
                    "success": 1,
                    "advantage": 1,
                    "triumph": 0,
                },
                {
                    "number": 8,
                    "success": 0,
                    "advantage": 2,
                    "triumph": 0,
                },
            ]

            proficiency = [
                {
                    "number": 1,
                    "success": 0,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 2,
                    "success": 1,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 3,
                    "success": 1,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 4,
                    "success": 2,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 5,
                    "success": 2,
                    "advantage": 0,
                    "triumph": 0,
                },
                {
                    "number": 6,
                    "success": 0,
                    "advantage": 1,
                    "triumph": 0,
                },
                {
                    "number": 7,
                    "success": 1,
                    "advantage": 1,
                    "triumph": 0,
                },
                {
                    "number": 8,
                    "success": 1,
                    "advantage": 1,
                    "triumph": 0,
                },
                {
                    "number": 9,
                    "success": 1,
                    "advantage": 1,
                    "triumph": 0,
                },
                {
                    "number": 10,
                    "success": 0,
                    "advantage": 2,
                    "triumph": 0,
                },
                {
                    "number": 11,
                    "success": 0,
                    "advantage": 2,
                    "triumph": 0,
                },
                {
                    "number": 12,
                    "success": 0,
                    "advantage": 0,
                    "triumph": 1,
                },
            ]
            
            setback = [
                {
                    "number": 1,
                    "failure": 0,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 2,
                    "failure": 0,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 3,
                    "failure": 1,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 4,
                    "failure": 1,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 5,
                    "failure": 0,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 6,
                    "failure": 0,
                    "threat": 1,
                    "despair": 0,
                },
            ]

            difficulty = [
                {
                    "number": 1,
                    "failure": 0,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 2,
                    "failure": 1,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 3,
                    "failure": 2,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 4,
                    "failure": 0,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 5,
                    "failure": 0,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 6,
                    "failure": 0,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 7,
                    "failure": 0,
                    "threat": 2,
                    "despair": 0,
                },
                {
                    "number": 8,
                    "failure": 1,
                    "threat": 1,
                    "despair": 0,
                },
            ]

            challenge = [
                {
                    "number": 1,
                    "failure": 0,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 2,
                    "failure": 1,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 3,
                    "failure": 1,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 4,
                    "failure": 2,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 5,
                    "failure": 2,
                    "threat": 0,
                    "despair": 0,
                },
                {
                    "number": 6,
                    "failure": 0,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 7,
                    "failure": 0,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 8,
                    "failure": 1,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 9,
                    "failure": 1,
                    "threat": 1,
                    "despair": 0,
                },
                {
                    "number": 10,
                    "failure": 0,
                    "threat": 2,
                    "despair": 0,
                },
                {
                    "number": 11,
                    "failure": 0,
                    "threat": 2,
                    "despair": 0,
                },
                {
                    "number": 12,
                    "failure": 0,
                    "threat": 0,
                    "despair": 1,
                },
            ]
            
            result_success = 0
            result_advantage = 0
            result_threat = 0
            result_triumph = 0
            result_despair = 0

            for _ in range(attempts):
                successes = 0
                advantages = 0
                triumphs = 0

                failures = 0
                threats = 0
                despairs = 0

                for _ in range(boosts):
                    roll = choice(boost)
                    successes += roll["success"] + roll["triumph"]
                    advantages += roll["advantage"]
                    triumphs += roll["triumph"]

                for _ in range(abilities):
                    roll = choice(ability)
                    successes += roll["success"] + roll["triumph"]
                    advantages += roll["advantage"]
                    triumphs += roll["triumph"]

                for _ in range(proficiencies):
                    roll = choice(proficiency)
                    successes += roll["success"] + roll["triumph"]
                    advantages += roll["advantage"]
                    triumphs += roll["triumph"]

                for _ in range(setbacks):
                    roll = choice(setback)
                    failures += roll["failure"] + roll["despair"]
                    threats += roll["threat"]
                    despairs += roll["despair"]

                for _ in range(difficulties):
                    roll = choice(difficulty)
                    failures += roll["failure"] + roll["despair"]
                    threats += roll["threat"]
                    despairs += roll["despair"]

                for _ in range(challenges):
                    roll = choice(challenge)
                    failures += roll["failure"] + roll["despair"]
                    threats += roll["threat"]
                    despairs += roll["despair"]

                is_success = successes > failures
                is_failure = failures >= successes
                is_advantage = advantages > threats
                is_threat = threats > advantages

                if is_success:
                    result_success += 1

                if is_advantage:
                    result_advantage += 1

                if is_threat:
                    result_threat += 1

                if triumphs > 0:
                    result_triumph += 1

                if despairs > 0:
                    result_despair += 1

            
            print("success:", percentize(result_success/attempts))
            print()
            print("advantage:", percentize(result_advantage/attempts))
            print("threat:", percentize(result_threat/attempts))
            print()
            print("triumph:", percentize(result_triumph/attempts))
            print("despair:", percentize(result_despair/attempts))
        

        def three_dice():
            die_a = 8
            die_b = 8
            die_c = 8
            c_bonus = 0

            target_number = 11

            complications = 0
            no_fuss = 0
            big_complications = 0
            full_successes = 0
            comp_successes = 0
            bigc_successes = 0
            successes = 0
            failures = 0
            regular_failures = 0
            comp_failures = 0
            bigc_failures = 0

            for _ in range(attempts):
                a = randint(1, die_a)
                b = randint(1, die_b)
                c = randint(1, die_c)

                is_complication = False
                is_big_complication = False

                if c + c_bonus > a + b:
                    big_complications += 1
                    is_big_complication = True
                elif c + c_bonus > b or c + c_bonus > a:
                    complications += 1
                    is_complication = True
                else:
                    no_fuss += 1

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
                    
                    if is_big_complication:
                        bigc_failures += 1
                    elif is_complication:
                        comp_failures += 1
                    else:
                        regular_failures += 1

            
            target_number_readout = f"{target_number}" if c_bonus == 0 else f"{target_number} (+{c_bonus})"

            print(f"{die_a} {die_b} [{die_c}] -vs- {target_number_readout}")
            # print("Success (full):", percentize(full_successes))
            # print("Success (comp):", percentize(comp_successes))
            # print("Success (bad):", percentize(bigc_successes))
            print()
            # print("Success:", percentize(successes))
            # print("Failure:", percentize(failures))
            # print()
            
            # print()
            # print()
            print(f"SUCCESS -- {percentize(successes)}%", )
            print(f"full {percentize(full_successes, successes)}%")
            print(f"comp {percentize(comp_successes, successes)}%")
            print(f"bad  {percentize(bigc_successes, successes)}%")
            print()
            print(f"FAILURE -- {percentize(failures)}%")
            print(f"reg  {percentize(regular_failures, failures)}%")
            print(f"comp {percentize(comp_failures, failures)}%")
            print(f"bad  {percentize(bigc_failures, failures)}%")
            print()
            print(f"No fuss {percentize(no_fuss)}%")
            print(f"Any comp {percentize(complications)}%")
            print(f"Any bad {percentize(big_complications)}%")

        three_dice()
        print()
        print()
        print()
