from maingame.models import Unit, Faction, Discovery


def initialize_gnomish_special_forces_units():
    gnomish_special_forces = Faction.objects.get(name="gnomish special forces")

    Unit.objects.create(
        name="Trencher",
        op=2,
        dp=4,
        cost_dict={
            "gold": 550,
            "ore": 300,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=gnomish_special_forces
    )

    Unit.objects.create(
        name="Greencap",
        op=6,
        dp=5, # If you change this or the perk, update world_js.html updateInfiltrateOffense() because they're hardcoded like a fucking idiot
        cost_dict={
            "gold": 2300,
            "ore": 300,
            "research": 1200,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=gnomish_special_forces,
        perk_dict={"invasion_plan_power": 4}, # If you change this or DP, update world_js.html updateInfiltrateOffense() because they're hardcoded like a fucking idiot
    )

    Unit.objects.create(
        name="Juggernaut Tank",
        op=28,
        dp=36,
        cost_dict={
            "ore": 11000,
            "wood": 4400,
        },
        upkeep_dict={
            "gold": 6,
            "food": 2,
            "wood": 5,
        },
        perk_dict={"casualty_multiplier": 0.5},
    )

    Unit.objects.create(
        name="Inferno Mine",
        op=0,
        dp=9,
        cost_dict={
            "mana": 350,
            "ore": 350,
        },
        upkeep_dict={
            "mana": 2,
        },
        perk_dict={"always_dies_on_defense": True},
    )


def initialize_gnomish_special_forces_discoveries():
    Discovery.objects.create(
        name="Juggernaut Tanks",
        description="""Powerful armored vehicles to support gnomish military efforts.""",
        associated_unit_name="Juggernaut Tank",
        required_faction_name="gnomish special forces",
    )

    Discovery.objects.create(
        name="Inferno Mines",
        description="""Many have wished for a safe method to leverage fireballs on defense. So far, only the GSF have found a way.""",
        associated_unit_name="Inferno Mine",
        required_faction_name="gnomish special forces",
        required_discoveries=["Fireballs"],
    )

    Discovery.objects.create(
        name="Rapid Deployment",
        description="""Careful planning and clever strategy keeps the GSF ahead of their enemies at all times. Units are trained in 6 ticks.""",
        required_faction_name="gnomish special forces",
    )