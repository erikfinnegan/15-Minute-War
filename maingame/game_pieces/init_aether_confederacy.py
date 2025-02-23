from maingame.models import Unit, Faction, Discovery

def initialize_aether_confederacy_units():
    aether_confederacy = Faction.objects.get(name="aether confederacy")
    
    Unit.objects.create(
        name="Stalker",
        op=5,
        dp=8,
        cost_dict={
            "gold": 1800,
            "mana": 725,
        },
        upkeep_dict={
            "gold": 3,
            "food": 1,
        },
        faction=aether_confederacy,
    )
    
    Unit.objects.create(
        name="Void Reaver",
        op=5,
        dp=4,
        cost_dict={
            "gold": 1150,
            "mana": 575,
        },
        faction=aether_confederacy,
    )
    
    
def initialize_aether_confederacy_discoveries():
    print()