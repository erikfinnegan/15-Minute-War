from django.core.management.base import BaseCommand

from maingame.models import Unit
from maingame.utils.testme import test_me


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        testdominion = test_me("mecha-dragon")
        testdominion.perk_dict["capacity_max"] = 15
        testdominion.save()

        mechadragon = Unit.objects.get(ruler=testdominion, name="Mecha-Dragon")
        mechadragon.lose(499)
        mechadragon.save()
