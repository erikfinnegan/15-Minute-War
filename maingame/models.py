import math, random
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime
from zoneinfo import ZoneInfo

from maingame.formatters import format_minutes


class Deity(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    
    def __str__(self):
        return f"{self.name}"
        
    class Meta: 
        verbose_name_plural = "deities"
        

class UserSettings(models.Model):
    associated_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    display_name = models.CharField(max_length=50, null=True, blank=True, default="")
    timezone = models.CharField(max_length=50, default="UTC")
    show_tutorials = models.BooleanField(default=True)
    theme = models.CharField(max_length=50, null=True, blank=True, default="OpenDominion")
    use_am_pm = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.display_name}'s settings"


class Dominion(models.Model):
    associated_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    name = models.CharField(max_length=30, null=True, blank=True, unique=True)
    is_starving = models.BooleanField(default=False)
    has_unread_events = models.BooleanField(default=False)
    protection_ticks_remaining = models.IntegerField(default=72)
    complacency = models.IntegerField(default=0)
    has_tick_units = models.BooleanField(default=False)
    is_abandoned = models.BooleanField(default=False)
    acres = models.IntegerField(default=100)
    incoming_acres_dict = models.JSONField(default=dict, blank=True)
    successful_invasions = models.IntegerField(default=0)
    failed_defenses = models.IntegerField(default=0)

    primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    primary_resource_per_acre = models.IntegerField(default=0)
    
    building_primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    building_secondary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    building_primary_cost_per_acre = models.IntegerField(default=100)
    building_secondary_cost_per_acre = models.IntegerField(default=50)

    upgrade_cost = models.IntegerField(default=10000)
    upgrade_exponent = models.FloatField(default=1.03, null=True, blank=True)
    
    perk_dict = models.JSONField(default=dict, blank=True)
    faction_name = models.CharField(max_length=50, null=True, blank=True)

    discovery_points = models.IntegerField(default=0)
    available_discoveries = models.JSONField(default=list, blank=True)
    learned_discoveries = models.JSONField(default=list, blank=True)

    last_sold_resource_name = models.CharField(max_length=50, null=True, blank=True)
    last_bought_resource_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def rulers_display_name(self):
        return UserSettings.objects.get(associated_user=self.associated_user).display_name
    
    @property
    def ticks_til_training_time(self):
        return self.protection_ticks_remaining - 12
    
    @property
    def resources(self):
        return Resource.objects.filter(ruler=self)

    @property
    def can_attack(self):
        if self.protection_ticks_remaining > 0:
            return False
        elif self.perk_dict.get("inquisition_rate") and self.perk_dict.get("inquisition_rate") > 0:
            return False
        
        return True

    @property
    def complacency_penalty_readout(self):
        penalty = self.complacency / 2

        return penalty

    @property
    def offense_multiplier(self):
        return 1

    @property
    def defense(self):
        defense = 0

        for unit in Unit.objects.filter(ruler=self):
            defense += unit.quantity_at_home * unit.dp

        multiplier = 1 - (self.complacency / 200)

        return max(0, int(defense * multiplier))
    
    @property
    def defense_short(self):
        defense = self.defense

        if defense < 100000: # 100k
            return f"{defense:2,}"
        elif defense < 1000000: # 1m
            return f"{int(defense/1000)}k"
        else:
            return f"{round(defense/1000000, 2)}m"

    @property
    def strid(self):
        return f"{self.id}"

    @property
    def building_count(self):
        building_count = 0
        
        for building in Building.objects.filter(ruler=self):
            building_count += building.quantity

        return building_count

    @property
    def has_units_returning(self):
        for unit in Unit.objects.filter(ruler=self):
            if unit.quantity_returning > 0:
                return True
            
        return False

    @property
    def building_primary_cost(self):
        return self.building_primary_cost_per_acre * self.acres
    
    @property
    def building_secondary_cost(self):
        return self.building_secondary_cost_per_acre * self.acres
    
    @property 
    def barren_acres(self):
        barren_acres = self.acres

        for building in Building.objects.filter(ruler=self):
            barren_acres -= building.quantity

        return barren_acres

    @property
    def incoming_acres(self):
        total = 0

        for key, value in self.incoming_acres_dict.items():
            total += value

        return total

    @property
    def header_rows(self):
        iterator = -1
        row_number = 0
        header_rows = {}

        for resource in Resource.objects.filter(ruler=self):
            iterator += 1
            
            if iterator % math.ceil(Resource.objects.filter(ruler=self).count() / 2) == 0:
                row_number += 1
                header_rows[str(row_number)] = []

            header_rows[str(row_number)].append({
                "name": resource.name,
                "quantity": f"{int(resource.quantity):,}"
            })

        return header_rows
    
    @property
    def ticks_to_next_discovery(self):
        return max(0, 50 - self.discovery_points % 50)
    
    @property
    def discoveries_to_make(self):
        return int(self.discovery_points / 50)
    
    @property
    def sorted_units(self):
        sorted_list = list(Unit.objects.filter(ruler=self))

        def op_dp_ratio(unit: Unit):
            if unit.dp == 0:
                return 99999999
            else:
                return unit.op / unit.dp
        
        sorted_list.sort(key=op_dp_ratio)

        return sorted_list

    def get_production(self, resource_name):
        production = 0

        for building in Building.objects.filter(ruler=self, resource_produced_name=resource_name):
            production += building.amount_produced * building.quantity

        if resource_name == self.primary_resource_name:
            production += self.primary_resource_per_acre * self.acres

        for unit in Unit.objects.filter(ruler=self):
            if f"{resource_name}_per_tick" in unit.perk_dict:
                production += unit.perk_dict[f"{resource_name}_per_tick"] * unit.quantity_at_home

        return production
    
    def get_consumption(self, resource_name):
        consumption = 0

        for unit in Unit.objects.filter(ruler=self):
            for upkeep_resource_name, upkeep in unit.upkeep_dict.items():
                if resource_name == upkeep_resource_name:
                    consumption += int(unit.quantity_trained_and_alive * upkeep)

        if resource_name == "faith" and "sinners" in self.perk_dict:
            consumption += self.perk_dict["sinners"]

        if resource_name == "faith" and "crusade_ticks_left" in self.perk_dict and self.perk_dict["crusade_ticks_left"] > 0:
            consumption += self.acres

        return consumption
    
    def do_resource_production(self):
        for resource in Resource.objects.filter(ruler=self):
            resource.quantity += self.get_production(resource.name)
            resource.quantity -= self.get_consumption(resource.name)

            self.is_starving = False

            if resource.quantity < 0:
                self.is_starving = True
                for unit in Unit.objects.filter(ruler=self):
                    if resource.name in unit.upkeep_dict:
                        unit.quantity_at_home = math.ceil(unit.quantity_at_home * 0.99)
                        
                        for tick, quantity in unit.returning_dict.items():
                            unit.returning_dict[tick] = math.ceil(quantity * 0.99)

                        unit.save()

            resource.quantity = max(0, resource.quantity)            
            resource.save()
            self.save()

    def advance_land_returning(self):
        for key, value in self.incoming_acres_dict.items():
            if key == "1":
                self.acres += value
            else:
                new_key = str(int(key) - 1)
                self.incoming_acres_dict[new_key] = value
            
            self.incoming_acres_dict[key] = 0

        self.save()

    def do_perks(self):
        if "book_of_grudges" in self.perk_dict and self.protection_ticks_remaining == 0:
            for dominion in Dominion.objects.filter(~Q(id=self.id), protection_ticks_remaining=0):
                if str(dominion.id) in self.perk_dict["book_of_grudges"]:
                    self.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] += self.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] * 0.003
                    
                    if self.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] >= 100:
                        rounding = 2
                    else:
                        rounding = 3

                    self.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] = round(self.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"], rounding)

        if "sinners_per_hundred_acres_per_tick" in self.perk_dict and "sinners" in self.perk_dict:
            if "inquisition_ticks_left" in self.perk_dict and self.perk_dict["inquisition_ticks_left"] > 0:
                self.perk_dict["sinners"] -= self.perk_dict["inquisition_rate"]
                self.perk_dict["sinners"] = max(0, self.perk_dict["sinners"])
                self.perk_dict["inquisition_ticks_left"] -= 1

                if self.perk_dict["inquisition_ticks_left"] == 0:
                    self.perk_dict["inquisition_rate"] = 0
                    self.perk_dict["sinners"] = 0
            elif self.protection_ticks_remaining == 0:
                self.perk_dict["sinners"] += self.perk_dict["sinners_per_hundred_acres_per_tick"]

        if "crusade_ticks_left" in self.perk_dict and self.perk_dict["crusade_ticks_left"] > 0:
            self.perk_dict["crusade_ticks_left"] -= 1

            if self.perk_dict["crusade_ticks_left"] == 0:
                self.perk_dict["martyr_cost"] = 1000

        if "experiment_cost_coefficient" in self.perk_dict and self.perk_dict["experiment_cost_coefficient"] > 0:
            self.perk_dict["experiment_cost_coefficient"] -= 1

    def do_tick(self):
        self.do_resource_production()
        self.advance_land_returning()
        self.do_perks()
        
        self.discovery_points += 1

        for unit in Unit.objects.filter(ruler=self):
            unit.advance_training_and_returning()
        
        if self.protection_ticks_remaining == 0:
            self.complacency += 1

        if self.has_tick_units:
            do_tick_units(self)

        self.save()


class Resource(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        if self.ruler:
            return f"{self.ruler}'s {self.name} {self.name}"
            
        return f"{self.name} {self.name}"
    
    @property
    def production(self):
        return self.ruler.get_production(self.name)


class Faction(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True, default="Placeholder description")
    primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    primary_resource_per_acre = models.IntegerField(default=0)
    building_primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    building_secondary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    starting_buildings = models.JSONField(default=list, blank=True)
    building_primary_cost_per_acre = models.IntegerField(default=10)
    building_secondary_cost_per_acre = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name}"


class Building(models.Model):
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    resource_produced_name = models.CharField(max_length=50, null=True, blank=True)
    amount_produced = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    trade_multiplier = models.IntegerField(default=0)
    defense_multiplier = models.IntegerField(default=0)
    upgrades = models.IntegerField(default=0)
    is_buildable = models.BooleanField(default=True)
    construction_dict = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        if self.ruler:
            return f"{self.ruler}'s {self.name}"
        else:
            return f"🟩Base --- {self.name}"
        
    @property
    def upgrade_cost(self):
        cost = self.ruler.upgrade_cost

        for _ in range(self.upgrades):
            cost = cost ** self.ruler.upgrade_exponent

        return int(cost)
    
    @property
    def description(self):
        perks = []
        if self.amount_produced > 0:
            resource_produced = Resource.objects.get(ruler=self.ruler, name=self.resource_produced_name)
            perks.append(f"Produces {self.amount_produced} {resource_produced.name} per tick.")

        return " ".join(perks)
    
    @property
    def percent(self):
        percent = (self.quantity / self.ruler.acres) * 100

        if percent.is_integer():
            return int(percent)
        
        return round(percent, 2)
    
    def max_x_or_self_quantity(self, x):
        return max(x, self.quantity)
    

class Unit(models.Model):
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    dp = models.IntegerField(default=0)
    op = models.IntegerField(default=0)
    is_trainable = models.BooleanField(default=True)
    cost_dict = models.JSONField(default=dict, blank=True)
    upkeep_dict = models.JSONField(default=dict, blank=True)
    training_dict = models.JSONField(default=dict, blank=True)
    returning_dict = models.JSONField(default=dict, blank=True)
    quantity_at_home = models.IntegerField(default=0)
    perk_dict = models.JSONField(default=dict, blank=True)
    faction = models.ForeignKey(Faction, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        base_name = f"{self.name} ({self.op}/{self.dp}) -- {self.id}"

        if self.ruler:
            return f"{self.ruler.name}'s {base_name}"
        
        return f"🟩Base --- {base_name}"
    
    @property
    def power_display(self):
        return f"{self.op:2,} / {self.dp:2,}"
    
    @property
    def quantity_trained_and_alive(self):
        return self.quantity_at_home + self.quantity_returning

    @property
    def max_affordable(self):
        if not self.ruler:
            return 0
        
        max_affordable = 9999999999999

        for resource_name, amount in self.cost_dict.items():
            resource = Resource.objects.get(ruler=self.ruler, name=resource_name)

            if resource.quantity > 0:
                max_affordable = min(max_affordable, math.floor(resource.quantity/amount))
            else:
                max_affordable = 0

        return max_affordable
    
    @property
    def perk_text(self):
        perk_text = ""
        
        if "surplus_research_consumed_to_add_one_op_and_dp" in self.perk_dict:
            perk_text += f"""Consumes 10% of any research points beyond your most expensive upgrade each tick. Gains 1 OP and 1 DP per  
            {self.perk_dict['surplus_research_consumed_to_add_one_op_and_dp']} consumed"""

        if "random_grudge_book_pages_per_tick" in self.perk_dict:
            pages_per_tick = self.perk_dict["random_grudge_book_pages_per_tick"]
            perk_text += f"Adds {pages_per_tick} pages to an existing grudge in your book of grudges each tick. "

        if "always_dies_on_offense" in self.perk_dict:
            perk_text += "Always dies when sent on an invasion. "

        if "immortal" in self.perk_dict:
            perk_text += "Does not die in combat. "

        if "faith_per_tick" in self.perk_dict:
            faith_produced = self.perk_dict["faith_per_tick"]
            perk_text += f"Produces {faith_produced} faith per tick. "

        return perk_text
    
    @property
    def has_perks(self):
        return self.perk_dict != {}
    
    def advance_training_and_returning(self):
        for key, value in self.training_dict.items():
            if key == "1":
                self.quantity_at_home += value
            else:
                new_key = str(int(key) - 1)
                self.training_dict[new_key] = value
            
            self.training_dict[key] = 0

        for key, value in self.returning_dict.items():
            if key == "1":
                self.quantity_at_home += value
            else:
                new_key = str(int(key) - 1)
                self.returning_dict[new_key] = value
            
            self.returning_dict[key] = 0

        self.save()

    @property
    def quantity_in_training(self):
        total = 0

        for key, value in self.training_dict.items():
            total += value

        return total
    
    @property
    def quantity_returning(self):
        total = 0

        for key, value in self.returning_dict.items():
            total += value

        return total


class Battle(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    attacker = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, related_name="battles_attacked")
    defender = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, related_name="battles_defended")
    winner = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, related_name="battles_won")
    units_sent_dict = models.JSONField(default=dict, null=True, blank=True)
    units_defending_dict = models.JSONField(default=dict, null=True, blank=True)
    # casualties_dict = models.JSONField(default=dict, null=True, blank=True)
    battle_report_notes = models.JSONField(default=list, null=True, blank=True)
    op = models.IntegerField(default=0)
    dp = models.IntegerField(default=0)
    acres_conquered = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.attacker} invades {self.defender}"

    @property
    def event_text(self):
        if self.winner == self.attacker:
            return f"{self.winner} invaded {self.defender} and conquered {self.acres_conquered:2,} acres, plus {self.acres_conquered:2,} more from surrounding areas"
        else:
            return f"{self.winner} repelled an attack from {self.attacker}"
        

class Event(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    reference_id = models.IntegerField(default=0)
    reference_type = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="?")
    message_override = models.CharField(max_length=150, default="")
    notified_dominions = models.ManyToManyField(Dominion)

    def __str__(self):
        return f"{self.message}"

    @property
    def message(self):
        if self.reference_type == "battle":
            battle = Battle.objects.get(id=self.reference_id)
            return battle.event_text
        elif self.reference_type == "signup":
            return self.message_override
        
        return "Unknown event type"
    
    @property
    def notified_dominions_list(self):
        return [*self.notified_dominions.all()]
    

class Round(models.Model):
    has_started = models.BooleanField(default=False)
    has_ended = models.BooleanField(default=False)
    winner = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    trade_price_dict = models.JSONField(default=dict, blank=True)
    base_price_dict = models.JSONField(default=dict, blank=True)
    resource_bank_dict = models.JSONField(default=dict, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    ticks_passed = models.IntegerField(default=0)
    ticks_to_end = models.IntegerField(default=0)

    @property
    def allow_ticks(self):
        return self.has_started and not self.has_ended
    
    @property
    def ticks_left(self):
        return self.ticks_to_end - self.ticks_passed
    
    @property
    def time_til_round_start(self):
        if self.has_started:
            return False
        
        now = datetime.now(ZoneInfo('UTC'))
        delta = self.start_time - now
        minutes_from_days = delta.days * 24 * 60
        minutes_from_seconds = int(delta.seconds / 60)

        return format_minutes(minutes_from_days + minutes_from_seconds)
    
    @property
    def time_til_round_end(self):
        now = datetime.now(ZoneInfo('America/New_York'))
        minutes_left_in_current_tick = 15 - (now.minute % 15)
        minutes_left_in_remaining_full_ticks = (self.ticks_left - 1) * 15
        return format_minutes(minutes_left_in_remaining_full_ticks + minutes_left_in_current_tick)
        

class Discovery(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    requirement = models.CharField(max_length=50, null=True, blank=True)
    not_for_factions = models.JSONField(default=list, blank=True)
    associated_unit_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def associated_unit(self):
        if self.associated_unit_name:
            return Unit.objects.get(name=self.associated_unit_name, ruler=None)
        
        return None


class Spell(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    requirement = models.CharField(max_length=50, null=True, blank=True)
    mana_cost_per_acre = models.IntegerField(default=99)
    is_starter = models.BooleanField(default=False)

    def __str__(self):
        if self.ruler:
            return f"{self.ruler}'s {self.name}"
        
        return f"🟩Base --- {self.name}"
    
    @property
    def mana_cost(self):
        if self.ruler == None:
            return 1
        
        return self.ruler.acres * self.mana_cost_per_acre
    

def do_tick_units(dominion: Dominion):
    for unit in Unit.objects.filter(ruler=dominion):
        for perk, value in unit.perk_dict.items():
            match perk:
                case "surplus_research_consumed_to_add_one_op_and_dp":
                    research = Resource.objects.get(ruler=dominion, name="research")
                    highest_upgrade_cost = 0

                    for building in Building.objects.filter(ruler=dominion):
                        highest_upgrade_cost = max(highest_upgrade_cost, building.upgrade_cost)

                    if research.quantity > highest_upgrade_cost + 10:
                        surplus_research_points = research.quantity - highest_upgrade_cost
                        consumable_research_points = int(surplus_research_points * 0.1)
                        instances_consumed = int(consumable_research_points / value)

                        research.quantity -= instances_consumed * value
                        unit.op += instances_consumed
                        unit.dp += instances_consumed
                        research.save()
                        unit.save()
                case "random_grudge_book_pages_per_tick":
                    keys_list = list(dominion.perk_dict["book_of_grudges"].keys())

                    if len(keys_list) > 0:
                        random_key = random.choice(keys_list)
                        dominion.perk_dict["book_of_grudges"][random_key]["pages"] += value
                        dominion.save()
