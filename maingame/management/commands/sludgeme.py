from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Dominion, Unit, Faction, Resource, Building, UserSettings, Round
from maingame.static_init import initialize_game_pieces
from maingame.utils import initialize_dominion
from datetime import datetime
from zoneinfo import ZoneInfo


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        my_faction_name = "sludgeling"

        my_starting_resource_quantity = 100123000

        print("Generating stuff...")

        initialize_game_pieces()

        round = Round.objects.first()
        round.start_time = datetime.now(ZoneInfo('America/New_York'))
        round.has_started = True
        round.ticks_to_end = 999
        round.save()

        for user in User.objects.all():
            if user.username != "test" and user.username != "dontdominionme":
                dominion = initialize_dominion(user=user, faction=Faction.objects.get(name="dwarf"), display_name=f"p-{user.username}")
                farm = Building.objects.get(ruler=dominion, name="farm")
                farm.quantity = 10
                farm.save()

            if not UserSettings.objects.filter(associated_user=user).exists():
                UserSettings.objects.create(associated_user=user, theme="OpenDominion", display_name=user.username)
            else:
                user_settings = UserSettings.objects.get(associated_user=user)
                user_settings.theme = "OpenDominion"
                user_settings.timezone = "EST"

                if user_settings.display_name == "":
                    user_settings.display_name = user.username

                user_settings.save()
        
        invade_me_test = Dominion.objects.get(name="p-nofaction")
        invade_me_test.name = "Invade me"

        for unit in Unit.objects.filter(ruler=invade_me_test):
            unit.quantity_at_home = 10
            unit.save()

        invade_me_test.protection_ticks_remaining = 0
        invade_me_test.save()

        testuser = User.objects.get(username="test")
        testdominion = initialize_dominion(user=testuser, faction=Faction.objects.get(name=my_faction_name), display_name="ERIKTEST")
        testdominion.protection_ticks_remaining = 0
        testdominion.discovery_points = 5000
        testdominion.save()

        buildings_each = int(100 / Building.objects.filter(ruler=testdominion).count())
        for building in Building.objects.filter(ruler=testdominion):
            building.percent_of_land = buildings_each
            building.save()

        for unit in Unit.objects.filter(ruler=testdominion):
            unit.quantity_at_home = 500
            unit.save()

        for resource in Resource.objects.filter(ruler=testdominion):
            resource.quantity = my_starting_resource_quantity
            resource.save()

        admindominion = Dominion.objects.get(name="p-admin")
        admindominion.protection_ticks_remaining = 0
        admindominion.discovery_points = 5000
        admindominion.save()

        for unit in Unit.objects.filter(ruler=admindominion):
            unit.quantity_at_home = 10000
            unit.save()

        print("Done generating stuff.")
