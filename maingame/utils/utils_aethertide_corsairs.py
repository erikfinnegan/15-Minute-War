from random import randint

from models import Dominion

def get_number_of_times_to_tick(dominion: Dominion):
    if dominion.faction_name != "aethertide corsairs":
        return 1
    
    if dominion.perk_dict["aethertide_increase_next_tick"]:
        dominion.perk_dict["aethertide_coefficient"] += 1
        
        if dominion.perk_dict["aethertide_coefficient"] >= dominion.perk_dict["aethertide_coefficient_max"]:
            dominion.perk_dict["aethertide_increase_next_tick"] = False
    else:
        dominion.perk_dict["aethertide_coefficient"] -= 1
    
        if dominion.perk_dict["aethertide_coefficient"] <= 0:
            dominion.perk_dict["aethertide_increase_next_tick"] = True
            dominion.perk_dict["aethertide_coefficient_max"] = 18 + randint(-3, 3)
    
    dominion.save()
    
    aethertide_coefficient = dominion.perk_dict["aethertide_coefficient"]
    aethertide_coefficient_max = dominion.perk_dict["aethertide_coefficient_max"]
    aethertide_max_chance = dominion.perk_dict["aethertide_max_chance"]
    double_ticks_and_op_penalty = dominion.perk_dict["double_ticks_and_op_penalty"]
    
    percent_chance = int((aethertide_coefficient/aethertide_coefficient_max) * aethertide_max_chance)
    
    roll = randint(1,100)
    
    if roll <= percent_chance:
        return 2 if double_ticks_and_op_penalty else 0
    else:
        return 1
    