import math
from random import randint
import random

from maingame.formatters import get_goblin_ruler
from maingame.models import Artifact, Battle, Unit, Dominion, Event, Round, Resource
from maingame.utils.artifacts import assign_artifact
from maingame.utils.utils import get_acres_conquered, get_grudge_bonus, get_random_resource


def get_unit_from_dict(unit_details_dict) -> Unit:
    return unit_details_dict["unit"]


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
        quantity_sent = unit_details_dict["quantity_sent"]

        if is_infiltration:
            if "invasion_plan_power" in unit.perk_dict:
                offense_sent += unit.perk_dict["invasion_plan_power"] * quantity_sent
            else:
                offense_sent -= 9999 * quantity_sent
        else:
            offense_sent += unit.op * quantity_sent

        raw_defense -= unit.dp * quantity_sent

    grudge_bonus = 0

    if "book_of_grudges" in attacker.perk_dict:
        grudge_bonus = get_grudge_bonus(attacker, defender)

    if not is_infiltration:
        offense_sent *= (attacker.offense_multiplier + grudge_bonus)

    offense_sent = int(offense_sent)

    defense_left = int(raw_defense * attacker.defense_multiplier)

    return offense_sent, defense_left


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
            unit.returning_dict[return_ticks] = survivors

        unit.save()
        offensive_casualties += casualties

    return offensive_casualties, new_corpses


def do_defensive_casualties(defender: Dominion):
    defensive_casualties = 0
    new_corpses = 0

    for unit in Unit.objects.filter(ruler=defender, op__gt=0, quantity_at_home__gt=0):
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
    offense_sent, dp_left = get_op_and_dp_left(units_sent_dict, attacker, defender=defender)
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
        

def do_invasion_old(units_sent_dict, my_dominion: Dominion, target_dominion: Dominion):
    print()
    print()
    print(units_sent_dict)
    print()
    print()
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

    if "infiltration_dict" in my_dominion.perk_dict and target_dominion.strid in my_dominion.perk_dict["infiltration_dict"]:
        offense_sent += my_dominion.perk_dict["infiltration_dict"][target_dominion.strid]

    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]
        offense_sent += unit.op * quantity_sent

        if "op_bonus_percent_for_stealing_artifacts" in unit.perk_dict:
            bonus_steal_offense_sent += (unit.perk_dict["op_bonus_percent_for_stealing_artifacts"] / 100) * unit.op * quantity_sent

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
            unit = get_unit_from_dict(unit_dict)
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

        # Defender might gain grudges
        if "book_of_grudges" in target_dominion.perk_dict:
            pages_to_gain = 50

            for _ in range(round.ticks_passed):
                pages_to_gain *= 1.002

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
    # defender_artifact_count = Artifact.objects.filter(ruler=target_dominion).count()

    # artifact_roll_string = "Defender has no artifacts to roll for."

    # if attacker_victory and defender_artifact_count > 0:
        # amount_over = steal_offense_sent - defense_snapshot
        # amount_over_percent = math.ceil((amount_over / defense_snapshot) * 100)

        # # 67% over is 100% to steal
        # # Make sure this matches world_js.html
        # percent_chance = amount_over_percent * 1.5

        # artifact_roll_string = f"{percent_chance}% to steal artifact, need to roll equal or under {percent_chance} on d100 at least once. Rolls:"

        # do_steal_artifact = False

        # for _ in range(defender_artifact_count):
        #     roll = randint(1, 100)
        #     artifact_roll_string += f"  {roll}"
        #     if percent_chance >= roll:
        #         do_steal_artifact = True

        # if do_steal_artifact:
        #     defenders_artifacts = []

        #     for artifact in Artifact.objects.filter(ruler=target_dominion):
        #         defenders_artifacts.append(artifact)

        #     stolen_artifact = random.choice(defenders_artifacts)
        #     assign_artifact(stolen_artifact, my_dominion)

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
        # artifact_roll_string=artifact_roll_string,
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

    # if stolen_artifact:
    #     artifact_event = Event.objects.create(
    #         reference_id=stolen_artifact.id, 
    #         reference_type="artifact", 
    #         category="Artifact Stolen",
    #         message_override=f"{my_dominion} stole {stolen_artifact.name} from {target_dominion}"
    #     )
    #     artifact_event.notified_dominions.add(my_dominion)
    #     artifact_event.notified_dominions.add(target_dominion)
    #     artifact_event.save()

    # Handle biclops patience
    if "partner_patience" in my_dominion.perk_dict:
        my_dominion.perk_dict["partner_patience"] = int(24 * my_dominion.acres / (target_dominion.acres))
        my_dominion.save()

    # Handle goblin Wreckin Ballers
    if "Wreckin Ballers" in my_dominion.learned_discoveries:
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

        # if Artifact.objects.filter(name="The Stable of the North Wind", ruler=my_dominion).exists():
        #     ticks_for_land = str(min(10, slowest_unit_return_ticks))
        
        my_dominion.incoming_acres_dict[ticks_for_land] += acres_conquered * 2

        my_dominion.save()
        
        battle.acres_conquered = acres_conquered
        battle.save()

        # Attackers erase their grudges for a dominion once they hit them amd halve the others
        if "book_of_grudges" in my_dominion.perk_dict and str(target_dominion.id) in my_dominion.perk_dict["book_of_grudges"]:
            if "grudge_page_keep_multiplier" in my_dominion.perk_dict:
                pages = my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["pages"]
                multiplier = my_dominion.perk_dict["grudge_page_keep_multiplier"]
                my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["pages"] = max(1, int(pages * multiplier))
                my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]["animosity"] *= 0
            else:
                del my_dominion.perk_dict["book_of_grudges"][str(target_dominion.id)]

            for grudge_dict in my_dominion.perk_dict["book_of_grudges"].values():
                grudge_dict["animosity"] /= 2

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
        # unit = get_unit_from_dict(unit_details_dict)
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
        
        # if Artifact.objects.filter(name="The Stable of the North Wind", ruler=my_dominion).exists():
        #     possible_return_ticks.append(10)
        
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

    # Handle clearing infiltration
    if attacker_victory and "infiltration_dict" in my_dominion.perk_dict:
        if target_dominion.strid in my_dominion.perk_dict["infiltration_dict"]:
            del my_dominion.perk_dict["infiltration_dict"][target_dominion.strid]
            my_dominion.save()

    return battle.id, "-- Congratulations, your invasion didn't crash! --"


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
                    
            do_invasion(units_sent_dict, my_dominion=dominion, target_dominion=other_dominion)
            hasnt_attacked_yet = False