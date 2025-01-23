from random import randint, choice
import random

from maingame.formatters import get_goblin_ruler
from maingame.models import Artifact, Unit, Dominion, Discovery, Building, Event, Round, Faction, Resource, Spell, UserSettings
from django.contrib.auth.models import User

from maingame.utils.give_stuff import create_resource_for_dominion, give_dominion_building, give_dominion_spell, give_dominion_unit


def get_random_resource(dominion: Dominion):
    resources = []

    for resource in Resource.objects.filter(ruler=dominion):
        if resource.name not in ["gold", "corpses", "rats"]:
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
            dominion.perk_dict["sinners_per_hundred_acres_per_tick"] *= 2
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


def round_x_to_nearest_y(x, round_to_nearest):
    return round_to_nearest * round(x/round_to_nearest)


def get_acres_conquered(attacker: Dominion, target: Dominion):
    return int(0.06 * target.acres * (target.acres / attacker.acres))


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

    my_dominion.incoming_acres_dict["12"] += 1
    my_dominion.save()

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