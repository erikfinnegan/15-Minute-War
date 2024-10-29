from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        # testuser = User.objects.get(username="test")
        # testdominion = Dominion.objects.get(associated_user=testuser)

        # unit = Unit.objects.get(ruler=testdominion, name="archer")
        # unit.advance_training_and_returning()
