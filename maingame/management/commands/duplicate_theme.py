from random import randint
from django.core.management.base import BaseCommand

from maingame.models import Theme

class Command(BaseCommand):
    help = "Two args: the ID of the theme to copy (int), then the name to use for the new one (string)"

    def add_arguments(self, parser):
        parser.add_argument("theme_id", type=int)
        parser.add_argument("new_name", type=str)

    def handle(self, *args, **options):
        try:
            existing_theme = Theme.objects.get(id=options["theme_id"])
            print(f"Cloning theme named {existing_theme.name}")
            new_theme = existing_theme
            new_theme.pk = None
            new_theme.creator_user_settings_id = None
            new_theme.name = options["new_name"]
            new_theme.save()
        except:
            print("No theme found")
            pass