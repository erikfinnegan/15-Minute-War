from maingame.game_pieces.init_aethertide_corsairs import initialize_aethertide_corsairs_discoveries, initialize_aethertide_corsairs_units
from maingame.formatters import generate_countdown_dict
from maingame.game_pieces.init_aether_confederacy import initialize_aether_confederacy_discoveries, initialize_aether_confederacy_units
from maingame.game_pieces.init_biclops import initialize_biclops_discoveries, initialize_biclops_units
from maingame.game_pieces.init_blessed_order import initialize_blessed_order_discoveries, initialize_blessed_order_units
from maingame.game_pieces.init_dwarf import initialize_dwarf_discoveries, initialize_dwarf_units
from maingame.game_pieces.init_generic import initialize_generic_discoveries, initialize_generic_units
from maingame.game_pieces.init_goblin import initialize_goblin_discoveries, initialize_goblin_units
from maingame.game_pieces.init_gsf import initialize_gnomish_special_forces_discoveries, initialize_gnomish_special_forces_units
from maingame.game_pieces.init_mechadragon import initialize_mechadragon_discoveries, initialize_mechadragon_units, initialize_mechadragon_modules
from maingame.game_pieces.init_sludgeling import initialize_sludgeling_discoveries, initialize_sludgeling_units
from maingame.models import Faction, Deity, Dominion, Building, Unit, Discovery, Round, Battle, Event, Resource, Spell, MechModule, Sludgene


def initialize_resources():
    resource_templates = [
        {
            "name": "gold",
        },
        {
            "name": "goop",
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
            "name": "heretics",
        },
        {
            "name": "mithril",
        },
        {
            "name": "rats",
        },
        {
            "name": "blasphemy",
        },
        {
            "name": "plunder",
        },
        {
            "name": "press gangers",
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
            "name": "fishery",
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
            "amount_produced": 95,
        },
        {
            "name": "mithril mine",
            "resource_produced_name": "mithril",
            "amount_produced": 40,
        },
        {
            "name": "ruler's favorite",
            "is_upgradable": False,
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
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry"],
        description_list=["""Dwarves keep a book of grudges, chronicling any slight against them, no matter how minor. When a dominion invades a dwarf, pages of 
        grudges are added about that dominion. Every tick, those grudges simmer and the dwarf's offense bonus against that dominion increases by 0.003% per page,
        accumulating until the dwarf invades that player successfully. 0.003% may not sound like much, but it adds up quickly. Attacking removes half of the
        accumulated bonus against each other dominion, as the grudge must not be that intense if you're fighting elsewhere."""],
        invasion_consequences="This dominion will gain a growing OP bonus against you.",
        play_if_you="like unlocking new units and getting revenge."
    )

    # Faction.objects.create(
    #     name="blessed order",
    #     primary_resource_name="gold",
    #     primary_resource_per_acre="50",
    #     starting_buildings=["farm", "lumberyard", "school", "tower", "quarry"],
    #     description="""The brothers of the Blessed Order generate faith, which is used to restore the vengeful spirits of warriors who fall defending
    #     their people. When they're invaded, any accumulated faith is spent to turn defensive casualties into blessed martyrs at the cost of 500 faith
    #     per martyr. However, one heretic appears per tick for each 100 acres and each drains 1 faith per tick until the order places their offense
    #     on hold for 24 ticks to begin an inquisition to root them out."""
    # )

    Faction.objects.create(
        name="sludgeling",
        primary_resource_name="goop",
        primary_resource_per_acre="50",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry", "cesspool"],
        description_list=["""Most alchemists pursue the creation of potions or the transmutation of cheap materials into gold, but some opt instead to work
        with goop and sludge. The "masterminds" behind the sludgelings experiment with vile substances to see what sort of awful creatures they might create.
        Sludelings uncover new sludgene sequences when attacking and being attacked that can be used to create units. They can also splice these
        sludgene sequences together to work towards creating the perfect units.""",
        """They gain two sludgenes of the same family the first time they invade or get invaded, and then gain two more other invasion/time invaded 
        after that. Every three hours, they're able to splice yet another experiment together."""
        ],
        invasion_consequences="This dominion will gain a sludgene sequence.",
        play_if_you="like customizing your units and creating your own strategy, plus a bit of gambling.",
    )

    Faction.objects.create(
        name="goblin",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry", "ruler's favorite",],
        description_list=["""Goblins are nasty little creatures. Whether they like it or not (though they definitely do), they produce 1 rat for every 3 acres.
        Each is ruled by an ambitious little wretch who favors one resource above all others, getting a 20% bonus to production. Every time goblins are 
        invaded, they eat their leader and replace them with a new one who favors a new resource and increases the production bonus by 1%. Leaders will 
        never favor gold or rats as it would be seen as too unoriginal."""],
        invasion_consequences="This dominion will change the resource they get a bonus to producing and the bonus will increase by 1%.",
        play_if_you="don't want to feel bad about getting invaded and enjoy adapting your strategy as you go, rather than planning."
    )

    Faction.objects.create(
        name="biclops",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry",],
        description_list=["""Fifteen feet tall, two heads, one eye apiece, and as greedy as they are cruel. Biclops have two distinct minds and their success in life almost always
        hinges on their ability to avoid conflict with themselves. You'll be playing just one half of a biclops leader and will need to share control over your dominion
        with your mostly-cooperative other head.""", 
        """Your other head will gain patience any time you invade another dominion (see Overview page), but if they run out of
        patience, they'll wait until you stop actively managing your dominion (i.e. have no units in training) and take over choosing when and who to invade (anyone 
        over 75% of your size who you can beat using only units with OP > DP). If they get TOO impatient, they'll ignore the restriction about units training. When biclops get invaded,
        they add half of their lost complacency penalty to their determination bonus."""],
        invasion_consequences="This dominion will add half their complacency penalty to their determination bonus.",
        play_if_you="like being aggressive and causing a little chaos."
    )

    Faction.objects.create(
        name="gnomish special forces",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry",],
        description_list=["""The GSF are as tricky as they are small. What they lack in power they make up for with their devious schemes, strategically undermining
        the defenses of their targets before striking a decisive blow."""],
        play_if_you="like carefully planning your moves and want to always have something to do."
    )

    Faction.objects.create(
        name="mecha-dragon",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        starting_buildings=["farm", "lumberyard", "school", "tower", "quarry",],
        description_list=["""Inspired by mythical creatures, they set out to construct the ultimate war machine. It is difficult to deny they've succeeded. The bulk of
        their offense comes from a single, powerful mecha-dragon comprised of modules that are upgraded and installed from the mech hangar."""],
        play_if_you="like tinkering with one big unit and juggling abilities with cooldowns."
    )
    
    Faction.objects.create(
        name="aethertide corsairs",
        primary_resource_name="gold",
        primary_resource_per_acre="50",
        starting_buildings=["fishery", "lumberyard", "school", "tower", "quarry"],
        description_list=["""The aethertide goes in cycles. First, you have a chance to double the tick. When this happens, your dominion processes two ticks while everyone 
        else processes one as normal. That chance scales up to 50% over ~18 ticks and back down to 0% over 18 ticks. The second half of the cycle is a chance to skip 
        the tick. This means everyone else processes the tick as normal, but you get nothing, as if you were frozen in time. This also scales up to 50% and down to 
        0% on the same time span. This cycle repeats throughout the whole round.""",
        """While you have a chance to double ticks, you have a penalty to your offense. While you have a chance to skip ticks, you get a bonus to your offense. These
        scale with the chance to skip/double ticks."""
        """Starts with a supply of plunder and gains more based on the raw defense of dominions that
        they invade or plunder. Plundering is an alternate attack type that always steals one acre, causes no casualties (except for units that always die on offense),
        has +100% OP, and does not trigger defensive faction abilities. Plundering generates plunder equal to half of the raw DP of the target and invasions grant a quarter of that.
        Only units with 'Crew' in the name can plunder.""",
        """Enemies attacking them will be time-cursed for 12 ticks. During this time, they have a 20% chance to skip each tick."""],
        invasion_consequences="You will be time-cursed for 12 ticks. During this time, you'll have a 20% chance to skip each tick. ",
        play_if_you="enjoy managing risk/reward for power and don't mind a bit of randomess."
    )


def initialize_units():
    initialize_generic_units()
    initialize_dwarf_units()
    # initialize_blessed_order_units()
    initialize_sludgeling_units()
    initialize_goblin_units()
    initialize_biclops_units()
    initialize_gnomish_special_forces_units()
    initialize_mechadragon_units()
    # initialize_aether_confederacy_units()
    initialize_aethertide_corsairs_units()

    for unit in Unit.objects.all():
        give_unit_timer_template(unit)


def initialize_modules():
    initialize_mechadragon_modules()


def give_unit_timer_template(unit: Unit):
    timer_template = generate_countdown_dict()

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
        mana_cost_per_acre=20,
        is_targeted=True,
        cooldown=36,
    )


def initialize_discoveries():
    initialize_generic_discoveries()
    initialize_dwarf_discoveries()
    # initialize_blessed_order_discoveries()
    initialize_sludgeling_discoveries()
    initialize_goblin_discoveries()
    initialize_biclops_discoveries()
    initialize_gnomish_special_forces_discoveries()
    initialize_mechadragon_discoveries()
    # initialize_aether_confederacy_discoveries()
    initialize_aethertide_corsairs_discoveries()


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
    Sludgene.objects.all().delete()
    MechModule.objects.all().delete()
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
    initialize_modules()
    initialize_spells()
