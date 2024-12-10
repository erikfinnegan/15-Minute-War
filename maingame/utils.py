from random import randint, choice
import random

from maingame.models import Unit, Dominion, Discovery, Building, Event, Round, Faction, Resource, Spell, UserSettings
from django.contrib.auth.models import User
from django.db.models import Q


def create_faction_perk_dict(dominion: Dominion, faction: Faction):
    if faction.name == "dwarf":
        dominion.perk_dict["grudge_page_multiplier"] = 1.5
        dominion.perk_dict["grudge_page_keep_multiplier"] = 0.05
    elif faction.name == "blessed order":
        dominion.perk_dict["sinners_per_hundred_acres_per_tick"] = 1
        dominion.perk_dict["inquisition_rate"] = 0
        dominion.perk_dict["inquisition_ticks_left"] = 0
        dominion.perk_dict["martyr_cost"] = 1000
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

    for spell in Spell.objects.filter(ruler=None, is_starter=True):
        dominions_spell = spell
        dominions_spell.pk = None
        dominions_spell.ruler = dominion
        dominions_spell.save()

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

    dominion.perk_dict["book_of_grudges"] = {}
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
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Fireball"))
        case "Grudgestoker":
            grudgestoker = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Grudgestoker"))
            grudgestoker.quantity_at_home = 1
            grudgestoker.save()
            dominion.has_tick_units = True
        case "Miners":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Miner"))
            dominion.perk_dict["mining_depth"] = 0
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

    if not can_take_multiple_times:
        dominion.available_discoveries.remove(discovery_name)

    message = update_available_discoveries(dominion)
    dominion.save()

    return message


def give_dominion_unit(dominion: Dominion, unit: Unit):
    dominions_unit = unit
    dominions_unit.pk = None
    dominions_unit.ruler = dominion
    dominions_unit.save()

    for resource in unit.cost_dict:
        create_resource_for_dominion(resource, dominion)

    return dominions_unit


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


def cast_spell(spell: Spell):
    dominion = spell.ruler
    mana = Resource.objects.get(ruler=dominion, name="mana")

    if mana.quantity < spell.mana_cost:
        return
    
    mana.quantity -= spell.mana_cost
    mana.save()

    match spell.name:
        case "Power Overwhelming":
            for unit in Unit.objects.filter(ruler=dominion):
                if unit.is_trainable and unit.op > unit.dp and "always_dies_on_offense" not in unit.perk_dict:
                    try:
                        overwhelming_unit = Unit.objects.get(ruler=dominion, name=f"Overwhelming {unit.name}")
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