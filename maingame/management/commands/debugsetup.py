from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Player, Deity, Terrain, Region, BuildingType, Unit
from maingame.static_init import initialize_game_pieces
from maingame.utils import generate_region, initialize_player


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Generating stuff...")

        initialize_game_pieces()

        for user in User.objects.all():
            initialize_player(user)

            player = Player.objects.get(associated_user=user)
            
            for unit in Unit.objects.filter(ruler=player):
                    unit.quantity_marshaled = 500
                    unit.save()

        for _ in range(3):
            generate_region()

        print("Done generating stuff.")
