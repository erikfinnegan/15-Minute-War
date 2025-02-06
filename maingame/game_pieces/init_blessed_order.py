from maingame.models import Unit, Faction, Discovery


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
        # Cost is determined by dominion_controls.py 
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

    # Unit.objects.create(
    #     name="Wight",
    #     op=12,
    #     dp=10,
    #     cost_dict={
    #         "faith": 2000,
    #         "mana": 1000,
    #         "corpses": 1,
    #     },
    #     upkeep_dict={
    #         "mana": 0.3,
    #     },
    #     perk_dict={"casualty_multiplier": 0.5},
    # )

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


def initialize_blessed_order_discoveries():
    Discovery.objects.create(
        name="Living Saints",
        description="Pray for assistance from the incredible living saints.",
        required_faction_name="blessed order",
        associated_unit_name="Living Saint",
    )

    Discovery.objects.create(
        name="Scrutiny",
        description="Doubles the number of sinners found per tick.",
        required_faction_name="blessed order",
        required_discoveries_or=["Grim Sacrament", "Penitent Engines"],
    )

    Discovery.objects.create(
        name="Grim Sacrament",
        description="Sinners killed by inquisition generate corpses.",
        required_faction_name="blessed order",
    )

    # Discovery.objects.create(
    #     name="Wights",
    #     description="Imbuing a dead body with a spirit other than its own creates a being of terrible power.",
    #     required_faction_name="blessed order",
    #     associated_unit_name="Wight",
    #     required_discoveries=["Heresy", "Grim Sacrament", "Zombies"],
    # )

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

    Discovery.objects.create(
        name="Heresy",
        description='Come, child. Reject the false teachings of these so-called "brothers" and embrace your true family.',
        required_faction_name="blessed order",
        required_perk_dict={"corruption": 250000},
    )