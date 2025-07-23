from django.core.management.base import BaseCommand

from maingame.models import Dominion
from maingame.utils.testme import test_me


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        testdominion = test_me("dwarf")

        for dom in Dominion.objects.all():
            if dom != testdominion:
                testdominion.perk_dict["book_of_grudges"][dom.strid] = {
                    "pages": 100,
                    "animosity": 1000,
                }
        
        testdominion.save()

        print("Done generating stuff.")
