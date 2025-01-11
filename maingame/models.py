import math, random
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime
from zoneinfo import ZoneInfo

from maingame.formatters import format_minutes, shorten_number


class Deity(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    
    def __str__(self):
        return f"{self.name}"
        
    class Meta: 
        verbose_name_plural = "deities"
        

class Theme(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True, unique=True)
    creator_user_settings_id = models.IntegerField(null=True, blank=True, unique=True)

    base_background = models.CharField(max_length=50, default="#000000")
    base_text = models.CharField(max_length=50, default="#FFFFFF")

    header_background = models.CharField(max_length=50, default="#000000")
    header_text = models.CharField(max_length=50, default="#FFFFFF")

    card_background = models.CharField(max_length=50, default="#000000")
    card_text = models.CharField(max_length=50, default="#FFFFFF")

    input_background = models.CharField(max_length=50, default="#FFFFFF")
    input_text = models.CharField(max_length=50, default="#000000")

    def __str__(self):
        return f"{self.name} -- id: {self.id}"
    
    @property
    def used_by(self):
        users_using = UserSettings.objects.filter(theme_model=self)
        return users_using


class UserSettings(models.Model):
    associated_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    display_name = models.CharField(max_length=25, null=True, blank=True, default="")
    timezone = models.CharField(max_length=50, default="UTC")
    show_tutorials = models.BooleanField(default=True)
    theme = models.CharField(max_length=50, null=True, blank=True, default="OpenDominion")
    theme_model = models.ForeignKey(Theme, on_delete=models.PROTECT, null=True, blank=True)
    use_am_pm = models.BooleanField(default=True)
    is_tutorial = models.BooleanField(default=True)
    hide_zero_resources = models.BooleanField(default=False)
    tutorial_stage = models.IntegerField(default=0)
    juicy_target_threshold = models.FloatField(default=0)

    def __str__(self):
        return f"{self.display_name} -- {self.theme_model}"
    
    @property
    def used_theme(self):
        if self.theme_model:
            return self.theme_model
        else:
            return Theme.objects.get(name="OpenDominion")
        
    @property
    def tutorial_step(self):
        if not self.is_tutorial:
            return 8888
        
        current_step = 0

        if Dominion.objects.filter(associated_user=self.associated_user).exists():
            current_step += 1 #1

            dominion = Dominion.objects.get(associated_user=self.associated_user)
            
            if dominion.faction_name != "dwarf":
                return 8888
            elif len(dominion.learned_discoveries) > 0 and "Palisades" not in dominion.learned_discoveries:
                return 8888
            elif dominion.acres > 500:
                return 8888
            
            if Building.objects.get(ruler=dominion, name="farm").percent_of_land > 0:
                current_step += 1 #2
            
            if dominion.protection_ticks_remaining <= 71:
                current_step += 1 #3

            if dominion.protection_ticks_remaining <= 59:
                current_step += 1 #4

            if Building.objects.get(ruler=dominion, name="quarry").upgrades >= 5:
                current_step += 1 #5

            if dominion.protection_ticks_remaining <= 12:
                current_step += 1 #6

            if Unit.objects.get(ruler=dominion, name="Stoneshield").training_dict["12"] == 500 or dominion.protection_ticks_remaining <= 11:
                current_step += 1 #7

            if Unit.objects.get(ruler=dominion, name="Hammerer").training_dict["12"] == 720 or dominion.protection_ticks_remaining <= 11:
                current_step += 1 #8

            if "Palisades" in dominion.learned_discoveries:
                current_step += 1 #9

            if Unit.objects.filter(ruler=dominion, name="Palisade").exists():
                if Unit.objects.get(ruler=dominion, name="Palisade").training_dict["12"] == 147 or dominion.protection_ticks_remaining <= 11:
                    current_step += 1 #10

            if dominion.protection_ticks_remaining <= 1:
                current_step += 1 #11
            
            if dominion.is_oop:
                current_step += 1 #12

            if dominion.successful_invasions >= 1:
                return 8888

        return current_step


class Dominion(models.Model):
    associated_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    name = models.CharField(max_length=40, null=True, blank=True, unique=True)
    is_starving = models.BooleanField(default=False)
    has_unread_events = models.BooleanField(default=False)
    protection_ticks_remaining = models.IntegerField(default=72)
    complacency = models.IntegerField(default=0)
    determination = models.IntegerField(default=0)
    has_tick_units = models.BooleanField(default=False)
    is_abandoned = models.BooleanField(default=False)
    acres = models.IntegerField(default=500)
    incoming_acres_dict = models.JSONField(default=dict, blank=True)
    successful_invasions = models.IntegerField(default=0)
    failed_defenses = models.IntegerField(default=0)
    highest_raw_op_sent = models.IntegerField(default=0, null=True, blank=True)
    op_quested = models.IntegerField(default=0)

    primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    primary_resource_per_acre = models.IntegerField(default=0)
    
    building_primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    building_secondary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    building_primary_cost_per_acre = models.IntegerField(default=100)
    building_secondary_cost_per_acre = models.IntegerField(default=50)

    upgrade_cost = models.IntegerField(default=50000)
    upgrade_exponent = models.FloatField(default=1.01, null=True, blank=True)
    
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
    def is_oop(self):
        return self.protection_ticks_remaining == 0

    @property
    def rulers_display_name(self):
        return UserSettings.objects.get(associated_user=self.associated_user).display_name
    
    @property
    def rulers_theme_name(self):
        try:
            return UserSettings.objects.get(associated_user=self.associated_user).theme_model.name
        except:
            return "None"

    @property
    def ticks_til_training_time(self):
        return max(0, self.protection_ticks_remaining - 12)
    
    @property
    def resources(self):
        return Resource.objects.filter(ruler=self)

    @property
    def can_attack(self):
        if self.protection_ticks_remaining > 0:
            return False
        elif self.perk_dict.get("inquisition_ticks_left") and self.perk_dict.get("inquisition_ticks_left") > 0:
            return False
        # elif self.has_units_returning:
        #     return False
        elif self.incoming_acres > 0:
            return False
        
        return True

    @property
    def complacency_penalty_percent(self):
        penalty = self.complacency * 0.33

        return penalty
    
    @property
    def determination_bonus_percent(self):
        # return 0
        bonus = self.determination * 0.33

        return bonus

    @property
    def offense_multiplier(self):
        multiplier = 1 + (self.determination_bonus_percent / 100)

        if Artifact.objects.filter(name="The Barbarian's Horn", ruler=self).exists():
            multiplier += self.complacency_penalty_percent / 100

        return multiplier
    
    @property
    def raw_defense(self):
        defense = 0

        for unit in Unit.objects.filter(ruler=self):
            defense += unit.quantity_at_home * unit.dp

        return defense
    
    @property
    def defense_multiplier(self):
        multiplier = 1 - (self.complacency_penalty_percent / 100)

        # if Artifact.objects.filter(name="The Three-Faced Coin", ruler=self).exists():
        #     multiplier -= Resource.objects.get(ruler=self, name="gold").quantity - self.get_production("gold")

        return multiplier

    @property
    def defense(self):
        return max(0, int(self.raw_defense * self.defense_multiplier))
    
    @property
    def defense_short(self):
        return shorten_number(self.defense)
        
    @property
    def defense_raw_short(self):
        return shorten_number(self.raw_defense)
        
    @property
    def highest_op_short(self):
        return shorten_number(self.highest_raw_op_sent)
    
    @property
    def op_quested_short(self):
        return shorten_number(self.op_quested)
    
    @property
    def op_quested_per_acre(self):
        return int(self.op_quested / self.acres)

    @property
    def artifact_count(self):
        return Artifact.objects.filter(ruler=self).count()

    @property
    def has_artifacts(self):
        return Artifact.objects.filter(ruler=self).count() > 0

    @property
    def artifacts_owned(self):
        return Artifact.objects.filter(ruler=self)

    @property
    def artifact_steal_chance_multiplier(self):
        if "percent_bonus_to_steal" in self.perk_dict:
            return 1 + (self.perk_dict["percent_bonus_to_steal"] / 100)
        else:
            return 1

    @property
    def juicy_target_threshold(self):
        return self.defense * UserSettings.objects.get(associated_user=self.associated_user).juicy_target_threshold

    @property
    def strid(self):
        return f"{self.id}"

    @property
    def has_units_returning(self):
        for unit in Unit.objects.filter(ruler=self):
            if unit.quantity_returning > 0:
                return True
            
        return False
    
    @property
    def has_units_in_training(self):
        for unit in Unit.objects.filter(ruler=self):
            if unit.quantity_in_training > 0:
                return True
            
        return False

    @property
    def ticks_til_soonest_return(self):
        soonest_return = 999

        for unit in Unit.objects.filter(ruler=self):
            for ticks, value in unit.returning_dict.items():
                if value > 0:
                    soonest_return = min(soonest_return, int(ticks))

        return soonest_return

    @property
    def ticks_til_all_units_return(self):
        latest_return = 0

        for unit in Unit.objects.filter(ruler=self):
            for ticks, value in unit.returning_dict.items():
                if value > 0:
                    latest_return = max(latest_return, int(ticks))

        return latest_return

    @property
    def ticks_til_all_acres_return(self):
        latest_return = 0

        for ticks, value in self.incoming_acres_dict.items():
            if value > 0:
                latest_return = max(latest_return, int(ticks))

        return latest_return

    @property
    def building_primary_cost(self):
        return 1000
    
    @property
    def building_secondary_cost(self):
        return 100
    
    @property
    def incoming_acres(self):
        total = 0

        for key, value in self.incoming_acres_dict.items():
            total += value

        return total

    @property
    def acres_with_incoming(self):
        return self.acres + self.incoming_acres

    @property
    def header_rows(self):
        iterator = -1
        row_number = 0
        header_rows = {}

        for resource in Resource.objects.filter(ruler=self):
            iterator += 1
            
            if iterator % math.ceil(Resource.objects.filter(ruler=self).count() / 3) == 0:
                row_number += 1
                header_rows[str(row_number)] = []

            header_rows[str(row_number)].append({
                "name": resource.name,
                "quantity": f"{int(resource.quantity):,}"
            })

        return header_rows
    
    @property
    def resource_types(self):
        return Resource.objects.filter(ruler=self).count()

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
            production += building.amount_produced * (building.percent_of_land/100) * self.acres

        if resource_name == self.primary_resource_name:
            production += self.primary_resource_per_acre * self.acres

        for unit in Unit.objects.filter(ruler=self):
            if f"{resource_name}_per_tick" in unit.perk_dict:
                production += unit.perk_dict[f"{resource_name}_per_tick"] * unit.quantity_at_home

        if resource_name == "sinners" and "sinners_per_hundred_acres_per_tick" in self.perk_dict:
            if "inquisition_ticks_left" in self.perk_dict and self.perk_dict["inquisition_ticks_left"] > 0:
                return 0
            
            if self.protection_ticks_remaining > 0:
                return 0
            
            sinners_gained = int((self.acres / 100) * self.perk_dict["sinners_per_hundred_acres_per_tick"])

            if random.randint(1,100) <= self.acres % 100:
                sinners_gained += 1

            production += sinners_gained

        if resource_name == "rats" and "rats_per_acre_per_tick" in self.perk_dict:
            production += self.acres * self.perk_dict["rats_per_acre_per_tick"]

        if "rulers_favorite_resource" in self.perk_dict:
            if resource_name == self.perk_dict["rulers_favorite_resource"]:
                bonus = 1 + ((10 + (2 * self.failed_defenses)) / 100)
                production *= bonus

        return int(production)
    
    def get_consumption(self, resource_name):
        if resource_name == "food" and Artifact.objects.filter(ruler=self, name="The Victor's Feast").exists():
            return 0

        consumption = 0

        for unit in Unit.objects.filter(ruler=self):
            for upkeep_resource_name, upkeep in unit.upkeep_dict.items():
                if resource_name == upkeep_resource_name:
                    consumption += int(unit.quantity_trained_and_alive * upkeep)

        if resource_name == "faith":
            try:
                sinners = Resource.objects.get(ruler=self, name="sinners")
                consumption += sinners.quantity
            except:
                pass

        return consumption
    
    def do_resource_production(self):
        self.is_starving = False
        
        for resource in Resource.objects.filter(ruler=self):
            resource.quantity += self.get_production(resource.name)
            resource.quantity -= self.get_consumption(resource.name)

            # if resource.name == "gold" and Artifact.objects.filter(name="The Three-Faced Coin", ruler=self).exists():
            #     resource.quantity *= 1.008

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
        if "book_of_grudges" in self.perk_dict and self.is_oop:
            for dominion in Dominion.objects.filter(~Q(id=self.id), protection_ticks_remaining=0):
                if str(dominion.id) in self.perk_dict["book_of_grudges"]:
                    self.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] += self.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] * 0.003
                    
                    if self.perk_dict["book_of_grudges"][str(dominion.id)]["pages"] >= 100:
                        rounding = 2
                    else:
                        rounding = 3

                    self.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"] = round(self.perk_dict["book_of_grudges"][str(dominion.id)]["animosity"], rounding)

        if "mining_depth" in self.perk_dict:
            miners = Unit.objects.get(ruler=self, name="Miner")
            self.perk_dict["mining_depth"] += miners.quantity_at_home * miners.perk_dict["cm_dug_per_tick"]

        if "inquisition_ticks_left" in self.perk_dict and self.perk_dict["inquisition_ticks_left"] > 0:
            sinners = Resource.objects.get(ruler=self, name="sinners")
            self.perk_dict["inquisition_ticks_left"] -= 1

            if self.perk_dict["inquisition_ticks_left"] == 0:
                self.perk_dict["inquisition_rate"] = 0

            sinners_killed = sinners.quantity if self.perk_dict["inquisition_ticks_left"] == 0 else min(self.perk_dict["inquisition_rate"], sinners.quantity)
            sinners.quantity -= sinners_killed

            if "inquisition_makes_corpses" in self.perk_dict:
                corpses = Resource.objects.get(ruler=self, name="corpses")
                corpses.quantity += sinners_killed
                corpses.save()

            sinners.save()

        if "The Deep Angels" in self.learned_discoveries:
            deep_angels = Unit.objects.get(ruler=self, name="Deep Angel")
            stoneshields = Unit.objects.get(ruler=self, name="Stoneshield")
            deep_apostles = Unit.objects.get(ruler=self, name="Deep Apostle")

            max_converts = min(stoneshields.quantity_at_home, deep_angels.quantity_at_home)
            stoneshields.quantity_at_home -= max_converts
            deep_apostles.quantity_at_home += max_converts

            stoneshields.save()
            deep_apostles.save()

        if "Inspiration" in self.learned_discoveries and Round.objects.first().ticks_passed % 4 == 0 and "free_experiments" in self.perk_dict:
            self.perk_dict["free_experiments"] += 1

        if "Always Be Digging" in self.learned_discoveries and Round.objects.first().ticks_passed % 4 == 0 and Round.objects.first().ticks_passed > 0:
            self.acres += int(self.acres / 400)

        if "partner_patience" in self.perk_dict and self.is_oop:
            self.perk_dict["partner_patience"] -= 1

        if "biclopean_ambition_ticks_remaining" in self.perk_dict:
            self.perk_dict["biclopean_ambition_ticks_remaining"] -= 1

            if self.perk_dict["biclopean_ambition_ticks_remaining"] == 0:
                del self.perk_dict["biclopean_ambition_ticks_remaining"]

    def do_artifacts(self):
        if Artifact.objects.filter(name="The Eternal Egg of the Flame Princess", ruler=self).exists():
            fireballs = Unit.objects.get(ruler=self, name="Fireball")
            fireballs.quantity_at_home += int(self.acres/250)

            if self.acres % 250 >= random.randint(1,250):
                fireballs.quantity_at_home += 1

            fireballs.save()

        if Artifact.objects.filter(name="The Infernal Contract", ruler=self).exists():
            imps = Unit.objects.get(ruler=self, name="Imp")
            imps.quantity_at_home += int(self.acres/250)

            if self.acres % 250 >= random.randint(1,250):
                imps.quantity_at_home += 1

            imps.save()

        if Artifact.objects.filter(name="The Hoarder's Boon", ruler=self).exists():
            acres_allocated = int(self.acres * 0.05)
            resource_gained = Resource.objects.get(ruler=self, name="food")
            lowest_resource_amount = 99999999999

            for resource in Resource.objects.filter(ruler=self):
                if resource.quantity < lowest_resource_amount and resource.name not in ["corpses", "faith", "rats", "sinners", "gold"]: 
                    resource_gained = resource
                    lowest_resource_amount = resource.quantity

            building = Building.objects.get(resource_produced_name=resource_gained.name, ruler=self)

            resource_gained.quantity += building.amount_produced * acres_allocated
            resource_gained.save()

        # if Artifact.objects.filter(name="A Ladder Made Entirely of Top Rungs", ruler=self).exists():
        #     largest_dominion = Dominion.objects.all().order_by("-acres").first()
        #     largest_size = largest_dominion.acres
        #     largest_dominions = Dominion.objects.filter(acres=largest_size)

        #     if largest_dominions.count() == 1 and largest_dominions.first() != self:
                
        #         if str(largest_dominion.id) in self.perk_dict["book_of_grudges"]:
        #             self.perk_dict["book_of_grudges"][str(largest_dominion.id)]["pages"] += 1
        #         else:
        #             self.perk_dict["book_of_grudges"][str(largest_dominion.id)] = {}
        #             self.perk_dict["book_of_grudges"][str(largest_dominion.id)]["pages"] = 1
        #             self.perk_dict["book_of_grudges"][str(largest_dominion.id)]["animosity"] = 0

    def do_tick(self):
        self.do_resource_production()
        self.advance_land_returning()
        self.do_perks()
        self.do_artifacts()
        
        self.discovery_points += 1

        if Artifact.objects.filter(name="The Cause of Nine Deaths", ruler=self).exists() and Round.objects.first().ticks_passed % 4 == 0:
            self.discovery_points += 1

        for unit in Unit.objects.filter(ruler=self):
            unit.advance_training_and_returning()

        do_tick_units(self)

        for spell in Spell.objects.filter(ruler=self):
            if spell.cooldown_remaining > 0:
                spell.cooldown_remaining -= 1
                spell.save()
        
        if self.is_oop:
            self.complacency += 1
            self.determination += 1

        self.save()


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
    percent_of_land = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    trade_multiplier = models.IntegerField(default=0)
    defense_multiplier = models.IntegerField(default=0)
    upgrades = models.IntegerField(default=0)
    is_buildable = models.BooleanField(default=True)
    construction_dict = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        if self.ruler:
            return f"{self.ruler.associated_user}'s {self.name} - upg x{self.upgrades}"
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
    

class Resource(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    
    def __str__(self):
        if self.ruler:
            return f"{self.ruler.associated_user}'s {self.name}"
            
        return f"{self.name}"
    
    @property
    def production(self):
        return self.ruler.get_production(self.name)
    
    @property
    def net_production(self):
        return self.ruler.get_production(self.name) - self.ruler.get_consumption(self.name)
    
    @property
    def should_show_in_header(self):
        user_settings = UserSettings.objects.get(associated_user=self.ruler.associated_user)
        
        if self.ruler.is_starving or not user_settings.hide_zero_resources:
            return True

        try:
            building = Building.objects.get(ruler=self.ruler, resource_produced_name=self.name)

            if building.percent_of_land == 0 and self.quantity == 0:
                return False
        except:
            if self.quantity == 0:
                return False
        
        return True


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
        base_name = f"{self.name} ({self.op}/{self.dp}) -- x{self.quantity_at_home}"

        if self.ruler:
            return f"{self.ruler.rulers_display_name} -- {base_name}"
        
        return f"🟩Base --- {base_name}"
    
    @property
    def power_display(self):
        return f"{self.op:2,} / {self.dp:2,}"
    
    @property
    def quantity_trained_and_alive(self):
        return self.quantity_at_home + self.quantity_returning
    
    @property
    def quantity_trained_and_training(self):
        return self.quantity_at_home + self.quantity_in_training
    
    @property
    def quantity_total_and_paid(self):
        return self.quantity_at_home + self.quantity_in_training + self.quantity_returning

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

        if "is_glorious" in self.perk_dict:
            perk_text += "My god, it's glorious. "

        if "is_more_glorious" in self.perk_dict:
            perk_text += "HOW IS THIS ONE EVEN BETTER? "
        
        if "surplus_research_consumed_to_add_one_op_and_dp" in self.perk_dict:
            perk_text += f"""Consumes half of your stockpiled research each tick, but leaves enough to afford your upgrades. Gains 1 OP and 1 DP per  
            {self.perk_dict['surplus_research_consumed_to_add_one_op_and_dp']} consumed. """

        if "random_grudge_book_pages_per_tick" in self.perk_dict:
            pages_per_tick = self.perk_dict["random_grudge_book_pages_per_tick"]
            perk_text += f"Adds {pages_per_tick} page{'s' if pages_per_tick > 1 else ''} to an existing grudge in your book of grudges each tick. "

        if "always_dies_on_offense" in self.perk_dict:
            perk_text += "Always dies when sent on an invasion. "

        if "always_dies_on_defense" in self.perk_dict:
            perk_text += "Always dies when successfully invaded. "

        if "immortal" in self.perk_dict:
            perk_text += "Does not die in combat. "

        for resource in Resource.objects.filter(ruler=None):
            if f"{resource.name}_per_tick" in self.perk_dict:
                amount_produced = self.perk_dict[f"{resource.name}_per_tick"]
                perk_text += f"Produces {amount_produced} {resource.name} per tick. "

        if "casualty_multiplier" in self.perk_dict:
            multiplier = self.perk_dict["casualty_multiplier"]
            if multiplier == 2:
                perk_text += f"Takes twice as many casualties. "
            elif multiplier == 3:
                perk_text += f"Takes three times as many casualties. "
            elif multiplier == 0.5:
                perk_text += f"Takes half as many casualties. "
            elif multiplier == 0.75:
                perk_text += "Takes 25% fewer casualties. "
            elif multiplier == 1.5:
                perk_text += "Takes 50% more casualties. "
            else:
                perk_text += f"Takes {multiplier}x as many casualties. "

        if "converts_apostles" in self.perk_dict:
            perk_text += "Converts one Stoneshield to a Deep Apostle every tick. "

        if "cm_dug_per_tick" in self.perk_dict:
            perk_text += "Digs 1 torchbright per tick. "

        if "returns_in_ticks" in self.perk_dict:
            ticks_to_return = self.perk_dict["returns_in_ticks"]
            perk_text += f"Returns from battle in {ticks_to_return} tick{'s' if ticks_to_return > 1 else ''}. "

        if "percent_attrition" in self.perk_dict:
            attrition_percent = self.perk_dict["percent_attrition"]
            perk_text += f"{attrition_percent}% of these die every tick, rounding up. "
        
        # if "percent_becomes_rats" in self.perk_dict:
        #     becomes_rats_percent = self.perk_dict["percent_becomes_rats"]
        #     perk_text += f"{becomes_rats_percent}% of these return to normal rats every tick, rounding up. "

        if "random_allies_killed_on_invasion" in self.perk_dict:
            random_allies_killed = self.perk_dict["random_allies_killed_on_invasion"]
            if random_allies_killed == 0.5:
                perk_text += f"When invading (or questing), half of these each kill one randomly selected own unit on the same invasion. "
            else:
                perk_text += f"When invading (or questing), each kills {random_allies_killed} randomly selected own unit{'s' if random_allies_killed > 1 else ''} on the same invasion. "

        if "food_from_rat" in self.perk_dict:
            food_from_rat = self.perk_dict["food_from_rat"]
            perk_text += f"Each carves up one rat per tick into {food_from_rat} food. "

        if "rats_trained_per_tick" in self.perk_dict:
            rats_trained_per_tick = self.perk_dict["rats_trained_per_tick"]
            perk_text += f"Attempts to train {rats_trained_per_tick} Trained Rat per tick, paying costs as normal. "
        
        if "op_bonus_percent_for_stealing_artifacts" in self.perk_dict:
            op_bonus_percent_for_stealing_artifacts = self.perk_dict["op_bonus_percent_for_stealing_artifacts"]
            perk_text += f"Offense counts as {op_bonus_percent_for_stealing_artifacts}% higher when calculating artifact steal chance. "

        if "invasion_plan_power" in self.perk_dict:
            invasion_plan_power = self.perk_dict["invasion_plan_power"]
            perk_text += f"Can be sent to infiltrate a target, increasing your offense on your next attack against them by {invasion_plan_power}. "

        return perk_text
    
    @property
    def has_perks(self):
        return self.perk_dict != {} and self.perk_dict != {"is_releasable": True}
    
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


class Artifact(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        if self.ruler:
            return f"{self.name} ({self.ruler})"
        
        return f"{self.name}"


class Battle(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    attacker = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, related_name="battles_attacked")
    defender = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, related_name="battles_defended")
    stolen_artifact = models.ForeignKey(Artifact, on_delete=models.PROTECT, null=True)
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
            event_text = f"{self.winner} invaded {self.defender} and conquered {self.acres_conquered:2,} acres, plus {self.acres_conquered:2,} more from surrounding areas"
            return event_text
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
        elif self.reference_type == "abandon":
            return self.message_override
        elif self.reference_type == "artifact":
            return self.message_override
        elif self.reference_type == "quest":
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
    ticks_to_end = models.IntegerField(default=672)
    is_ticking = models.BooleanField(default=False)

    @property
    def allow_ticks(self):
        return self.has_started and not self.has_ended
    
    @property
    def ticks_left(self):
        return self.ticks_to_end - self.ticks_passed
    
    @property
    def time_til_round_start(self):
        if self.has_started or not self.start_time:
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

        if self.ticks_left == 0:
            return format_minutes(minutes_left_in_current_tick)

        minutes_left_in_remaining_full_ticks = (self.ticks_left - 1) * 15
        minutes_left_in_round = minutes_left_in_remaining_full_ticks + minutes_left_in_current_tick

        return format_minutes(minutes_left_in_round)
    
    @property
    def percent_chance_for_round_end(self):
        if self.ticks_passed > self.ticks_to_end:
            return 1
        else:
            return 0
        # ticks_past_end = self.ticks_passed - self.ticks_to_end

        # if ticks_past_end < 1:
        #     return 0

        # return math.ceil(ticks_past_end / 4)
        

class Discovery(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    required_discoveries = models.JSONField(default=list, blank=True)
    required_discoveries_or = models.JSONField(default=list, blank=True)
    required_faction_name = models.CharField(max_length=50, null=True, blank=True)
    required_perk_dict = models.JSONField(default=dict, blank=True)
    other_requirements_dict = models.JSONField(default=dict, blank=True)
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
    cooldown = models.IntegerField(default=0)
    cooldown_remaining = models.IntegerField(default=0)
    is_targeted = models.BooleanField(default=False)

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

                    consumable_research_points = min(int(research.quantity / 2), research.quantity - highest_upgrade_cost)

                    if consumable_research_points >= value:
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
                case "percent_attrition":
                    attrition_multiplier = 1 - (value / 100)
                    unit.quantity_at_home = math.floor(unit.quantity_at_home * attrition_multiplier)
                        
                    for tick, quantity in unit.returning_dict.items():
                        unit.returning_dict[tick] = math.floor(quantity * attrition_multiplier)
                    
                    unit.save()

                    if unit.quantity_total_and_paid == 0 and "Overwhelming" in unit.name:
                        unit.delete()
                # case "percent_becomes_rats":
                #     attrition_multiplier = value / 100
                #     rats = Resource.objects.get(ruler=unit.ruler, name="rats")
                #     quantity_becomes_rats = math.ceil(unit.quantity_at_home * attrition_multiplier)

                #     unit.quantity_at_home -= quantity_becomes_rats
                #     unit.save()
                #     rats.quantity += quantity_becomes_rats
                #     rats.save()
                case "rats_trained_per_tick":
                    try:
                        trained_rats = Unit.objects.get(ruler=unit.ruler, name="Trained Rat")
                        rats = Resource.objects.get(ruler=unit.ruler, name="rats")
                        food = Resource.objects.get(ruler=unit.ruler, name="food")
                        max_trainable = min(
                            unit.quantity_at_home * unit.perk_dict["rats_trained_per_tick"], 
                            int(food.quantity / trained_rats.cost_dict["food"]), 
                            int(rats.quantity / trained_rats.cost_dict["rats"])
                        )
                        rats.quantity -= max_trainable * trained_rats.cost_dict["rats"]
                        rats.save()
                        food.quantity -= max_trainable * trained_rats.cost_dict["food"]
                        food.save()
                        trained_rats.training_dict["12"] += max_trainable
                        trained_rats.save()
                    except:
                        pass