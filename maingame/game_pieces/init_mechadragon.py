from maingame.models import Unit, Faction, Discovery


def initialize_mechadragon_units():
    mechadragon = Faction.objects.get(name="mecha-dragon")

    Unit.objects.create(
        name="Placeholder",
        op=0,
        dp=1,
        cost_dict={
            "gold": 1,
            "ore": 1,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=mechadragon
    )


def initialize_mechadragon_discoveries():
    Discovery.objects.create(
        name="Placeholder Discovery",
        description="This holds a place.",
        required_faction_name="mecha-dragon",
    )