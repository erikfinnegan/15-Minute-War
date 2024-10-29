from random import randint, choice

from maingame.formatters import create_or_add_to_key
from maingame.models import Unit, Dominion, Discovery, Building, Deity, Event, Round, Faction, Resource, Spell
from django.contrib.auth.models import User
from django.db.models import Q


def create_faction_perk_dict(dominion: Dominion, faction: Faction):
    if faction.name == "dwarf":
        dominion.perk_dict["book_of_grudges"] = {}

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


def initialize_dominion(user: User, faction: Faction, display_name):
    starter_discovery_names = []

    for discovery in Discovery.objects.filter(requirement=None):
        starter_discovery_names.append(discovery.name)

    for discovery in Discovery.objects.filter(requirement=faction.name):
        starter_discovery_names.append(discovery.name)

    dominion = Dominion.objects.create(
        associated_user=user, 
        name=display_name, 
        faction_name=faction.name, 
        available_discoveries=starter_discovery_names
    )

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
    primary_building_resource.quantity = dominion.acres * dominion.building_primary_cost
    primary_building_resource.save()
    dominion.last_bought_resource_name = primary_building_resource.name
    dominion.last_sold_resource_name = primary_building_resource.name

    secondary_building_resource = Resource.objects.get(ruler=dominion, name=dominion.building_secondary_resource_name)
    secondary_building_resource.quantity = dominion.acres * dominion.building_secondary_cost
    secondary_building_resource.save()

    event = Event.objects.create(
        reference_id=dominion.id, 
        reference_type="signup", 
        icon="👋",
        message_override=f"{dominion} has joined under the {faction} faction!"
    )

    dominion.save()

    create_faction_perk_dict(dominion, faction)

    return dominion


def abandon_dominion(dominion: Dominion):
    print("Abandoning", dominion)
    dominion.is_abandoned = True
    dominion.associated_user = None
    dominion.save()


def get_trade_value(resource_name):
    this_round = Round.objects.first()
    total_production = 0

    for dominion in Dominion.objects.all():
        total_production += dominion.get_production(resource_name)
    
    price_modifier = 1

    if total_production > 0 and resource_name in this_round.resource_bank_dict:
        price_modifier = 1 + ((this_round.resource_bank_dict[resource_name] / (total_production * 12)) * -0.2)

    if resource_name == "gold":
        trade_value = 5 * price_modifier
    else:
        building = Building.objects.get(resource_produced_name=resource_name, ruler=None)
        trade_value = (500 / building.amount_produced) * price_modifier

    trade_value = round(trade_value, 2)

    if resource_name == "gems":
        trade_value *= 1.3
    
    return max(1, trade_value)


def update_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        round.trade_price_dict[resource_name] = get_trade_value(resource_name)

        if resource_name not in round.base_price_dict:
            round.base_price_dict[resource_name] = get_trade_value(resource_name)

    round.save()


def get_grudge_bonus(my_dominion: Dominion, other_dominion: Dominion):
    try:
        return my_dominion.perk_dict["book_of_grudges"][str(other_dominion.id)]["animosity"] / 100
    except:
        return 0
    

def prune_buildings(dominion: Dominion):
    while dominion.building_count > dominion.acres:
        surplus = dominion.building_count - dominion.acres

        for building in Building.objects.filter(ruler=dominion).order_by('-quantity'):
            if building.quantity > 0 and surplus > 0:
                building.quantity -= 1
                building.save()
                surplus -= 1


def unlock_discovery(dominion: Dominion, discovery_name):
    if not discovery_name in dominion.available_discoveries:
        return
    
    dominion.available_discoveries.remove(discovery_name)
    dominion.learned_discoveries.append(discovery_name)

    for unlocked_discovery in Discovery.objects.filter(requirement=discovery_name):
        dominion.available_discoveries.append(unlocked_discovery.name)

    match discovery_name:
        case "Battering Ram":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Battering Ram"))
        case "Palisade":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Palisade"))
        case "Bastion":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Bastion"))
        case "Zombies":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Zombie"))
        case "Butcher":
            print("Implement spells, silly")
        case "Archmagus":
            archmagus = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Archmagus"))
            archmagus.quantity_at_home = 1
            archmagus.save()
            dominion.has_tick_units = True
        case "Fireball":
            give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Fireball"))
        case "Grudgestoker":
            grudgestoker = give_dominion_unit(dominion, Unit.objects.get(ruler=None, name="Grudgestoker"))
            grudgestoker.quantity_at_home = 1
            grudgestoker.save()
            dominion.has_tick_units = True
        case "Gem Mines":
            give_dominion_building(dominion, Building.objects.get(ruler=None, name="mine"))

    dominion.save()


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
                if mana.name not in unit.upkeep_dict and unit.op > unit.dp:
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
                        overwhelming_unit_upkeep = overwhelming_unit.op / 5

                        if overwhelming_unit_upkeep == int(overwhelming_unit_upkeep):
                            overwhelming_unit_upkeep = int(overwhelming_unit_upkeep)

                        overwhelming_unit.upkeep_dict[mana.name] = overwhelming_unit_upkeep
                        
                    overwhelming_quantity = int(unit.quantity_at_home * 0.2)
                    overwhelming_unit.quantity_at_home += overwhelming_quantity
                    unit.quantity_at_home -= overwhelming_quantity

                    unit.save()
                    overwhelming_unit.save()