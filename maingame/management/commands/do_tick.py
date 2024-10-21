from datetime import datetime
from zoneinfo import ZoneInfo
from django.core.management.base import BaseCommand

from maingame.models import Round
from maingame.tick_processors import do_global_tick

class Command(BaseCommand):
    help = "Do a tick"

    def handle(self, *args, **options):
        print("start")
        round = Round.objects.first()
        print("round")
        print(round)
        print()

        now = datetime.now(ZoneInfo('America/New_York'))

        if now > round.start_time and not round.has_started:
            print("startround")
            round.has_started = True
        elif round.ticks_left > 0 and round.has_started:
            print("ticksleft -= 1")
            round.ticks_left -= 1
            
            if round.ticks_left <= 0:
                round.has_ended = True

        print("save round")
        round.save()

        do_global_tick()