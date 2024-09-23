from django.core.management.base import BaseCommand

from maingame.models import Player, Terrain, Deity, Region, Unit, Building, BuildingType
from django.contrib.auth.models import User

from maingame.tick_processors import do_global_tick

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        # testuser = User.objects.get(username="test")
        # testplayer = Player.objects.get(associated_user=testuser)

        do_global_tick()
        
