from random import randint
from django.core.management.base import BaseCommand

from maingame.models import Player, Terrain, Deity, Region, Unit, Building, BuildingType, Faction
from django.contrib.auth.models import User

from maingame.tick_processors import do_resource_production, do_tick


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        def get_unit_gold_cost(unit: Unit, discount=0):
            base_value = (unit.dp * 1.2) + (unit.op * 0.8)
            base_gold = 10 * base_value
            scaled_gold = base_gold ** 1.2
            scaled_gold = scaled_gold * ((100-discount)/100)
            rounded_gold = 25 * round(scaled_gold/25)

            return rounded_gold


        # def generate_random_unit(terrain: Terrain):
        #     power_level = min(randint(1,4), randint(1,4))

        #     base_power = 6
            
        #     for _ in range(power_level):
        #         base_power *= randint(1, 4)

        #     op = int(terrain.unit_op_dp_ratio * base_power)
        #     dp = int((2 - terrain.unit_op_dp_ratio) * base_power)

        #     new_unit = Unit.objects.create(
        #         name=f"Testunit{randint(1,10000)}",
        #         op=op,
        #         dp=dp,
        #     )

        #     return new_unit

        def generate_bespoke_unit(name, op, dp, secondary_resource):
            unit = Unit.objects.create(name=name, op=op, dp=dp)
            gold_cost = get_unit_gold_cost(unit)

            secondary_building_ticks = gold_cost / 533
            secondary_resource_production_building = BuildingType.objects.filter(resource_produced=secondary_resource).first()
            secondary_cost_amount = secondary_building_ticks * secondary_resource_production_building.amount_produced
            secondary_cost_amount = 5 * round(secondary_cost_amount/5)

            print()
            print(f"{name}")
            print(f"{op}/{dp}")
            print(f"{gold_cost} gold")
            print(f"{secondary_cost_amount} {secondary_resource}")
            print()

            unit.delete()


        print("IT'S DEBUG TIME BABY")
        # testuser = User.objects.get(username="test")
        # testplayer = Player.objects.get(associated_user=testuser)

        generate_bespoke_unit("archer", 2, 4, "🪵"),
        generate_bespoke_unit("knight", 5, 6, "🪨"),
        generate_bespoke_unit("trebuchet", 10, 0, "🪵")
