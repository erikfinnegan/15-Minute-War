from maingame.models import Unit, Faction, Discovery


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
        faction=goblin,
        perk_dict={"percent_attrition": 2},
    )

    Unit.objects.create(
        name="Shanker",
        op=3,
        dp=1,
        cost_dict={
            "gold": 825,
            "wood": 500,
        },
        upkeep_dict={
            "gold": 1,
            "food": 0.3,
        },
        faction=goblin,
    )

    # Unit.objects.create(
    #     name="Wreckin Baller",
    #     op=8,
    #     dp=0,
    #     cost_dict={
    #         "gold": 700,
    #         "ore": 1500,
    #     },
    #     upkeep_dict={
    #         "gold": 1,
    #         "food": 0.3,
    #     },
    #     perk_dict={"random_allies_killed_on_invasion": 0.5},
    # )

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
        perk_dict={"food_per_tick": 18},
    )

    Unit.objects.create(
        name="Rat Trainer",
        op=0,
        dp=2,
        cost_dict={
            "gold": 650,
            "food": 450,
        },
        upkeep_dict={
            "gold": 1,
            "food": 0.3,
        },
        perk_dict={"rats_trained_per_tick": 1},
    )

    Unit.objects.create(
        name="Ratapult",
        op=1,
        dp=0,
        cost_dict={
            "ore": 30000,
            "wood": 30000,
        },
        upkeep_dict={
            "wood": 4,
        },
        perk_dict={"immortal": True, "rats_launched": 100, "op_if_rats_launched": 100},
    )


def initialize_goblin_discoveries():
    # Discovery.objects.create(
    #     name="Wreckin Ballers",
    #     description="Make the mistake of arming goblins with flails bigger than they are. Expect friendly fire.",
    #     required_faction_name="goblin",
    #     associated_unit_name="Wreckin Baller",
    # )

    Discovery.objects.create(
        name="Charcutiers",
        description="Goblin cuisine is famous for its dishes intended to be tasted twice.",
        required_faction_name="goblin",
        associated_unit_name="Charcutier",
    )

    Discovery.objects.create(
        name="Rat Trainers",
        description="Some goblins attempt the Sisyphean task of maintaining a standing army of trained rats.",
        required_faction_name="goblin",
        associated_unit_name="Rat Trainer",
    )

    Discovery.objects.create(
        name="Ratapults",
        description="Exactly what you're imagining.",
        required_faction_name="goblin",
        associated_unit_name="Ratapult",
    )