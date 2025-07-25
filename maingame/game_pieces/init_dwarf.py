from maingame.models import Unit, Faction, Discovery


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
            "gold": 2200,
            "mithril": 2500,
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
            "mithril": 15331,
        },
        upkeep_dict={
            "mithril": 919,
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
        op=10,
        dp=0,
        cost_dict={
            "Hammerer": 1,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        perk_dict={"casualty_multiplier": 3},
    )
    
    Unit.objects.create(
        name="Hatetheist",
        op=0,
        dp=0,
        upkeep_dict={
            "gold": 3,
            "food": 1,
            "research": 1,
        },
        perk_dict={"keeps_grudges_updated": True},
        is_trainable=False,
    )
    
    Unit.objects.create(
        name="Hateriarch",
        op=0,
        dp=0,
        upkeep_dict={
            "gold": 3,
            "food": 1,
            "research": 1,
        },
        perk_dict={"bonus_percent_to_animosity": 10, "retains_extra_grudge_percent": 5},
        is_trainable=False,
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
        description='The dwarf language lacks a distinction between "seeking" and "prospecting". Doom Prospectors are hammerers whose grudges against themselves have grown too heavy to bear and prospect for glorious death in battle. Train instantly.',
        required_faction_name="dwarf",
        associated_unit_name="Doom Prospector",
    )

    Discovery.objects.create(
        name="Always Be Digging",
        description="All dwarves love digging, but some truly can't help it. Once the round starts, expand your dominion vertically by one acre every hour for every 400 acres you have.",
        required_faction_name="dwarf",
    )
    
    Discovery.objects.create(
        name="Hatetheism",
        description="When you attack someone against whom you've recorded at least 50 pages of grudges, recruit 5 Hatetheists.",
        required_faction_name="dwarf",
        associated_unit_name="Hatetheist",
        required_discoveries=["Never Forget", "Doom Prospectors"],
    )
    
    Discovery.objects.create(
        name="Hatetheism Spreads",
        description="When recruiting Hatetheists, get 8 instead of 5",
        required_faction_name="dwarf",
        required_discoveries=["Hatetheism"],
    )
    
    Discovery.objects.create(
        name="Hatetheism Rising",
        description="When recruiting Hatetheists, get 10 instead of 8.",
        required_faction_name="dwarf",
        required_discoveries=["Hatetheism Spreads"],
    )
    
    Discovery.objects.create(
        name="Hateriarchy",
        description="Gain a Hateriarch.",
        required_faction_name="dwarf",
        associated_unit_name="Hateriarch",
        required_discoveries=["Hatetheism Rising"],
        repeatable=True,
    )