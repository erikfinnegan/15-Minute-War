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
        
        whispers = 0
        heretics = 0
        
        for _ in range(96 * 5):
            heretics += 5
            whispers += heretics

            if heretics >= 48 * 5:
                heretics = 0

        print(f"{whispers:2,}")

        print()
        print()
        print()
