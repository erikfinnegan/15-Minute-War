from maingame.models import Faction, Deity, Dominion, Building, Unit, Discovery, Round, Battle, Event, Resource, Spell, Artifact
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
        # {
        #     "name": "gems",
        # },
        {
            "name": "faith",
        },
        {
            "name": "sludge",
        },
        {
            "name": "sinners",
        },
        {
            "name": "mithril",
        },
        {
            "name": "rats",
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
            "amount_produced": 70,
        },
        {
            "name": "lumberyard",
            "resource_produced_name": "wood",
            "amount_produced": 85,
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
            "amount_produced": 50,
        },
        # {
        #     "name": "mine",
        #     "resource_produced_name": "gems",
        #     "amount_produced": 8,
        # },
        {
            "name": "cesspool",
            "resource_produced_name": "sludge",
            "amount_produced": 60,
        },
        {
            "name": "mithril mine",
            "resource_produced_name": "mithril",
            "amount_produced": 30,
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
        description="""Dwarves keep the most meticulous grudges, gaining 50% more pages than anyone else. They also unlock unique abilities to expand
        their grudges and even retain a bit of them instead of forgiving and forgetting like less stalwart folk."""
        # description="""Dwarves keep a book of grudges, chronicling any slight against them, no matter how minor. When a dominion invades a dwarf, 100 pages of 
        # grudges are added about that dominion. Every tick, those grudges simmer and the dwarf's offense bonus against that dominion increases by 0.003% per page,
        # accumulating until the dwarf invades that player successfully. 0.003% may not sound like much, but it adds up quickly."""
    )

    Faction.objects.create(
        name="blessed order",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry"],
        description="""The brothers of the Blessed Order generate faith, which is used to restore the vengeful spirits of warriors who fall defending
        their people. When they're invaded, any accumulated faith is spent to turn defensive casualties into blessed martyrs at the cost of 1,000 faith
        per martyr. However, one sinner appears per tick for each 100 acres and each drains 1 faith per tick until the order places their offense
        # on hold for 24 ticks to begin an inquisition to root them out."""
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

    Faction.objects.create(
        name="goblin",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry",],
        description="""Goblins are nasty little creatures. Whether they like it or not (though they definitely do), they produce 1 rat for every 3 acres.
        Each is ruled by an ambitious little wretch who favors one resource above all others, getting a 10% bonus to production. Every time goblins are 
        invaded, they eat their leader and replace them with a new one who favors a new resource and increases the production bonus by 2%. Leaders will 
        never favor gold as it would be seen as too unoriginal."""
    )

    Faction.objects.create(
        name="biclops",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        building_primary_resource_name="gold",
        building_secondary_resource_name="wood",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry",],
        description="""Fifteen feet tall, two heads, one eye apiece, and as greedy as they are cruel. Biclops have two distinct minds and their success in life almost always
        hinges on their ability to avoid conflict with themselves. You'll be playing just one half of a biclops leader and will need to share control over your dominion
        with your mostly-cooperative other head. Your other head will gain patience any time you invade another dominion (see Overview page), but if they run out of
        patience, they'll wait until you stop actively managing your dominion (i.e. have no units in training) and take over choosing when and who to invade (anyone 
        over 75% of your size who you can beat using only units with OP > DP). If they get TOO impatient, they'll ignore this restriction."""
    )


def initialize_generic_units():
    Unit.objects.create(
        name="Battering Ram",
        op=15,
        dp=0,
        cost_dict={
            "wood": 5000,
            "ore": 4000,
        },
        upkeep_dict={
            "wood": 4,
        },
    )

    Unit.objects.create(
        name="Palisade",
        op=0,
        dp=5,
        cost_dict={
            "wood": 1900,
        },
        upkeep_dict={
            "wood": 5,
        },
    )

    Unit.objects.create(
        name="Bastion",
        op=0,
        dp=30,
        cost_dict={
            "ore": 15000,
        },
    )

    Unit.objects.create(
        name="Zombie",
        op=4,
        dp=3,
        cost_dict={
            "mana": 1000,
            "corpses": 1,
        },
        upkeep_dict={
            "mana": 0.3,
        },
        perk_dict={"casualty_multiplier": 0.75},
    )

    Unit.objects.create(
        name="Archmage",
        op=1,
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
            "mana": 750,
        },
        is_trainable=False,
        perk_dict={"always_dies_on_offense": True}
    )

    Unit.objects.create(
        name="Gingerbrute Man",
        op=6,
        dp=5,
        cost_dict={
            "food": 3600,
        },
        perk_dict={"returns_in_ticks": 4, "casualty_multiplier": 1.5}
    )

    Unit.objects.create(
        name="Imp",
        op=3,
        dp=1,
        upkeep_dict={
            "mana": 1,
        },
        is_trainable=False,
    )

    Unit.objects.create(
        name="Mercenary",
        op=6,
        dp=6,
        cost_dict={
            "gold": 1699,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
    )


def initialize_dwarf_units():
    dwarf = Faction.objects.get(name="dwarf")

    Unit.objects.create(
        name="Stoneshield",
        op=3,
        dp=6,
        cost_dict={
            "gold": 1200,
            "ore": 700,
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
            "gold": 1250,
            "ore": 800,
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
        name="Miner",
        op=0,
        dp=3,
        cost_dict={
            "gold": 700,
            "ore": 400,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        perk_dict={"ore_per_tick": 3, "cm_dug_per_tick": 1},
    )

    Unit.objects.create(
        name="Steelbreaker",
        op=12,
        dp=8,
        cost_dict={
            "gold": 2000,
            "mithril": 2000,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        perk_dict={"casualty_multiplier": 0.5},
    )

    Unit.objects.create(
        name="Deep Angel",
        op=7,
        dp=151,
        cost_dict={
            "mana": 17351,
            "mithril": 12527,
        },
        upkeep_dict={
            "mithril": 739,
        },
        perk_dict={"immortal": True, "converts_apostles": True},
    )

    Unit.objects.create(
        name="Deep Apostle",
        op=7,
        dp=11,
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        is_trainable=False,
        perk_dict={"casualty_multiplier": 0.5},
    )

    Unit.objects.create(
        name="Doom Prospector",
        op=14,
        dp=0,
        cost_dict={
            "gold": 1200,
            "ore": 800,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        perk_dict={"casualty_multiplier": 3},
    )


def initialize_blessed_order_units():
    blessed_order = Faction.objects.get(name="blessed order")

    Unit.objects.create(
        name="Blessed Brother",
        op=0,
        dp=2,
        cost_dict={
            "gold": 350,
            "research": 350,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        perk_dict={"faith_per_tick": 1, "casualty_multiplier": 0.5},
        faction=blessed_order,
    )

    Unit.objects.create(
        name="Zealot",
        op=5,
        dp=5,
        cost_dict={
            "gold": 875,
            "ore": 600,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=blessed_order,
        perk_dict={"casualty_multiplier": 2},
    )

    Unit.objects.create(
        name="Blessed Martyr",
        op=5,
        dp=0,
        upkeep_dict={
            "faith": 1,
        },
        perk_dict={
            "immortal": True,
        },
        is_trainable=False,
        faction=blessed_order,
    )

    Unit.objects.create(
        name="Living Saint",
        op=0,
        dp=100,
        cost_dict={
            "gold": 9000,
            "faith": 8000,
            "mana": 7000,
        },
        upkeep_dict={
            "faith": 10,
            "food": 1,
        },
    )

    Unit.objects.create(
        name="Penitent Engine",
        op=19,
        dp=7,
        cost_dict={
            "gold": 2250,
            "ore": 4600,
            "sinners": 1,
        },
        upkeep_dict={
            "gold": 3,
            "faith": 1,
            "food": 1,
        },
        perk_dict={"casualty_multiplier": 2},
    )

    Unit.objects.create(
        name="Wight",
        op=12,
        dp=10,
        cost_dict={
            "faith": 2000,
            "mana": 1000,
            "corpses": 1,
        },
        upkeep_dict={
            "mana": 0.3,
        },
        perk_dict={"casualty_multiplier": 0.5},
    )

    Unit.objects.create(
        name="Cathedral Titan",
        op=0,
        dp=300,
        cost_dict={
            "gold": 21500,
            "faith": 10000,
            "ore": 85000,
        },
        upkeep_dict={
            "faith": 10,
        },
        perk_dict={"casualty_multiplier": 0.5},
    )

    Unit.objects.create(
        name="Cremain Knight",
        op=14,
        dp=0,
        cost_dict={
            "faith": 250,
            "mana": 750,
        },
        perk_dict={"always_dies_on_offense": True}
    )


def initialize_sludgeling_units():
    sludgeling = Faction.objects.get(name="sludgeling")

    Unit.objects.create(
        name="Dreg",
        op=0,
        dp=4,
        cost_dict={
            "gold": 550,
            "food": 450,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=sludgeling,
    )


def initialize_goblin_units():
    goblin = Faction.objects.get(name="goblin")

    Unit.objects.create(
        name="Stabber",
        op=0,
        dp=3,
        cost_dict={
            "gold": 700,
            "wood": 425,
        },
        upkeep_dict={
            "gold": 1,
            "food": 0.3,
        },
        faction=goblin,
    )

    Unit.objects.create(
        name="Trained Rat",
        op=0,
        dp=1,
        cost_dict={
            "food": 100,
            "rats": 1,
        },
        upkeep_dict={
            "food": 0.1,
        },
        faction=goblin,
        perk_dict={"percent_becomes_rats": 2},
    )

    Unit.objects.create(
        name="Shanker",
        op=3,
        dp=1,
        cost_dict={
            "gold": 900,
            "wood": 550,
        },
        upkeep_dict={
            "gold": 1,
            "food": 0.3,
        },
        faction=goblin,
    )

    Unit.objects.create(
        name="Wreckin Baller",
        op=8,
        dp=0,
        cost_dict={
            "gold": 700,
            "ore": 1500,
        },
        upkeep_dict={
            "gold": 1,
            "food": 0.3,
        },
        perk_dict={"random_allies_killed_on_invasion": 0.5},
    )

    Unit.objects.create(
        name="Charcutier",
        op=0,
        dp=2,
        cost_dict={
            "gold": 1000,
            "ore": 25,
            "research": 700,
        },
        upkeep_dict={
            "gold": 1,
            "food": 0.3,
            "rats": 1,
        },
        perk_dict={"food_per_tick": 15},
    )


def initialize_biclops_units():
    biclops = Faction.objects.get(name="biclops")

    Unit.objects.create(
        name="Smasher",
        op=8,
        dp=16,
        cost_dict={
            "gold": 2400,
            "wood": 2200,
        },
        upkeep_dict={
            "gold": 12,
            "food": 4,
        },
        faction=biclops,
    )

    Unit.objects.create(
        name="Ironclops",
        op=20,
        dp=12,
        cost_dict={
            "gold": 2600,
            "ore": 6400,
        },
        upkeep_dict={
            "gold": 12,
            "food": 4,
        },
        faction=biclops,
        perk_dict={"casualty_multiplier": 0.5},
    )


def initialize_units():
    initialize_generic_units()
    initialize_dwarf_units()
    initialize_blessed_order_units()
    initialize_sludgeling_units()
    initialize_goblin_units()
    initialize_biclops_units()

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
        description="""Takes 20% (rounded down) of your units at home that have a higher OP than DP and transforms them permanently into a 
        new unit with the same DP but twice the OP... but every tick, 3% of them will die. Does not transform units that always die on offense 
        or that cannot be trained.""",
        mana_cost_per_acre=20,
        is_starter=True,
    )

    Spell.objects.create(
        name="Bestow Biclopean Ambition",
        description="""For the next 11 ticks, the target dominion will attack anyone within 75% of their size if they can do so successfully using
        only units with OP > DP and without the "always dies on offense" perk.""",
        mana_cost_per_acre=150,
        is_targeted=True,
        cooldown=0,
    )


def initialize_generic_discoveries():
    Discovery.objects.create(
        name="Prosperity",
        description="Increases gold per acre by 1. Can be taken multiple times.",
    )

    Discovery.objects.create(
        name="Raiders",
        description="Increases chance of stealing an artifact by 10%. Can be taken multiple times, stacking additively.",
    )

    Discovery.objects.create(
        name="Battering Rams",
        description="Allows for the creation of a powerful offensive unit costing wood and ore.",
        associated_unit_name="Battering Ram"
    )

    Discovery.objects.create(
        name="Palisades",
        description="Unlocks the ability to build cheap defenses using only wood.",
        associated_unit_name="Palisade",
    )

    Discovery.objects.create(
        name="Bastions",
        description="A blueprint for building large fortifications out of ore.",
        associated_unit_name="Bastion",
    )

    Discovery.objects.create(
        name="Zombies",
        description="""Gain bodies from invasion casualties when you're victorious and use them to magically raise undead soldiers. Note that you don't get corpses from
        units with a mana cost or mana upkeep, units that always die on invasions, or units that always kill allied units on invasions.""",
        associated_unit_name="Zombie",
    )

    # Discovery.objects.create(
    #     name="Butcher",
    #     requirement="Zombies",
    #     description="Learn a terrifying ritual to slaughter a portion of your army for bodies."
    # )

    Discovery.objects.create(
        name="Archmage",
        description="""Gain the allegiance of a terrifyingly powerful sorcerer who consumes half of your stockpiled research each tick, but leaves 
        enough to afford your upgrades. Gains OP and DP according to the amount of research consumed (see tooltip).""",
        associated_unit_name="Archmage",
    )

    Discovery.objects.create(
        name="Fireballs",
        description="Conjure massive fireballs to support your invasions.",
        associated_unit_name="Fireball",
    )

    # Discovery.objects.create(
    #     name="Gem Mines",
    #     description="Construct a new building to mine for precious gems. Produces 8 gems per tick. When trade values are determined, gems get a +30% bonus."
    # )

    Discovery.objects.create(
        name="Gingerbrute Men",
        description="Run, run, as fast as you can.",
        associated_unit_name="Gingerbrute Man",
    )

    Discovery.objects.create(
        name="Mercenaries",
        description="Got some gold burning a hole in your pocket? Hire mercenaries to burn a hole in your enemies!",
        associated_unit_name="Mercenary",
    )


def initialize_dwarf_discoveries():
    Discovery.objects.create(
        name="Grudgestoker",
        description="A holy scribe takes up residence with you and appends three pages to your book of grudges each tick.",
        required_faction_name="dwarf",
        associated_unit_name="Grudgestoker",
    )

    Discovery.objects.create(
        name="Never Forget",
        description="Instead of forgetting your grudges once you successfully retaliate, you retain 20% of the pages.",
        required_faction_name="dwarf",
        required_discoveries=["Grudgestoker"],
    )

    Discovery.objects.create(
        name="Miners",
        description="Industrious dwarves who dig ever deeper in search of valuable ore. Who knows what they might find if they dig deep enough...",
        required_faction_name="dwarf",
        associated_unit_name="Miner",
    )

    Discovery.objects.create(
        name="Mithril",
        description="Having dug very deep, your miners discover mithril deposits. Construct mithril mines to gather it and equip mighty Steelbreakers to crush your enemies.",
        required_faction_name="dwarf",
        associated_unit_name="Steelbreaker",
        required_perk_dict={"mining_depth": 250000},
    )

    Discovery.objects.create(
        name="The Deep Angels",
        description="Praise the depths and honor the deep angels beneath. They shall bless their apostles with mithril and their enemies with a merciful death.",
        required_faction_name="dwarf",
        required_perk_dict={"mining_depth": 500000},
        required_discoveries=["Mithril"],
    )

    Discovery.objects.create(
        name="Doom Prospectors",
        description='The dwarf language lacks a distinction between "seeking" and "prospecting". Doom Prospectors are dwarves whose grudges against themselves have grown too heavy to bear and prospect for glorious death in battle.',
        required_faction_name="dwarf",
        associated_unit_name="Doom Prospector",
    )

    Discovery.objects.create(
        name="Always Be Digging",
        description="All dwarves love digging, but some truly can't help it. Once the round starts, expand your dominion vertically by one acre every hour for every 400 acres you have.",
        required_faction_name="dwarf",
    )


def initialize_blessed_order_discoveries():
    Discovery.objects.create(
        name="Living Saints",
        description="Pray for assistance from the incredible living saints.",
        required_faction_name="blessed order",
        associated_unit_name="Living Saint",
    )

    Discovery.objects.create(
        name="Heresy",
        description="Triples the number of sinners generated.",
        required_faction_name="blessed order",
        required_discoveries_or=["Grim Sacrament", "Penitent Engines"],
    )

    Discovery.objects.create(
        name="Grim Sacrament",
        description="Sinners killed by inquisition generate corpses.",
        required_faction_name="blessed order",
    )

    Discovery.objects.create(
        name="Wights",
        description="Imbuing a dead body with a spirit other than its own creates a being of terrible power.",
        required_faction_name="blessed order",
        associated_unit_name="Wight",
        required_discoveries=["Heresy", "Grim Sacrament", "Zombies"],
    )

    Discovery.objects.create(
        name="Penitent Engines",
        description="Deadly machines of war piloted by sinners given a chance for redemption through glorious death.",
        required_faction_name="blessed order",
        associated_unit_name="Penitent Engine",
    )

    Discovery.objects.create(
        name="Cathedral Titans",
        description="Towering masterworks driven by fervor given form.",
        required_faction_name="blessed order",
        associated_unit_name="Cathedral Titan",
        required_discoveries=["Living Saints", "Penitent Engines", "Bastions"],
    )

    Discovery.objects.create(
        name="Funerals",
        description="Your casualties will be mourned, generating 10 faith per OP (on offense) or per DP (on defense). Does not apply to units that always die on offense.",
        required_faction_name="blessed order",
    )

    Discovery.objects.create(
        name="Cremain Knights",
        description="Deceased spirits seeking absolution in fire before passing to the afterlife.",
        required_faction_name="blessed order",
        associated_unit_name="Cremain Knight",
        required_discoveries=["Funerals", "Fireballs"],
    )


def initialize_sludgeling_discoveries():
    Discovery.objects.create(
        name="More Experiment Slots",
        description="Provides an extra slot for experimental units, taking you from three to four.",
        required_faction_name="sludgeling",
    )

    Discovery.objects.create(
        name="Even More Experiment Slots",
        description="Provides two more extra slots for experimental units, taking you from four to six.",
        required_discoveries=["More Experiment Slots"],
        required_faction_name="sludgeling",
    )

    Discovery.objects.create(
        name="Recycling Center",
        description="Increases refund for terminated experiments from 80% to 95%",
        required_discoveries=["More Experiment Slots", "Even More Experiment Slots"],
        required_faction_name="sludgeling",
    )
    
    Discovery.objects.create(
        name="Speedlings",
        description="33% of experimental units will cost slightly more and gain the 'returns in 8 ticks' perk.",
        required_faction_name="sludgeling",
        required_discoveries=["More Experiment Slots"],
    )

    Discovery.objects.create(
        name="Toughlings",
        description="33% of experimental units will cost slightly more and gain the 'takes half as many casualties' perk.",
        required_faction_name="sludgeling",
        required_discoveries=["More Experiment Slots"],
    )

    Discovery.objects.create(
        name="Cheaplings",
        description="33% of experimental units will cost less and gain the 'takes twice as many casualties' perk.",
        required_faction_name="sludgeling",
        required_discoveries=["More Experiment Slots"],
    )

    Discovery.objects.create(
        name="Magnum Goopus",
        description="""Behold your glorious magnum goopus! At the time this is selected, combine all units at home with a sludge 
            cost into a single unit with their combined offense and defense. Your incredible masterpiece requires no gold or sludge
            upkeep and consumes just as much food as all of the units that went into making it. If a unit with perks is included, it also 
            gains those perks. You can still train more of those experimental units afterwards.""",
        required_faction_name="sludgeling",
        required_discoveries_or=["Speedlings", "Toughlings", "Cheaplings"],
    )

    Discovery.objects.create(
        name="Inspiration",
        description="""Your creativity runs wild! Gain a free experiment every 4 ticks.""",
        required_faction_name="sludgeling",
        required_discoveries=["Magnum Goopus"],
    )

    Discovery.objects.create(
        name="Encore",
        description="""Another magnum goopus! ANOTHER!! Your fans love you and cannot get enough and you WILL NOT let them down!""",
        required_faction_name="sludgeling",
        required_discoveries=["Magnum Goopus", "Inspiration"],
    )


def initialize_goblin_discoveries():
    Discovery.objects.create(
        name="Wreckin Ballers",
        description="Make the mistake of arming goblins with flails bigger than they are. Expect friendly fire.",
        required_faction_name="goblin",
        associated_unit_name="Wreckin Baller",
    )

    Discovery.objects.create(
        name="Charcutiers",
        description="Goblin cuisine is famous for its dishes intended to be tasted twice.",
        required_faction_name="goblin",
        associated_unit_name="Charcutier",
    )


def initialize_biclops_discoveries():
    Discovery.objects.create(
        name="Bestow Biclopean Ambition",
        description="""Share the gift of desperate, biclopean ambition with another dominion. Unlocks a spell with an 84-tick cooldown that gives 
        the target dominion 11 ticks of an impatient second head hungry for invasion, except it won't use units that always die on offense.""",
        required_faction_name="biclops",
    )

    Discovery.objects.create(
        name="Triclops",
        description="""Rumor has it that every biclops has an invisible third eye that can see the future. When you attack, there is a 5% chance your
        troops will predict a counterattack and instantly return to defensive positions.""",
        required_faction_name="biclops",
    )


def initialize_discoveries():
    initialize_generic_discoveries()
    initialize_dwarf_discoveries()
    initialize_blessed_order_discoveries()
    initialize_sludgeling_discoveries()
    initialize_goblin_discoveries()
    initialize_biclops_discoveries()


def initialize_artifacts():
    Artifact.objects.create(
        name="The Eternal Egg of the Flame Princess",
        description="Generates one fireball per tick for every 500 acres of the dominion that possesses it."
    )

    Artifact.objects.create(
        name="The Infernal Contract",
        description="Generates one imp per tick for every 500 acres of the dominion that possesses it."
    )

    Artifact.objects.create(
        name="The Hoarder's Boon",
        description="Generates an amount of your lowest resource as if you had 5% land dedicated to the building that generates it."
    )

    Artifact.objects.create(
        name="The Stable of the North Wind",
        description="Your units and land return in 10 ticks, unless they'd return faster."
    )

    Artifact.objects.create(
        name="Death's True Name",
        description="You suffer no casualties on defense."
    )

    Artifact.objects.create(
        name="A Ladder Made Entirely of Top Rungs",
        description="Each tick you gain one page of grudges against the largest player (unless it's you)."
    )

    Artifact.objects.create(
        name="The Barbarian's Horn",
        description="Your complacency gives you an equivalent bonus to offense."
    )

    # Artifact.objects.create(
    #     name="The Three-Faced Coin",
    #     description="Your gold gains 0.8% interest per tick."
    # )

    Artifact.objects.create(
        name="The Cause of Nine Deaths",
        description="You gain discoveries 25% faster."
    )


def initialize_trade_prices():
    round = Round.objects.first()
    # round.resource_bank_dict["gold"] = 0

    for building in Building.objects.all():
        if building.amount_produced > 0 and building.resource_produced_name not in ["corpses", "mithril", "faith"]:
            round.resource_bank_dict[building.resource_produced_name] = 0

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
    Artifact.objects.all().delete()
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
    initialize_artifacts()
    update_trade_prices()
