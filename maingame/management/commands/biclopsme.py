from django.core.management.base import BaseCommand

from maingame.utils.testme import test_me


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        testdominion = test_me("biclops")

        testdominion.perk_dict["partner_patience"] = 1
        testdominion.perk_dict["partner_attack_on_sight"] = True
        testdominion.save()
