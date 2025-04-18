from maingame.models import Unit, Faction, Discovery


def initialize_sludgeling_units():
    sludgeling = Faction.objects.get(name="sludgeling")

    Unit.objects.create(
        name="Sludgeling",
        op=6,
        dp=7,
        cost_dict={
            "goop": 1550,
            "sludge": 1250,
        },
        upkeep_dict={
            "goop": 3,
            "food": 1,
        },
        faction=sludgeling,
    )


def initialize_sludgeling_discoveries():
    Discovery.objects.create(
        name="More Experiment Slots",
        description="Provides an extra slot for experimental units.",
        required_faction_name="sludgeling",
    )

    Discovery.objects.create(
        name="Even More Experiment Slots",
        description="Provides two more extra slots for experimental units.",
        required_discoveries=["More Experiment Slots"],
        required_faction_name="sludgeling",
    )

    Discovery.objects.create(
        name="Sludgehoarder",
        description="What if every new creation is a masterpiece just waiting to be recognized? You shouldn't throw anything away ever! Adds three more extra slots for experimental units (up to 25).",
        repeatable=True,
        required_faction_name="sludgeling",
        required_discoveries=["Inspiration"],
    )

    Discovery.objects.create(
        name="Recycling Center",
        description="Increases refund for terminated experiments from 80% to 97%",
        required_discoveries=["More Experiment Slots", "Even More Experiment Slots"],
        required_faction_name="sludgeling",
    )
    
    # Discovery.objects.create(
    #     name="Speedlings",
    #     description="33% of experimental units will cost slightly more and gain the 'returns in 8 ticks' perk.",
    #     required_faction_name="sludgeling",
    #     required_discoveries=["More Experiment Slots"],
    # )

    # Discovery.objects.create(
    #     name="Toughlings",
    #     description="33% of experimental units will cost slightly more and gain the 'takes half as many casualties' perk.",
    #     required_faction_name="sludgeling",
    #     required_discoveries=["More Experiment Slots"],
    # )

    # Discovery.objects.create(
    #     name="Cheaplings",
    #     description="33% of experimental units will cost less and gain the 'takes twice as many casualties' perk.",
    #     required_faction_name="sludgeling",
    #     required_discoveries=["More Experiment Slots"],
    # )

    Discovery.objects.create(
        name="Magnum Goopus",
        description="""Behold your glorious magnum goopus! Go to the experiment page and merge any units at home with a sludge 
            cost into a single unit with their combined offense and defense. Your incredible masterpiece requires no goop or food
            upkeep but consumes 2 sludge per merged unit. It will return from battle at the
            speed of the slowest unit used to create it.""",
        required_faction_name="sludgeling",
        required_discoveries=["Recycling Center"],
        # required_discoveries_or=["Speedlings", "Toughlings", "Cheaplings"],
    )

    Discovery.objects.create(
        name="Inspiration",
        description="""Your creativity runs wild! Gain twice the splices!.""",
        required_faction_name="sludgeling",
        required_discoveries=["Magnum Goopus"],
    )

    Discovery.objects.create(
        name="Encore",
        description="""Another magnum goopus! ANOTHER!! Your fans love you and cannot get enough and you WILL NOT let them down!""",
        required_faction_name="sludgeling",
        required_discoveries=["Magnum Goopus", "Inspiration"],
    )