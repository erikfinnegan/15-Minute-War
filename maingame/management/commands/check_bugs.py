from django.core.management.base import BaseCommand

from maingame.models import Round

from maingame.game_pieces.initialize import initialize_blessed_order_discoveries

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print()
        print()
        print()
        print("Checking bugs...")
        print()
        
        round = Round.objects.first()

        for bug in round.bugs:
            print(bug)

        print()
        print()
        print()
