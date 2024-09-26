from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Player, Deity, Terrain, Region, Faction, BuildingType, Unit
from maingame.static_init import initialize_game_pieces
from maingame.utils import assign_faction, construct_building, mock_up_player, generate_region


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Generating stuff...")

        initialize_game_pieces()

        for user in User.objects.all():
            if "test" in user.username:
                mock_up_player(user, Faction.objects.get(name="human"))
            else:
                mock_up_player(user, Faction.objects.get(name="undead"))

            player = Player.objects.get(associated_user=user)
            
            for unit in Unit.objects.filter(ruler=player):
                    unit.quantity_marshaled = 500
                    unit.save()

        for _ in range(3):
            generate_region()

        print("Done generating stuff.")
