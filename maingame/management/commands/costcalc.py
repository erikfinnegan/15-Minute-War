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
        
        op = 5000
        dp = 5000
        secondary_resource_name = "research"
        casualty_multiplier = 0
        return_ticks = 12
        
        # primary secondary hybrid
        cost_type = "secondary"
        
        
        # Goblin is 1/3, biclops is 4, etc.
        units_in_bundle = 1
        primary_resource_name = "gold"
        cost_multiplier = 1 # WARNING
        
        cost_dict = generate_unit_cost_dict(op/units_in_bundle, dp/units_in_bundle, primary_resource_name, secondary_resource_name, cost_type, casualty_multiplier, return_ticks, cost_multiplier)
        
        for k, v in cost_dict.items():
            cost_dict[k] = int(v * units_in_bundle)
        
        output_str = "" if units_in_bundle == 1 else f"{units_in_bundle} bundle "
        output_str += f"{op}/{dp} using {secondary_resource_name}, cost type {cost_type}. Takes {casualty_multiplier}x casualties and returns in {return_ticks} ticks."
        print(output_str)
        print()
        print(cost_dict)
        print()
        
        