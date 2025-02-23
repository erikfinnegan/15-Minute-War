from django.core.management.base import BaseCommand

from maingame.models import Unit
from maingame.utils.testme import test_me


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        testdominion = test_me("sludgeling")

        for unit in Unit.objects.filter(ruler=testdominion):
            unit.gain(2000)