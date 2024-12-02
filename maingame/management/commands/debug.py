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

        attempts = 100000
        lowest = 99999999
        highest = 0
        total = 0

        for _ in range(attempts):
            ticks = 1

            keep_going = True

            while keep_going:
                roll = randint(1,100)
                keep_going = roll > (ticks/4)
                ticks += 1

            total += ticks
            lowest = min(lowest, ticks)
            highest = max(highest, ticks)

        print(int(total/attempts))
        print(lowest)
        print(highest)
