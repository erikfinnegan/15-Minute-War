import random
from string import Formatter


def get_perk_text(perk_dict, resource_name_list, faction_name="none"):
    if not perk_dict:
        return ""
    
    perk_text = ""

    if "is_glorious" in perk_dict:
        perk_text += "My god, it's glorious. "

    if "is_more_glorious" in perk_dict:
        perk_text += "HOW IS THIS ONE EVEN BETTER? "
    
    if "surplus_research_consumed_to_add_one_op_and_dp" in perk_dict:
        perk_text += f"""Consumes half of your stockpiled research each tick, but leaves enough to afford your upgrades. Gains 1 OP and 1 DP per  
        {perk_dict['surplus_research_consumed_to_add_one_op_and_dp']} consumed. """

    if "random_grudge_book_pages_per_tick" in perk_dict:
        pages_per_tick = perk_dict["random_grudge_book_pages_per_tick"]
        perk_text += f"Adds {pages_per_tick} page{'s' if pages_per_tick > 1 else ''} to an existing grudge in your book of grudges each tick. "

    if "always_dies_on_offense" in perk_dict:
        perk_text += "Always dies when sent on an invasion. "

    if "always_dies_on_defense" in perk_dict:
        perk_text += "Always dies when successfully invaded. "

    if "immortal" in perk_dict:
        perk_text += "Does not die in combat. "

    for resource in resource_name_list:
        if f"{resource}_per_tick" in perk_dict:
            amount_produced = perk_dict[f"{resource}_per_tick"]
            amount_produced = int(amount_produced) if amount_produced == int(amount_produced) else amount_produced
            
            if faction_name == "sludgeling":
                verb = "Secretes"
            else:
                verb = "Produces"
                
            perk_text += f"{verb} {amount_produced} {resource} per tick. "

    if "casualty_multiplier" in perk_dict:
        multiplier = perk_dict["casualty_multiplier"]
        perk_text += f"Takes {multiplier}x casualties. "
        # if multiplier == 2:
        #     perk_text += f"Takes twice as many casualties. "
        # elif multiplier == 3:
        #     perk_text += f"Takes three times as many casualties. "
        # elif multiplier == 0.25:
        #     perk_text += f"Takes a quarter as many casualties. "
        # elif multiplier == 0.5:
        #     perk_text += f"Takes half as many casualties. "
        # elif multiplier == 0.75:
        #     perk_text += "Takes 25% fewer casualties. "
        # elif multiplier == 1.5:
        #     perk_text += "Takes 50% more casualties. "
        # else:
        #     perk_text += f"Takes {multiplier}x as many casualties. "

    if "returns_in_ticks" in perk_dict:
        ticks_to_return = perk_dict["returns_in_ticks"]
        perk_text += f"Returns from battle in {ticks_to_return} tick{'s' if ticks_to_return > 1 else ''}. "

    if "percent_attrition" in perk_dict:
        attrition_percent = perk_dict["percent_attrition"]
        perk_text += f"{attrition_percent}% of these die every tick, rounding up. "

    if "converts_apostles" in perk_dict:
        perk_text += "Converts one Stoneshield to a Deep Apostle every tick. "

    if "cm_dug_per_tick" in perk_dict:
        perk_text += "Digs 1 torchbright per tick. "

    if "sacrifices_brothers_chance_percent" in perk_dict and "sacrifices_brothers_amount" in perk_dict:
        sacrifices_brothers_chance_percent = perk_dict["sacrifices_brothers_chance_percent"]
        sacrifices_brothers_amount = perk_dict["sacrifices_brothers_amount"]
        perk_text += f"Every {sacrifices_brothers_amount} (rounding up) has a {sacrifices_brothers_chance_percent}% chance per tick to sacrifice up to {sacrifices_brothers_amount} Blessed Brothers to create one Grisly Altar. "

    if "zealots_chosen_per_tick" in perk_dict:
        zealots_chosen_per_tick = perk_dict["zealots_chosen_per_tick"]
        perk_text += f"Elevates {zealots_chosen_per_tick} zealot per tick to a Chosen One. "

    if "percent_becomes_500_blasphemy" in perk_dict:
        percent_becomes_500_blasphemy = perk_dict["percent_becomes_500_blasphemy"]
        perk_text += f"{percent_becomes_500_blasphemy}% attrition into 500 blasphemy per tick. "

    if "gets_op_bonus_equal_to_percent_of_target_complacency" in perk_dict:
        gets_op_bonus_equal_to_percent_of_target_complacency = perk_dict["gets_op_bonus_equal_to_percent_of_target_complacency"]
        perk_text += f"Increases OP by {gets_op_bonus_equal_to_percent_of_target_complacency}% of the target's complacency penalty. "

    # if "percent_becomes_rats" in perk_dict:
    #     becomes_rats_percent = perk_dict["percent_becomes_rats"]
    #     perk_text += f"{becomes_rats_percent}% of these return to normal rats every tick, rounding up. "

    if "random_allies_killed_on_invasion" in perk_dict:
        random_allies_killed = perk_dict["random_allies_killed_on_invasion"]
        if random_allies_killed == 0.5:
            perk_text += f"When invading, half of these each kill one randomly selected own unit on the same invasion. "
        else:
            perk_text += f"When invading, each kills {random_allies_killed} randomly selected own unit{'s' if random_allies_killed > 1 else ''} on the same invasion. "

    if "food_from_rat" in perk_dict:
        food_from_rat = perk_dict["food_from_rat"]
        perk_text += f"Each carves up one rat per tick into {food_from_rat} food. "

    if "rats_trained_per_tick" in perk_dict:
        rats_trained_per_tick = perk_dict["rats_trained_per_tick"]
        perk_text += f"Attempts to train {rats_trained_per_tick} Trained Rat per tick, paying costs as normal. "
    
    if "invasion_plan_power" in perk_dict:
        invasion_plan_power = perk_dict["invasion_plan_power"]
        perk_text += f"Can be sent to infiltrate a target, increasing your offense on your next attack against them by {invasion_plan_power}. "
        
    if "subverted_target_id" in perk_dict:
        # op_modified_by_aethertide = perk_dict["op_modified_by_aethertide"]
        perk_text += f"Does not return from infiltration until you invade the target or recall manually from the target's Overview page. Until then, the target subtracts your infiltration against them from their OP against you (after any modifiers). "

    if "rats_launched" in perk_dict and "op_if_rats_launched" in perk_dict:
        rats_launched = perk_dict["rats_launched"]
        op_if_rats_launched = perk_dict["op_if_rats_launched"]
        perk_text += f"When invading, each launches {rats_launched} rats for +{op_if_rats_launched} OP. "

    if "repairs_mechadragons" in perk_dict:
        perk_text += f"Repairs 1 durability/tick to a damaged mecha-dragon module. "
        
    if "hides_for_ticks_after_defense" in perk_dict:
        hides_for_ticks_after_defense = perk_dict["hides_for_ticks_after_defense"]
        perk_text += f"After a failed defense, goes into the units returning queue for {hides_for_ticks_after_defense} ticks. "
        
    if "op_modified_by_aethertide" in perk_dict:
        op_modified_by_aethertide = perk_dict["op_modified_by_aethertide"]
        perk_text += f"OP increased {op_modified_by_aethertide}x when you skip a tick, divided by {op_modified_by_aethertide} when you double one, otherwise multiplied/divided by 1.03 to get back towards 1,000. "
        
    if "reduced_gold_upkeep_by_teamwork" in perk_dict:
        reduced_gold_upkeep_by_teamwork = perk_dict["reduced_gold_upkeep_by_teamwork"]
        # perk_text += f"-{reduced_gold_upkeep_by_teamwork} gold upkeep for each invasion against a player larger than you. "
        perk_text += f"Reduce gold upkeep by {reduced_gold_upkeep_by_teamwork} times the lowest number of attacks made by you compared to your other head. "
        
    return perk_text


def cost_after_x_ticks(cost, ticks):
    for _ in range(ticks):
        cost *= 0.9281
        cost = int(cost)
        
    return cost


def get_casualty_mod_cost_multiplier(casualty_multiplier):
    total_spent = 0
    total_normal_spent = 0
    unit_price = 2300
    target = 50000
    unit_op = 8
    units = 0
    normal_units = 0
    attacks = 7
    casualty_multiplier = casualty_multiplier

    casualty_percent = 10 * casualty_multiplier
    survival_rate = 1 - (casualty_percent/100)

    for _ in range(attacks):
        while units * unit_op < target:
            units += 1
            total_spent += unit_price

        units = int(units * survival_rate)

        while normal_units * unit_op < target:
            normal_units += 1
            total_normal_spent += unit_price

        normal_units = int(normal_units * 0.9)

    cost_increase = 1 / (total_spent/total_normal_spent)

    return round(cost_increase, 2)


def get_fast_return_cost_multiplier(return_ticks, op, dp):
    base_cost = 10000
    cost = base_cost
    faster = 12 - return_ticks
    increase_per_speed = 1.02 + (faster/300)
    
    for _ in range(faster):
        cost *= increase_per_speed
        
    multiplier = int(cost)/base_cost
    
    extra_cost_decimal = multiplier - 1
    proportion_of_multiplier = min(op / max(1, dp), dp / max(1, op)) # 2/10 and 10/2 both end up with 20%
    third_extra_cost_decimal = extra_cost_decimal / 3
    
    return 1 + third_extra_cost_decimal + (third_extra_cost_decimal * proportion_of_multiplier * 2)


def get_low_turtle_cost_multiplier(op, dp):
    # Up to a 15% discount based on how much turtle the unit doesn't have
    return min(1, 1 - (1 - (dp / max(1, op))) * 0.15)


def smart_comma(base, addition):
    if len(base) > 0:
        return f", {addition}"
    else:
        return addition
    

def create_or_add_to_key(dict, key, amount):
    if key in dict:
        dict[key] += amount
    else:
        dict[key] = amount

    return dict


def format_minutes(minutes):
    days, minutes = divmod(minutes, 1440) # 1440 minutes in a day
    hours, minutes = divmod(minutes, 60)

    if days > 0:
        return f'{days} day{"s" if days != 1 else ""}, {hours} hour{"s" if hours != 1 else ""}'
    elif hours > 0:
        return f'{hours} hour{"s" if hours != 1 else ""}, {minutes} minute{"s" if minutes != 1 else ""}'
    else:
        return f'{minutes} minute{"s" if minutes != 1 else ""}'


def get_sludgeling_name():
    return random.choice(
        [
            "Sludger", "Oozer", "Gooper", "Marsher", "Sogger", "Squisher", "Slimer", "Pudder", "Swamper", "Snotter", "Slurper", "Slopper", "Damper", "Grosser",
            "Oozeling", "Goopling", "Marshling", "Sogling", "Squishling", "Slimeling", "Pudling", "Swampling", "Snotling", "Slurpling", "Dampling", "Grossling",
            "Sludgezoid", "Oozoid", "Goopazoid", "Marshazoid", "Soggazoid", "Squishazoid", "Slimazoid", "Swampazoid", "Snotazoid", "Slurpazoid", "Sloppazoid",
        ]
    )
    

def get_sludgene_name():
    letters = ["S", "L", "U", "D", "G", "E", "G", "O", "P"]
    name = ""
    
    for _ in range(5):
        name += random.choice(letters)
        
    return name


def get_goblin_name():
    name_base = random.choice(["Tok", "Gor", "Grum", "Grim", "Gut", "Kork", "Mux", "Buzzz", "Ruk", "Tuk", "Zu", "Zew", "Bok", "Wok", "Rik", "Yux", "Pox",
                               "Sik", "Dux", "Fum", "Hog", "Juk", "Lug", "Zug", "Xix", "Cug", "Vit", "Nox", "Mud"])
    
    return f"{name_base}-{name_base}"


def get_goblin_title():
    roll = random.randint(1,103)

    if roll <= 50:
        return "Queen"
    elif roll <= 100:
        return "King"
    elif roll <= 101:
        return "Arch-arsonist"
    elif roll <= 102:
        return "Supreme Chancellor"
    elif roll <= 103:
        return "Almightiest"

    return "Scumbucket"


def get_goblin_ruler():
    return f"{get_goblin_title()} {get_goblin_name()}"


def divide_hack(x, y):
    if y == 0:
        return 99999999999999
    else:
        return x / y


def shorten_number(num):
    hundred_thousand = 100000
    one_million = 1000000
    ten_million = 10000000
    
    if num < hundred_thousand: # 100k
        return f"{num:2,}"
    elif num < one_million: # 1m
        return f"{int(num/1000)}k"
    elif num < ten_million: #10m
        return f"{round(num/one_million, 2)}m"
    else:
        return f"{round(num/one_million, 1)}m"
    

def get_roman_numeral(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90,
        100, 400, 500, 900, 1000]
    sym = ["I", "IV", "V", "IX", "X", "XL",
        "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12
    
    roman_numeral = ""
    
    while number:
        div = number // num[i]
        number %= num[i]

        while div:
            roman_numeral += sym[i]
            div -= 1
        i -= 1
        
    return roman_numeral


def generate_countdown_dict():
    return {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "10": 0,
        "11": 0,
        "12": 0,
        "13": 0,
        "14": 0,
        "15": 0,
        "16": 0,
        "17": 0,
        "18": 0,
        "19": 0,
        "20": 0,
        "21": 0,
        "22": 0,
        "23": 0,
        "24": 0,
    }