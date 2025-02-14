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
        
        rats = 1000
        food_spent = 0
        
        for _ in range(96):
            survivors = int(0.02 * rats)
            casualties = rats - survivors
            food_spent += 100 * casualties

        food_spent_per_tick_per_rat = food_spent / 96 / 1000

        print(f"{food_spent_per_tick_per_rat:2,}")

        print()
        print()
        print()
