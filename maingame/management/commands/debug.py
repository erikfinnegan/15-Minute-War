from django.core.management.base import BaseCommand

from maingame.models import UserSettings, Resource
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("IT'S DEBUG TIME BABY")
        user = User.objects.get(username="erik")
        user_settings = UserSettings.objects.get(associated_user=user)

