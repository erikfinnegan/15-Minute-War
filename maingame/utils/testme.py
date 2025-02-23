from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.formatters import get_goblin_name
from maingame.models import Dominion, Unit, Faction, Resource, Building, UserSettings, Round
from maingame.game_pieces.initialize import initialize_game_pieces
from maingame.utils.dominion_controls import initialize_dominion
from datetime import datetime
from zoneinfo import ZoneInfo

def test_me(my_faction_name):
    their_faction_name = "goblin"

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
            if user.username == "finn":
                name = "Invade me"
            elif user.username == "admin":
                name = "Strong Guy"
            else:
                name = get_goblin_name()

            dominion = initialize_dominion(user=user, faction=Faction.objects.get(name=their_faction_name), display_name=name)
            dominion.protection_ticks_remaining = 0
            dominion.save()
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
    
    invade_me_test = Dominion.objects.get(name="Invade me")

    for unit in Unit.objects.filter(ruler=invade_me_test):
        unit.gain(100)

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
        unit.gain(500)

    for resource in Resource.objects.filter(ruler=testdominion):
        resource.gain(my_starting_resource_quantity)

    admindominion = Dominion.objects.get(name="Strong Guy")
    admindominion.protection_ticks_remaining = 0
    admindominion.discovery_points = 5000
    admindominion.save()
    
    for resource in Resource.objects.filter(ruler=admindominion):
        resource.gain(my_starting_resource_quantity)

    for unit in Unit.objects.filter(ruler=admindominion):
        unit.gain(100000)

    testdominion.save()

    print("Done generating stuff.")

    return testdominion