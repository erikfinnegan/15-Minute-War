from django.core.management.base import BaseCommand

from maingame.models import Dominion, Unit
from maingame.utils.testme import test_me
from maingame.utils.utils_sludgeling import create_random_sludgene


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        testdominion = test_me("sludgeling")
        
        for _ in range(10):
            sludgene = create_random_sludgene(Dominion.objects.get(name="ERIKTEST"))

        for unit in Unit.objects.filter(ruler=testdominion):
            unit.gain(2000)
            
        testdominion.perk_dict["splices"] = 9999
        testdominion.perk_dict["masterpieces_to_create"] = 1
        testdominion.save()