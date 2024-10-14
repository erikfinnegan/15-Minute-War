from random import randint, choice

from maingame.formatters import create_or_add_to_key
from maingame.models import Unit, Player, Discovery, Building, Deity, Event, Round, Faction, Resource, Spell
from django.contrib.auth.models import User
from django.db.models import Q


def create_faction_perk_dict(player: Player, faction: Faction):
    if faction.name == "dwarf":
        player.perk_dict["book_of_grudges"] = {}

    player.save()


def create_resource_for_player(resource_identifier, player: Player):
    resource_name = resource_identifier

    if len(resource_identifier) == 1:
        resource_name = Resource.objects.get(icon=resource_identifier, ruler=None).name

    if not Resource.objects.filter(ruler=player, name=resource_name).exists():
        base_resource = Resource.objects.get(name=resource_name, ruler=None)
        players_resource = base_resource
        players_resource.pk = None
        players_resource.ruler = player
        players_resource.save()


def initialize_player(user: User, faction: Faction, display_name, timezone="UTC"):
    starter_discovery_names = []

    for discovery in Discovery.objects.filter(requirement=None):
        starter_discovery_names.append(discovery.name)

    for discovery in Discovery.objects.filter(requirement=faction.name):
        starter_discovery_names.append(discovery.name)

    player = Player.objects.create(
        associated_user=user, 
        name=display_name, 
        timezone=timezone, 
        faction_name=faction.name, 
        available_discoveries=starter_discovery_names
    )

    for unit in Unit.objects.filter(ruler=None, faction=faction):
        give_player_unit(player, unit)

    for building_name in faction.starting_buildings:
        base_building = Building.objects.get(name=building_name, ruler=None)
        players_building = base_building
        players_building.pk = None
        players_building.ruler = player
        players_building.save()

        if players_building.resource_produced_name:
            create_resource_for_player(players_building.resource_produced_name, player)

    for spell in Spell.objects.filter(ruler=None, is_starter=True):
        players_spell = spell
        players_spell.pk = None
        players_spell.ruler = player
        players_spell.save()

    player.primary_resource_name = faction.primary_resource_name
    player.primary_resource_per_acre = faction.primary_resource_per_acre
    player.building_primary_resource_name = faction.building_primary_resource_name
    player.building_secondary_resource_name = faction.building_secondary_resource_name
    player.building_primary_cost_per_acre = faction.building_primary_cost_per_acre
    player.building_secondary_cost_per_acre = faction.building_secondary_cost_per_acre
    player.incoming_acres_dict = {
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

    primary_building_resource = Resource.objects.get(ruler=player, name=player.building_primary_resource_name)
    primary_building_resource.quantity = player.acres * player.building_primary_cost
    primary_building_resource.save()

    secondary_building_resource = Resource.objects.get(ruler=player, name=player.building_secondary_resource_name)
    secondary_building_resource.quantity = player.acres * player.building_secondary_cost
    secondary_building_resource.save()

    event = Event.objects.create(
        reference_id=player.id, 
        reference_type="signup", 
        icon="👋",
        message_override=f"{player} has joined under the {faction} faction!"
    )

    player.save()

    create_faction_perk_dict(player, faction)

    return player


def get_trade_value(resource_name):
        this_round = Round.objects.first()
        total_production = 0

        for player in Player.objects.all():
            total_production += player.get_production(resource_name)
        
        price_modifier = 1

        if total_production > 0 and resource_name in this_round.resource_bank_dict:
            price_modifier = 1 + ((this_round.resource_bank_dict[resource_name] / (total_production * 12)) * -0.2)

        if resource_name == "gold":
            trade_value = 5 * price_modifier
        else:
            building = Building.objects.get(resource_produced_name=resource_name, ruler=None)
            trade_value = (500 / building.amount_produced) * price_modifier

        trade_value = round(trade_value, 2)
        
        return max(1, trade_value)


def update_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        round.trade_price_dict[resource_name] = get_trade_value(resource_name)

        if resource_name not in round.base_price_dict:
            round.base_price_dict[resource_name] = get_trade_value(resource_name)

    round.save()


def get_grudge_bonus(my_player: Player, other_player: Player):
    try:
        return my_player.perk_dict["book_of_grudges"][str(other_player.id)]["animosity"] * 0.00003
    except:
        return 0
    

def prune_buildings(player: Player):
    while player.building_count > player.acres:
        surplus = player.building_count - player.acres

        for building in Building.objects.filter(ruler=player).order_by('-quantity'):
            if building.quantity > 0 and surplus > 0:
                building.quantity -= 1
                building.save()
                surplus -= 1


def unlock_discovery(player: Player, discovery_name):
    if not discovery_name in player.available_discoveries:
        return
    
    player.available_discoveries.remove(discovery_name)

    for unlocked_discovery in Discovery.objects.filter(requirement=discovery_name):
        player.available_discoveries.append(unlocked_discovery.name)

    match discovery_name:
        case "Battering Ram":
            give_player_unit(player, Unit.objects.get(ruler=None, name="Battering Ram"))
        case "Palisade":
            give_player_unit(player, Unit.objects.get(ruler=None, name="Palisade"))
        case "Bastion":
            give_player_unit(player, Unit.objects.get(ruler=None, name="Bastion"))
        case "Zombies":
            give_player_unit(player, Unit.objects.get(ruler=None, name="Zombies"))
        case "Butcher":
            print("Implement spells, silly")
        case "Archmagus":
            archmagus = give_player_unit(player, Unit.objects.get(ruler=None, name="Archmagus"))
            archmagus.quantity = 1
            archmagus.save()
            player.has_tick_units = True
        case "Fireball":
            give_player_unit(player, Unit.objects.get(ruler=None, name="Fireball"))
        case "Grudgestoker":
            grudgestoker = give_player_unit(player, Unit.objects.get(ruler=None, name="Grudgestoker"))
            grudgestoker.quantity = 1
            grudgestoker.save()
            player.has_tick_units = True

    player.save()


def give_player_unit(player: Player, unit: Unit):
    players_unit = unit
    players_unit.pk = None
    players_unit.ruler = player
    players_unit.save()

    for resource in unit.cost_dict:
        create_resource_for_player(resource, player)

    return players_unit


def cast_spell(spell: Spell):
    player = spell.ruler
    mana = Resource.objects.get(ruler=player, name="mana")

    if mana.quantity < spell.mana_cost:
        return
    
    mana.quantity -= spell.mana_cost
    mana.save()

    match spell.name:
        case "Power Overwhelming":
            for unit in Unit.objects.filter(ruler=player):
                if mana.icon not in unit.upkeep_dict and unit.op > unit.dp:
                    try:
                        overwhelming_unit = Unit.objects.get(ruler=player, name=f"Overwhelming {unit.name}")
                    except:
                        overwhelming_unit = unit
                        overwhelming_unit.pk = None
                        overwhelming_unit.name = f"Overwhelming {unit.name}"
                        overwhelming_unit.op *= 2
                        overwhelming_unit.quantity = 0
                        overwhelming_unit_upkeep = overwhelming_unit.op / 10

                        if overwhelming_unit_upkeep == int(overwhelming_unit_upkeep):
                            overwhelming_unit_upkeep = int(overwhelming_unit_upkeep)

                        overwhelming_unit.upkeep_dict[mana.icon] = overwhelming_unit_upkeep
                        

                    overwhelming_quantity = int(unit.quantity * 0.2)
                    overwhelming_unit.quantity += overwhelming_quantity
                    unit.quantity -= overwhelming_quantity

                    unit.save()
                    overwhelming_unit.save()