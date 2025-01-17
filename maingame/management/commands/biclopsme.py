from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Dominion, Unit, Faction, Resource, Building, UserSettings, Round
from maingame.game_pieces.initialize import initialize_game_pieces
from maingame.utils.dominion_controls import initialize_dominion
from datetime import datetime
from zoneinfo import ZoneInfo


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        my_faction_name = "biclops"

        my_starting_resource_quantity = 1234567

        print("Generating stuff...")

        initialize_game_pieces()

        round = Round.objects.first()
        round.start_time = datetime.now(ZoneInfo('America/New_York'))
        round.has_started = True
        round.ticks_to_end = 999
        round.save()

        for user in User.objects.all():
            if user.username != "test" and user.username != "dontdominionme":
                dominion = initialize_dominion(user=user, faction=Faction.objects.get(name="biclops"), display_name=f"p-{user.username}")
                dominion.protection_ticks_remaining = 0
                dominion.perk_dict["partner_attack_on_sight"] = True
                dominion.save()
                farm = Building.objects.get(ruler=dominion, name="farm")
                farm.quantity = 50
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

        for unit in Unit.objects.all():
            unit.quantity_at_home = 1000
            unit.save()
        
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
        testdominion.discovery_points = 1000
        testdominion.perk_dict["partner_patience"] = 1
        testdominion.perk_dict["partner_attack_on_sight"] = True
        testdominion.save()

        buildings_each = int(100 / Building.objects.filter(ruler=testdominion).count())
        for building in Building.objects.filter(ruler=testdominion):
            building.percent_of_land = buildings_each
            building.save()

        for unit in Unit.objects.filter(ruler=testdominion):
            unit.quantity_at_home = 5000
            unit.save()

        for resource in Resource.objects.filter(ruler=testdominion):
            resource.quantity = my_starting_resource_quantity
            resource.save()

        admindominion = Dominion.objects.get(name="p-admin")
        admindominion.protection_ticks_remaining = 0
        admindominion.discovery_points = 9000
        admindominion.perk_dict["partner_attack_on_sight"] = True
        admindominion.save()

        for unit in Unit.objects.filter(ruler=admindominion):
            unit.quantity_at_home = 100000
            unit.save()

        print("Done generating stuff.")
