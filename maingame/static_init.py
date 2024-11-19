from maingame.models import Faction, Deity, Dominion, Building, Unit, Discovery, Round, Battle, Event, Resource, Spell, UserSettings
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
        {
            "name": "faith",
        },
        {
            "name": "sludge",
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
            "amount_produced": 150,
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
        {
            "name": "cesspool",
            "resource_produced_name": "sludge",
            "amount_produced": 60,
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
        name="dwarf",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry"],
        description="""Dwarves keep a book of grudges, chronicling any slight against them, no matter how minor. When a dominion invades a dwarf, 100 pages of 
        grudges are added. Every tick, dwarves gain +0.03% offense against each dominion equal to the number of pages of grudges they have about that dominion. It 
        doesn't sound like much, but it adds up quick. When a dwarf invades another dominion, any grudges they have against that dominion are 
        satisfied and cleared. Oh, and simply viewing a dwarf's overview page is enough to warrant one page of grudges."""
    )

    Faction.objects.create(
        name="blessed order",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry"],
        description="""The priests of the Blessed Order generate faith, which is used to restore the vengeful spirits of warriors who fall defending
        their people. When they're invaded, any accumulated faith is spent to turn defensive casualties into blessed martyrs at the cost of 1,000 faith
        per martyr. However, one sinner appears per tick for each 100 acres and each drains 1 faith per tick until the order places their offense
        on hold for 24 ticks to begin an inquisition to root them out. The Blessed Order may declare a crusade, which raises blessed martyrs from
        offensive casualties as well, but doubles the cost of blessed martyrs and costs 1 faith per acre per tick. This crusade will last until
        24 ticks pass without invading."""
    )

    Faction.objects.create(
        name="sludgeling",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry", "cesspool"],
        description="""Most alchemists pursue the creation of potions or the transmutation of cheap materials into gold, but some opt instead to work
        with sludge. The "masterminds" behind the sludgelings experiment with vile substances to see what sort of awful creatures they might create. Sludgelings
        can spend research and sludge to create random unit types in pursuit of the perfect army. If a unit outgrows its usefulness, it can be melted down
        to recoup most of its cost and make room for a new unit type. Every time you generate an experimental unit, it's random and different, but the more experiments
        you run, the greater your chance of getting lucky with a very powerful unit."""
    )


def initialize_units():
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

    blessed_order = Faction.objects.get(name="blessed order")
    Unit.objects.create(
        name="Priest",
        op=0,
        dp=2,
        cost_dict={
            "gold": 400,
            "research": 450,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        perk_dict={"faith_per_tick": 1},
        faction=blessed_order,
    )
    Unit.objects.create(
        name="Novitiate",
        op=5,
        dp=5,
        cost_dict={
            "gold": 1400,
            "ore": 250,
            "wood": 500,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=blessed_order,
    )
    Unit.objects.create(
        name="Blessed Martyr",
        op=15,
        dp=8,
        upkeep_dict={
            "faith": 1,
        },
        perk_dict={"immortal": True},
        is_trainable=False,
        faction=blessed_order,
    )
    Unit.objects.create(
        name="Living Saint",
        op=0,
        dp=100,
        cost_dict={
            "gold": 12000,
            "faith": 6000,
            "mana": 2000,
        },
        upkeep_dict={
            "faith": 10,
            "food": 1,
        },
    )

    sludgeling = Faction.objects.get(name="sludgeling")
    Unit.objects.create(
        name="Dreg",
        op=0,
        dp=4,
        cost_dict={
            "gold": 800,
            "food": 600,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=sludgeling,
    )

    Unit.objects.create(
        name="Battering Ram",
        op=15,
        dp=0,
        cost_dict={
            "wood": 4000,
            "ore": 2200,
        },
    )
    Unit.objects.create(
        name="Palisade",
        op=0,
        dp=5,
        cost_dict={
            "wood": 3000,
        },
        upkeep_dict={
            "wood": 1,
        },
    )
    Unit.objects.create(
        name="Bastion",
        op=0,
        dp=30,
        cost_dict={
            "ore": 12000,
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
        perk_dict={"surplus_research_consumed_to_add_one_op_and_dp": 1300}
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
        give_unit_timer_template(unit)


def give_unit_timer_template(unit: Unit):
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

    unit.training_dict = timer_template
    unit.returning_dict = timer_template
    unit.save()


def initialize_spells():
    Spell.objects.create(
        name="Power Overwhelming",
        description="""Takes 20% of your units that have a higher OP than DP and no mana upkeep and transforms them permanently into a new unit with the same DP but twice the
        OP... and adds a hefty mana upkeep equal to 20% of their OP. Does not affect units that always die on offense.""",
        mana_cost_per_acre=20,
        is_starter=True,
    )


def initialize_discoveries():
    Discovery.objects.create(
        name="Battering Ram",
        description="Allows for the creation of a powerful offensive unit costing wood and ore.",
        associated_unit_name="Battering Ram"
    )

    Discovery.objects.create(
        name="Palisade",
        description="Unlocks the ability to build cheap defenses using only wood.",
        associated_unit_name="Palisade",
    )

    Discovery.objects.create(
        name="Bastion",
        description="A blueprint for building large fortifications out of ore.",
        associated_unit_name="Bastion",
    )

    Discovery.objects.create(
        name="Zombies",
        description="""Gain bodies from invasion casualties when you're victorious and use them to magically raise undead soldiers. Note that you don't get corpses from
        units with a mana cost or mana upkeep or units that always die on invasions.""",
        associated_unit_name="Zombie",
        not_for_factions=["blessed order"]
    )

    # Discovery.objects.create(
    #     name="Butcher",
    #     requirement="Zombies",
    #     description="Learn a terrifying ritual to slaughter a portion of your army for bodies."
    # )

    Discovery.objects.create(
        name="Archmagus",
        description="""Gain the allegiance of a terrifyingly powerful sorcerer who will, each tick, consume 10% of any research points beyond your most 
        expensive upgrade to gain 1 OP and DP per 1300 consumed.""",
        associated_unit_name="Archmagus",
    )

    Discovery.objects.create(
        name="Fireball",
        description="Conjure massive fireballs to support your invasions.",
        associated_unit_name="Fireball",
    )

    Discovery.objects.create(
        name="Gem Mines",
        description="Construct a new building to mine for precious gems. Produces 8 gems per tick. When trade values are determined, gems get a +30% bonus."
    )

    Discovery.objects.create(
        name="Grudgestoker",
        description="A holy scribe takes up residence with you and appends three pages to your book of grudges each tick.",
        requirement="dwarf",
        associated_unit_name="Grudgestoker",
    )

    Discovery.objects.create(
        name="Living Saint",
        description="Pray for assistance from the incredible living saints.",
        requirement="blessed order",
        associated_unit_name="Living Saint",
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

    for dominion in Dominion.objects.all():
        print(dominion)

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
    Dominion.objects.all().delete()
    Deity.objects.all().delete()
    Round.objects.create()

    print()
    print("After delete dominions")

    for dominion in Dominion.objects.all():
        print(dominion)

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
