from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Dominion, Spell, Resource, Unit, Building
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        username_to_delete = "asdf"

        print(f"Deleting user {username_to_delete}")
        
        user = User.objects.filter(username=username_to_delete).first()
        
        try:
            user_settings = UserSettings.objects.get(associated_user=user)
            user_settings.delete()
        except:
            print(f"User {username_to_delete} not found")
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

        try:
            user.delete()
        except:
            pass

        print()

        for username_to_delete in ["test2", "test3", "test4", "test5", "new", "newb", "noob"]:
            user = User.objects.filter(username=username_to_delete).first()
        
            try:
                user_settings = UserSettings.objects.get(associated_user=user)
                user_settings.delete()
            except:
                print(f"User {username_to_delete} not found")
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

            try:
                user.delete()
            except:
                pass
