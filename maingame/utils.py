import math
from random import randint, choice
import random

from maingame.formatters import get_goblin_ruler
from maingame.models import Artifact, Battle, Unit, Dominion, Discovery, Building, Event, Round, Faction, Resource, Spell, UserSettings
from django.contrib.auth.models import User


def get_random_resource(dominion: Dominion):
    resources = []

    for resource in Resource.objects.filter(ruler=dominion):
        if resource.name not in ["gold", "corpses", "rats"]:
            resources.append(resource)

    return choice(resources)


def create_faction_perk_dict(dominion: Dominion, faction: Faction):
    # dominion.perk_dict["book_of_grudges"] = {}

    if faction.name == "dwarf":
        dominion.perk_dict["book_of_grudges"] = {}
        # dominion.perk_dict["grudge_page_multiplier"] = 1.5
        # dominion.perk_dict["grudge_page_keep_multiplier"] = 0.05
    elif faction.name == "blessed order":
        dominion.perk_dict["sinners_per_hundred_acres_per_tick"] = 1
        dominion.perk_dict["inquisition_rate"] = 0
        dominion.perk_dict["inquisition_ticks_left"] = 0
        dominion.perk_dict["martyr_cost"] = 500
    elif faction.name == "sludgeling":
        dominion.perk_dict["free_experiments"] = 10
        dominion.perk_dict["latest_experiment_id"] = 0
        dominion.perk_dict["latest_experiment"] = {
            "should_display": False,
            "name": "",
            "op": 0,
            "dp": 0,
            "cost_dict": {
                "gold": 0,
                "sludge": 0,
            },
            "upkeep_dict": {
                "gold": 0,
                "sludge": 0,
            },
            "perk_dict": {},
        }
        dominion.perk_dict["experiment_cost_dict"] = {
            "research_per_acre": 100,
            "sludge_per_acre": 18,
        }
        dominion.perk_dict["custom_units"] = 0
        dominion.perk_dict["max_custom_units"] = 3
        dominion.perk_dict["experiments_done"] = 0
        dominion.perk_dict["recycling_refund"] = 0.8
    elif faction.name == "goblin":
        dominion.perk_dict["rats_per_acre_per_tick"] = 0.3333
        dominion.perk_dict["goblin_ruler"] = get_goblin_ruler()
        dominion.perk_dict["rulers_favorite_resource"] = get_random_resource(dominion).name
    elif faction.name == "biclops":
        dominion.perk_dict["partner_patience"] = 36
        # dominion.perk_dict["partner_unit_training_0random_1offense_2defense"] = 0
        dominion.perk_dict["partner_attack_on_sight"] = False
    elif faction.name == "gnomish special forces":
        dominion.perk_dict["infiltration_dict"] = {}

    dominion.save()


def create_resource_for_dominion(resource_identifier, dominion: Dominion):
    resource_name = resource_identifier

    resource_name = Resource.objects.get(name=resource_identifier, ruler=None).name

    if not Resource.objects.filter(ruler=dominion, name=resource_name).exists():
        base_resource = Resource.objects.get(name=resource_name, ruler=None)
        dominions_resource = base_resource
        dominions_resource.pk = None
        dominions_resource.ruler = dominion
        dominions_resource.save()


def meets_discovery_requirements(dominion: Dominion, discovery: Discovery):
    if discovery.required_faction_name and dominion.faction_name != discovery.required_faction_name:
        return False
    
    if dominion.faction_name in discovery.not_for_factions:
        return False

    for requirement in discovery.required_discoveries:
        if requirement not in dominion.learned_discoveries:
            return False
        
    if len(discovery.required_discoveries_or) > 0:
        has_at_least_one = False

        for requirement in discovery.required_discoveries_or:
            if requirement in dominion.learned_discoveries:
                has_at_least_one = True

        if not has_at_least_one:
            return False
    
    for perk, required_value in discovery.required_perk_dict.items():
        if perk not in dominion.perk_dict:
            return False
        elif required_value == True and dominion.perk_dict[perk] == False:
            return False
        elif required_value > dominion.perk_dict[perk]:
            return False

    return True


def update_available_discoveries(dominion: Dominion):
    new_discoveries = []

    for discovery in Discovery.objects.all():
        if discovery.name not in dominion.learned_discoveries and discovery.name not in dominion.available_discoveries and meets_discovery_requirements(dominion, discovery):
            dominion.available_discoveries.insert(0, discovery.name)
            new_discoveries.append(discovery.name)

    dominion.save()

    return ", ".join(new_discoveries)


def initialize_dominion(user: User, faction: Faction, display_name):
    dominion = Dominion.objects.create(
        associated_user=user, 
        name=display_name, 
        faction_name=faction.name, 
    )

    update_available_discoveries(dominion)

    for unit in Unit.objects.filter(ruler=None, faction=faction):
        give_dominion_unit(dominion, unit)

    for building_name in faction.starting_buildings:
        base_building = Building.objects.get(name=building_name, ruler=None)
        dominions_building = base_building
        dominions_building.pk = None
        dominions_building.ruler = dominion
        dominions_building.save()

        if dominions_building.resource_produced_name:
            create_resource_for_dominion(dominions_building.resource_produced_name, dominion)

    for unit in Unit.objects.filter(ruler=dominion):
        for perk_name in unit.perk_dict:
            if perk_name[-9:] == "_per_tick":
                create_resource_for_dominion(perk_name[:-9], dominion)

    if dominion.faction_name == "blessed order":
        create_resource_for_dominion("sinners", dominion)
    elif dominion.faction_name == "goblin":
        create_resource_for_dominion("rats", dominion)

    for spell in Spell.objects.filter(ruler=None, is_starter=True):
        give_dominion_spell(dominion, spell)

    dominion.primary_resource_name = faction.primary_resource_name
    dominion.primary_resource_per_acre = faction.primary_resource_per_acre
    dominion.building_primary_resource_name = faction.building_primary_resource_name
    dominion.building_secondary_resource_name = faction.building_secondary_resource_name
    dominion.building_primary_cost_per_acre = faction.building_primary_cost_per_acre
    dominion.building_secondary_cost_per_acre = faction.building_secondary_cost_per_acre
    dominion.incoming_acres_dict = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
    }

    primary_building_resource = Resource.objects.get(ruler=dominion, name=dominion.building_primary_resource_name)
    dominion.last_bought_resource_name = primary_building_resource.name
    dominion.last_sold_resource_name = primary_building_resource.name

    user_settings, _ = UserSettings.objects.get_or_create(associated_user=user)

    event = Event.objects.create(
        reference_id=dominion.id, 
        reference_type="signup", 
        category="Signup",
        message_override=f"{user_settings.display_name} has created a {faction} dominion named {dominion}"
    )

    dominion.save()

    create_faction_perk_dict(dominion, faction)

    return dominion


def abandon_dominion(dominion: Dominion):
    event = Event.objects.create(
        reference_id=dominion.id, 
        reference_type="abandon", 
        category="Abandon",
        message_override=f"{dominion} has been abandoned by {dominion.rulers_display_name}"
    )

    dominion.is_abandoned = True
    dominion.associated_user = None
    dominion.save()


def delete_dominion(dominion: Dominion):
    Resource.objects.filter(ruler=dominion).delete()
    Building.objects.filter(ruler=dominion).delete()
    Unit.objects.filter(ruler=dominion).delete()
    Spell.objects.filter(ruler=dominion).delete()
    Event.objects.filter(reference_id=dominion.id, reference_type="signup").delete()
    
    dominion.delete()


def get_trade_value(resource_name):
    building = Building.objects.get(resource_produced_name=resource_name, ruler=None)
    return 1000 / building.amount_produced

    this_round = Round.objects.first()
    total_production = 0

    for dominion in Dominion.objects.all():
        total_production += dominion.get_production(resource_name)
    
    price_modifier = 1

    if total_production > 0 and resource_name in this_round.resource_bank_dict:
        price_modifier = 1 + ((this_round.resource_bank_dict[resource_name] / (total_production * 9)) * -0.2)

    if resource_name == "gold":
        trade_value = 10 * price_modifier
    else:
        building = Building.objects.get(resource_produced_name=resource_name, ruler=None)
        trade_value = (500 / building.amount_produced) * price_modifier

    trade_value = round(trade_value, 2)

    # if resource_name == "gems":
    #     trade_value *= 1.3

    return max(1, trade_value)


def update_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        if resource_name in round.trade_price_dict:
            current_value = round.trade_price_dict[resource_name]
            goal_value = get_trade_value(resource_name)
            
            if goal_value > current_value:
                new_value = min(goal_value, current_value * 1.01)
                round.trade_price_dict[resource_name] = new_value
                round.save()
            elif goal_value < current_value:
                new_value = max(goal_value, current_value / 1.01)
                round.trade_price_dict[resource_name] = new_value
                round.save()
        else:
            round.trade_price_dict[resource_name] = get_trade_value(resource_name)

        if resource_name not in round.base_price_dict:
            round.base_price_dict[resource_name] = get_trade_value(resource_name)

    round.save()


def get_grudge_bonus(my_dominion: Dominion, other_dominion: Dominion):
    try:
        # Offense gets calculated as 1 + this
        # 0.003 gets added to animosity per page, which makes sense as it's +0.003% per page
        # X animosity is +X% OP, so we need to turn 0.003 into 0.00003 because that's how percents work
        return my_dominion.perk_dict["book_of_grudges"][str(other_dominion.id)]["animosity"] / 100
    except:
        return 0
    

def create_magnum_goopus(dominion: Dominion, encore=False):
    total_quantity = 0
    total_op = 0
    total_dp = 0
    food_upkeep = 0

    if encore:
        perk_dict = {"is_more_glorious": True}
    else:
        perk_dict = {"is_glorious": True}

    for unit in Unit.objects.filter(ruler=dominion):
        if "sludge" in unit.cost_dict and unit.quantity_at_home > 0:
            total_quantity += unit.quantity_at_home
            total_op += unit.quantity_at_home * unit.op
            total_dp += unit.quantity_at_home * unit.dp

            if "food" in unit.upkeep_dict:
                food_upkeep += unit.quantity_at_home * unit.upkeep_dict["food"]

            for perk, value in unit.perk_dict.items():
                if perk == "casualty_multiplier" and perk in perk_dict:
                    perk_dict[perk] = min(value, perk_dict[perk])
                else:
                    perk_dict[perk] = value
            
            unit.quantity_at_home = 0
            unit.save()

    encore_suffixes = [" Mk II", " 2: Electric Goopaloo", " Remastered", ": the Remix", " 2", " Jr.", " Magnum Goopier"]

    if encore:
        name = f"Magnum Goopus {random.choice(encore_suffixes)}"
    else:
        name = "Magnum Goopus"

    timer_template = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
    }

    Unit.objects.create(
        ruler=dominion,
        name=name,
        op=total_op,
        dp=total_dp,
        upkeep_dict={
            "food": food_upkeep,
        },
        perk_dict=perk_dict,
        is_trainable=False,
        quantity_at_home=1,
        training_dict=timer_template,
        returning_dict=timer_template,
    )


def unlock_discovery(dominion: Dominion, discovery_name):
    if not discovery_name in dominion.available_discoveries:
        return False
    
    dominion.learned_discoveries.append(discovery_name)

    can_take_multiple_times = False

    match discovery_name:
        case "Prosperity":
            dominion.primary_resource_per_acre += 1
            can_take_multiple_times = True
        case "Raiders":
            if "percent_bonus_to_steal" in dominion.perk_dict:
                dominion.perk_dict["percent_bonus_to_steal"] += 10
            else:
                dominion.perk_dict["percent_bonus_to_steal"] = 10
            
            dominion.save()
            can_take_multiple_times = True
        case "Battering Rams":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Battering Ram"))
        case "Palisades":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Palisade"))
        case "Bastions":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Bastion"))
        case "Zombies":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Zombie"))
        # case "Butcher":
        #     print("Implement spells, silly")
        case "Archmage":
            archmage = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Archmage"))
            archmage.quantity_at_home = 1
            archmage.save()
            dominion.has_tick_units = True
        case "Fireballs":
            fireballs = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Fireball"))
            fireballs.is_trainable = True
            fireballs.save()
        case "Gingerbrute Men":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Gingerbrute Man"))
        case "Mercenaries":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Mercenary"))
        case "Grudgestoker":
            grudgestoker = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Grudgestoker"))
            grudgestoker.quantity_at_home = 1
            grudgestoker.save()
            dominion.has_tick_units = True
        case "Never Forget":
            dominion.perk_dict["grudge_page_keep_multiplier"] = 0.2
        case "Miners":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Miner"))
            dominion.perk_dict["mining_depth"] = 0
        case "Doom Prospectors":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Doom Prospector"))
        case "Mithril":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Steelbreaker"))
            give_dominion_building(dominion, Building.objects.get(ruler=None, name="mithril mine"))
        case "The Deep Angels":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Deep Angel"))
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Deep Apostle"))
        # case "Gem Mines":
        #     give_dominion_building(dominion, Building.objects.get(ruler=None, name="mine"))
        case "Living Saints":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Living Saint"))
        case "Penitent Engines":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Penitent Engine"))
        case "Heresy":
            dominion.perk_dict["sinners_per_hundred_acres_per_tick"] *= 3
        case "Grim Sacrament":
            dominion.perk_dict["inquisition_makes_corpses"] = True
            create_resource_for_dominion("corpses", dominion)
        case "Wights":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Wight"))
        case "Cathedral Titans":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Cathedral Titan"))
        case "Funerals":
            dominion.perk_dict["faith_per_power_died"] = 10
        case "Cremain Knights":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Cremain Knight"))
        case "More Experiment Slots":
            dominion.perk_dict["max_custom_units"] = 4
        case "Even More Experiment Slots":
            dominion.perk_dict["max_custom_units"] = 6
        case "Recycling Center":
            dominion.perk_dict["recycling_refund"] = 0.95
        case "Magnum Goopus":
            create_magnum_goopus(dominion)
        case "Encore":
            create_magnum_goopus(dominion, encore=True)
        case "Wreckin Ballers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Wreckin Baller"))
        case "Charcutiers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Charcutier"))
        case "Rat Trainers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Rat Trainer"))
        case "Bestow Biclopean Ambition":
            give_dominion_spell(dominion, Spell.objects.get(ruler=None, name="Bestow Biclopean Ambition"))
        case "Triclops":
            dominion.perk_dict["percent_chance_of_instant_return"] = 10
        case "Safecrackers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Safecracker"))
        case "Juggernaut Tanks":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Juggernaut Tank"))
        case "Inferno Mines":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Inferno Mine"))
        case "Rapid Deployment":
            dominion.perk_dict["unit_training_time"] = "6"

    if not can_take_multiple_times:
        dominion.available_discoveries.remove(discovery_name)

    message = update_available_discoveries(dominion)
    dominion.save()

    return message


def give_dominion_unit(dominion: Dominion, unit: Unit):
    try:
        dominions_unit = Unit.objects.get(ruler=dominion, name=unit.name)
    except:
        dominions_unit = unit
        dominions_unit.pk = None
        dominions_unit.ruler = dominion
        dominions_unit.save()

        for resource in unit.cost_dict:
            create_resource_for_dominion(resource, dominion)

    return dominions_unit


def give_dominion_spell(dominion: Dominion, spell: Spell):
    dominions_spell = spell
    dominions_spell.pk = None
    dominions_spell.ruler = dominion
    dominions_spell.save()

    return dominions_spell


def give_dominion_building(dominion: Dominion, building: Building):
    dominions_building = building
    dominions_building.pk = None
    dominions_building.ruler = dominion
    dominions_building.save()

    if building.amount_produced > 0:
        create_resource_for_dominion(building.resource_produced_name, dominion)

    return dominions_building


def round_x_to_nearest_y(x, round_to_nearest):
    return round_to_nearest * round(x/round_to_nearest)


def get_acres_conquered(attacker: Dominion, target: Dominion):
    return int(0.06 * target.acres * (target.acres / attacker.acres))


def do_biclops_partner_attack(dominion: Dominion):
    if "partner_attack_on_sight" not in dominion.perk_dict:
        return
    
    if not dominion.perk_dict["partner_attack_on_sight"]:
        if dominion.has_units_in_training and dominion.perk_dict["partner_patience"] > -24:
            return
        elif dominion.perk_dict["partner_patience"] > 0:
            return
        
    do_forced_attack(dominion, use_always_dies_units=True)
    

def do_forced_attack(dominion: Dominion, use_always_dies_units=False):
    if dominion.incoming_acres > 0:
        return    
    
    op_from_offensive_units_at_home = 0
    offensive_units = []

    for unit in Unit.objects.filter(ruler=dominion):
        if unit.op > unit.dp:
            op_from_offensive_units_at_home += unit.quantity_at_home * unit.op

            if "always_dies_on_offense" not in unit.perk_dict:
                offensive_units.append(unit)
            elif "always_dies_on_offense" in unit.perk_dict and use_always_dies_units:
                offensive_units.append(unit)

    def op_dp_ratio(op, dp):
        if dp == 0:
            return 999999
        else:
            return op/dp

    offensive_units = sorted(offensive_units, key=lambda x: op_dp_ratio(x.op, x.dp), reverse=True)

    hasnt_attacked_yet = True

    for other_dominion in Dominion.objects.all().order_by("-acres"):
        op_multiplier = dominion.offense_multiplier + get_grudge_bonus(dominion, other_dominion)
        op_against_this_dominion = op_from_offensive_units_at_home * op_multiplier

        if (other_dominion != dominion and 
            other_dominion.is_oop and 
            other_dominion.acres > 0.75 * dominion.acres and 
            op_against_this_dominion > other_dominion.defense and
            hasnt_attacked_yet
        ):
            # {'16650': {'unit': <Unit: ERIKTEST -- Ironclops (20/12) -- x490>, 'quantity_sent': 10}}
            units_sent_dict = {}
            raw_op_sent = 0

            for offensive_unit in offensive_units:
                this_unit_dict = {"unit": offensive_unit, "quantity_sent": 0}
                while raw_op_sent * op_multiplier <= other_dominion.defense and this_unit_dict["quantity_sent"] < offensive_unit.quantity_at_home:
                    this_unit_dict["quantity_sent"] += 1
                    raw_op_sent += offensive_unit.op
                
                if this_unit_dict["quantity_sent"] > 0:
                    units_sent_dict[str(offensive_unit.id)] = this_unit_dict
                    
            do_invasion(units_sent_dict, my_dominion=dominion, target_dominion=other_dominion)
            hasnt_attacked_yet = False


def do_invasion(units_sent_dict, my_dominion: Dominion, target_dominion: Dominion):
    round = Round.objects.first()
    total_units_sent = 0
    defense_snapshot = target_dominion.defense

    for unit_id, unit_dict in units_sent_dict.items():
        unit = Unit.objects.get(id=unit_id)
        total_units_sent += unit_dict["quantity_sent"]

    # Calculate OP, land return speed, and others
    offense_sent = 0
    bonus_steal_offense_sent = 0
    slowest_unit_return_ticks = 1

    for unit_details_dict in units_sent_dict.values():
        unit = unit_details_dict["unit"]
        quantity_sent = unit_details_dict["quantity_sent"]
        offense_sent += unit.op * quantity_sent

        if "op_bonus_percent_for_stealing_artifacts" in unit.perk_dict:
            bonus_steal_offense_sent += (unit.perk_dict["op_bonus_percent_for_stealing_artifacts"] / 100) * unit.op

        if "returns_in_ticks" in unit.perk_dict:
            slowest_unit_return_ticks = max(slowest_unit_return_ticks, unit.perk_dict["returns_in_ticks"])
        else:
            slowest_unit_return_ticks = 12

    steal_offense_sent = offense_sent + bonus_steal_offense_sent
    offense_sent *= (my_dominion.offense_multiplier + get_grudge_bonus(my_dominion, target_dominion))
    steal_offense_sent *= (my_dominion.offense_multiplier + get_grudge_bonus(my_dominion, target_dominion))

    # Determine victor
    if offense_sent >= target_dominion.defense:
        for unit_id, unit_dict in units_sent_dict.items():
            unit = Unit.objects.get(id=unit_id)
            total_units_sent += unit_dict["quantity_sent"]
            unit.quantity_at_home -= unit_dict["quantity_sent"]
            unit.save()
        
        my_dominion.highest_raw_op_sent = max(offense_sent, my_dominion.highest_raw_op_sent)
        my_dominion.save()
        attacker_victory = True
        target_dominion.complacency = 0
        target_dominion.failed_defenses += 1
        target_dominion.save()
        my_dominion.successful_invasions += 1
        my_dominion.determination = 0
        my_dominion.save()

        # Handle grudges
        if "book_of_grudges" in target_dominion.perk_dict:
            pages_to_gain = 50

            for _ in range(round.ticks_passed):
                pages_to_gain *= 1.0015

            if "grudge_page_multiplier" in target_dominion.perk_dict:
                pages_to_gain *= target_dominion.perk_dict["grudge_page_multiplier"]
            
            pages_to_gain = int(pages_to_gain)

            if str(my_dominion.id) in target_dominion.perk_dict["book_of_grudges"]:
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["pages"] += pages_to_gain
            else:
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)] = {}
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["pages"] = pages_to_gain
                target_dominion.perk_dict["book_of_grudges"][str(my_dominion.id)]["animosity"] = 0

        if "free_experiments" in target_dominion.perk_dict:
            target_dominion.perk_dict["free_experiments"] += 5
    else:
        return 0, "Only successful invasions allowed (for now?)"
    
    stolen_artifact = None

    # Handle stealing artifacts
    defender_artifact_count = Artifact.objects.filter(ruler=target_dominion).count()

    if attacker_victory and defender_artifact_count > 0:
        print("defense_snapshot", defense_snapshot)
        print("offense_sent", offense_sent)
        print("steal_offense_sent", steal_offense_sent)

        percent_chance = ((steal_offense_sent / defense_snapshot) - 1) * 100
        percent_chance *= my_dominion.artifact_steal_chance_multiplier
        
        # 1.5% chance to steal per 1% OP exceeds DP
        percent_chance *= 1.5

        print("percent_chance", percent_chance)

        do_steal_artifact = False

        for _ in range(defender_artifact_count):
            if percent_chance >= randint(1, 100):
                do_steal_artifact = True

        if do_steal_artifact:
            defenders_artifacts = []

            for artifact in Artifact.objects.filter(ruler=target_dominion):
                defenders_artifacts.append(artifact)

            stolen_artifact = random.choice(defenders_artifacts)
            assign_artifact(stolen_artifact, my_dominion)

    battle_units_sent_dict = {}
    battle_units_defending_dict = {}

    for unit_id, data in units_sent_dict.items():
        battle_units_sent_dict[unit_id] = data["quantity_sent"]

    for unit in Unit.objects.filter(ruler=target_dominion):
        if unit.quantity_at_home > 0 and unit.dp > 0:
            battle_units_defending_dict[str(unit.id)] = unit.quantity_at_home
    
    battle = Battle.objects.create(
        attacker=my_dominion,
        defender=target_dominion,
        stolen_artifact=stolen_artifact,
        winner=my_dominion if attacker_victory else target_dominion,
        op=offense_sent,
        dp=defense_snapshot,
        units_sent_dict=battle_units_sent_dict,
        units_defending_dict=battle_units_defending_dict,
    )

    event = Event.objects.create(
        reference_id=battle.id, 
        reference_type="battle", 
        category="Invasion",
    )

    event.notified_dominions.add(my_dominion)
    event.notified_dominions.add(target_dominion)
    target_dominion.has_unread_events = True
    target_dominion.save()

    if stolen_artifact:
        artifact_event = Event.objects.create(
            reference_id=stolen_artifact.id, 
            reference_type="artifact", 
            category="Artifact Stolen",
            message_override=f"{my_dominion} stole {stolen_artifact.name} from {target_dominion}"
        )
        artifact_event.notified_dominions.add(my_dominion)
        artifact_event.notified_dominions.add(target_dominion)
        artifact_event.save()

    # Handle biclops patience
    if "partner_patience" in my_dominion.perk_dict:
        my_dominion.perk_dict["partner_patience"] = int(24 * my_dominion.acres / (target_dominion.acres))
        my_dominion.save()

    # Handle goblin Wreckin Ballers
    if "Wreckin Ballers" in my_dominion.learned_discoveries:
        for unit_details_dict in units_sent_dict.values():
            unit = unit_details_dict["unit"]
            quantity_sent = unit_details_dict["quantity_sent"]

            # Right now it assumes a value of 0.5. Please don't make me figure out how to handle something greater than 1.
            if "random_allies_killed_on_invasion" in unit.perk_dict:
                # When in doubt, they kill themselves, just to help avoid exceptions
                victim = unit_details_dict
                victim_count = 0

                for _ in range(int(quantity_sent / 2)):
                    roll = randint(1, total_units_sent - victim_count)

                    for victim_details_dict in units_sent_dict.values():
                        if roll <= victim_details_dict["quantity_sent"]:
                            victim = victim_details_dict
                            break
                        else:
                            roll -= victim_details_dict["quantity_sent"]

                    victim_count += 1
                    victim["quantity_sent"] -= 1

    # Determine casualty rates and handle victory triggers
    if attacker_victory:
        offensive_survival = 0.9
        defensive_survival = 0.95

        if Artifact.objects.filter(name="Death's True Name", ruler=target_dominion).exists():
            defensive_survival_bonus = (1 - defensive_survival) / 2
            defensive_survival += defensive_survival_bonus

        acres_conquered = get_acres_conquered(my_dominion, target_dominion)
        target_dominion.acres -= acres_conquered
        target_dominion.save()

        ticks_for_land = str(slowest_unit_return_ticks)

        if Artifact.objects.filter(name="The Stable of the North Wind", ruler=my_dominion).exists():
            ticks_for_land = str(min(10, slowest_unit_return_ticks))
        
        my_dominion.incoming_acres_dict[ticks_for_land] += acres_conquered * 2

        my_dominion.save()
        
        battle.acres_conquered = acres_conquered
        battle.save()

        # Attackers erase their grudges for a dominion once they hit them
        if "book_of_grudges" in my_dominion.perk_dict and str(target_dominion.id) in my_dominion.perk_dict["book_of_grudges"]:
            if "grudge_page_keep_multiplier" in my_dominion.perk_dict:
                pages = my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["pages"]
                multiplier = my_dominion.perk_dict["grudge_page_keep_multiplier"]
                my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["pages"] = max(1, int(pages * multiplier))
                my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["animosity"] *= 0
            else:
                del my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]

            my_dominion.save()
    else:
        offensive_survival = 0.85

        # If you're not close, then no casualties
        if offense_sent < target_dominion.defense / 2:
            defensive_survival = 1
        else:
            defensive_survival = 0.98

    total_casualties = 0
    defensive_casualties = 0
    offensive_casualties = 0

    # Apply offensive casualties and return the survivors home
    for unit_details_dict in units_sent_dict.values():
        # unit = unit_details_dict["unit"]
        unit = Unit.objects.get(ruler=my_dominion, name=unit_details_dict["unit"].name)
        quantity_sent = unit_details_dict["quantity_sent"]

        if "immortal" in unit.perk_dict:
            survivors = quantity_sent
            deaths = 0
        else:
            survivors = math.ceil(quantity_sent * offensive_survival)
            deaths = quantity_sent - survivors

            if "casualty_multiplier" in unit.perk_dict:
                bonus_death_multiplier = unit.perk_dict["casualty_multiplier"] - 1
                survivors -= int(deaths * bonus_death_multiplier)

        if "always_dies_on_offense" in unit.perk_dict:
            survivors = 0
        elif "faith_per_power_died" in my_dominion.perk_dict:
            faith = Resource.objects.get(ruler=my_dominion, name="faith")
            faith.quantity += deaths * unit.op * my_dominion.perk_dict["faith_per_power_died"]
            faith.save()

        casualties = quantity_sent - survivors

        if "mana" not in unit.upkeep_dict and "mana" not in unit.cost_dict and "always_dies_on_offense" not in unit.perk_dict:
            offensive_casualties += casualties

        # Handle units returning
        possible_return_ticks = [12]

        if "returns_in_ticks" in unit.perk_dict:
            # unit.returning_dict[str(unit.perk_dict["returns_in_ticks"])] += survivors
            possible_return_ticks.append(unit.perk_dict["returns_in_ticks"])
        
        if Artifact.objects.filter(name="The Stable of the North Wind", ruler=my_dominion).exists():
            possible_return_ticks.append(10)
        
        possible_return_ticks.sort()
        do_instant_return = False

        if "percent_chance_of_instant_return" in my_dominion.perk_dict:
            percent_chance_of_instant_return = my_dominion.perk_dict["percent_chance_of_instant_return"]
            
            if percent_chance_of_instant_return >= randint(1, 100):
                do_instant_return = True

        if do_instant_return:
            unit.quantity_at_home += survivors
        else:
            unit.returning_dict[str(possible_return_ticks[0])] += survivors

        unit.save()

    # Apply defensive casualties
    for unit in Unit.objects.filter(ruler=target_dominion):
        if "immortal" in unit.perk_dict or unit.dp == 0:
            survivors = unit.quantity_at_home
            deaths = 0
        elif "always_dies_on_defense" in unit.perk_dict:
            survivors = 0
        else:
            deaths = int((1 - defensive_survival) * unit.quantity_at_home)

            if "casualty_multiplier" in unit.perk_dict:
                deaths = int(unit.perk_dict["casualty_multiplier"] * deaths)

            survivors = unit.quantity_at_home - deaths

        casualties = unit.quantity_at_home - survivors

        if "faith_per_power_died" in target_dominion.perk_dict:
            faith = Resource.objects.get(ruler=target_dominion, name="faith")
            faith.quantity += deaths * unit.dp * target_dominion.perk_dict["faith_per_power_died"]
            faith.save()

        if "mana" not in unit.upkeep_dict and "mana" not in unit.cost_dict and "always_dies_on_defense" not in unit.perk_dict:
            defensive_casualties += casualties

        unit.quantity_at_home = survivors
        unit.save()

    total_casualties = offensive_casualties + defensive_casualties

    # Handle martyrs
    if target_dominion.faction_name == "blessed order":
        faith = Resource.objects.get(ruler=target_dominion, name="faith")
        martyrs_affordable = int(faith.quantity / target_dominion.perk_dict["martyr_cost"])
        martyrs_gained = min(martyrs_affordable, defensive_casualties)
        faith.quantity -= target_dominion.perk_dict["martyr_cost"] * martyrs_gained
        faith.save()
        martyrs = Unit.objects.get(ruler=target_dominion, name="Blessed Martyr")
        martyrs.quantity_at_home += martyrs_gained
        martyrs.save()

    # Handle corpses
    if attacker_victory and Resource.objects.filter(ruler=my_dominion, name="corpses").exists():
        my_bodies = Resource.objects.get(ruler=my_dominion, name="corpses")
        my_bodies.quantity += total_casualties
        my_bodies.save()
        battle.battle_report_notes.append(f"{my_dominion} gained {total_casualties} corpses.")
        battle.save()
    elif not attacker_victory and Resource.objects.filter(ruler=target_dominion, name="corpses").exists():
        targets_bodies = Resource.objects.get(ruler=target_dominion, name="corpses")
        targets_bodies.quantity += total_casualties
        targets_bodies.save()
        battle.battle_report_notes.append(f"{target_dominion} gained {total_casualties} corpses.")
        battle.save()

    # Handle goblin leadership change
    if attacker_victory and "goblin_ruler" in target_dominion.perk_dict:
        target_dominion.perk_dict["goblin_ruler"] = get_goblin_ruler()
        target_dominion.perk_dict["rulers_favorite_resource"] = get_random_resource(target_dominion).name
        target_dominion.save()

    return battle.id, "-- Congratulations, your invasion didn't crash! --"


def do_quest(units_sent_dict, my_dominion: Dominion):
    total_units_sent = 0

    for unit_id, unit_dict in units_sent_dict.items():
        unit = Unit.objects.get(id=unit_id)
        total_units_sent += unit_dict["quantity_sent"]
        unit.quantity_at_home -= unit_dict["quantity_sent"]
        unit.save()

    offense_sent = 0

    # Calculate OP
    for unit_details_dict in units_sent_dict.values():
        unit = unit_details_dict["unit"]
        quantity_sent = unit_details_dict["quantity_sent"]
        offense_sent += unit.op * quantity_sent

    my_dominion.highest_raw_op_sent = max(offense_sent, my_dominion.highest_raw_op_sent)

    offense_sent *= my_dominion.offense_multiplier

    my_dominion.op_quested += offense_sent
    my_dominion.save()

    # battle_units_sent_dict = {}
    # battle_units_defending_dict = {}

    # for unit_id, data in units_sent_dict.items():
    #     battle_units_sent_dict[unit_id] = data["quantity_sent"]

    # for unit in Unit.objects.filter(ruler=target_dominion):
    #     if unit.quantity_at_home > 0 and unit.dp > 0:
    #         battle_units_defending_dict[str(unit.id)] = unit.quantity_at_home
    
    # battle = Battle.objects.create(
    #     attacker=my_dominion,
    #     defender=target_dominion,
    #     winner=my_dominion if attacker_victory else target_dominion,
    #     op=offense_sent,
    #     dp=target_dominion.defense,
    #     units_sent_dict=battle_units_sent_dict,
    #     units_defending_dict=battle_units_defending_dict,
    # )

    event = Event.objects.create(
        reference_type="quest", 
        category="Quest",
        message_override=f"{my_dominion} went on a quest with {int(offense_sent):2,} OP"
    )
    
    event.notified_dominions.add(my_dominion)

    # Handle goblin Wreckin Ballers
    if "Wreckin Ballers" in my_dominion.learned_discoveries:
        for unit_details_dict in units_sent_dict.values():
            unit = unit_details_dict["unit"]
            quantity_sent = unit_details_dict["quantity_sent"]

            # RIght now it assumes a value of 0.5. Please don't make me figure out how to handle something greater than 1.
            if "random_allies_killed_on_invasion" in unit.perk_dict:
                # When in doubt, they kill themselves, just to help avoid exceptions
                victim = unit
                victim_count = 0

                for _ in range(int(quantity_sent / 2)):
                    roll = randint(1, total_units_sent - victim_count)

                    for victim_details_dict in units_sent_dict.values():
                        if roll <= victim_details_dict["quantity_sent"]:
                            victim = victim_details_dict
                            break
                        else:
                            roll -= victim_details_dict["quantity_sent"]

                    victim_count += 1
                    victim["quantity_sent"] -= 1

    # Apply offensive casualties and return the survivors home
    for unit_details_dict in units_sent_dict.values():
        unit = Unit.objects.get(ruler=my_dominion, name=unit_details_dict["unit"].name)
        quantity_sent = unit_details_dict["quantity_sent"]
        unit.returning_dict["12"] += quantity_sent
        unit.save()

    # chance for an artifact if you're highest quester
    artifact_chance_percent = 20
    base_artifact_chance = artifact_chance_percent * 100
    your_quest_ratio = (my_dominion.op_quested_per_acre) / get_highest_op_quested()
    your_artifact_chance = max(100, base_artifact_chance * your_quest_ratio)
    roll = randint(1, 10000)

    if your_artifact_chance >= roll and Artifact.objects.filter(ruler=None).count() > 0:
        artifact = give_random_unowned_artifact_to_dominion(my_dominion)
        artifact_event = Event.objects.create(
            reference_id=artifact.id, 
            reference_type="artifact", 
            category="Artifact Discovered",
            message_override=f"{my_dominion} found {artifact.name}"
        )
        artifact_event.notified_dominions.add(my_dominion)
        artifact_event.save()
        my_dominion.op_quested = 0
        my_dominion.save()
        return f"You embark upon a quest and find {artifact.name}!"

    return "You embark upon a quest"


def give_random_unowned_artifact_to_dominion(dominion: Dominion):
    unowned_artifacts = []

    for artifact in Artifact.objects.filter(ruler=None):
        if dominion.faction_name == "Blessed Order" and artifact.name == "Death's True Name":
            pass
        else:
            unowned_artifacts.append(artifact)

    given_artifact = random.choice(unowned_artifacts)
    assign_artifact(given_artifact, dominion)

    return given_artifact


def assign_artifact(artifact: Artifact, new_owner: Dominion):
    if new_owner.faction_name == "Blessed Order" and artifact.name == "Death's True Name":
        pass
    else:
        artifact.ruler = new_owner

    if artifact.name == "The Eternal Egg of the Flame Princess":
        give_dominion_unit(new_owner, Unit.objects.get(ruler=None, name="Fireball"))
    elif artifact.name == "The Infernal Contract":
        give_dominion_unit(new_owner, Unit.objects.get(ruler=None, name="Imp"))

    artifact.save()


def get_highest_op_quested():
    highest_op_quested = 0.0001
    
    for dominion in Dominion.objects.all():
        highest_op_quested = max(highest_op_quested, dominion.op_quested_per_acre)

    return highest_op_quested


def cast_spell(spell: Spell, target=None):
    dominion = spell.ruler
    mana = Resource.objects.get(ruler=dominion, name="mana")

    if mana.quantity < spell.mana_cost:
        return
    elif spell.cooldown_remaining > 0:
        return
    
    mana.quantity -= spell.mana_cost
    mana.save()

    spell.cooldown_remaining = spell.cooldown
    spell.save()

    match spell.name:
        case "Bestow Biclopean Ambition":
            if target:
                target.perk_dict["biclopean_ambition_ticks_remaining"] = 11
                target.save()
        case "Power Overwhelming":
            for unit in Unit.objects.filter(ruler=dominion):
                if unit.is_trainable and unit.op > unit.dp and "always_dies_on_offense" not in unit.perk_dict:
                    try:
                        overwhelming_unit = Unit.objects.get(ruler=dominion, name=f"Overwhelming {unit.name}", op=(2 * unit.op), dp=unit.dp)
                    except:
                        overwhelming_unit = Unit.objects.get(id=unit.id)  # If I set it to 'unit' then it fucks up
                        overwhelming_unit.pk = None
                        overwhelming_unit.name = f"Overwhelming {unit.name}"
                        overwhelming_unit.op *= 2
                        overwhelming_unit.quantity_at_home = 0
                        overwhelming_unit.is_trainable = False
                        overwhelming_unit.cost_dict = {}
                        overwhelming_unit.perk_dict["is_releasable"] = True
                        overwhelming_unit.perk_dict["percent_attrition"] = 3

                    overwhelming_quantity = int(unit.quantity_at_home * 0.2)

                    if overwhelming_quantity > 0:
                        overwhelming_unit.quantity_at_home += overwhelming_quantity
                        unit.quantity_at_home -= overwhelming_quantity
                        unit.save()

                        timer_template = {
                            "1": 0,
                            "2": 0,
                            "3": 0,
                            "4": 0,
                            "5": 0,
                            "6": 0,
                            "7": 0,
                            "8": 0,
                            "9": 0,
                            "10": 0,
                            "11": 0,
                            "12": 0,
                        }

                        overwhelming_unit.training_dict = timer_template
                        overwhelming_unit.returning_dict = timer_template
                        overwhelming_unit.save()