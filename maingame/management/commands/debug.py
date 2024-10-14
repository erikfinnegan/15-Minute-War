from django.core.management.base import BaseCommand

from maingame.models import Player, Deity, Unit, Building
from django.contrib.auth.models import User

from maingame.utils import update_trade_prices

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        # testuser = User.objects.get(username="test")
        # testplayer = Player.objects.get(associated_user=testuser)

        # unit = Unit.objects.get(ruler=testplayer, name="archer")
        # unit.advance_training_and_returning()
