import math, random
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import datetime
from zoneinfo import ZoneInfo

from maingame.formatters import cost_after_x_ticks, divide_hack, format_minutes, get_perk_text, get_roman_numeral, shorten_number


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
    complacency = models.FloatField(default=0)
    determination = models.FloatField(default=0)
    has_tick_units = models.BooleanField(default=False)
    is_abandoned = models.BooleanField(default=False)
    successful_invasions = models.IntegerField(default=0)
    failed_defenses = models.IntegerField(default=0)
    highest_raw_op_sent = models.IntegerField(default=0, null=True, blank=True)
    invasion_consequences = models.CharField(max_length=1000, null=True, blank=True)
    score = models.IntegerField(default=0)

    times_ruler_killed = models.IntegerField(default=0)
    ruler_respawn_timer = models.IntegerField(default=0)

    acres = models.IntegerField(default=500)
    acres_gained = models.IntegerField(default=0)
    acres_lost = models.IntegerField(default=0)
    incoming_acres_dict = models.JSONField(default=dict, blank=True)
    acres_in_void = models.IntegerField(default=0)
    void_return_cost = models.IntegerField(default=0)

    primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    primary_resource_per_acre = models.IntegerField(default=0)
    
    upgrade_cost = models.IntegerField(default=50000)
    upgrade_exponent = models.FloatField(default=1.01, null=True, blank=True)
    
    perk_dict = models.JSONField(default=dict, blank=True)
    faction_name = models.CharField(max_length=50, null=True, blank=True)

    discovery_points = models.IntegerField(default=0)
    available_discoveries = models.JSONField(default=list, blank=True)
    learned_discoveries = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def is_oop(self):
        return self.protection_ticks_remaining == 0

    @property
    def ruler_is_dead(self):
        return self.ruler_respawn_timer > 0
    
    @property
    def rulers_display_name(self):
        display_name = UserSettings.objects.get(associated_user=self.associated_user).display_name
        
        if self.ruler_is_dead:
            return f"💀 ({self.ruler_respawn_timer})"
        elif self.times_ruler_killed > 0:
            return display_name + " " + get_roman_numeral(self.times_ruler_killed)
        else:
            return display_name
    
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
    def ticks_til_first_discovery(self):
        return max(0, self.protection_ticks_remaining - 22)

    @property
    def resources(self):
        return Resource.objects.filter(ruler=self)

    @property
    def can_attack(self):
        if self.protection_ticks_remaining > 0:
            return False
        elif self.perk_dict.get("order_cant_attack_ticks_left") and self.perk_dict.get("order_cant_attack_ticks_left") > 0:
            return False
        # elif self.has_units_returning:
        #     return False
        elif self.incoming_acres > 0:
            return False
        elif self.acres_in_void > 0:
            return False
        
        return True

    @property
    def complacency_penalty_percent(self):
        penalty = self.complacency * 0.33

        return max(0, penalty)
    
    @property
    def determination_bonus_percent(self):
        # return 0
        bonus = self.determination * 0.33

        return bonus

    @property
    def offense_multiplier(self):
        multiplier = 1 + (self.determination_bonus_percent / 100)
        
        if self.faction_name == "aethertide corsairs":
            multiplier += (self.aethertide_dict["op_mod"] / 100)

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

        return multiplier
    
    @property
    def score_short(self):
        return shorten_number(self.score)

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
        soonest_return = -1

        for unit in Unit.objects.filter(ruler=self):
            for ticks, value in unit.returning_dict.items():
                if value > 0 and soonest_return == -1:
                    soonest_return = int(ticks)
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
    def ticks_til_infiltrators_return(self):
        try:
            greencaps = Unit.objects.get(ruler=self, name="Greencap")
            latest_return = 0

            for ticks, value in greencaps.returning_dict.items():
                if value > 0:
                    latest_return = max(latest_return, int(ticks))

            return latest_return
        except:
            return 0

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

        return total + self.acres_in_void

    @property
    def acres_with_incoming(self):
        return self.acres + self.incoming_acres
    
    @property
    def net_acres(self):
        return self.acres_gained - self.acres_lost

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

    @property
    def goblin_bonus(self):
        if self.faction_name != "goblin":
            return 0
        else:
            return 20 + (1 * self.failed_defenses)
        
    @property
    def void_cost_preview_text(self):
        text = f"6 ticks: {cost_after_x_ticks(self.void_return_cost, 6):2,} // "
        text += f"12 ticks: {cost_after_x_ticks(self.void_return_cost, 12):2,} // "
        text += f"18 ticks: {cost_after_x_ticks(self.void_return_cost, 18):2,}"
        
        return text
    
    @property
    def red_beret_target_id(self):
        try:
            red_beret = Unit.objects.get(ruler=self, name="Red Beret")
            return red_beret.perk_dict["subverted_target_id"]
        except:
            return 0
    
    @property
    def aethertide_dict(self):
        chance_to_trigger = 0
        action = ""
        op_mod = 0
        direction_next_tick = ""
        
        if self.faction_name == "aethertide corsairs":
            aethertide_increase_next_tick = self.perk_dict["aethertide_increase_next_tick"]
            aethertide_coefficient = self.perk_dict["aethertide_coefficient"]
            aethertide_coefficient_max = self.perk_dict["aethertide_coefficient_max"]
            double_ticks_and_op_penalty = self.perk_dict["double_ticks_and_op_penalty"]
            
            chance_to_trigger = int(aethertide_coefficient / aethertide_coefficient_max * 50)
            op_mod = int((chance_to_trigger / 2) * 0.67) if double_ticks_and_op_penalty else int((chance_to_trigger / 2) * 1.33)
            direction_next_tick = "⬆️" if aethertide_increase_next_tick else "⬇️"
            
            op_mod = (-1 * op_mod) if double_ticks_and_op_penalty else op_mod
            action = "double" if double_ticks_and_op_penalty else "skip"
            
        aethertide_dict = {
            "chance_to_trigger": chance_to_trigger,
            "action": action,
            "op_mod": op_mod,
            "direction_next_tick": direction_next_tick,
        }
        
        return aethertide_dict
    
    def get_production(self, resource_name):
        production = 0

        for building in Building.objects.filter(ruler=self, resource_produced_name=resource_name):
            production += building.amount_produced * (building.percent_of_land/100) * self.acres

        if resource_name == self.primary_resource_name:
            production += self.primary_resource_per_acre * self.acres

        for unit in Unit.objects.filter(ruler=self):
            if f"{resource_name}_per_tick" in unit.perk_dict:
                production += unit.perk_dict[f"{resource_name}_per_tick"] * unit.quantity_at_home

        # if resource_name == "heretics" and "heretics_per_hundred_acres_per_tick" in self.perk_dict:
        #     if "order_cant_attack_ticks_left" in self.perk_dict and self.perk_dict["order_cant_attack_ticks_left"] > 0:
        #         return 0
            
        #     if self.protection_ticks_remaining > 0:
        #         return 0
            
        #     heretics_gained = int((self.acres / 100) * self.perk_dict["heretics_per_hundred_acres_per_tick"])

        #     if random.randint(1,100) <= self.acres % 100:
        #         heretics_gained += 1

        #     production += heretics_gained

        if resource_name == "rats" and "rats_per_acre_per_tick" in self.perk_dict:
            production += self.acres * self.perk_dict["rats_per_acre_per_tick"]

        if "rulers_favorite_resource" in self.perk_dict:
            if resource_name == self.perk_dict["rulers_favorite_resource"]:
                favorite_building = Building.objects.get(ruler=self, name="ruler's favorite")

                try:
                    actual_building = Building.objects.get(ruler=self, resource_produced_name=resource_name)
                    production += actual_building.amount_produced * (favorite_building.percent_of_land/100) * self.acres
                except:
                    pass

                bonus = 1 + (self.goblin_bonus / 100)
                production *= bonus

        return int(production)
    
    def get_consumption(self, resource_name):
        consumption = 0

        for unit in Unit.objects.filter(ruler=self):
            for upkeep_resource_name, upkeep in unit.upkeep_dict.items():
                if resource_name == upkeep_resource_name:
                    consumption += int(unit.quantity_total * upkeep)
                    
        # if resource_name == "faith":
        #     try:
        #         heretics = Resource.objects.get(ruler=self, name="heretics")
        #         consumption += heretics.quantity
        #     except:
        #         pass

        return consumption
    
    def do_resource_production(self):
        self.is_starving = False
        
        for resource in Resource.objects.filter(ruler=self):
            resource.gain(self.get_production(resource.name))
            resource.spend(self.get_consumption(resource.name))

            if resource.quantity < 0:
                self.is_starving = True
                for unit in Unit.objects.filter(ruler=self):
                    if resource.name in unit.upkeep_dict:
                        new_amount = math.ceil(unit.quantity_at_home * 0.99)
                        amount_lost = unit.quantity_at_home - new_amount
                        unit.lose(amount_lost)
                        
                        for tick, quantity in unit.returning_dict.items():
                            new_amount_returning = math.ceil(quantity * 0.99)
                            unit.lost += quantity - new_amount_returning
                            unit.returning_dict[tick] = new_amount_returning

                        unit.save()

            if resource.quantity < 0:
                resource.gain(resource.quantity * -1)
            # resource.quantity = max(0, resource.quantity)
            # resource.save()
            self.save()

    def advance_land_returning(self):
        for key, value in self.incoming_acres_dict.items():
            if key == "1":
                self.gain_acres(value)
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

        # if "order_cant_attack_ticks_left" in self.perk_dict and self.perk_dict["order_cant_attack_ticks_left"] > 0:
        #     self.perk_dict["order_cant_attack_ticks_left"] -= 1
            
        #     # Inquisition kills heretics
        #     try:
        #         heretics = Resource.objects.get(ruler=self, name="heretics")
        #         heretics_killed = heretics.quantity if self.perk_dict["order_cant_attack_ticks_left"] == 0 else min(self.perk_dict["inquisition_rate"], heretics.quantity)
        #         heretics.spend(heretics_killed)

        #         if "inquisition_makes_corpses" in self.perk_dict:
        #             corpses = Resource.objects.get(ruler=self, name="corpses")
        #             corpses.gain(heretics_killed)

        #         heretics.save()
        #     except:
        #         pass

        #     if self.perk_dict["order_cant_attack_ticks_left"] == 0 and self.faction_name == "blessed order":
        #         self.perk_dict["inquisition_rate"] = 0

        # if "corruption" in self.perk_dict and Resource.objects.filter(ruler=self, name="heretics").exists():
        #     self.perk_dict["corruption"] += Resource.objects.get(ruler=self, name="heretics").quantity

        if "The Deep Angels" in self.learned_discoveries:
            deep_angels = Unit.objects.get(ruler=self, name="Deep Angel")
            stoneshields = Unit.objects.get(ruler=self, name="Stoneshield")
            deep_apostles = Unit.objects.get(ruler=self, name="Deep Apostle")

            max_converts = min(stoneshields.quantity_at_home, deep_angels.quantity_at_home)
            stoneshields.lose(max_converts)
            deep_apostles.gain(max_converts)

            stoneshields.save()
            deep_apostles.save()
            
        if "splices" in self.perk_dict and Round.objects.first().ticks_passed % 12 == 0 and self.is_oop:
            self.perk_dict["splices"] += 1
            
            if "Inspiration" in self.learned_discoveries:
                self.perk_dict["splices"] += 1    

        if "Always Be Digging" in self.learned_discoveries and Round.objects.first().ticks_passed % 4 == 0 and Round.objects.first().ticks_passed > 0:
            self.gain_acres(int(self.acres / 400))

        if "partner_patience" in self.perk_dict and self.is_oop:
            self.perk_dict["partner_patience"] -= 1

        if "biclopean_ambition_ticks_remaining" in self.perk_dict:
            self.perk_dict["biclopean_ambition_ticks_remaining"] -= 1

            if self.perk_dict["biclopean_ambition_ticks_remaining"] == 0:
                del self.perk_dict["biclopean_ambition_ticks_remaining"]
                
        if "ticks_until_next_share_change" in self.perk_dict:
            self.perk_dict["ticks_until_next_share_change"] -= 1
                

    def update_capacity(self):
        used_capacity = 0
        mechadragon = Unit.objects.get(ruler=self, name="Mecha-Dragon")
        module_power = 0

        for module in MechModule.objects.filter(ruler=self, zone="mech"):
            used_capacity += module.capacity
            module_power += module.power
        
        mechadragon.op = 1 + module_power
        mechadragon.dp = module_power
        
        try:
            spirit_bomb = MechModule.objects.get(ruler=self, name="Tiamat-class Spirit Bomb PL#001", zone="mech")
            mechadragon.dp -= spirit_bomb.power
        except:
            pass
        
        mechadragon.save()

        self.perk_dict["capacity_used"] = used_capacity
        self.save()

    def do_tick(self):
        self.do_resource_production()
        self.advance_land_returning()
        self.do_perks()
        
        self.discovery_points += 1

        for unit in Unit.objects.filter(ruler=self):
            unit.advance_training_and_returning()
            
        for module in MechModule.objects.filter(ruler=self):
            if module.battery_current < module.battery_max:
                module.battery_current += 1
                module.save()
                
            try:
                op_growth_per_capacity_per_tick = module.perk_dict["op_growth_per_capacity_per_tick"]
                
                if module.durability_percent >= 100:
                    module.base_power += op_growth_per_capacity_per_tick
                    module.save()
            except:
                pass

        self.void_return_cost = int(self.void_return_cost * 0.9281)
        do_tick_units(self)

        for spell in Spell.objects.filter(ruler=self):
            if spell.cooldown_remaining > 0:
                spell.cooldown_remaining -= 1
                spell.save()
        
        if self.is_oop:
            self.complacency += 1
            self.determination += 1

            if "bonus_determination" in self.perk_dict:
                self.determination += self.perk_dict["bonus_determination"]
                
            if self.faction_name == "mecha-dragon":
                self.update_capacity()
                
            self.score += self.acres
                
        if self.ruler_respawn_timer > 0:
            self.ruler_respawn_timer -= 1
            
        self.save()

    def gain_acres(self, quantity):
        self.acres += quantity
        self.acres_gained += quantity
        self.save()

    def lose_acres(self, quantity):
        self.acres -= quantity
        self.acres_lost += quantity
        self.save()


class Faction(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True, default="Placeholder description")
    description_list = models.JSONField(default=list, blank=True)
    description_paragraphs = models.JSONField(default=list, blank=True)
    primary_resource_name = models.CharField(max_length=50, null=True, blank=True)
    primary_resource_per_acre = models.IntegerField(default=0)
    starting_buildings = models.JSONField(default=list, blank=True)
    invasion_consequences = models.CharField(max_length=1000, null=True, blank=True)

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
    is_upgradable = models.BooleanField(default=True)
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

        if self.name == "ruler's favorite":
            perks.append("Counts as whichever building produces the ruler's favorite resource.")

        return " ".join(perks)
    
    @property
    def derived_quantity(self):
        return int((self.percent_of_land / 100) * self.ruler.acres)
    

class Resource(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    produced = models.IntegerField(default=0)
    spent = models.IntegerField(default=0)
    
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
    
    @property
    def net(self):
        return max(0, self.produced - self.spent)

    def spend(self, quantity):
        self.quantity -= quantity
        self.spent += quantity
        self.save()

    def gain(self, quantity):
        self.quantity += quantity
        self.produced += quantity
        self.save()


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
    quantity_in_void = models.IntegerField(default=0)
    quantity_at_home = models.IntegerField(default=0)
    perk_dict = models.JSONField(default=dict, blank=True)
    faction = models.ForeignKey(Faction, on_delete=models.PROTECT, null=True, blank=True)
    gained = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)

    def __str__(self):
        base_name = f"{self.name} ({self.op}/{self.dp}) -- x{self.quantity_at_home}"

        if self.ruler:
            return f"{self.ruler.rulers_display_name} -- {base_name}"
        
        return f"🟩Base --- {base_name}"
    
    @property
    def power_display(self):
        return f"{self.op:2,} / {self.dp:2,}"
    
    @property
    def quantity_total(self):
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
        resource_name_list = []
        
        for resource in Resource.objects.filter(ruler=None):
            resource_name_list.append(resource.name)
            
        faction_name = self.ruler.faction_name if self.ruler else "none"
            
        return get_perk_text(self.perk_dict, resource_name_list, faction_name)
    
    @property
    def has_perks(self):
        if len(self.perk_dict) == 1 and "sludgene_sequence" in self.perk_dict:
            return False
        
        return self.perk_dict != {} and self.perk_dict != {"is_releasable": True}
    
    def advance_training_and_returning(self):
        for key, value in self.training_dict.items():
            if key == "1":
                self.gain(value)
                # self.quantity_at_home += value
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

        return total + self.quantity_in_void
    
    @property
    def quantity_in_training_and_returning(self):
        return self.quantity_in_training + self.quantity_returning


    @property
    def net(self):
        return max(0, self.gained - self.lost)


    def gain(self, quantity):
        self.quantity_at_home += quantity
        self.gained += quantity
        self.save()

    def put_into_training(self, quantity, ticks_to_train):
        self.training_dict[str(ticks_to_train)] += quantity
        # self.gained += quantity
        self.save()

    def lose(self, quantity):
        self.quantity_at_home -= quantity
        self.lost += quantity
        self.save()


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
            event_text = f"{self.winner} ({self.winner.rulers_display_name}) invaded {self.defender} ({self.defender.rulers_display_name}) and conquered {self.acres_conquered:2,} acres, plus {self.acres_conquered:2,} more from surrounding areas"
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
        elif self.reference_type == "spell":
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
    last_tick_finished = models.DateTimeField(null=True, blank=True)
    ticks_passed = models.IntegerField(default=0)
    ticks_to_end = models.IntegerField(default=672)
    is_ticking = models.BooleanField(default=False)
    bugs = models.JSONField(default=list, blank=True)
    has_bugs = models.BooleanField(default=False)

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

    @property
    def faction_count_list(self):
        faction_counts = []

        for faction in Faction.objects.all():
            faction_count = {
                "name": faction.name,
                "count": Dominion.objects.filter(faction_name=faction.name, is_abandoned=False).count()
            }
            
            faction_counts.append(faction_count)
            
        faction_counts.append(
            {
                "name": "fallen order",
                "count": Dominion.objects.filter(faction_name="fallen order").count()
            }
        )
        
        return faction_counts
        

class Discovery(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    repeatable = models.BooleanField(default=False)
    required_discoveries = models.JSONField(default=list, blank=True)
    required_discoveries_or = models.JSONField(default=list, blank=True)
    required_faction_name = models.CharField(max_length=50, null=True, blank=True)
    required_perk_dict = models.JSONField(default=dict, blank=True)
    other_requirements_dict = models.JSONField(default=dict, blank=True)
    not_for_factions = models.JSONField(default=list, blank=True)
    associated_unit_name = models.CharField(max_length=50, null=True, blank=True)
    associated_module_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def associated_unit(self):
        if self.associated_unit_name:
            return Unit.objects.get(name=self.associated_unit_name, ruler=None)
        
        return None
    
    @property
    def associated_module(self):
        if self.associated_module_name:
            return MechModule.objects.get(name=self.associated_module_name, ruler=None)
        
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
    

class MechModule(models.Model):
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    version = models.IntegerField(default=0)
    capacity = models.IntegerField(default=1)
    base_power = models.IntegerField(default=0)
    base_upgrade_cost_dict = models.JSONField(default=dict, blank=True)
    base_repair_cost_dict = models.JSONField(default=dict, blank=True)
    perk_dict = models.JSONField(default=dict, blank=True)
    durability_current = models.IntegerField(default=100)
    durability_max = models.IntegerField(default=100)
    battery_current = models.IntegerField(default=0)
    battery_max = models.IntegerField(default=0)
    fragility = models.IntegerField(default=20)
    zone = models.CharField(max_length=50, default="hangar", choices={"mech": "mech", "hangar": "hangar", "repair": "repair"})
    faction = models.ForeignKey(Faction, on_delete=models.PROTECT, null=True, blank=True)
    order = models.IntegerField(default=0)
    upgrade_increases_capacity = models.BooleanField(default=True)
    upgrade_increases_durability = models.BooleanField(default=True)
    is_upgradable = models.BooleanField(default=True)

    def __str__(self):
        base_name = f"{self.name} @ {self.power} power ({self.durability_current}/{self.durability_max}) -- {self.order}"

        if self.ruler:
            return f"{self.ruler.rulers_display_name} -- {base_name}"
        
        return f"🟩Base --- {base_name}"
    
    @property
    def versioned_name(self):
        versioned_name = self.name.replace("#", f"{self.version}")

        # if self.version == 0:
        #     versioned_name += " (P)"

        return versioned_name
    
    @property
    def versioned_power(self):
        versioned_power = self.capacity * self.base_power

        if self.version == 0:
            versioned_power = int(0.1 * self.base_power)

        return versioned_power
    
    @property
    def power(self):
        durability_modifier = 0.5 + (0.5 * (self.durability_percent / 100))

        a = 0.5 * min(100, self.durability_percent+50) / 100
        b = 0.5 * (self.durability_percent / 100)
        durability_modifier = a + b

        return int(self.versioned_power * durability_modifier)
    
    @property
    def power_short(self):
        return shorten_number(self.power)
    
    @property
    def upgrade_cost_dict(self):
        upgrade_cost_dict = {}

        for resource, amount in self.base_upgrade_cost_dict.items():
            # 1, 1, 2, 4, 8
            # 0, 1, 2, 3, 4
            if self.version <= 1:
                upgrade_cost_dict[resource] = amount
            else:
                upgrade_cost_dict[resource] = amount * (2 ** (self.version - 1))
            # upgrade_cost_dict[resource] = self.capacity * amount

        return upgrade_cost_dict
    
    @property
    def upgrade_cost_dict_short(self):
        shortened_upgrade_cost_dict = {}

        for resource, amount in self.upgrade_cost_dict.items():
            shortened_upgrade_cost_dict[resource] = shorten_number(amount)

        return shortened_upgrade_cost_dict
    
    @property
    def repair_cost_dict(self):
        repair_cost_dict = {}

        for resource, amount in self.base_repair_cost_dict.items():
            repair_cost_dict[resource] = amount

        return repair_cost_dict
    
    @property
    def repair_cost_list(self):
        repair_cost_string = ""

        for resource, amount in self.repair_cost_dict.items():
            repair_cost_string += f"{shorten_number(amount)} {resource}, "

        return repair_cost_string[:-2]
    
    @property
    def durability_percent(self):
        ratio = self.durability_current / self.durability_max
        return int(100 * ratio)
    
    @property
    def battery_percent(self):
        ratio = self.battery_current / self.battery_max
        return int(100 * ratio)
    
    @property
    def can_afford_upgrade(self):
        for resource_name, amount in self.upgrade_cost_dict.items():
            resource = Resource.objects.get(ruler=self.ruler, name=resource_name)

            if amount > resource.quantity:
                return False
            
        return True
    
    @property
    def can_fit_upgrade(self):
        extra_capacity = 0

        if self.version + 1 >= 2 and self.upgrade_increases_capacity:
            extra_capacity = self.capacity

        return self.ruler.perk_dict["capacity_used"] + extra_capacity <= self.ruler.perk_dict["capacity_max"]
    
    @property
    def perk_text(self):
        perk_text = ""

        if "durability_damage_percent_reduction" in self.perk_dict:
            damage_reduction_percent = self.perk_dict["durability_damage_percent_reduction"]
            perk_text += f"Reduces durability loss for modules by {damage_reduction_percent}% (except the Tiamat-class Spirit Bomb). "

        if "returns_faster" in self.perk_dict:
            perk_text += f"Return from battle in {12 - self.version} ticks. "

        if "recall_instantly" in self.perk_dict:
            perk_text += f"When equipped on an invasion, activate from the mech hangar to instantly return the mecha-dragon home. This module will be removed from existence in the process to avoid paradoxes and all modules will be reduced to 0 durability. The Magefield cannot prevent this."

        if "modifies_determination" in self.perk_dict:
            perk_text += f"Rather than clearing your determination when invading, instead multiply it by {self.version_based_determination_multiplier}."
            
        if "allies_are_immortal" in self.perk_dict:
            perk_text += f"All units sent on this invasion suffer no casualties (unless they always die)."
            
        if "op_growth_per_capacity_per_tick" in self.perk_dict:
            if self.version == 0:
                op_growth_per_capacity_per_tick = 1.5
            else:
                op_growth_per_capacity_per_tick = self.perk_dict["op_growth_per_capacity_per_tick"]
            
            perk_text += f"Gains {op_growth_per_capacity_per_tick * self.capacity} OP per tick while at full durability. Resets to zero on invasion. Does not provide DP."
            
        if "op_bonus_percent" in self.perk_dict:
            op_bonus_percent = self.perk_dict["op_bonus_percent"]
            perk_text += f"Increases all OP sent by {op_bonus_percent}%."

        return perk_text
    
    @property
    def version_based_determination_multiplier(self):
        return (self.version + 1) * 0.5

    def upgrade(self):
        if self.zone == "mech" and not self.can_fit_upgrade:
            return False, f"Insufficient capacity, uninstall this module before upgrading."

        if not self.can_afford_upgrade:
            return False, f"Insufficient resources to upgrade {self.versioned_name}"
            
        for resource_name, amount in self.upgrade_cost_dict.items():
            resource = Resource.objects.get(ruler=self.ruler, name=resource_name)
            resource.spend(amount)

        self.version += 1

        if self.version >= 2:
            if self.upgrade_increases_capacity:
                self.capacity *= 2
                
            if self.upgrade_increases_durability:
                self.durability_current *= 2
                self.durability_max *= 2

        self.save()
        return True, f"Upgraded {self.versioned_name}"


class Sludgene(models.Model):
    ruler = models.ForeignKey(Dominion, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    op = models.IntegerField(default=0)
    dp = models.IntegerField(default=0)
    return_ticks = models.IntegerField(default=12)
    casualty_rate = models.FloatField(default=1)
    resource_secreted_name = models.CharField(max_length=50, null=True, blank=True, choices={"food": "food", "ore": "ore", "wood": "wood", "mana": "mana"})
    amount_secreted = models.FloatField(default=1)
    cost_type = models.CharField(max_length=50, null=True, blank=True, choices={"primary": "primary", "secondary": "secondary", "hybrid": "hybrid"})
    upkeep_type = models.CharField(max_length=50, null=True, blank=True, choices={"primary": "primary", "secondary": "secondary", "hybrid": "hybrid"})
    cost_dict = models.JSONField(default=dict, blank=True)
    upkeep_dict = models.JSONField(default=dict, blank=True)
    discount_percent = models.IntegerField(default=0)
    
    def __str__(self):
        base_name = f"{self.name} {self.op}/{self.dp}"

        if self.ruler:
            return f"{self.ruler.rulers_display_name} -- {base_name}"
        
        return f"🟩Base --- {base_name}"
    
    @property
    def discount_cost_multiplier(self):
        return 1 - (self.discount_percent / 100)
    
    @property
    def perk_dict(self):
        perk_dict = {}
        
        if self.casualty_rate != 1:
            perk_dict["casualty_multiplier"] = self.casualty_rate
            
        if self.amount_secreted > 0:
            perk_dict[f"{self.resource_secreted_name}_per_tick"] = self.amount_secreted
            
        if self.return_ticks != 12:
            perk_dict["returns_in_ticks"] = self.return_ticks
            
        return perk_dict
    
    @property
    def perk_text(self):
        resource_name_list = []
        
        for resource in Resource.objects.filter(ruler=None):
            resource_name_list.append(resource.name)
            
        faction_name = self.ruler.faction_name if self.ruler else "none"
        
        return get_perk_text(self.perk_dict, resource_name_list, faction_name)
    
    # @property
    # def cost_type(self):
    #     if self.upkeep_goop_multiplier > 0.66:
    #         return "Mostly goop"
    #     elif self.upkeep_goop_multiplier > 0.33:
    #         return "About even"
    #     elif self.upkeep_goop_multiplier > 0:
    #         return "Mostly sludge"
    #     else:
    #         return "All sludge"
        
    # @property
    # def upkeep_type(self):
    #     if self.cost_goop_multiplier > 0.66:
    #         return "Mostly goop"
    #     elif self.cost_goop_multiplier > 0.33:
    #         return "About even"
    #     elif self.cost_goop_multiplier > 0:
    #         return "Mostly sludge"
    #     else:
    #         return "All sludge"


def do_tick_units(dominion: Dominion):
    for unit in Unit.objects.filter(ruler=dominion):
        update_harbingers = False

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
                        research.spend(instances_consumed * value)
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
                    new_quantity = math.floor(unit.quantity_at_home * attrition_multiplier)
                    quantity_lost = unit.quantity_at_home - new_quantity
                    unit.lose(quantity_lost)
                        
                    for tick, quantity in unit.returning_dict.items():
                        new_quantity = math.floor(quantity * attrition_multiplier)
                        quantity_lost = unit.returning_dict[tick] - new_quantity
                        unit.returning_dict[tick] = new_quantity
                        unit.lost += quantity_lost
                    
                    unit.save()

                    if unit.quantity_total_and_paid == 0 and "Overwhelming" in unit.name:
                        unit.delete()
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
                        rats.spend(max_trainable * trained_rats.cost_dict["rats"])
                        food.spend(max_trainable * trained_rats.cost_dict["food"])
                        trained_rats.training_dict["12"] += max_trainable
                        trained_rats.save()
                    except:
                        pass
                case "sacrifices_brothers_amount":
                    sacrifices_brothers_amount = unit.perk_dict["sacrifices_brothers_amount"]
                    sacrifices_brothers_chance_percent = unit.perk_dict["sacrifices_brothers_chance_percent"]
                    
                    try:
                        brothers = Unit.objects.get(ruler=dominion, name="Blessed Brother")
                        grisly_altars = Unit.objects.get(ruler=dominion, name="Grisly Altar")
                        harbingers = unit
                        iterations = max(1, int(harbingers.quantity_at_home / 1000))

                        for _ in range(iterations):
                            if random.randint(1, 100) <= sacrifices_brothers_chance_percent and brothers.quantity_at_home > 0:
                                brothers.lose(min(brothers.quantity_at_home, sacrifices_brothers_amount))
                                grisly_altars.gain(1)
                        
                        grisly_altars.save()

                        if brothers.quantity_total_and_paid <= 0:
                            brothers.delete()
                            update_harbingers = True
                        else:
                            brothers.save()
                    except:
                        pass
                case "zealots_chosen_per_tick":
                    grisly_altars = unit
                    zealots = Unit.objects.get(ruler=dominion, name="Zealot")
                    chosen_ones = Unit.objects.get(ruler=dominion, name="Chosen One")
                    conversions = min(grisly_altars.quantity_at_home, zealots.quantity_at_home)
                    zealots.lose(conversions)
                    chosen_ones.gain(conversions)
                case "percent_becomes_500_blasphemy":
                    attrition_multiplier = value / 100
                    blasphemy = Resource.objects.get(ruler=unit.ruler, name="blasphemy")
                    quantity_becomes_500_blasphemy_each = math.ceil(unit.quantity_at_home * attrition_multiplier)

                    unit.lose(quantity_becomes_500_blasphemy_each)
                    blasphemy.gain(quantity_becomes_500_blasphemy_each * 500)
                case "repairs_mechadragons":
                    repairs = unit.quantity_at_home
                    gold = Resource.objects.get(ruler=unit.ruler, name="gold")
                    ore = Resource.objects.get(ruler=unit.ruler, name="ore")
                    mana = Resource.objects.get(ruler=unit.ruler, name="mana")
                    research = Resource.objects.get(ruler=unit.ruler, name="research")
                    
                    if Unit.objects.get(ruler=unit.ruler, name="Mecha-Dragon").quantity_at_home > 0:
                        repairable_modules = MechModule.objects.filter(ruler=unit.ruler).order_by("order")
                    else:
                        repairable_modules = MechModule.objects.filter(ruler=unit.ruler, zone="hangar").order_by("order")
                        
                    for module in repairable_modules:
                        gold_cost = module.repair_cost_dict["gold"] if "gold" in module.repair_cost_dict else 0
                        ore_cost = module.repair_cost_dict["ore"] if "ore" in module.repair_cost_dict else 0
                        mana_cost = module.repair_cost_dict["mana"] if "mana" in module.repair_cost_dict else 0
                        research_cost = module.repair_cost_dict["research"] if "research" in module.repair_cost_dict else 0
                        
                        while (
                            gold.quantity >= gold_cost and 
                            ore.quantity >= ore_cost and 
                            mana.quantity >= mana_cost and 
                            research.quantity >= research_cost and 
                            module.durability_current < module.durability_max and 
                            repairs > 0
                        ):
                            repairs_needed = module.durability_max - module.durability_current
                            repairs_possible = min(
                                repairs, 
                                repairs_needed,
                                int(divide_hack(gold.quantity, gold_cost)),
                                int(divide_hack(ore.quantity, ore_cost)),
                                int(divide_hack(mana.quantity, mana_cost)),
                                int(divide_hack(research.quantity, research_cost)),
                            )
                            
                            repairs -= repairs_possible
                            gold.spend(gold_cost * repairs_possible)
                            ore.spend(ore_cost * repairs_possible)
                            mana.spend(mana_cost * repairs_possible)
                            research.spend(research_cost * repairs_possible)
                            module.durability_current += repairs_possible

                        module.save()

        if update_harbingers:
            del unit.perk_dict["sacrifices_brothers_amount"]
            del unit.perk_dict["sacrifices_brothers_chance_percent"]
            unit.perk_dict["percent_becomes_500_blasphemy"] = 2
            unit.save()