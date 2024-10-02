import math
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from maingame.formatters import create_or_add_to_key, smart_comma, get_resource_name


class Deity(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    icon = models.CharField(max_length=10, null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.name} ({self.icon})"
        
    class Meta: 
        verbose_name_plural = "deities"

    @property
    def favored_player(self):
        player_devotion_dict = {}

        for region in Region.objects.filter(~Q(ruler=None), deity=self):
            player_devotion_dict = create_or_add_to_key(player_devotion_dict, str(region.ruler.id), 1)
        
        favored_player_id = 0
        favored_player_devotion = 0
        tied_for_highest = False

        for player_id, devotion in player_devotion_dict.items():
            if devotion > favored_player_devotion:
                favored_player_devotion = devotion
                favored_player_id = player_id
                tied_for_highest = False
            elif devotion == favored_player_devotion:
                tied_for_highest = True

        if favored_player_devotion >= 0 and not tied_for_highest:
            return Player.objects.get(id=favored_player_id)
        
        return None


class Terrain(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    icon = models.CharField(max_length=10, null=True, blank=True, unique=True)
    unit_op_dp_ratio = models.FloatField(null=True, blank=True)
    unit_perk_options = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
        
    class Meta: 
        verbose_name_plural = "Terrain"
        

class Player(models.Model):
    associated_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    timezone = models.CharField(max_length=50, default="UTC")
    resource_dict = models.JSONField(default=dict)
    xp_dict = models.JSONField(default=dict, blank=True, null=True)
    is_starving = models.BooleanField(default=False)
    has_unread_events = models.BooleanField(default=False)
    upgrade_cost = models.IntegerField(default=150)
    upgrade_exponent = models.FloatField(default=1.02, null=True, blank=True)
    protection_ticks_remaining = models.IntegerField(default=96)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def marshaled_op(self):
        marshaled_op = 0

        for marshaled_unit in Unit.objects.filter(ruler=self, quantity_marshaled__gt=0):
            marshaled_op += (marshaled_unit.op * marshaled_unit.quantity_marshaled)

        return marshaled_op

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

            readout = f"{resource}: {int(amount):,}"

            if resource == "🍞" and self.is_starving:
                readout += "⚠️"

            tooltip = get_resource_name(resource)

            if resource == "🍞" and self.is_starving:
                tooltip = "⚠️ YOU ARE STARVING ⚠️"

            header_rows[str(row_number)].append({
                "readout": readout,
                "tooltip": tooltip
            })

        return header_rows
    
    @property
    def gold_production(self):
        gold_production = 3000
        beautiful_terrain = Terrain.objects.get(name="beautiful")

        for region in Region.objects.filter(ruler=self):
            if region.primary_terrain == beautiful_terrain:
                gold_production += 500
            elif region.secondary_terrain == beautiful_terrain:
                gold_production += 400
            else:
                gold_production += 300

        return gold_production
    
    @property
    def influence_production(self):
        influence_production = 0
        influential_terrain = Terrain.objects.get(name="influential")

        for region in Region.objects.filter(ruler=self):
            if region.primary_terrain == influential_terrain:
                influence_production += 2
            elif region.secondary_terrain == influential_terrain:
                influence_production += 1.5
            else:
                influence_production += 1

        return influence_production

    @property
    def average_defense(self):
        total_defense = 0
        regions = Region.objects.filter(ruler = self)

        for region in regions:
            total_defense += region.defense

        return total_defense / regions.count()

    @property
    def has_underdefended_regions(self):
        for region in Region.objects.filter(ruler=self):
            if region.is_underdefended:
                return True
            
        return False

    def adjust_resource(self, resource, amount):
        if self.is_starving and resource != "🍞":
            amount = min(amount, 0)

        self.resource_dict = create_or_add_to_key(self.resource_dict, resource, amount)
        self.resource_dict[resource] = max(self.resource_dict[resource], 0)
        self.save()

    def adjust_xp(self, terrain: Terrain, amount):
        self.xp_dict = create_or_add_to_key(self.xp_dict, terrain.icon, amount)
        self.xp_dict[terrain.icon] = max(self.xp_dict[terrain.icon], 0)
        self.save()

    def get_devotion(self, deity):
        return Region.objects.filter(ruler=self, deity=deity).count()

    def get_production(self, resource):
        production = 0

        if resource == "🪙":
            production += self.gold_production
        elif resource == "👑":
            production += self.influence_production

        for building in Building.objects.filter(ruler=self):
            if building.type.resource_produced == resource:
                underdefended_penalty = 0.2 if building.region.is_underdefended else 1

                if building.built_on_ideal_terrain:
                    production += int(building.type.amount_produced * 2 * underdefended_penalty)
                else:
                    production += int(building.type.amount_produced * underdefended_penalty)

        return production
    
    def get_food_consumption(self):
        total_units = 0

        for unit in Unit.objects.filter(ruler=self):
            if not "no_food" in unit.perk_dict:
                total_units += unit.quantity_marshaled

        for region in Region.objects.filter(ruler=self):
            for unit_id, amount in region.units_here_dict.items():
                if not "no_food" in Unit.objects.get(id=unit_id).perk_dict:
                    total_units += amount

        return int(total_units / 25)
    
    def do_food_consumption(self):
        consumption = self.get_food_consumption()
        self.is_starving = consumption > self.resource_dict["🍞"]
        self.adjust_resource("🍞", (consumption * -1))
        self.save()

    def do_resource_production(self):
        self.adjust_resource("🪙", self.gold_production)
        self.adjust_resource("👑", self.influence_production)
        self.adjust_resource("📜", 100)
        self.save()
        
        for building in Building.objects.filter(ruler=self):
            if building.type.amount_produced > 0:
                amount_produced = building.type.amount_produced
                
                if building.built_on_ideal_terrain:
                    amount_produced *= 2

                self.adjust_resource(building.type.resource_produced, amount_produced)

        for region in Region.objects.filter(ruler=self):
            self.adjust_xp(region.primary_terrain, 2)
            self.adjust_xp(region.secondary_terrain, 1)

    def progress_journeys(self):
        for journey in Journey.objects.filter(ruler=self):
            journey.ticks_to_arrive -= 1
            journey.save()

            if journey.ticks_to_arrive == 0:
                region = journey.destination
                unit = journey.unit
                unit_id_str = str(unit.id)
                quantity = journey.quantity

                region.units_here_dict = create_or_add_to_key(region.units_here_dict, unit_id_str, quantity)

                if region.ruler != self:
                    region.invasion_this_tick = True
                
                region.save()
                journey.delete()

    def do_tick(self):
        self.do_resource_production()
        self.do_food_consumption()
        self.progress_journeys()


class BuildingType(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    resource_produced = models.CharField(max_length=15, null=True, blank=True)
    amount_produced = models.IntegerField(default=0)
    trade_multiplier = models.IntegerField(default=0)
    defense_multiplier = models.IntegerField(default=0)
    ideal_terrain = models.ForeignKey(Terrain, on_delete=models.PROTECT, null=True, blank=True)
    upgrades = models.IntegerField(default=0)
    is_starter = models.BooleanField(default=False)

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


class Unit(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    dp = models.IntegerField(default=0)
    op = models.IntegerField(default=0)
    is_trainable = models.BooleanField(default=True)
    cost_dict = models.JSONField(default=dict, blank=True)
    quantity_marshaled = models.IntegerField(default=0)
    perk_dict = models.JSONField(default=dict, blank=True)
    is_starter = models.BooleanField(default=False)

    def __str__(self):
        base_name = f"{self.name} ({self.op}/{self.dp}) -- {self.id}"

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
    def perk_text(self):
        print(self.perk_dict)
        if "no_food" in self.perk_dict:
            return "Consumes no food"
        
        return ""
    
    @property
    def has_perks(self):
        return self.perk_dict != {}


class Region(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    primary_terrain = models.ForeignKey(Terrain, on_delete=models.PROTECT, related_name="regions_as_primary_terrain")
    secondary_terrain = models.ForeignKey(Terrain, on_delete=models.PROTECT, related_name="regions_as_secondary_terrain")
    deity = models.ForeignKey(Deity, on_delete=models.PROTECT)
    ticks_ruled = models.IntegerField(default=0)
    units_here_dict = models.JSONField(default=dict, null=True, blank=True)
    invasion_this_tick = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.primary_terrain.icon}{self.primary_terrain.icon}{self.secondary_terrain.icon} / {self.deity.icon}"

    def icon_name(self):
        return f"{self.name} {self.primary_terrain.icon}{self.primary_terrain.icon}{self.secondary_terrain.icon} / {self.deity.icon}"
    
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
            if unit.ruler == self.ruler:
                defense += quantity * unit.dp

        defense_modifier = 100

        for building in self.buildings_here.all():
            defense_modifier += building.type.defense_multiplier

        return int(defense * (defense_modifier / 100))
    
    @property
    def defense_with_incoming(self):
        defense_with_incoming = self.defense
        
        for journey in Journey.objects.filter(ruler=self.ruler, destination=self):
            defense_with_incoming += journey.quantity * journey.unit.dp

        return defense_with_incoming
    
    @property
    def is_underdefended(self):
        return self.ruler and self.defense < (self.ruler.average_defense / 3)
    

class Building(models.Model):
    ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True)
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
    

class Battle(models.Model):
    winner = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, related_name="battles_won")
    target = models.ForeignKey(Region, on_delete=models.PROTECT)
    attackers = models.ManyToManyField(Player)
    units_involved_dict = models.JSONField(default=dict, null=True, blank=True)
    casualties_dict = models.JSONField(default=dict, null=True, blank=True)
    original_ruler = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, related_name="battles_defended")
    dp = models.IntegerField(default=0)

    @property
    def event_text(self):
        if not self.winner in self.attackers.all():
            attackers = ""

            for attacker in self.attackers.all():
                attackers += smart_comma(attackers, attacker.name)

            return f"{self.winner} repelled {attackers} to defend {self.target}"

        return f"{self.winner} defeated {self.original_ruler} to conquer {self.target}"


class Event(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    reference_id = models.IntegerField(default=0)
    reference_type = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, default="?")
    extra_text = models.CharField(max_length=150, default="")
    notified_players = models.ManyToManyField(Player)

    def __str__(self):
        return f"{self.message}"

    @property
    def message(self):
        if self.reference_type == "battle":
            battle = Battle.objects.get(id=self.reference_id)
            return battle.event_text
        elif self.reference_type == "signup":
            player = Player.objects.get(id=self.reference_id)
            return f"{player} has joined the game!"
        elif self.reference_type == "colonize":
            region = Region.objects.get(id=self.reference_id)
            return f"{region.ruler} has colonized {region}"
        elif self.reference_type == "discover":
            region = Region.objects.get(id=self.reference_id)
            return f"Explorers have discovered {region}"
        
        return "Unknown event type"


class Round(models.Model):
    has_started = models.BooleanField(default=True)
    has_ended = models.BooleanField(default=False)
    winner = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True)
    trade_price_dict = models.JSONField(default=dict, blank=True)
    resource_bank_dict = models.JSONField(default=dict, blank=True)

    @property
    def allow_ticks(self):
        return self.has_started and not self.has_ended
        