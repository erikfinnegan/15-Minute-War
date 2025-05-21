from maingame.models import Unit, Faction, Discovery


def initialize_biclops_units():
    biclops = Faction.objects.get(name="biclops")

    Unit.objects.create(
        name="Crusher",
        op=10,
        dp=20,
        cost_dict={
            "gold": 3000,
            "wood": 2400,
        },
        upkeep_dict={
            "gold": 12,
            "food": 4,
        },
        faction=biclops,
        perk_dict={"reduced_gold_upkeep_per_big_hit": 0.2},
    )

    Unit.objects.create(
        name="Ironclops",
        op=24,
        dp=14,
        cost_dict={
            "gold": 3400,
            "ore": 6500,
        },
        upkeep_dict={
            "gold": 12,
            "food": 4,
        },
        faction=biclops,
        perk_dict={"casualty_multiplier": 0.5, "reduced_gold_upkeep_per_big_hit": 0.2},
    )

    Unit.objects.create(
        name="Gatesmasher",
        op=39,
        dp=14,
        cost_dict={
            "gold": 3400+0,
            "wood": 0+7000,
            "ore": 6500+1200,
        },
        upkeep_dict={
            "gold": 12,
            "food": 4,
            "wood": 4,
        },
        perk_dict={"casualty_multiplier": 0.5, "gets_op_bonus_equal_to_percent_of_target_complacency": 40, "reduced_gold_upkeep_per_big_hit": 0.2},
    )


def initialize_biclops_discoveries():
    Discovery.objects.create(
        name="Bestow Biclopean Ambition",
        description="""Share the gift of desperate, biclopean ambition with another dominion. Unlocks a spell with a 36-tick cooldown that gives 
        the target dominion 11 ticks of an impatient second head hungry for invasion, except it won't use units that always die on offense.""",
        required_faction_name="biclops",
    )

    Discovery.objects.create(
        name="Triclops",
        description="""Rumor has it that every biclops has an invisible third eye that can see the future. When you attack, there is a 10% chance your
        troops will predict a counterattack and instantly return to defensive positions. Your land will still return at the normal rate.""",
        required_faction_name="biclops",
    )

    Discovery.objects.create(
        name="Gatesmashers",
        description="""Some biclops look at how battering rams are suspended by swinging ropes or chains and think "yeah, I could do better than that".""",
        associated_unit_name="Gatesmasher",
        required_faction_name="biclops",
        required_discoveries=["Battering Rams"],
    )

    Discovery.objects.create(
        name="Growing Determination",
        description="""Biclops hate not attacking. Increases determination gained by 15% of the base rate.""",
        required_faction_name="biclops",
        repeatable=True,
    )
    
    Discovery.objects.create(
        name="Spurred to Action",
        description="""Finish what they started. Increase the bonus determination you get when invaded from 50% of complaceny to 70%.""",
        required_faction_name="biclops",
    )
    
    Discovery.objects.create(
        name="Pay It Forward",
        description="""Violence is its own reward. Increase the bonus determination you get when invaded from 70% of complaceny to 100%.""",
        required_faction_name="biclops",
        required_discoveries=["Spurred to Action"],
    )