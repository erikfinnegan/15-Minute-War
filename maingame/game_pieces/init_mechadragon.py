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
        name="Greasedrake",
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

    MechModule.objects.create(
        name="XV-# Rocket Pods",
        capacity=1,
        base_power=325,
        base_upgrade_cost_dict={
            "ore": 10000,
        },
        base_repair_cost_dict={
            "ore": 100,
        },
        fragility=100,
        faction=mechadragon,
    )

    MechModule.objects.create(
        name="AC# Magefield",
        capacity=1,
        base_power=0,
        base_upgrade_cost_dict={
            "mana": 15000,
        },
        base_repair_cost_dict={
            "gold": 100,
            "mana": 15,
        },
        fragility=15,
        perk_dict={"durability_damage_percent_reduction_for_capacity_or_smaller": 20},
        faction=mechadragon,
    )

    MechModule.objects.create(
        name='"# fast # furious" Hyperwings',
        capacity=1,
        base_power=0,
        base_upgrade_cost_dict={
            "ore": 125000,
            "research": 250000,
        },
        base_repair_cost_dict={
            "gold": 100,
            "ore": 25,
        },
        fragility=30,
        perk_dict={"returns_faster": True},
        faction=mechadragon,
    )

    MechModule.objects.create(
        name="Back-#-U Town Portal System",
        capacity=1,
        base_power=0,
        base_upgrade_cost_dict={
            "mana": 1,
            "research": 1,
        },
        base_repair_cost_dict={
            "mana": 1,
            "research": 1,
        },
        fragility=5,
        perk_dict={"recall_instantly": True}, # If all attached modules are the same size or smaller, return home instantly and reset version to 0... or maybe destroy it?
    )
    


def initialize_mechadragon_discoveries():
    Discovery.objects.create(
        name="Back-2-U Town Portal System",
        description="Quantum magic has become advanced enough to reverse increasingly large objects through the timestream, just not the source of the magic itself. Note that two of these may not co-exist simultaneously.",
        required_faction_name="mecha-dragon",
        associated_module_name="Back-#-U Town Portal System",
        repeatable=True,
    )