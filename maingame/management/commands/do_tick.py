from datetime import datetime
from zoneinfo import ZoneInfo
from django.core.management.base import BaseCommand

from maingame.models import Round
from maingame.tick_processors import do_global_tick

class Command(BaseCommand):
    help = "Do a tick"

    def handle(self, *args, **options):
        do_global_tick()