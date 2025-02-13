from maingame.models import Unit, Faction, Discovery


def initialize_generic_units():
    Unit.objects.create(
        name="Battering Ram",
        op=15,
        dp=0,
        cost_dict={
            "wood": 7000,
            "ore": 1800,
        },
        upkeep_dict={
            "wood": 4,
        },
        perk_dict={"gets_op_bonus_equal_to_percent_of_target_complacency": 15},
    )

    Unit.objects.create(
        name="Palisade",
        op=0,
        dp=5,
        cost_dict={
            "wood": 1900,
        },
        upkeep_dict={
            "wood": 4,
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
            "mana": 1200,
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
        perk_dict={"surplus_research_consumed_to_add_one_op_and_dp": 1400}
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
        dp=4,
        cost_dict={
            "food": 3150,
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


def initialize_generic_discoveries():
    Discovery.objects.create(
        name="Prosperity",
        description="Increases gold per acre by 1.",
        repeatable=True,
    )

    # Discovery.objects.create(
    #     name="Raiders",
    #     description="Increases chance of stealing an artifact by 10%. Can be taken multiple times, stacking additively.",
    # )

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