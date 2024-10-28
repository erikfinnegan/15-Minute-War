from maingame.models import Faction, Deity, Player, Building, Unit, Discovery, Round, Battle, Event, Resource, Spell
from maingame.utils import update_trade_prices


def initialize_resources():
    resource_templates = [
        {
            "name": "gold",
        },
        {
            "name": "wood",
        },
        {
            "name": "ore",
        },
        {
            "name": "food",
        },
        {
            "name": "research",
        },
        {
            "name": "mana",
        },
        {
            "name": "corpses",
        },
        {
            "name": "gems",
        },
    ]

    for resource_template in resource_templates:
        Resource.objects.create(**resource_template)


def initialize_buildings():
    building_templates = [
        {
            "name": "farm",
            "resource_produced_name": "food",
            "amount_produced": 100,
        },
        {
            "name": "quarry",
            "resource_produced_name": "ore",
            "amount_produced": 50,
        },
        {
            "name": "lumberyard",
            "resource_produced_name": "wood",
            "amount_produced": 100,
        },
        {
            "name": "school",
            "resource_produced_name": "research",
            "amount_produced": 5,
        },
        {
            "name": "stronghold",
            "defense_multiplier": 20,
        },
        {
            "name": "tower",
            "resource_produced_name": "mana",
            "amount_produced": 10,
        },
        {
            "name": "mine",
            "resource_produced_name": "gems",
            "amount_produced": 8,
        },
    ]

    for building_template in building_templates:
        Building.objects.create(**building_template)


def initialize_deities():
    Deity.objects.create(name="Hunger Without End")
    Deity.objects.create(name="Rubecus Swiftstrike")
    Deity.objects.create(name="The Many Who Are One")


def initialize_factions():
    Faction.objects.create(
        name="human",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry"],
        description="""This is a placeholder created during prototyping. None of the costs are balanced and they don't have any unique mechanics."""
    )

    Faction.objects.create(
        name="dwarf",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry"],
        description="""Dwarves keep a book of grudges, chronicling any slight against them, no matter how minor. When a player invades a dwarf, 100 pages of 
        grudges are added. Every tick, dwarves gain +0.03% offense against each player equal to the number of pages of grudges they have about that player. It 
        doesn't sound like much, but it adds up quick. When a dwarf invades another player, any grudges they have against that player are 
        satisfied and cleared. Oh, and simply viewing a dwarf's overview page is enough to warrant one page of grudges."""
    )


def initialize_units():
    human = Faction.objects.get(name="human")
    Unit.objects.create(
        name="archer",
        op=2,
        dp=4,
        cost_dict={
            "gold": 150,
            "wood": 30,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=human
    )
    Unit.objects.create(
        name="knight",
        op=6,
        dp=5,
        cost_dict={
            "gold": 275,
            "ore": 25,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=human
    )

    dwarf = Faction.objects.get(name="dwarf")
    Unit.objects.create(
        name="Stoneshield",
        op=3,
        dp=6,
        cost_dict={
            "gold": 1200,
            "ore": 450,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=dwarf
    )
    Unit.objects.create(
        name="Hammerer",
        op=5,
        dp=4,
        cost_dict={
            "gold": 1300,
            "ore": 500,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=dwarf
    )
    Unit.objects.create(
        name="Grudgestoker",
        op=0,
        dp=0,
        upkeep_dict={
            "gold": 3,
            "food": 1,
            "research": 1,
        },
        perk_dict={"random_grudge_book_pages_per_tick": 3},
        is_trainable=False,
    )

    Unit.objects.create(
        name="Battering Ram",
        op=15,
        dp=0,
        cost_dict={
            "🪵": 4000,
            "ore": 2200,
        },
    )
    Unit.objects.create(
        name="Palisade",
        op=0,
        dp=5,
        cost_dict={
            "🪵": 3000,
        },
        upkeep_dict={
            "🪵": 1,
        },
    )
    Unit.objects.create(
        name="Bastion",
        op=0,
        dp=30,
        cost_dict={
            "ore": 20000,
        },
    )
    Unit.objects.create(
        name="Zombie",
        op=4,
        dp=3,
        cost_dict={
            "mana": 100,
            "corpses": 1,
        },
        upkeep_dict={
            "mana": 0.1,
        },
    )
    Unit.objects.create(
        name="Archmagus",
        op=0,
        dp=0,
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        is_trainable=False,
        perk_dict={"surplus_research_consumed_to_add_one_op_and_dp": 75}
    )
    Unit.objects.create(
        name="Fireball",
        op=9,
        dp=0,
        cost_dict={
            "mana": 250,
        },
        perk_dict={"always_dies_on_offense": True}
    )

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

    for unit in Unit.objects.all():
        unit.training_dict = timer_template
        unit.returning_dict = timer_template
        unit.save()


def initialize_spells():
    Spell.objects.create(
        name="Power Overwhelming",
        description="Double the offensive power of 20% of your units that have higher OP than DP and no mana upkeep... but they'll gain a hefty mana upkeep equal to 20% of their new OP.",
        mana_cost_per_acre=20,
        is_starter=True,
    )


def initialize_discoveries():
    Discovery.objects.create(
        name="Battering Ram",
        description="Allows for the creation of a powerful offensive unit costing wood and ore."
    )

    Discovery.objects.create(
        name="Palisade",
        description="Unlocks the ability to build cheap defenses using only wood."
    )

    Discovery.objects.create(
        name="Bastion",
        description="A blueprint for building large fortifications out of ore."
    )

    Discovery.objects.create(
        name="Zombies",
        description="Gain bodies from invasion casualties when you're victorious and use them to magically raise undead soldiers."
    )

    # Discovery.objects.create(
    #     name="Butcher",
    #     requirement="Zombies",
    #     description="Learn a terrifying ritual to slaughter a portion of your army for bodies."
    # )

    Discovery.objects.create(
        name="Archmagus",
        description="""Gain the allegiance of a terrifyingly powerful sorcerer who will, each tick, consume 10% of any research points beyond your most 
        expensive upgrade to gain 1 OP and DP per 75 consumed."""
    )

    Discovery.objects.create(
        name="Fireball",
        description="Conjure massive fireballs to support your invasions."
    )

    Discovery.objects.create(
        name="Gem Mines",
        description="Construct a new building to mine for precious gems. When trade values are determined, gems get a +30% bonus."
    )

    Discovery.objects.create(
        name="Grudgestoker",
        description="A holy scribe takes up residence with you and appends three pages to your book of grudges each tick.",
        requirement="dwarf",
    )


def initialize_trade_prices():
    round = Round.objects.first()

    for building in Building.objects.all():
        if building.amount_produced > 0:
            round.resource_bank_dict[building.resource_produced_name] = 0

    round.resource_bank_dict["gold"] = 0
    round.save()
    update_trade_prices()
    round.base_price_dict = round.trade_price_dict.copy()
    round.save()


def initialize_game_pieces():
    print()
    print("-- PLAYERS --")

    for player in Player.objects.all():
        print(player)

    print()
    print("-- EVENTS --")

    for event in Event.objects.all():
        print(event)

    Resource.objects.all().delete()
    Battle.objects.all().delete()
    Event.objects.all().delete()
    Round.objects.all().delete()
    Discovery.objects.all().delete()
    Building.objects.all().delete()
    Unit.objects.all().delete()
    Spell.objects.all().delete()
    Faction.objects.all().delete()
    Player.objects.all().delete()
    Deity.objects.all().delete()
    Round.objects.create()

    print()
    print("After delete players")

    for player in Player.objects.all():
        print(player)

    print("After delete events")

    for event in Event.objects.all():
        print(event)

    print()

    initialize_discoveries()
    initialize_factions()
    initialize_resources()
    initialize_deities()
    initialize_buildings()
    initialize_units()
    initialize_spells()
    initialize_trade_prices()
    update_trade_prices()
