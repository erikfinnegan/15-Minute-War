from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from maingame.models import Player, Deity, Terrain, Region, Faction, BuildingType
from maingame.static_init import initialize_game_pieces
from maingame.utils import assign_faction, construct_building


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Generating stuff...")

        initialize_game_pieces()

        for user in User.objects.all():
            new_player = Player.objects.create(associated_user=user, name=f"ERROR {user.username}")
            new_player.resource_dict["🍞"] = 1
            new_player.save()

        testplayer = Player.objects.get(associated_user=User.objects.get(username="test"))

        assign_faction(testplayer, Faction.objects.get(name="human"))

        testplayer.adjust_resource("🪙", 5000)
        testplayer.adjust_resource("🪵", 5000)
        testplayer.adjust_resource("🪨", 5000)
        testplayer.save()

        region_templates = [
            {
                "ruler": testplayer,
                "name": "New Rhode Island",
                "primary_terrain": Terrain.objects.get(name="grassy"),
                "secondary_terrain": Terrain.objects.get(name="mountainous"),
                "deity": Deity.objects.get(name="Rubecus"),
            },
            {
                "ruler": testplayer,
                "name": "New Michigan",
                "primary_terrain": Terrain.objects.get(name="forested"),
                "secondary_terrain": Terrain.objects.get(name="coastal"),
                "deity": Deity.objects.get(name="Hunger Without End"),
            },
            {
                "ruler": testplayer,
                "name": "Richland",
                "primary_terrain": Terrain.objects.get(name="beautiful"),
                "secondary_terrain": Terrain.objects.get(name="swampy"),
                "deity": Deity.objects.get(name="Hunger Without End"),
            },
            {
                "ruler": testplayer,
                "name": "Brokeland",
                "primary_terrain": Terrain.objects.get(name="barren"),
                "secondary_terrain": Terrain.objects.get(name="swampy"),
                "deity": Deity.objects.get(name="Hunger Without End"),
            },
        ]

        newri = Region.objects.create(**region_templates[0])
        newmi = Region.objects.create(**region_templates[1])
        richland = Region.objects.create(**region_templates[2])
        brokeland = Region.objects.create(**region_templates[3])

        my_farm = BuildingType.objects.get(ruler=testplayer, name="farm")
        my_quarry = BuildingType.objects.get(ruler=testplayer, name="quarry")
        my_lumberyard = BuildingType.objects.get(ruler=testplayer, name="lumberyard")
        my_tower = BuildingType.objects.get(ruler=testplayer, name="tower")
        my_school = BuildingType.objects.get(ruler=testplayer, name="school")

        construct_building(testplayer, newri.id, my_farm.id, 2)
        construct_building(testplayer, newri.id, my_quarry.id, 1)

        construct_building(testplayer, newmi.id, my_lumberyard.id, 1)
        construct_building(testplayer, newmi.id, my_school.id, 2)

        construct_building(testplayer, richland.id, my_tower.id, 1)
        construct_building(testplayer, richland.id, my_school.id, 2)

        construct_building(testplayer, brokeland.id, my_school.id, 3)

        print("Done generating stuff.")
