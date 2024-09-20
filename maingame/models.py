import math
from django.db import models
from django.contrib.auth.models import User
from random import randint

from maingame.formatters import smart_comma, get_resource_name


class Deity(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.name} ({self.emoji})"
    
    @property
    def emoji(self):
        if self.name == "Hunger Without End":
            return "🪙"
        elif self.name == "Rubecus":
            return "🪺"
        elif self.name == "The Many Who Are One":
            return "🍄"
        # elif self.name == "The Champion's Majestic Steed":
        #     return "🦄"
        # elif self.name == "She Who Ends the World":
        #     return "👹"
        # elif self.name == "Akara":
        #     return "❤️‍🔥"
        # elif self.name == "The Rumorkin Counsel":
        #     return "👁️‍🗨️"
        # elif self.name == "The Prince of Progress":
        #     return "?"
        # elif self.name == "Celebara":
        #     return "🎵"
        # elif self.name == "Flihara":
        #     return "🌺"
        # elif self.name == "Freedom's Unforgettable Sacrifice":
        #     return "⛓️‍💥"
        else:
            return "🆘"
        
    class Meta: 
        verbose_name_plural = "deities"
        

class Terrain(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    emoji = models.CharField(max_length=10, null=True, blank=True, unique=True)
    unit_op_dp_ratio = models.FloatField(null=True, blank=True)
    unit_perk_options = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
        
    class Meta: 
        verbose_name_plural = "Terrain"
        

class BuildingType(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    resource_produced = models.CharField(max_length=15, null=True, blank=True)
    amount_produced = models.IntegerField(default=0)
    trade_multiplier = models.IntegerField(default=0)
    defense_multiplier = models.IntegerField(default=0)
    ideal_terrain = models.ForeignKey(Terrain, on_delete=models.PROTECT, null=True, blank=True)
    housing = models.IntegerField(default=10)

    def __str__(self):
        name = f"{self.name}"

        if self.amount_produced > 0:
            name += f" @ {self.amount_produced} {self.resource_produced}/tick"
        
        is_base = True

        for player in Player.objects.all():
            if self in player.building_types_available.all():
                name = f"{player}'s {name}"
                is_base = False

        if is_base:
            name = "🟩Base --- " + name

        return name
    

class Faction(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    starter_building_types = models.ManyToManyField(BuildingType)

    def __str__(self):
        return f"{self.name} ({self.id})"


class Player(models.Model):
    associated_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    resource_dict = models.JSONField(default=dict)
    building_types_available = models.ManyToManyField(BuildingType)
    faction = models.ForeignKey(Faction, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.name} ({self.associated_user.username})"
    
    @property
    def unconstructed_plots(self):
        unconstructed_plots = 0

        for region in Region.objects.filter(ruler=self):
            unconstructed_plots += region.plots_available

        return unconstructed_plots
    
    @property
    def regions_ruled(self):
        return Region.objects.filter(ruler=self).count()
    
    @property
    def has_marshaled_units(self):
        return Unit.objects.filter(ruler=self, quantity_marshaled__gt=0).count() > 0
    
    @property
    def header_rows(self):
        iterator = -1
        row_number = 0
        header_rows = {}

        for resource, amount in self.resource_dict.items():
            iterator += 1
            
            if iterator % math.ceil(len(self.resource_dict) / 2) == 0:
                row_number += 1
                header_rows[str(row_number)] = []

            header_rows[str(row_number)].append({
                "readout": f"{resource}: {amount}",
                "tooltip": get_resource_name(resource)
            })

        return header_rows

    
    def adjust_resource(self, resource, amount):
        if resource in self.resource_dict:
            self.resource_dict[resource] += amount
        else:
            self.resource_dict[resource] = amount

        self.resource_dict[resource] = max(self.resource_dict[resource], 0)

        self.save()

    def get_production(self, resource):
        production = 0

        for building in Building.objects.filter(ruler=self):
            if building.built_on_ideal_terrain:
                production += (building.type.amount_produced * 2)
            else:
                production += building.type.amount_produced

        return production
    
    def get_food_consumption(self):
        total_units = 0

        for unit in Unit.objects.filter(ruler=self):
            total_units += unit.quantity_marshaled

        for region in Region.objects.filter(ruler=self):
            for unit_id, amount in region.units_here_dict.items():
                total_units += amount

        return total_units / 50


class Unit(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True)
    faction_for_which_is_default = models.ForeignKey(Faction, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    dp = models.IntegerField(default=0)
    op = models.IntegerField(default=0)
    is_trainable = models.BooleanField(default=True)
    cost_dict = models.JSONField(default=dict)
    associated_deity = models.ForeignKey(Deity, on_delete=models.PROTECT, null=True, blank=True)
    sacred_site_requirement = models.IntegerField(default=0)
    quantity_marshaled = models.IntegerField(default=0)
    perk_string = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        base_name = f"{self.name} ({self.op}/{self.dp})"

        if self.ruler:
            return f"{self.ruler.name}'s {base_name}"
        
        return f"🟩Base --- {base_name}"
    
    def max_affordable(self):
        if not self.ruler:
            return 0
        
        max_affordable = 9999999999999

        for resource, amount in self.cost_dict.items():
            if self.ruler.resource_dict[resource] > 0:
                max_affordable = min(max_affordable, math.floor(self.ruler.resource_dict[resource]/amount))
            else:
                max_affordable = 0

        return max_affordable
    
    def max_marshal_to_all_regions(self):
        return math.floor(self.quantity_marshaled / self.ruler.regions_ruled)

    @property
    def cost_string(self):
        cost_string = ""
        if self.gold_cost:
            cost_string += smart_comma(cost_string, f"{self.gold_cost}🪙")
        
        if self.ore_cost:
            cost_string += smart_comma(cost_string, f"{self.ore_cost}🪨")

        if self.lumber_cost:
            cost_string += smart_comma(cost_string, f"{self.lumber_cost}🪵")

        if self.gem_cost:
            cost_string += smart_comma(cost_string, f"{self.gem_cost}💎")

            # if self.gem_cost > 1:
            #     cost_string += "s"

        if self.mana_cost:
            cost_string += smart_comma(cost_string, f"{self.mana_cost}🔮")

        if self.food_cost:
            cost_string += smart_comma(cost_string, f"{self.food_cost}🍞")
            
        return cost_string


class Region(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    primary_terrain = models.ForeignKey(Terrain, on_delete=models.PROTECT, related_name="regions_as_primary_terrain")
    secondary_terrain = models.ForeignKey(Terrain, on_delete=models.PROTECT, related_name="regions_as_secondary_terrain")
    deity = models.ForeignKey(Deity, on_delete=models.PROTECT)
    ticks_ruled = models.IntegerField(default=0)
    units_here_dict = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} {self.primary_terrain.emoji}{self.primary_terrain.emoji}{self.secondary_terrain.emoji} / {self.deity.emoji}"

    def emoji_name(self):
        return f"{self.name} {self.primary_terrain.emoji}{self.primary_terrain.emoji}{self.secondary_terrain.emoji} / {self.deity.emoji}"
    
    def description(self):
        if self.primary_terrain == "defensible" or self.secondary_terrain == "defensible":
            return "something"
        else:
            return f"{self.name} has a mostly {self.primary_terrain} landscape, but is also somewhat {self.secondary_terrain}. It has a site sacred to {self.deity}."
        
    @property
    def primary_plots_available(self):
        primary_plots_available = 2

        for building in self.buildings_here.all():
            if building.type.ideal_terrain == self.primary_terrain:
                primary_plots_available -= 1

        return primary_plots_available > 0
    
    @property
    def secondary_plots_available(self):
        for building in self.buildings_here.all():
            if building.type.ideal_terrain == self.secondary_terrain:
                return False

        return True
    
    @property
    def plots_available(self):
        return 3 - self.buildings_here.all().count()
    
    @property
    def defense(self):
        defense = 0

        for unit_id, quantity in self.units_here_dict.items():
            unit = Unit.objects.get(id=int(unit_id))
            defense += quantity * unit.dp

        return defense
    

class Building(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True)
    type = models.ForeignKey(BuildingType, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="buildings_here")
    built_on_ideal_terrain = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.region} --- {self.type}"
    

class Journey(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    destination = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="journey_destination_set")
    ticks_to_arrive = models.IntegerField(default=12)

    def __str__(self):
        return f"{self.quantity}x {self.unit} ... to {self.destination} ({self.ticks_to_arrive} ticks)"