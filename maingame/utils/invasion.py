import math
from random import randint
import random

from maingame.formatters import get_goblin_ruler
from maingame.models import Artifact, Battle, Unit, Dominion, Event, Round, Resource
from maingame.utils.utils import get_acres_conquered, get_grudge_bonus, get_random_resource, get_unit_from_dict


def handle_grudges_from_attack(attacker: Dominion, defender: Dominion=None):
    if "book_of_grudges" in defender.perk_dict:
        round = Round.objects.first()
        pages_to_gain = 50

        for _ in range(round.ticks_passed):
            pages_to_gain *= 1.002

        if "grudge_page_multiplier" in defender.perk_dict:
            pages_to_gain *= defender.perk_dict["grudge_page_multiplier"]
        
        pages_to_gain = int(pages_to_gain)

        if str(attacker.id) in defender.perk_dict["book_of_grudges"]:
            defender.perk_dict["book_of_grudges"][str(attacker.id)]["pages"] += pages_to_gain
        else:
            defender.perk_dict["book_of_grudges"][str(attacker.id)] = {}
            defender.perk_dict["book_of_grudges"][str(attacker.id)]["pages"] = pages_to_gain
            defender.perk_dict["book_of_grudges"][str(attacker.id)]["animosity"] = 0

        defender.save()
    
    if "book_of_grudges" in attacker.perk_dict and str(defender.id) in attacker.perk_dict["book_of_grudges"]:
        if "grudge_page_keep_multiplier" in attacker.perk_dict:
            pages = attacker.perk_dict["book_of_grudges"][defender.strid]["pages"]
            multiplier = attacker.perk_dict["grudge_page_keep_multiplier"]
            attacker.perk_dict["book_of_grudges"][defender.strid]["pages"] = max(1, int(pages * multiplier))
            attacker.perk_dict["book_of_grudges"][defender.strid]["animosity"] *= 0
        else:
            del attacker.perk_dict["book_of_grudges"][defender.strid]

        for grudge_dict in attacker.perk_dict["book_of_grudges"].values():
            grudge_dict["animosity"] /= 2

        attacker.save()


def update_units_sent_dict_for_wreckin_ballers(units_sent_dict, total_units_sent):
    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
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

    return units_sent_dict


def generate_battle(units_sent_dict, attacker: Dominion, defender: Dominion, offense_sent, defense_snapshot, acres_conquered):
    battle_units_sent_dict = {}
    battle_units_defending_dict = {}

    for unit_id, data in units_sent_dict.items():
        battle_units_sent_dict[unit_id] = data["quantity_sent"]

    for unit in Unit.objects.filter(ruler=defender):
        if unit.quantity_at_home > 0 and unit.dp > 0:
            battle_units_defending_dict[str(unit.id)] = unit.quantity_at_home
    
    battle = Battle.objects.create(
        attacker=attacker,
        defender=defender,
        winner=attacker,
        op=offense_sent,
        dp=defense_snapshot,
        units_sent_dict=battle_units_sent_dict,
        units_defending_dict=battle_units_defending_dict,
        acres_conquered=acres_conquered,
    )

    event = Event.objects.create(
        reference_id=battle.id, 
        reference_type="battle", 
        category="Invasion",
    )

    event.notified_dominions.add(attacker)
    event.notified_dominions.add(defender)
    defender.has_unread_events = True
    defender.save()

    return battle


def get_op_and_dp_left(units_sent_dict, attacker: Dominion, defender: Dominion=None, is_infiltration=False):
    offense_sent = 0
    raw_defense = attacker.raw_defense

    if defender and "infiltration_dict" in attacker.perk_dict and defender.strid in attacker.perk_dict["infiltration_dict"] and not is_infiltration:
        offense_sent += attacker.perk_dict["infiltration_dict"][defender.strid]

    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        modified_unit_op = unit.op
        quantity_sent = unit_details_dict["quantity_sent"]

        if "gets_op_bonus_equal_to_percent_of_target_complacency" in unit.perk_dict:
            op_multiplier = (defender.complacency_penalty_percent / 100) * (unit.perk_dict["gets_op_bonus_equal_to_percent_of_target_complacency"] / 100)
            modified_unit_op *= 1 + op_multiplier

        if "rats_launched" in unit.perk_dict and "op_if_rats_launched" in unit.perk_dict:
            rats = Resource.objects.get(ruler=attacker, name="rats")
            max_launches = min(quantity_sent, int(rats.quantity / unit.perk_dict["rats_launched"]))
            offense_sent = max_launches * unit.perk_dict["op_if_rats_launched"]

        if is_infiltration:
            if "invasion_plan_power" in unit.perk_dict:
                offense_sent += unit.perk_dict["invasion_plan_power"] * quantity_sent
        else:
            offense_sent += modified_unit_op * quantity_sent

        raw_defense -= unit.dp * quantity_sent

    grudge_bonus = 0

    if "book_of_grudges" in attacker.perk_dict:
        grudge_bonus = get_grudge_bonus(attacker, defender)

    if not is_infiltration:
        offense_sent *= (attacker.offense_multiplier + grudge_bonus)

    offense_sent = int(offense_sent)

    defense_left = int(raw_defense * attacker.defense_multiplier)

    return offense_sent, defense_left, raw_defense


def handle_invasion_perks(attacker: Dominion, defender: Dominion, defensive_casualties):
    handle_grudges_from_attack(attacker, defender)

    if "free_experiments" in defender.perk_dict:
        defender.perk_dict["free_experiments"] += 5

    if "partner_patience" in attacker.perk_dict:
        attacker.perk_dict["partner_patience"] = int(24 * attacker.acres / (defender.acres))
        attacker.save()

    if "infiltration_dict" in attacker.perk_dict:
        if defender.strid in attacker.perk_dict["infiltration_dict"]:
            del attacker.perk_dict["infiltration_dict"][defender.strid]
            attacker.save()

    if "goblin_ruler" in defender.perk_dict:
        defender.perk_dict["goblin_ruler"] = get_goblin_ruler()
        defender.perk_dict["rulers_favorite_resource"] = get_random_resource(defender).name
        defender.save()

    if defender.faction_name == "blessed order":
        faith = Resource.objects.get(ruler=defender, name="faith")
        martyrs_affordable = int(faith.quantity / defender.perk_dict["martyr_cost"])
        martyrs_gained = min(martyrs_affordable, defensive_casualties)
        faith.quantity -= defender.perk_dict["martyr_cost"] * martyrs_gained
        faith.save()
        martyrs = Unit.objects.get(ruler=defender, name="Blessed Martyr")
        martyrs.quantity_at_home += martyrs_gained
        martyrs.save()


def do_offensive_casualties_and_return(units_sent_dict, attacker: Dominion):
    offensive_casualties = 0
    new_corpses = 0

    do_instant_return = False

    if "percent_chance_of_instant_return" in attacker.perk_dict:
        percent_chance_of_instant_return = attacker.perk_dict["percent_chance_of_instant_return"]
        
        if percent_chance_of_instant_return >= randint(1, 100):
            do_instant_return = True

    for unit_details_dict in units_sent_dict.values():
        offensive_casualty_rate = 0.1
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]
        casualties = 0
        offensive_casualty_rate = 0.1

        if "immortal" in unit.perk_dict:
            offensive_casualty_rate = 0
        elif "always_dies_on_offense" in unit.perk_dict:
            offensive_casualty_rate = 1
        elif "casualty_multiplier" in unit.perk_dict:
            offensive_casualty_rate *= unit.perk_dict["casualty_multiplier"]

        casualties = int(quantity_sent * offensive_casualty_rate)
        survivors = quantity_sent - casualties

        if "food" in unit.upkeep_dict:
            new_corpses += casualties

        if do_instant_return:
            unit.quantity_at_home += survivors
        else:
            return_ticks = str(unit.perk_dict["returns_in_ticks"]) if "returns_in_ticks" in unit.perk_dict else "12"
            unit.quantity_at_home -= quantity_sent
            unit.returning_dict[return_ticks] = survivors

        unit.save()
        offensive_casualties += casualties

    return offensive_casualties, new_corpses


def do_defensive_casualties(defender: Dominion):
    defensive_casualties = 0
    new_corpses = 0

    for unit in Unit.objects.filter(ruler=defender, dp__gt=0, quantity_at_home__gt=0):
        defensive_casualty_rate = 0.05
        casualties = 0

        if "immortal" in unit.perk_dict:
            defensive_casualty_rate = 0
        elif "always_dies_on_defense" in unit.perk_dict:
            defensive_casualty_rate = 1
        elif "casualty_multiplier" in unit.perk_dict:
            defensive_casualty_rate *= unit.perk_dict["casualty_multiplier"]

        casualties = int(unit.quantity_at_home * defensive_casualty_rate)

        if "faith_per_power_died" in defender.perk_dict:
            faith = Resource.objects.get(ruler=defender, name="faith")
            faith.quantity += casualties * unit.dp * defender.perk_dict["faith_per_power_died"]
            faith.save()

        if "food" in unit.upkeep_dict:
            new_corpses += casualties

        unit.quantity_at_home -= casualties
        unit.save()
        defensive_casualties += casualties

    return defensive_casualties, new_corpses


def do_invasion(units_sent_dict, attacker: Dominion, defender: Dominion):
    total_units_sent = 0
    raw_op_sent = 0
    defense_snapshot = defender.defense
    slowest_unit_return_ticks = 1
    offense_sent, dp_left, _ = get_op_and_dp_left(units_sent_dict, attacker, defender=defender)
    acres_conquered = get_acres_conquered(attacker, defender)

    if defender.defense > offense_sent:
        return 0, "No failed invasions allowed"
    if dp_left < attacker.acres * 5:
        return 0, "Insufficient defense left by attacker"
    
    # Get units sent for wreckin ballers, slowest return time for land return time, raw OP sent for updating max
    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]
        raw_op_sent += unit.op * quantity_sent

        if "returns_in_ticks" in unit.perk_dict:
            slowest_unit_return_ticks = max(slowest_unit_return_ticks, unit.perk_dict["returns_in_ticks"])
        else:
            slowest_unit_return_ticks = 12

        if "rats_launched" in unit.perk_dict and "op_if_rats_launched" in unit.perk_dict:
            rats = Resource.objects.get(ruler=attacker, name="rats")
            max_launches = min(quantity_sent, int(rats.quantity / unit.perk_dict["rats_launched"]))
            rats.quantity -= max_launches * unit.perk_dict["rats_launched"]
            rats.save()

    defender.complacency = 0
    defender.failed_defenses += 1
    defender.acres -= acres_conquered
    defender.save()

    attacker.highest_raw_op_sent = max(raw_op_sent, attacker.highest_raw_op_sent)
    attacker.successful_invasions += 1
    attacker.determination = 0
    ticks_for_land = str(slowest_unit_return_ticks)
    attacker.incoming_acres_dict[ticks_for_land] += acres_conquered * 2
    attacker.save()

    battle = generate_battle(units_sent_dict, attacker, defender, offense_sent, defense_snapshot, acres_conquered)

    if "Wreckin Ballers" in attacker.learned_discoveries:
        units_sent_dict = update_units_sent_dict_for_wreckin_ballers(units_sent_dict, total_units_sent)

    _, offensive_corpses = do_offensive_casualties_and_return(units_sent_dict, attacker)
    defensive_casualties, defensive_corpses = do_defensive_casualties(defender)

    new_corpses = offensive_corpses + defensive_corpses

    try:
        corpses = Resource.objects.get(ruler=attacker, name="corpses")
        corpses.quantity += new_corpses
        corpses.save()
        battle.battle_report_notes.append(f"{attacker} gained {new_corpses} corpses.")
        battle.save()
    except:
        pass

    handle_invasion_perks(attacker, defender, defensive_casualties)

    return battle.id, "-- Congratulations, your invasion didn't crash! --"


def do_gsf_infiltration(units_sent_dict, attacker: Dominion, defender: Dominion):
    infiltration_power_sent = 0

    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]

        if "invasion_plan_power" in unit.perk_dict:
            infiltration_power_sent += unit.perk_dict["invasion_plan_power"] * quantity_sent
        else:
            return False, f"You can't send {unit.name} to infiltrate."
    
    if defender.strid not in attacker.perk_dict["infiltration_dict"] or infiltration_power_sent > attacker.perk_dict["infiltration_dict"][defender.strid]:
        attacker.perk_dict["infiltration_dict"][defender.strid] = infiltration_power_sent
        attacker.save()

        for unit_details_dict in units_sent_dict.values():
            unit.quantity_at_home -= quantity_sent
            unit.returning_dict["12"] += quantity_sent
            unit.save()

        return True, f"Successfully infiltrated {defender.name} for {infiltration_power_sent:2,} bonus OP."
    else:
        return False, "You already have a greater infiltration against that target."
        

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

    for other_dominion in Dominion.objects.filter(is_abandoned=False).order_by("-acres", "?"):
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
            raw_dp_at_home = dominion.raw_defense
            own_dp_multiplier = dominion.defense_multiplier

            for offensive_unit in offensive_units:
                this_unit_dict = {"unit": offensive_unit, "quantity_sent": 0}
                while (
                    raw_op_sent * op_multiplier <= other_dominion.defense and
                    this_unit_dict["quantity_sent"] < offensive_unit.quantity_at_home and
                    raw_dp_at_home * own_dp_multiplier >= dominion.acres * 5
                ):
                    this_unit_dict["quantity_sent"] += 1
                    raw_op_sent += offensive_unit.op
                    raw_dp_at_home -= offensive_unit.dp
                
                if this_unit_dict["quantity_sent"] > 0:
                    units_sent_dict[str(offensive_unit.id)] = this_unit_dict
            
            op_to_send, defense_left, _ = get_op_and_dp_left(units_sent_dict, attacker=dominion, defender=other_dominion)

            if op_to_send >= other_dominion.defense and defense_left >= dominion.acres * 5:
                do_invasion(units_sent_dict, attacker=dominion, defender=other_dominion)
                hasnt_attacked_yet = False