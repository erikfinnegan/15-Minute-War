from django.core.management.base import BaseCommand

from maingame.static_init import initialize_static_elements


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Generating stuff...")

        initialize_static_elements()

        print("Done generating stuff.")
