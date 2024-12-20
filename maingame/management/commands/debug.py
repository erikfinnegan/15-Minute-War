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

        # pages = 50
        # days = 2

        # for _ in range(6 * 24 * days):
        #     pages *= 1.0018

        # print(pages)


        # total = 0
        # shortest = 99999999999999999
        # longest = 0
        # attempts = 100

        # for _ in range(attempts):
        #     keep_going = True
        #     ticks_it_lasted = 0

        #     while keep_going:
        #         ticks_it_lasted += 1
        #         keep_going = randint(1, 100) <= 99

        #     total += ticks_it_lasted
        #     longest = max(longest, ticks_it_lasted)
        #     shortest = min(shortest, ticks_it_lasted)

        # print("average", total/attempts)
        # print("shortest", shortest)
        # print("longest", longest)
