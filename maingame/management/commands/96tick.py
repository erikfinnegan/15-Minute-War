from datetime import datetime
from zoneinfo import ZoneInfo
from django.core.management.base import BaseCommand

from maingame.tick_processors import do_global_tick

class Command(BaseCommand):
    help = "Do a tick"

    def handle(self, *args, **options):
        print("Running 12tick script", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))
        
        for _ in range(96):
            do_global_tick()
        
        print("Finished 12tick script", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))