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
        
        mult = 10
        x = 1000
        y = x * mult

        total_x = 0
        total_y = 0

        while x > 0:
            total_x += x
            x = int(x * 0.98)

        while y > 0:
            total_y += y
            y = int(y * 0.98)

        mod_x = total_x * mult
        print(total_x)
        print(total_y)
        print(mod_x / total_y)

        print()
        print()
        print()
