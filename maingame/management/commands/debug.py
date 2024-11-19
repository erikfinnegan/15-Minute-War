from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Resource, Round
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        # user = User.objects.get(username="erik")
        # user_settings = UserSettings.objects.get(associated_user=user)

        # perk_dict = {"inquisition_ratexx": 5}

        # if perk_dict.get("inquisition_rate") and perk_dict.get("inquisition_rate") > 0:
        #     print("INQUISITION ACTIVE")
        # else:
        #     print("No inquisition here")

        # round = Round.objects.first()

        # print(round.start_time)

        # 0.3% Op per animosity

        totals = {}

        for user in UserSettings.objects.all():
            if user.theme in totals:
                totals[user.theme] += 1
            else:
                totals[user.theme] = 1

        print(totals)