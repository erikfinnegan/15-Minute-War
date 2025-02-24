from random import randint
from django.core.management.base import BaseCommand

from maingame.formatters import get_fast_return_cost_multiplier
from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit
from django.contrib.auth.models import User

from maingame.utils.utils_sludgeling import create_random_sludgene
from tick_processors import audit_for_bugs

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Auditing bugs")
        
        audit_for_bugs()