from maingame.models import Unit, Faction, Discovery


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