from random import randint

from maingame.models import Dominion, Unit

def get_number_of_times_to_tick(dominion: Dominion, start_timestamp):
    if "time_curse" in dominion.perk_dict:
        dominion.perk_dict["time_curse"] -= 1
        
        if dominion.perk_dict["time_curse"] <= 0:
            del dominion.perk_dict["time_curse"]
            
        roll = randint(1,6)
        
        if roll <= 3:
            ticks = 0
        elif roll >= 6:
            ticks = 2
        else:
            ticks = 1
        
        dominion.perk_dict["aethertide_roll_history"].insert(0, f"{start_timestamp.strftime('%H:%M:%S')} ... rolled {roll} => 1-3 skip, 4-5 normal, 6 double... running {ticks} ticks")
        dominion.save()
    elif dominion.faction_name != "aethertide corsairs":
        return 1
    else:
        if dominion.perk_dict["aethertide_increase_next_tick"]:
            dominion.perk_dict["aethertide_coefficient"] += 1
            
            if dominion.perk_dict["aethertide_coefficient"] >= dominion.perk_dict["aethertide_coefficient_max"]:
                dominion.perk_dict["aethertide_increase_next_tick"] = False
        else:
            dominion.perk_dict["aethertide_coefficient"] -= 1
        
            if dominion.perk_dict["aethertide_coefficient"] <= 0:
                dominion.perk_dict["aethertide_increase_next_tick"] = True
                dominion.perk_dict["aethertide_coefficient_max"] = 18 + randint(-3, 3)
                dominion.perk_dict["double_ticks_and_op_penalty"] = not dominion.perk_dict["double_ticks_and_op_penalty"]
        
        aethertide_coefficient = dominion.perk_dict["aethertide_coefficient"]
        aethertide_coefficient_max = dominion.perk_dict["aethertide_coefficient_max"]
        aethertide_max_chance = dominion.perk_dict["aethertide_max_chance"]
        double_ticks_and_op_penalty = dominion.perk_dict["double_ticks_and_op_penalty"]
        
        percent_chance = int((aethertide_coefficient/aethertide_coefficient_max) * aethertide_max_chance)
        
        roll = randint(1,100)
        
        if roll <= percent_chance:
            ticks = 2 if double_ticks_and_op_penalty else 0
        else:
            ticks = 1
            
        dominion.perk_dict["aethertide_roll_history"].insert(0, f"{start_timestamp.strftime('%H:%M:%S')} ... {roll} vs {percent_chance} for {'double' if double_ticks_and_op_penalty else 'skip'} tick - running {ticks} ticks")
        dominion.save()

    try:
        chronokrakens = Unit.objects.get(ruler=dominion, name="Chronokraken")
        big_mult = chronokrakens.perk_dict["op_modified_by_aethertide"]
        small_mult = 1 + ((big_mult - 1) / 3)
        
        if ticks == 0:
            chronokrakens.op *= big_mult
        elif ticks == 2:
            chronokrakens.op /= big_mult
        elif chronokrakens.op > 1000:
            chronokrakens.op /= small_mult
        elif chronokrakens.op < 1000:
            chronokrakens.op *= small_mult
            
        chronokrakens.save()
    except:
        pass
    
    return ticks
    