from math import ceil
from random import randint
from django.core.management.base import BaseCommand

from maingame.formatters import get_fast_return_cost_multiplier
from maingame.models import UserSettings, Resource, Round, Event, Dominion, Unit, MechModule
from django.contrib.auth.models import User

from maingame.utils.utils_sludgeling import create_random_sludgene
from maingame.utils.utils import generate_unit_cost_dict

class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("UNIT COST CALCULATOR")
        print()
        
        op = 8
        dp = 4
        secondary_resource_name = "food"
        casualty_multiplier = 1
        return_ticks = 12
        
        # primary secondary hybrid
        cost_type = "hybrid"
        
        
        # Goblin is 1/3, biclops is 4, etc.
        unit_chunks = 1
        primary_resource_name = "gold"
        cost_multiplier = 1
        
        cost_dict = generate_unit_cost_dict(op, dp, primary_resource_name, secondary_resource_name, cost_type, casualty_multiplier, return_ticks, cost_multiplier)
        
        for k, v in cost_dict.items():
            cost_dict[k] = int(v * unit_chunks)
        
        output_str = "" if unit_chunks == 1 else f"{unit_chunks} of a "
        output_str += f"{op}/{dp} using {secondary_resource_name}, cost type {cost_type}. Takes {casualty_multiplier}x casualties and returns in {return_ticks} ticks."
        print(output_str)
        print()
        print(cost_dict)
        print()
        
        