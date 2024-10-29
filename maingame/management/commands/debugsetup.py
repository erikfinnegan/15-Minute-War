from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Player, Deity, Unit, Faction, Resource, Building
from maingame.static_init import initialize_game_pieces
from maingame.utils import initialize_player


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Generating stuff...")

        initialize_game_pieces()

        for user in User.objects.all():
            if user.username != "test" and user.username != "dontplayerme":
                player = initialize_player(user=user, faction=Faction.objects.get(name="human"), display_name=f"p-{user.username}")
                farm = Building.objects.get(ruler=player, name="farm")
                farm.quantity = 10
                farm.save()
        
        invade_me_test = Player.objects.get(name="p-nofaction")
        invade_me_test.name = "Invade me"

        for unit in Unit.objects.filter(ruler=invade_me_test):
            unit.quantity_at_home = 10
            unit.save()

        invade_me_test.protection_ticks_remaining = 0
        invade_me_test.save()

        testuser = User.objects.get(username="test")
        testplayer = initialize_player(user=testuser, faction=Faction.objects.get(name="dwarf"), display_name="ERIKTEST")
        testplayer.protection_ticks_remaining = 0
        testplayer.discovery_points = 5000
        testplayer.theme = "Elesh Norn"
        testplayer.save()

        for building in Building.objects.filter(ruler=testplayer):
            building.quantity = 20
            building.save()

        for unit in Unit.objects.filter(ruler=testplayer):
            unit.quantity_at_home = 500
            unit.save()

        for resource in Resource.objects.filter(ruler=testplayer):
            resource.quantity = 1000000
            resource.save()

        adminplayer = Player.objects.get(name="p-admin")
        adminplayer.protection_ticks_remaining = 0
        adminplayer.discovery_points = 5000
        adminplayer.save()

        for unit in Unit.objects.filter(ruler=adminplayer):
            unit.quantity_at_home = 50000
            unit.save()

        print("Done generating stuff.")
