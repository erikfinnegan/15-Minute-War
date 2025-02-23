from django.core.management.base import BaseCommand

from maingame.models import Dominion
from maingame.utils.testme import test_me


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        testdominion = test_me("aether confederacy")

        print("Done generating stuff.")
