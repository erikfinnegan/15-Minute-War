from random import randint
from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit, Building
from django.contrib.auth.models import User
import os

from maingame.game_pieces.initialize import initialize_blessed_order_discoveries

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
       for dominion in Dominion.objects.all().order_by("-acres"):
            for building in Building.objects.filter(ruler=dominion):
                print(f"{building.upgrades} - {building}")
            
            print()
            print()