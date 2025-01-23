from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Round
from maingame.game_pieces.initialize import initialize_game_pieces


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Initializing game pieces...")

        # Deletes and inits everything
        initialize_game_pieces()

        round = Round.objects.first()

        # 4 ticks per hour * 24 hours in a day * X days of round
        how_many_days_this_round = 7
        round.ticks_to_end = 4 * 24 * how_many_days_this_round

        round.save()

        print("Done initializing.")
