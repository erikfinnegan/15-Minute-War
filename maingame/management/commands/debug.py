from random import randint
from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Resource, Round, Event, Dominion
from django.contrib.auth.models import User
import os

from maingame.static_init import initialize_blessed_order_discoveries

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        initialize_blessed_order_discoveries()
        # user = User.objects.get(username="erik")
        # user_settings = UserSettings.objects.get(associated_user=user)

        # totals = {}

        # for user in UserSettings.objects.all():
        #     if user.theme in totals:
        #         totals[user.theme] += 1
        #     else:
        #         totals[user.theme] = 1

        # print(totals)

        # event = Event.objects.filter(category="Signup").last()
        # user = User.objects.get(username="test")
        # testdom = Dominion.objects.get(associated_user=user)
        # print(testdom)
        # print(testdom in event.notified_dominions.all())
        # print(event.reference_id, testdom.id)
        
        pages = 1
        opbonus = 0

        for x in range(96*2):
            if x % 24 == 0:
                pages += 1

            opbonus += pages * 0.003

        print(opbonus)