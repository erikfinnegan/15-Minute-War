from django.core.management.base import BaseCommand

from maingame.utils.testme import test_me


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        testdominion = test_me("blessed order")

        heretics = Resource.objects.get(ruler=testdominion, name="heretics")
        heretics.quantity = 10000
        heretics.save()

        testdominion.perk_dict["corruption"] = 999000
        testdominion.save()