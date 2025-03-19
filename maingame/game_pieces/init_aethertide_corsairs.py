from maingame.models import Unit, Faction, Discovery

def initialize_aethertide_corsairs_units():
    aethertide_corsairs = Faction.objects.get(name="aethertide corsairs")
    
    Unit.objects.create(
        name="Pirate Crew",
        op=48,
        dp=57,
        cost_dict={
            "gold": 17000,
            "wood": 9000,
        },
        upkeep_dict={
            "gold": 15,
            "food": 5,
            "plunder": 1,
        },
        faction=aethertide_corsairs,
    )
    
    Unit.objects.create(
        name="Gilded Veterans",
        op=50,
        dp=60,
        cost_dict={
            "gold": 17000,
            "wood": 4500,
            "ore": 4000,
            "plunder": 250,
        },
        upkeep_dict={
            "gold": 15,
            "food": 5,
            "plunder": 15,
        },
        faction=aethertide_corsairs,
        perk_dict={"casualty_multiplier": 0.5, "returns_in_ticks": 8},
    )
    
def initialize_aethertide_corsairs_discoveries():
    Discovery.objects.create(
        name="Gilded Veterans",
        description="Some pirates just deserve more.",
        required_faction_name="aethertide corsairs",
        associated_unit_name="Gilded Veterans",
    )
    
    Discovery.objects.create(
        name="Impressment",
        description="When plundering, capture folk for use as press-gangers. They can be used to do stuff.",
        required_faction_name="aethertide corsairs",
    )