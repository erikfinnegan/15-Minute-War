from random import randint

from maingame.formatters import get_goblin_ruler
from maingame.models import Battle, Unit, Dominion, Event, Round, Resource, MechModule
from maingame.utils.utils import get_acres_conquered, get_grudge_bonus, get_random_resource, get_unit_from_dict
from maingame.utils.utils_sludgeling import create_random_sludgene, create_two_same_type_sludgenes


def handle_grudges_from_attack(attacker: Dominion, defender: Dominion=None):
    if "book_of_grudges" in defender.perk_dict:
        round = Round.objects.first()
        pages_to_gain = 50

        for _ in range(round.ticks_passed):
            pages_to_gain *= 1.002

        # This was mostly just a thing in the "everyone has grudges" era, as of 3/17/2025 it isn't currently used by anything
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


def generate_battle(units_sent_dict, attacker: Dominion, defender: Dominion, offense_sent, defense_snapshot, acres_conquered, is_plunder=False):
    battle_units_sent_dict = {}
    battle_units_defending_dict = {}
    
    for unit_id, data in units_sent_dict.items():
        battle_units_sent_dict[units_sent_dict[unit_id]["unit"].name] = data["quantity_sent"]

    for unit in Unit.objects.filter(ruler=defender):
        if unit.quantity_at_home > 0 and unit.dp > 0:
            battle_units_defending_dict[unit.name] = unit.quantity_at_home
    
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


def get_conditional_op(unit: Unit, attacker: Dominion, defender: Dominion):
    modified_unit_op = unit.op

    if "gets_op_bonus_equal_to_percent_of_target_complacency" in unit.perk_dict:
        op_multiplier = (defender.complacency_penalty_percent / 100) * (unit.perk_dict["gets_op_bonus_equal_to_percent_of_target_complacency"] / 100)
        modified_unit_op *= 1 + op_multiplier

    return modified_unit_op


def get_op_and_dp_left(units_sent_dict, attacker: Dominion, defender: Dominion=None, is_infiltration=False, is_plunder=False):
    offense_sent = 0
    infiltration_power_sent = 0
    infiltration_power_gained = 0
    raw_defense = attacker.raw_defense

    if defender and "infiltration_dict" in attacker.perk_dict and defender.strid in attacker.perk_dict["infiltration_dict"] and not is_infiltration:
        offense_sent += attacker.perk_dict["infiltration_dict"][defender.strid]
        
    if is_infiltration:
        try:
            current_infiltration_power = attacker.perk_dict["infiltration_dict"][defender.strid]
        except:
            current_infiltration_power = 0

    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        modified_unit_op = get_conditional_op(unit, attacker, defender)
        quantity_sent = unit_details_dict["quantity_sent"]

        if "rats_launched" in unit.perk_dict and "op_if_rats_launched" in unit.perk_dict:
            rats = Resource.objects.get(ruler=attacker, name="rats")
            max_launches = min(quantity_sent, int(rats.quantity / unit.perk_dict["rats_launched"]))
            offense_sent += max_launches * unit.perk_dict["op_if_rats_launched"]

        if is_infiltration:
            if "invasion_plan_power" in unit.perk_dict:
                infiltration_power_sent += unit.perk_dict["invasion_plan_power"] * quantity_sent
                
        else:
            offense_sent += modified_unit_op * quantity_sent

        raw_defense -= unit.dp * quantity_sent
        
    if is_infiltration:
        new_infiltration_power = max(0, infiltration_power_sent - current_infiltration_power)
        repeat_infiltration_power = infiltration_power_sent - new_infiltration_power
        infiltration_power_gained = new_infiltration_power + int(repeat_infiltration_power / 2)

    grudge_bonus = 0

    if "book_of_grudges" in attacker.perk_dict:
        grudge_bonus = get_grudge_bonus(attacker, defender)
        
    if attacker.faction_name == "mecha-dragon":
        try:
            vox_shrieker = MechModule.objects.get(ruler=attacker, name="Vox Shrieker", zone="mech")
            
            if vox_shrieker.battery_percent == 100:
                vox_shrieker_multiplier = 1 + (vox_shrieker.perk_dict["op_bonus_percent"] / 100)
                offense_sent *= vox_shrieker_multiplier
        except:
            pass

    if not is_infiltration:
        offense_sent *= (attacker.offense_multiplier + grudge_bonus)
        
    if is_plunder:
        offense_sent *= 2
        
    try:
        red_beret = Unit.objects.get(ruler=defender, name="Red Beret")
        if red_beret.perk_dict["subverted_target_id"] == attacker.strid:
            offense_sent -= defender.perk_dict["infiltration_dict"][attacker.strid]
    except:
        pass

    offense_sent = int(offense_sent)
    defense_left = int(raw_defense * attacker.defense_multiplier)

    if is_infiltration:
        return infiltration_power_gained, defense_left, raw_defense
    else:
        return offense_sent, defense_left, raw_defense


def does_x_of_unit_break_defender(quantity_theorized, unit: Unit, units_sent_dict, attacker: Dominion, defender: Dominion, is_plunder=False):
    faux_units_sent_dict = units_sent_dict.copy()
    strid = str(unit.id)

    faux_units_sent_dict[strid] = {
        "quantity_sent": quantity_theorized,
        "unit": unit
    }

    faux_op, _, _ = get_op_and_dp_left(faux_units_sent_dict, attacker, defender, is_plunder=is_plunder)
    
    return faux_op >= defender.defense


def handle_invasion_perks(attacker: Dominion, defender: Dominion, defensive_casualties, raw_defense_snapshot, is_plunder=False):
    handle_grudges_from_attack(attacker, defender)

    if attacker.faction_name == "sludgeling":
        try:
            if attacker.perk_dict["get_sludgenes"] == True:
                create_two_same_type_sludgenes(attacker)
                attacker.perk_dict["get_sludgenes"] = False
            else:
                attacker.perk_dict["get_sludgenes"] = True
        except:
            pass

    if "partner_patience" in attacker.perk_dict:
        attacker.perk_dict["partner_patience"] = int(24 * (defender.acres / attacker.acres))

    if "infiltration_dict" in attacker.perk_dict:
        if defender.strid in attacker.perk_dict["infiltration_dict"]:
            del attacker.perk_dict["infiltration_dict"][defender.strid]

    if defender.faction_name == "sludgeling" and not is_plunder:
        try:
            if defender.perk_dict["get_sludgenes"] == True:
                create_two_same_type_sludgenes(defender)
                defender.perk_dict["get_sludgenes"] = False
            else:
                defender.perk_dict["get_sludgenes"] = True
        except:
            pass

    if "goblin_ruler" in defender.perk_dict and not is_plunder:
        defender.perk_dict["goblin_ruler"] = get_goblin_ruler()
        current_favorite_name = defender.perk_dict["rulers_favorite_resource"]
        defender.perk_dict["rulers_favorite_resource"] = get_random_resource(
            defender, excluded_options=["gold", "corpses", "rats", current_favorite_name]
        ).name
        
    if attacker.faction_name == "aethertide corsairs":
        plunder = Resource.objects.get(ruler=attacker, name="plunder")
        plunder_gained = raw_defense_snapshot if is_plunder else int(raw_defense_snapshot / 4)
        plunder.gain(plunder_gained)
        
        try:
            press_gangers = Resource.objects.get(ruler=attacker, name="press gangers")
            press_gangers.gain(int(plunder_gained * 0.02))
        except:
            pass
        
    if defender.faction_name == "aethertide corsairs" and not is_plunder:
        attacker.perk_dict["time_curse"] = 12

    # if defender.faction_name == "blessed order":
    #     faith = Resource.objects.get(ruler=defender, name="faith")
    #     martyrs_affordable = int(faith.quantity / defender.perk_dict["martyr_cost"])
    #     martyrs_gained = min(martyrs_affordable, defensive_casualties)
    #     faith.spend(defender.perk_dict["martyr_cost"] * martyrs_gained)
    #     martyrs = Unit.objects.get(ruler=defender, name="Blessed Martyr")
    #     martyrs.gain(martyrs_gained)

    attacker.save()
    defender.save()


def handle_module_durability(mechadragon: Unit, is_attacker):
    try:
        magefield = MechModule.objects.get(ruler=mechadragon.ruler, name="AC# Magefield", zone="mech")
        damage_reduction_percent = magefield.perk_dict["durability_damage_percent_reduction"] if magefield.battery_current >= magefield.battery_max else 0
        perk_based_fragility_modifier = 1 - (damage_reduction_percent / 100)
    except:
        perk_based_fragility_modifier = 1

    for module in MechModule.objects.filter(ruler=mechadragon.ruler, zone="mech"):
        # The spirit bomb doesn't get protected by magefield
        modified_fragility = module.fragility if module.name == "Tiamat-class Spirit Bomb PL#001" else module.fragility * perk_based_fragility_modifier

        if not is_attacker:
            modified_fragility /= 2

        new_durability_multiplier = 1 - (modified_fragility / 100)

        module.durability_current = int(module.durability_current * new_durability_multiplier)
        
        if is_attacker and module.battery_current == module.battery_max:
            module.battery_current = 0
            
        if is_attacker and "op_growth_per_capacity_per_tick" in module.perk_dict:
            module.base_power = 0
        
        module.save()


def do_offensive_casualties_and_return(units_sent_dict, attacker: Dominion, defender: Dominion, defense_snapshot, is_plunder=False):
    offensive_casualties = 0
    new_corpses = 0
    
    try:
        comrade_carapace = MechModule.objects.get(ruler=attacker, name="THAC# Comrade Carapace", zone="mech")
        units_dont_die = comrade_carapace.battery_current >= comrade_carapace.battery_max
    except:
        units_dont_die = False

    do_instant_return = False

    if "percent_chance_of_instant_return" in attacker.perk_dict:
        percent_chance_of_instant_return = attacker.perk_dict["percent_chance_of_instant_return"]
        
        if percent_chance_of_instant_return >= randint(1, 100):
            do_instant_return = True

    for unit_details_dict in units_sent_dict.values():
        offensive_casualty_rate = 0 if is_plunder else 0.1
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]
        casualties = 0

        if units_dont_die and "always_dies_on_offense" not in unit.perk_dict:
            offensive_casualty_rate = 0
        elif "immortal" in unit.perk_dict:
            offensive_casualty_rate = 0
        elif "always_dies_on_offense" in unit.perk_dict:
            offensive_casualty_rate = 1
        elif "casualty_multiplier" in unit.perk_dict:
            offensive_casualty_rate *= unit.perk_dict["casualty_multiplier"]

        casualties = int(quantity_sent * offensive_casualty_rate)
        survivors = quantity_sent - casualties

        if "food" in unit.upkeep_dict:
            new_corpses += casualties

        return_ticks = str(unit.perk_dict["returns_in_ticks"]) if "returns_in_ticks" in unit.perk_dict else "12"
        
        if unit.name == "Mecha-Dragon":
            try:
                hyperwings = MechModule.objects.get(ruler=attacker, name='"# fast # furious" Hyperwings', zone="mech")
                return_ticks = 12 - hyperwings.version if hyperwings.battery_current >= hyperwings.battery_max else 12
            except:
                return_ticks = 12
            handle_module_durability(unit, is_attacker=True)

        if do_instant_return:
            unit.lose(casualties)
        else:
            unit.quantity_at_home -= quantity_sent
            unit.lost += casualties
            unit.returning_dict[return_ticks] = survivors

        unit.save()
        offensive_casualties += casualties
        
    # if defender.faction_name == "aether confederacy" and attacker.faction_name != "aether confederacy":
    #     attacker.void_return_cost += (defense_snapshot * 10)
    
    try:
        red_beret = Unit.objects.get(ruler=attacker, name="Red Beret")
        
        if red_beret.perk_dict["subverted_target_id"] == defender.strid:
            red_beret.perk_dict["subverted_target_id"] = 0
            red_beret.quantity_in_void -= 1
            red_beret.returning_dict["12"] = 1
            red_beret.save()
    except:
        pass
    
    attacker.save()

    return offensive_casualties, new_corpses


def do_defensive_casualties(defender: Dominion, is_plunder=False):
    defensive_casualties = 0
    new_corpses = 0

    for unit in Unit.objects.filter(ruler=defender, dp__gt=0, quantity_at_home__gt=0):
        defensive_casualty_rate = 0 if is_plunder else 0.05
        casualties = 0

        if "immortal" in unit.perk_dict:
            defensive_casualty_rate = 0
        elif "always_dies_on_defense" in unit.perk_dict and not is_plunder:
            defensive_casualty_rate = 1
        elif "casualty_multiplier" in unit.perk_dict:
            defensive_casualty_rate *= unit.perk_dict["casualty_multiplier"]

        casualties = int(unit.quantity_at_home * defensive_casualty_rate)

        if "faith_per_power_died" in defender.perk_dict:
            faith = Resource.objects.get(ruler=defender, name="faith")
            faith.gain(casualties * unit.dp * defender.perk_dict["faith_per_power_died"])

        if "food" in unit.upkeep_dict:
            new_corpses += casualties

        if unit.name == "Mecha-Dragon" and not is_plunder:
            handle_module_durability(unit, is_attacker=False)

        unit.lose(casualties)
        defensive_casualties += casualties
        
        if "hides_for_ticks_after_defense" in unit.perk_dict and not is_plunder:
            return_ticks = str(unit.perk_dict["hides_for_ticks_after_defense"])
            unit.returning_dict[return_ticks] = unit.quantity_at_home
            unit.quantity_at_home = 0
            unit.save()

    return defensive_casualties, new_corpses


def do_invasion(units_sent_dict, attacker: Dominion, defender: Dominion, is_plunder=False):
    raw_op_sent = 0
    defense_snapshot = defender.defense
    raw_defense_snapshot = defender.raw_defense
    slowest_unit_return_ticks = 1
    offense_sent, dp_left, _ = get_op_and_dp_left(units_sent_dict, attacker, defender=defender, is_plunder=is_plunder)
    acres_conquered = get_acres_conquered(attacker, defender, is_plunder)

    if defender.defense > offense_sent:
        return 0, "No failed invasions allowed"
    if dp_left < attacker.acres * 5:
        return 0, "Insufficient defense left by attacker"
    
    # Get slowest return time for land return time, raw OP sent for updating max
    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]
        raw_op_sent += unit.op * quantity_sent

        if "returns_in_ticks" in unit.perk_dict:
            slowest_unit_return_ticks = max(slowest_unit_return_ticks, unit.perk_dict["returns_in_ticks"])
        elif unit.name == "Mecha-Dragon":
            try:
                return_ticks = 12 - MechModule.objects.get(ruler=attacker, name='"# fast # furious" Hyperwings', zone="mech").version
            except:
                return_ticks = 12
            
            slowest_unit_return_ticks = max(slowest_unit_return_ticks, return_ticks)
        else:
            slowest_unit_return_ticks = max(slowest_unit_return_ticks, 12)

        if "rats_launched" in unit.perk_dict and "op_if_rats_launched" in unit.perk_dict:
            rats = Resource.objects.get(ruler=attacker, name="rats")
            max_launches = min(quantity_sent, int(rats.quantity / unit.perk_dict["rats_launched"]))
            rats.spend(max_launches * unit.perk_dict["rats_launched"])

    if "percent_complacency_to_determination_when_hit" in defender.perk_dict and not is_plunder:
        defender.determination += defender.complacency * (defender.perk_dict["percent_complacency_to_determination_when_hit"] / 100)
        defender.save()

    if not is_plunder:
        defender.complacency = 0
        defender.failed_defenses += 1
        
    defender.lose_acres(acres_conquered)
    defender.save()

    attacker.highest_raw_op_sent = max(raw_op_sent, attacker.highest_raw_op_sent)
    
    if not is_plunder:
        attacker.successful_invasions += 1
    
    try:
        adrenaline_pump = MechModule.objects.get(ruler=attacker, name="PP# Pseudrenaline Pump", zone="mech")
        attacker.determination = int(attacker.determination * adrenaline_pump.version_based_determination_multiplier) if adrenaline_pump.battery_current >= adrenaline_pump.battery_max else 0
    except:
        if not is_plunder:
            attacker.determination = 0
    
    ticks_for_land = str(slowest_unit_return_ticks)
    attacker.incoming_acres_dict[ticks_for_land] += acres_conquered * 2
    
    attacker.save()

    battle = generate_battle(units_sent_dict, attacker, defender, offense_sent, defense_snapshot, acres_conquered, is_plunder=is_plunder)

    # if is_plunder:
    #     offensive_corpses = 0
    #     defensive_corpses = 0
    #     defensive_casualties = 0
    # else:
    #     _, offensive_corpses = do_offensive_casualties_and_return(units_sent_dict, attacker, defender, defense_snapshot, is_plunder=is_plunder)
    #     defensive_casualties, defensive_corpses = do_defensive_casualties(defender, is_plunder=is_plunder)
    
    _, offensive_corpses = do_offensive_casualties_and_return(units_sent_dict, attacker, defender, defense_snapshot, is_plunder=is_plunder)
    defensive_casualties, defensive_corpses = do_defensive_casualties(defender, is_plunder=is_plunder)

    new_corpses = offensive_corpses + defensive_corpses

    try:
        corpses = Resource.objects.get(ruler=attacker, name="corpses")
        corpses.gain(new_corpses)
        battle.battle_report_notes.append(f"{attacker} gained {new_corpses} corpses.")
        battle.save()
    except:
        pass

    handle_invasion_perks(attacker, defender, defensive_casualties, raw_defense_snapshot, is_plunder=is_plunder)

    return battle.id, "-- Congratulations, your invasion didn't crash! --"


def do_gsf_infiltration(infiltration_power_gained, units_sent_dict, attacker: Dominion, defender: Dominion):
    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]

        if "invasion_plan_power" not in unit.perk_dict:
            return False, f"You can't send {unit.name} to infiltrate."
        
    try:
        current_infiltration_power = attacker.perk_dict["infiltration_dict"][defender.strid]
    except:
        current_infiltration_power = 0
        
    updated_infiltration_power = current_infiltration_power + infiltration_power_gained
    
    attacker.perk_dict["infiltration_dict"][defender.strid] = updated_infiltration_power
    attacker.save()
    
    for unit_details_dict in units_sent_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_sent = unit_details_dict["quantity_sent"]
        
        unit.quantity_at_home -= quantity_sent
        
        if "subverted_target_id" in unit.perk_dict:
            unit.quantity_in_void += 1
            unit.perk_dict["subverted_target_id"] = defender.strid
        else:
            unit.returning_dict["12"] += quantity_sent
        
        unit.save()
    
    return True, f"Successfully infiltrated {defender.name} for {infiltration_power_gained:2,} bonus OP."
    
    # if defender.strid not in attacker.perk_dict["infiltration_dict"] or infiltration_power_sent > attacker.perk_dict["infiltration_dict"][defender.strid]:
    #     attacker.perk_dict["infiltration_dict"][defender.strid] = infiltration_power_sent
    #     attacker.save()

    #     for unit_details_dict in units_sent_dict.values():
    #         unit.quantity_at_home -= quantity_sent
    #         unit.returning_dict["12"] += quantity_sent
    #         unit.save()

    #     return True, f"Successfully infiltrated {defender.name} for {infiltration_power_sent:2,} bonus OP."
    # else:
    #     return False, "You already have a greater infiltration against that target."
        

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
                    raw_op_sent += get_conditional_op(offensive_unit, dominion, other_dominion)
                    raw_dp_at_home -= offensive_unit.dp
                
                if this_unit_dict["quantity_sent"] > 0:
                    units_sent_dict[str(offensive_unit.id)] = this_unit_dict
            
            op_to_send, defense_left, _ = get_op_and_dp_left(units_sent_dict, attacker=dominion, defender=other_dominion)

            if op_to_send >= other_dominion.defense and defense_left >= dominion.acres * 5:
                do_invasion(units_sent_dict, attacker=dominion, defender=other_dominion)
                hasnt_attacked_yet = False
                

# def update_units_sent_dict_for_wreckin_ballers(units_sent_dict, total_units_sent):
#     for unit_details_dict in units_sent_dict.values():
#         unit = get_unit_from_dict(unit_details_dict)
#         quantity_sent = unit_details_dict["quantity_sent"]

#         # Right now it assumes a value of 0.5. Please don't make me figure out how to handle something greater than 1.
#         if "random_allies_killed_on_invasion" in unit.perk_dict:
#             # When in doubt, they kill themselves, just to help avoid exceptions
#             victim = unit_details_dict
#             victim_count = 0

#             for _ in range(int(quantity_sent / 2)):
#                 roll = randint(1, total_units_sent - victim_count)

#                 for victim_details_dict in units_sent_dict.values():
#                     if roll <= victim_details_dict["quantity_sent"]:
#                         victim = victim_details_dict
#                         break
#                     else:
#                         roll -= victim_details_dict["quantity_sent"]

#                 victim_count += 1
#                 victim["quantity_sent"] -= 1

#     return units_sent_dict