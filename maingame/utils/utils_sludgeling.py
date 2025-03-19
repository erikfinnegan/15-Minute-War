import random
from random import randint

from maingame.formatters import generate_countdown_dict, get_sludgeling_name, get_sludgene_name
from maingame.game_pieces.initialize import give_unit_timer_template
from maingame.models import Unit, Dominion, Sludgene
from maingame.utils.utils import generate_unit_cost_dict, get_unit_from_dict, round_x_to_nearest_y


def generate_random_sludgene_op_or_dp():
    # 0 to 12, skewing average
    op_list = [randint(0,12), randint(0,12), randint(0,12)]
    op_list.sort()
    return op_list[1]


def generate_random_sludgene_return_ticks():
    if randint(1,3) > 1:
        return 12
    
    # 2 to 12, skewing high
    return_ticks_list = [randint(2,11), randint(2,12), randint(2,13)]
    return_ticks_list.sort(reverse=True)
    
    return return_ticks_list[0]


def generate_random_sludgene_casualty_rate():
    if randint(1,3) > 1:
        return 1
    
    # 0.25 to 1.75, skewing average
    casualty_rate = 1
    roll = randint(-1, 1)
    casualty_rate += roll * 0.25
    roll = randint(-1, 1)
    casualty_rate += roll * 0.25
    roll = randint(-1, 1)
    casualty_rate += roll * 0.15
    roll = randint(-1, 1)
    casualty_rate += roll * 0.10
    
    return round(casualty_rate, 2)


def generate_random_sludgene_discount_percent():
    if randint(1, 3) == 1:
        # 1 to 20, skewing low
        return_discount_list = [randint(1,20), randint(1,20), randint(1,20)]
        return_discount_list.sort()
        
        return return_discount_list[0]
    else:
        return 0


def generate_random_sludgene_cost_type():
    return random.choice(["primary", "secondary", "hybrid"])

    
def generate_random_sludgene_resource_secreted():
    if randint(1, 10) == 1:
        resource_secreted_name = random.choice(["food", "ore", "wood", "mana"])
        if resource_secreted_name == "food":
            amount_secreted = round(randint(15, 18) / 10, 1)
        elif resource_secreted_name == "ore":
            amount_secreted = round(randint(11, 13) / 10, 1)
        elif resource_secreted_name == "wood":
            amount_secreted = round(randint(14, 17) / 10, 1)
        elif resource_secreted_name == "mana":
            amount_secreted = round(randint(8, 10) / 10, 1)
        else:
            amount_secreted = 0
    else:
        resource_secreted_name = "none"
        amount_secreted = 0
        
    return resource_secreted_name, amount_secreted
    

def generate_random_sludgene_upkeep_dict(upkeep_type, extra_sludge=0):
    upkeep_options = [
        {
            "goop": 3,
            "food": 1
        },
        {
            "sludge": 5,
            "food": 1
        },
        {
            "goop": 1.5,
            "sludge": 3,
        },
    ]
    
    for upkeep_option in upkeep_options:
        if extra_sludge > 0:
            if "sludge" in upkeep_option:
                upkeep_option["sludge"] += extra_sludge
            else:
                upkeep_option["sludge"] = extra_sludge
    
    if upkeep_type == "primary":
        return upkeep_options[0]
    elif upkeep_type == "secondary":
        return upkeep_options[1]
    else:
        return upkeep_options[2]
    

def create_random_sludgene(ruler: Dominion):
    name = get_sludgene_name()
    op = generate_random_sludgene_op_or_dp()
    dp = generate_random_sludgene_op_or_dp()
    return_ticks = generate_random_sludgene_return_ticks()
    casualty_rate = generate_random_sludgene_casualty_rate()
    resource_secreted_name, amount_secreted = generate_random_sludgene_resource_secreted()
    cost_type = generate_random_sludgene_cost_type()
    upkeep_type = generate_random_sludgene_cost_type()
    upkeep_dict = generate_random_sludgene_upkeep_dict(upkeep_type, amount_secreted > 0)
    discount_percent = generate_random_sludgene_discount_percent()
    
    cost_multiplier = (100 - discount_percent) / 100
    cost_dict = generate_unit_cost_dict(op, dp, "goop", "sludge", cost_type, casualty_rate, return_ticks, cost_multiplier)
    
    return Sludgene.objects.create(
        name=name,
        ruler=ruler,
        op=op,
        dp=dp,
        return_ticks=return_ticks,
        casualty_rate=casualty_rate,
        cost_type=cost_type,
        upkeep_type=upkeep_type,
        resource_secreted_name=resource_secreted_name,
        amount_secreted=amount_secreted,
        cost_dict=cost_dict,
        upkeep_dict=upkeep_dict,
        discount_percent=discount_percent,
    )
    
    
def breed_sludgenes(father: Sludgene, mother: Sludgene):
    if randint(1,3) == 1:
        op = random.choice([father.op, mother.op])
    else:
        op = randint(min(father.op, mother.op), max(father.op, mother.op))
    
    if randint(1,3) == 1:
        dp = random.choice([father.dp, mother.dp])
    else:
        dp = randint(min(father.dp, mother.dp), max(father.dp, mother.dp))
    
    if randint(1,3) == 1:
        return_ticks = min(father.return_ticks, mother.return_ticks)
    else:
        return_ticks = randint(min(father.return_ticks, mother.return_ticks), max(father.return_ticks, mother.return_ticks))
        
    if randint(1,3) == 1:
        casualty_rate = min(father.casualty_rate, mother.casualty_rate)
    else:
        casualty_rate = randint(min(father.casualty_rate, mother.casualty_rate) * 100, max(father.casualty_rate, mother.casualty_rate) * 100)
        casualty_rate = round_x_to_nearest_y(casualty_rate, 5) / 100
        
    cost_type = random.choice([father.cost_type, mother.cost_type])
    upkeep_type = random.choice([father.upkeep_type, mother.upkeep_type])
        
    if randint(1, 2) == 1:
        if randint(1, 2):
            resource_secreted_name = father.resource_secreted_name
            amount_secreted = father.amount_secreted
        else:
            resource_secreted_name = mother.resource_secreted_name
            amount_secreted = mother.amount_secreted
    else:
        resource_secreted_name = "none"
        amount_secreted = 0
        
    if randint(1, 2) == 1:
        discount_percent = randint(min(father.discount_percent, mother.discount_percent), max(father.discount_percent, mother.discount_percent))
    else:
        discount_percent = 0
        
    cost_multiplier = (100 - discount_percent) / 100
        
    return Sludgene.objects.create(
        name=get_sludgene_name(),
        ruler=father.ruler,
        op=op,
        dp=dp,
        return_ticks=return_ticks,
        casualty_rate=casualty_rate,
        cost_type=cost_type,
        upkeep_type=upkeep_type,
        resource_secreted_name=resource_secreted_name,
        amount_secreted=amount_secreted,
        cost_dict=generate_unit_cost_dict(op, dp, "goop", "sludge", cost_type, cost_multiplier=cost_multiplier),
        upkeep_dict=generate_random_sludgene_upkeep_dict(upkeep_type, amount_secreted > 0),
        discount_percent=discount_percent,
    )
        

def create_unit_from_sludgene(sludgene: Sludgene):
    name = get_sludgeling_name()
    current_names = []
    
    for unit in Unit.objects.filter(ruler=sludgene.ruler):
        current_names.append(unit.name)
    
    if len(current_names) < 30:
        while name in current_names:
            name = get_sludgeling_name()
    
    unit = Unit.objects.create(
        name=name,
        ruler=sludgene.ruler,
        op=sludgene.op,
        dp=sludgene.dp,
        cost_dict=sludgene.cost_dict,
        upkeep_dict=sludgene.upkeep_dict,
        perk_dict=sludgene.perk_dict,
    )
    
    give_unit_timer_template(unit)
    
    return unit


def create_magnum_goopus(dominion: Dominion, units_included_dict, encore=False):
    total_quantity = 0
    total_op = 0
    total_dp = 0
    sludge_upkeep = 0
    return_ticks = 1

    if encore:
        perk_dict = {"is_more_glorious": True}
    else:
        perk_dict = {"is_glorious": True}

    for unit_details_dict in units_included_dict.values():
        unit = get_unit_from_dict(unit_details_dict)
        quantity_included = unit_details_dict["quantity_sent"]
        
        if "sludge" in unit.cost_dict and quantity_included <= unit.quantity_at_home:
            total_quantity += quantity_included
            total_op += quantity_included * unit.op
            total_dp += quantity_included * unit.dp

            # if "food" in unit.upkeep_dict:
            #     food_upkeep += quantity_included * unit.upkeep_dict["food"]
            sludge_upkeep += quantity_included * 2
                
            try:
                return_ticks = max(return_ticks, unit.perk_dict["returns_in_ticks"])
            except:
                return_ticks = 12
                
            unit.lose(quantity_included)

    encore_suffixes = [" Mk II", " 2: Electric Goopaloo", " Remastered", ": the Remix", " 2", " Jr.", " Magnum Goopier"]

    if encore:
        name = f"Magnum Goopus{random.choice(encore_suffixes)}"
    else:
        name = "Magnum Goopus"
        
    if return_ticks < 12:
        perk_dict["returns_in_ticks"] = return_ticks

    dominion.perk_dict["masterpieces_to_create"] -= 1
    dominion.save()

    timer_template = generate_countdown_dict()

    return Unit.objects.create(
        ruler=dominion,
        name=name,
        op=total_op,
        dp=total_dp,
        upkeep_dict={
            # "food": food_upkeep,
            "sludge": sludge_upkeep,
        },
        perk_dict=perk_dict,
        is_trainable=False,
        quantity_at_home=1,
        training_dict=timer_template,
        returning_dict=timer_template,
    )
