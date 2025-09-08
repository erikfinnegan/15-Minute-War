from random import choice
import random

from maingame.formatters import generate_countdown_dict, get_casualty_mod_cost_multiplier, get_fast_return_cost_multiplier, get_low_turtle_cost_multiplier
from maingame.models import Event, Unit, Dominion, Discovery, Building, Resource, Spell, MechModule

from maingame.utils.give_stuff import create_resource_for_dominion, give_dominion_building, give_dominion_module, give_dominion_spell, give_dominion_unit


def get_primary_type_base_costs(power, secondary_resource_name, is_offense):
    building = Building.objects.filter(ruler=None, resource_produced_name=secondary_resource_name).first()
    btick_amount = building.amount_produced + 10
    
    if power == 1:
        primary_cost = 75
    elif power == 2:
        primary_cost = 175
    else:
        primary_cost = (power * 300) - 600
    
    secondary_cost = power * 1.5 * btick_amount
    
    if is_offense:
        return primary_cost * 1.3, secondary_cost * 1.3
    else:
        return primary_cost, secondary_cost


def get_secondary_type_base_costs(power, secondary_resource_name, is_offense):
    building = Building.objects.filter(ruler=None, resource_produced_name=secondary_resource_name).first()
    btick_amount = building.amount_produced + 10
    
    if power == 1:
        secondary_cost = 0.75 * btick_amount
    else:
        secondary_cost = ((power * 6) - 10) * btick_amount
        
    if is_offense:
        return 0, secondary_cost * 1.3
    else:
        return 0, secondary_cost


def generate_unit_cost_dict(op, dp, primary_resource_name, secondary_resource_name, type, casualty_multiplier=1, return_ticks=12, cost_multiplier=1):
    if type not in ["primary", "secondary", "hybrid"]:
        return {"error": 1}
    
    primary_op_primary_cost, primary_op_secondary_cost = get_primary_type_base_costs(op, secondary_resource_name, True)
    primary_dp_primary_cost, primary_dp_secondary_cost = get_primary_type_base_costs(dp, secondary_resource_name, False)
    
    secondary_op_primary_cost, secondary_op_secondary_cost = get_secondary_type_base_costs(op, secondary_resource_name, True)
    secondary_dp_primary_cost, secondary_dp_secondary_cost = get_secondary_type_base_costs(dp, secondary_resource_name, False)
        
    hybrid_op_primary_cost = (primary_op_primary_cost + secondary_op_primary_cost) / 2
    hybrid_op_secondary_cost = (primary_op_secondary_cost + secondary_op_secondary_cost) / 2
    
    hybrid_dp_primary_cost = (primary_dp_primary_cost + secondary_dp_primary_cost) / 2
    hybrid_dp_secondary_cost = (primary_dp_secondary_cost + secondary_dp_secondary_cost) / 2
    
    if type == "primary":
        primary_cost = max(primary_op_primary_cost, primary_dp_primary_cost)
        secondary_cost = max(primary_op_secondary_cost, primary_dp_secondary_cost)
    elif type == "secondary":
        primary_cost = max(secondary_op_primary_cost, secondary_dp_primary_cost)
        secondary_cost = max(secondary_op_secondary_cost, secondary_dp_secondary_cost)
    else:
        primary_cost = max(hybrid_op_primary_cost, hybrid_dp_primary_cost)
        secondary_cost = max(hybrid_op_secondary_cost, hybrid_dp_secondary_cost)
    
    cost_multiplier *= get_low_turtle_cost_multiplier(op, dp)
    cost_multiplier *= get_casualty_mod_cost_multiplier(casualty_multiplier)
    cost_multiplier *= get_fast_return_cost_multiplier(return_ticks, op, dp)
    
    primary_cost = primary_cost * cost_multiplier
    secondary_cost = secondary_cost * cost_multiplier
    
    if primary_cost > 1000:
        primary_cost = round_x_to_nearest_y(primary_cost, 50)
    elif primary_cost > 500:
        primary_cost = round_x_to_nearest_y(primary_cost, 25)
    else:
        primary_cost = round_x_to_nearest_y(primary_cost, 5)
        
    if secondary_cost > 1000:
        secondary_cost = round_x_to_nearest_y(secondary_cost, 50)
    elif secondary_cost > 500:
        secondary_cost = round_x_to_nearest_y(secondary_cost, 25)
    else:
        secondary_cost = round_x_to_nearest_y(secondary_cost, 5)
        
    cost_dict = {}
    
    if primary_cost > 0:
        cost_dict[primary_resource_name] = primary_cost
        
    if secondary_cost > 0:
        cost_dict[secondary_resource_name] = secondary_cost

    return cost_dict


def get_unit_from_dict(unit_details_dict) -> Unit:
    return unit_details_dict["unit"]


def get_random_resource(dominion: Dominion, excluded_options=["gold", "corpses", "rats"]):
    resources = []

    for resource in Resource.objects.filter(ruler=dominion):
        if resource.name not in excluded_options:
            resources.append(resource)

    return choice(resources)


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


def get_grudge_bonus(my_dominion: Dominion, other_dominion: Dominion):
    try:
        # Offense gets calculated as 1 + this
        # 0.003 gets added to animosity per page, which makes sense as it's +0.003% per page
        # X animosity is +X% OP, so we need to turn 0.003 into 0.00003 because that's how percents work
        return my_dominion.perk_dict["book_of_grudges"][str(other_dominion.id)]["animosity"] / 100
    except:
        return 0
    

def unlock_discovery(dominion: Dominion, discovery_name):
    if not discovery_name in dominion.available_discoveries:
        return False
    
    discovery = Discovery.objects.get(name=discovery_name)
    dominion.learned_discoveries.append(discovery_name)

    match discovery_name:
        case "Prosperity":
            dominion.primary_resource_per_acre += 1
            dominion.save()
        case "Battering Rams":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Battering Ram"))
        case "Palisades":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Palisade"))
        case "Bastions":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Bastion"))
        case "Zombies":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Zombie"))
        case "Archmage":
            archmage = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Archmage"))
            archmage.gain(1)
            dominion.has_tick_units = True
        case "Fireballs":
            fireballs = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Fireball"))
            fireballs.is_trainable = True
            fireballs.save()
        case "Gingerbrute Men":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Gingerbrute Man"))
        case "Mercenaries":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Mercenary"))
        case "Hill Giants":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Hill Giant"))            
        case "Grudgestoker":
            grudgestoker = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Grudgestoker"))
            grudgestoker.gain(1)
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
        case "Hatetheism":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Hatetheist"))
            dominion.perk_dict["hatetheists_gained"] = 4
        case "Hatetheism Spreads":
            dominion.perk_dict["hatetheists_gained"] = 7
        case "Hatetheism Rising":
            dominion.perk_dict["hatetheists_gained"] = 10
        case "Hateriarchy":
            hateriarch = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Hateriarch"))
            hateriarch.gain(1)
        # case "Gem Mines":
        #     give_dominion_building(dominion, Building.objects.get(ruler=None, name="mine"))
        case "Living Saints":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Living Saint"))
        case "Penitent Engines":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Penitent Engine"))
        case "Zealous Persecution":
            dominion.perk_dict["heretics_per_hundred_acres_per_tick"] *= 2

            if "The Final Heresy" in dominion.available_discoveries:
                dominion.available_discoveries.remove("The Final Heresy")
        case "Grim Sacrament":
            dominion.perk_dict["inquisition_makes_corpses"] = True
            create_resource_for_dominion("corpses", dominion)
        # case "Wights":
        #     give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Wight"))
        case "Cathedral Titans":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Cathedral Titan"))
        case "Funerals":
            dominion.perk_dict["faith_per_power_died"] = 10
        case "Cremain Knights":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Cremain Knight"))
        case "The Final Heresy":
            dominion.perk_dict["fallen_order"] = True
            dominion.faction_name = "fallen order"

            if "Zealous Persecution" in dominion.available_discoveries:
                dominion.available_discoveries.remove("Zealous Persecution")

            if "Funerals" in dominion.available_discoveries:
                dominion.available_discoveries.remove("Funerals")

            if "Penitent Engines" in dominion.available_discoveries:
                dominion.available_discoveries.remove("Penitent Engines")

            if "Cathedral Titans" in dominion.available_discoveries:
                dominion.available_discoveries.remove("Cathedral Titans")

            if "Living Saints" in dominion.available_discoveries:
                dominion.available_discoveries.remove("Living Saints")

            dominion.save()
        case "More Experiment Slots":
            dominion.perk_dict["max_custom_units"] += 1
        case "Even More Experiment Slots":
            dominion.perk_dict["max_custom_units"] += 2
        case "Sludgehoarder":
            dominion.perk_dict["max_custom_units"] += 3
            dominion.perk_dict["max_custom_units"] = min(25, dominion.perk_dict["max_custom_units"])
        case "Recycling Center":
            dominion.perk_dict["recycling_refund"] = 0.97
        case "Magnum Goopus":
            # create_magnum_goopus(dominion)
            dominion.perk_dict["masterpieces_to_create"] += 1
        case "Encore":
            # create_magnum_goopus(dominion, encore=True)
            dominion.perk_dict["masterpieces_to_create"] += 1
        case "Wreckin Ballers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Wreckin Baller"))
        case "Charcutiers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Charcutier"))
        case "Rat Trainers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Rat Trainer"))
        case "Ratapults":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Ratapult"))
        case "Bestow Biclopean Ambition":
            give_dominion_spell(dominion, Spell.objects.get(ruler=None, name="Bestow Biclopean Ambition"))
        case "Triclops":
            dominion.perk_dict["percent_chance_of_instant_return"] = 10
        case "Gatesmashers":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Gatesmasher"))
        case "Growing Determination":
            if "bonus_determination" in dominion.perk_dict:
                dominion.perk_dict["bonus_determination"] += 0.15
        case "Spurred to Action":
            dominion.perk_dict["percent_complacency_to_determination_when_hit"] += 20
            dominion.invasion_consequences = f"This dominion will add {dominion.perk_dict['percent_complacency_to_determination_when_hit']}% of their complacency penalty to their determination bonus."
        case "Pay It Forward":
            dominion.perk_dict["percent_complacency_to_determination_when_hit"] += 30
            dominion.invasion_consequences = f"This dominion will add {dominion.perk_dict['percent_complacency_to_determination_when_hit']}% of their complacency penalty to their determination bonus."
        case "Juggernaut Tanks":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Juggernaut Tank"))
        case "Inferno Mines":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Inferno Mine"))
        case "Rapid Deployment":
            dominion.perk_dict["unit_training_time"] = "6"
        case "Red Beret":
            red_beret = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Red Beret"))
            red_beret.gain(1)
        case "Back-2-U Town Portal System":
            give_dominion_module(dominion, MechModule.objects.get(ruler=None, name="Back-#-U Town Portal System"))
        case "PP0 Pseudrenaline Pump":
            give_dominion_module(dominion, MechModule.objects.get(ruler=None, name="PP# Pseudrenaline Pump"))
        case "THAC0 Comrade Carapace":
            give_dominion_module(dominion, MechModule.objects.get(ruler=None, name="THAC# Comrade Carapace"))
        case "Tiamat-class Spirit Bomb PL9001":
            give_dominion_module(dominion, MechModule.objects.get(ruler=None, name="Tiamat-class Spirit Bomb PL#001"))
        case "Vox Shrieker":
            give_dominion_module(dominion, MechModule.objects.get(ruler=None, name="Vox Shrieker"))
        case "Gilded Veterans":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Gilded Veterans"))
        case "Impressment":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Realitylubber Crew"))
        case "Laeviathans":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Laeviathan"))
        case "Chronokrakens":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Chronokraken"))

    if not discovery.repeatable:
        dominion.available_discoveries.remove(discovery_name)

    message = update_available_discoveries(dominion)
    dominion.save()

    return message


def round_x_to_nearest_y(x, round_to_nearest):
    return round_to_nearest * round(x/round_to_nearest)


def get_acres_conquered(attacker: Dominion, target: Dominion, is_plunder=False):
    if is_plunder:
        return 1
    
    base = 0.06 * target.acres
    land_ratio = target.acres / max(1, attacker.acres)
    multiplier = land_ratio
    
    if land_ratio > 1:
        bonus_percent = land_ratio - 1
        multiplier = 1 + (0.8 * bonus_percent)
        
    multiplier = min(multiplier, 3)

    return int(base * multiplier)


def create_unit_dict(request_data, id_prefix):
    unit_dict = {}
    total_units = 0
    # id_prefix is like "send_"
    for key, string_amount in request_data.items():
        # key is like "send_123" where 123 is the ID of the Unit
        if id_prefix in key and string_amount != "":
            unit = Unit.objects.get(id=key[len(id_prefix):])
            amount = int(string_amount)

            # if amount <= unit.quantity_at_home and amount > 0:
            if amount > 0:
                total_units += amount
                unit_dict[str(unit.id)] = {
                    "unit": unit,
                    "quantity_sent": amount,
                }

    return unit_dict, total_units


def cast_spell(spell: Spell, target=None):
    dominion = spell.ruler
    mana = Resource.objects.get(ruler=dominion, name="mana")

    if mana.quantity < spell.mana_cost:
        return
    elif spell.cooldown_remaining > 0:
        return
    
    mana.spend(spell.mana_cost)

    spell.cooldown_remaining = spell.cooldown
    spell.save()

    match spell.name:
        case "Bestow Biclopean Ambition":
            duration = 11
            
            if target:
                target.perk_dict["biclopean_ambition_ticks_remaining"] = duration
                target.save()
                event = Event.objects.create(
                    reference_id=target.id, 
                    reference_type="spell", 
                    category="spell",
                    message_override=f"{dominion} bestowed biclopean ambition on {target} for {duration} ticks."
                )
                event.notified_dominions.add(target)
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
                        overwhelming_unit.gain(overwhelming_quantity)
                        unit.lose(overwhelming_quantity)

                        timer_template = generate_countdown_dict()

                        overwhelming_unit.training_dict = timer_template
                        overwhelming_unit.returning_dict = timer_template
                        overwhelming_unit.save()