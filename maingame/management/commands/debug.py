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
        
        total_spent = 0
        total_normal_spent = 0
        unit_price = 2300
        target = 50000
        unit_op = 8
        units = 0
        normal_units = 0
        attacks = 7
        casualty_multiplier = 0.5

        casualty_percent = 10 * casualty_multiplier
        survival_rate = 1 - (casualty_percent/100)

        for _ in range(attacks):
            while units * unit_op < target:
                units += 1
                total_spent += unit_price

            units = int(units * survival_rate)

            while normal_units * unit_op < target:
                normal_units += 1
                total_normal_spent += unit_price

            normal_units = int(normal_units * 0.9)

        cost_increase = 1 / (total_spent/total_normal_spent)

        print(f"{attacks} attacks at casualties x{casualty_multiplier}")
        print(f"Total spend: {total_spent:2,}")
        print(total_spent/27312500)
        print(f"Increase cost by {round(cost_increase, 2)}")


        print()
        print()
        print()
