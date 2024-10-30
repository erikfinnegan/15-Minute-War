from datetime import datetime
from zoneinfo import ZoneInfo
from django.core.management.base import BaseCommand

from maingame.models import Round
from maingame.tick_processors import do_global_tick

class Command(BaseCommand):
    help = "Do a tick"

    def handle(self, *args, **options):
        print("Running do_tick.py")
        round = Round.objects.first()

        now = datetime.now(ZoneInfo('America/New_York'))

        if now > round.start_time and not round.has_started:
            round.has_started = True
        elif round.ticks_left > 0 and round.has_started:
            round.ticks_left -= 1
            
            if round.ticks_left <= 0:
                round.has_ended = True

        round.save()

        do_global_tick()