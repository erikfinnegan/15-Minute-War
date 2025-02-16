from maingame.models import Unit, Faction, Discovery, MechModule


def initialize_mechadragon_units():
    mechadragon = Faction.objects.get(name="mecha-dragon")

    Unit.objects.create(
        name="Forgewarden",
        op=0,
        dp=7,
        cost_dict={
            "gold": 1500,
            "ore": 850,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=mechadragon
    )

    Unit.objects.create(
        name="Mechanic",
        op=0,
        dp=0,
        cost_dict={
            "gold": 500,
            "research": 500,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        perk_dict={"repairs_mechadragons": True},
        faction=mechadragon
    )

    Unit.objects.create(
        name="Mecha-Dragon",
        op=1,
        dp=0,
        faction=mechadragon,
        is_trainable=False,
    )


def initialize_mechadragon_modules():
    mechadragon = Faction.objects.get(name="mecha-dragon")

    MechModule.objects.create(
        name="Scrapper Claws v1.#.0",
        capacity=1,
        base_power=425,
        base_upgrade_cost_dict={
            "ore": 66500,
        },
        base_repair_cost_dict={
            "gold": 100,
            "ore": 25,
        },
        fragility=40,
        faction=mechadragon,
    )

    MechModule.objects.create(
        name="#XL Chompers",
        capacity=1,
        base_power=335,
        base_upgrade_cost_dict={
            "ore": 52000,
        },
        base_repair_cost_dict={
            "gold": 100,
            "ore": 25,
        },
        fragility=20,
        faction=mechadragon,
    )

    MechModule.objects.create(
        name="Fire Breath Mk#",
        capacity=1,
        base_power=300,
        base_upgrade_cost_dict={
            "ore": 46500,
        },
        base_repair_cost_dict={
            "gold": 100,
            "ore": 25,
        },
        fragility=10,
        faction=mechadragon,
    )


def initialize_mechadragon_discoveries():
    Discovery.objects.create(
        name="Placeholder Discovery",
        description="This holds a place.",
        required_faction_name="mecha-dragon",
    )