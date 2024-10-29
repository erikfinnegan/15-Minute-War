from django.core.management.base import BaseCommand

from maingame.models import UserSettings
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        print()
        print("here my settings yo")
        user = User.objects.get(username="erik")
        user_settings = UserSettings.objects.get(associated_user=user)
        # user_settings = UserSettings.objects.first()
        print(user_settings)
        print
        # testuser = User.objects.get(username="test")
        # testdominion = Dominion.objects.get(associated_user=testuser)

        # unit = Unit.objects.get(ruler=testdominion, name="archer")
        # unit.advance_training_and_returning()
