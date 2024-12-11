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

        exps = 100
        minroll = 0

        for _ in range(exps):
            minroll += (100-minroll) / 75

        print(minroll)