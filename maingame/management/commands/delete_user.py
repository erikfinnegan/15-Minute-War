from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Dominion, Spell, Resource, Unit, Building
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        username_to_delete = "newsignup"

        print(f"Deleting user {username_to_delete}")
        
        user = User.objects.get(username=username_to_delete)
        
        try:
            user_settings = UserSettings.objects.get(associated_user=user)
            user_settings.delete()
        except:
            pass

        try:
            dominion = Dominion.objects.get(associated_user=user)
            print(dominion)

            for x in Spell.objects.filter(ruler=dominion):
                x.delete()
            
            for x in Resource.objects.filter(ruler=dominion):
                x.delete()

            for x in Unit.objects.filter(ruler=dominion):
                x.delete()

            for x in Building.objects.filter(ruler=dominion):
                x.delete()
        except:
            pass

        user.delete()