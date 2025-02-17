from random import choice
import random

from maingame.models import Unit, Dominion, Discovery, Building, Resource, Spell, MechModule

from maingame.utils.give_stuff import create_resource_for_dominion, give_dominion_building, give_dominion_module, give_dominion_spell, give_dominion_unit


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
    

def create_magnum_goopus(dominion: Dominion, units_included_dict, encore=False):
    total_quantity = 0
    total_op = 0
    total_dp = 0
    food_upkeep = 0

    if encore:
        perk_dict = {"is_more_glorious": True}
    else:
        perk_dict = {"is_glorious": True}

    for unit_details_dict in units_included_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_included = unit_details_dict["quantity_sent"]

        if "sludge" in unit.cost_dict and quantity_included <= unit.quantity_at_home:
            total_quantity += quantity_included
            total_op += quantity_included * unit.op
            total_dp += quantity_included * unit.dp

            if "food" in unit.upkeep_dict:
                food_upkeep += quantity_included * unit.upkeep_dict["food"]

            for perk, value in unit.perk_dict.items():
                if perk == "casualty_multiplier" and perk in perk_dict:
                    perk_dict[perk] = min(value, perk_dict[perk])
                else:
                    perk_dict[perk] = value
            
            unit.lose(quantity_included)

    encore_suffixes = [" Mk II", " 2: Electric Goopaloo", " Remastered", ": the Remix", " 2", " Jr.", " Magnum Goopier"]

    if encore:
        name = f"Magnum Goopus {random.choice(encore_suffixes)}"
    else:
        name = "Magnum Goopus"

    dominion.perk_dict["masterpieces_to_create"] -= 1
    dominion.save()

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

    return Unit.objects.create(
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


def update_capacity(dominion: Dominion):
    used_capacity = 0
    mechadragon = Unit.objects.get(ruler=dominion, name="Mecha-Dragon")
    module_power = 0

    for module in MechModule.objects.filter(ruler=dominion, zone="mech"):
        used_capacity += module.capacity
        module_power += module.power
    
    mechadragon.op = module_power
    mechadragon.dp = module_power
    mechadragon.save()

    dominion.perk_dict["capacity_used"] = used_capacity
    dominion.save()


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
            dominion.perk_dict["max_custom_units"] = 4
        case "Even More Experiment Slots":
            dominion.perk_dict["max_custom_units"] = 6
        case "Recycling Center":
            dominion.perk_dict["recycling_refund"] = 0.95
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
                dominion.perk_dict["bonus_determination"] += 0.1
        case "Juggernaut Tanks":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Juggernaut Tank"))
        case "Inferno Mines":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Inferno Mine"))
        case "Rapid Deployment":
            dominion.perk_dict["unit_training_time"] = "6"
        case "Back-2-U Town Portal System":
            give_dominion_module(dominion, MechModule.objects.get(ruler=None, name="Back-#-U Town Portal System"))

    if not discovery.repeatable:
        dominion.available_discoveries.remove(discovery_name)

    message = update_available_discoveries(dominion)
    dominion.save()

    return message


def round_x_to_nearest_y(x, round_to_nearest):
    return round_to_nearest * round(x/round_to_nearest)


def get_acres_conquered(attacker: Dominion, target: Dominion):
    base = 0.06 * target.acres
    land_ratio = target.acres / attacker.acres
    multiplier = land_ratio
    
    if land_ratio > 1:
        bonus_percent = land_ratio - 1
        multiplier = 1 + (0.8 * bonus_percent)

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

            if amount <= unit.quantity_at_home and amount > 0:
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
                        overwhelming_unit.gain(overwhelming_quantity)
                        unit.lose(overwhelming_quantity)

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