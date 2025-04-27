from maingame.models import Unit, Faction, Discovery

def initialize_aethertide_corsairs_units():
    aethertide_corsairs = Faction.objects.get(name="aethertide corsairs")
    
    Unit.objects.create(
        name="Pirate Crew",
        op=48,
        dp=57,
        cost_dict={
            "gold": 14750,
            "wood": 9000,
            "plunder": 1,
        },
        upkeep_dict={
            "gold": 15,
            "food": 5,
            "plunder": 1,
        },
        faction=aethertide_corsairs,
    )
    
    # Unit.objects.create(
    #     name="Gilded Veterans",
    #     op=50,
    #     dp=60,
    #     cost_dict={
    #         "gold": 14750,
    #         "wood": 4500,
    #         "ore": 4500,
    #         "plunder": 250,
    #     },
    #     upkeep_dict={
    #         "gold": 15,
    #         "food": 5,
    #         "plunder": 15,
    #     },
    #     perk_dict={"casualty_multiplier": 0.5, "returns_in_ticks": 8},
    # )
    
    Unit.objects.create(
        name="Realitylubber Crew",
        op=24,
        dp=28,
        cost_dict={
            "wood": 6000,
            "press gangers": 5,
        },
        upkeep_dict={
            "gold": 5,
            "food": 5,
        },
        perk_dict={"casualty_multiplier": 2, "returns_in_ticks": 15},
    )
    
    Unit.objects.create(
        name="Laeviathan",
        op=0,
        dp=1000,
        cost_dict={
            "food": 500000,
        },
        upkeep_dict={
            "food": 100,
        },
        perk_dict={"hides_for_ticks_after_defense": 6, "immortal": True},
    )
    
    Unit.objects.create(
        name="Chronokraken",
        op=1000,
        dp=0,
        cost_dict={
            "food": 1138888,
        },
        upkeep_dict={
            "food": 100,
        },
        perk_dict={"immortal": True, "op_modified_by_aethertide": 1.1},
    )
    
    
def initialize_aethertide_corsairs_discoveries():
    # Discovery.objects.create(
    #     name="Gilded Veterans",
    #     description="Some pirates just deserve more.",
    #     required_faction_name="aethertide corsairs",
    #     associated_unit_name="Gilded Veterans",
    # )
    
    Discovery.objects.create(
        name="Impressment",
        description="When plundering or invading, capture folk for use as press_gangers equal to 2% of the amount of plunder gained.",
        associated_unit_name="Realitylubber Crew",
        required_faction_name="aethertide corsairs",
    )
    
    Discovery.objects.create(
        name="Grim Pragmatism",
        description="Sometimes the parts are worth more than the whole. Allows press gangers to be killed for their corpses.",
        required_faction_name="aethertide corsairs",
        required_discoveries=["Zombies"],
    )
    
    Discovery.objects.create(
        name="Laeviathans",
        description="Powerful monstrosities, but need time to recover after defeat.",
        required_faction_name="aethertide corsairs",
        associated_unit_name="Laeviathan",
    )
    
    Discovery.objects.create(
        name="Chronokrakens",
        description="Unkillable sea monsters that prey on time.",
        required_faction_name="aethertide corsairs",
        associated_unit_name="Chronokraken",
    )