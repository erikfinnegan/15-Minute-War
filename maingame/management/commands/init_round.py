from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Round
from maingame.static_init import initialize_game_pieces


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Initializing game pieces...")

        initialize_game_pieces()

        round = Round.objects.first()
        round.ticks_to_end = 4
        round.save()

        print("Done initializing.")
