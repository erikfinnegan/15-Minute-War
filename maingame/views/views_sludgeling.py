from random import randint
import random

from django.shortcuts import render, redirect
from django.contrib import messages

from maingame.formatters import get_sludgeling_name
from maingame.models import Dominion, Unit, Round, Resource
from maingame.utils.utils import create_magnum_goopus, create_unit_dict, round_x_to_nearest_y


def experimentation(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    try:
        masterpieces_available = dominion.perk_dict["masterpieces_to_create"]
    except:
        return redirect("world")

    if dominion.faction_name != "sludgeling":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    research_cost = int(dominion.perk_dict["experiment_cost_dict"]["research_per_acre"] * dominion.acres)
    sludge_cost = int(dominion.perk_dict["experiment_cost_dict"]["sludge_per_acre"] * dominion.acres)

    experimental_units = []

    for unit in Unit.objects.filter(ruler=dominion):
        if "sludge" in unit.cost_dict:
            experimental_units.append(unit)

    latest_experiment_unit = Unit.objects.filter(id=dominion.perk_dict["latest_experiment_id"]).first()
    
    context = {
        "research_cost": research_cost,
        "sludge_cost": sludge_cost,
        "allow_new_experiments": dominion.perk_dict["custom_units"] < dominion.perk_dict["max_custom_units"],
        "latest_experiment": dominion.perk_dict["latest_experiment"],
        "latest_experiment_unit": latest_experiment_unit,
        "experimental_units": experimental_units,
        "has_experimental_units": dominion.perk_dict["custom_units"] > 0,
        "units": dominion.sorted_units,
        "masterpieces_available": masterpieces_available,
    }
    
    return render(request, "maingame/faction_pages/experimentation.html", context)


def generate_experiment(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("experimentation")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("experimentation")

    if dominion.faction_name != "sludgeling":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    experiment_research_cost = int(dominion.perk_dict["experiment_cost_dict"]["research_per_acre"] * dominion.acres)
    experiment_sludge_cost = int(dominion.perk_dict["experiment_cost_dict"]["sludge_per_acre"] * dominion.acres)

    players_research = Resource.objects.get(ruler=dominion, name="research")
    players_sludge = Resource.objects.get(ruler=dominion, name="sludge")

    if dominion.perk_dict["free_experiments"] == 0:
        if experiment_research_cost > players_research.quantity or experiment_sludge_cost > players_sludge.quantity:
            messages.error(request, f"You can't afford this experiment")
            return redirect("experimentation")
    
    try:
        old_experiment = Unit.objects.get(id=dominion.perk_dict["latest_experiment_id"])
        old_experiment.delete()
    except:
        pass
    
    if dominion.perk_dict["free_experiments"] == 0:
        players_research.quantity -= experiment_research_cost
        players_research.save()

        players_sludge.quantity -= experiment_sludge_cost
        players_sludge.save()
    else:
        dominion.perk_dict["free_experiments"] -= 1
        dominion.save()
    
    past_experiments = dominion.perk_dict["experiments_done"]

    low_gold_cost = False
    low_sludge_cost = False
    low_upkeep = False
    high_op = False
    high_dp = False

    bonus_roll = randint(1,6)
    low_gold_cost = bonus_roll == 1
    low_sludge_cost = bonus_roll == 2
    low_upkeep = bonus_roll == 3
    high_op = bonus_roll == 4
    high_dp = bonus_roll == 5

    if past_experiments >= randint(1, 100):
        second_bonus_roll = randint(1,5)
        low_gold_cost = second_bonus_roll == 1 or low_gold_cost
        low_sludge_cost = second_bonus_roll == 2 or low_sludge_cost
        low_upkeep = second_bonus_roll == 3 or low_upkeep
        high_op = second_bonus_roll == 4 or high_op
        high_dp = second_bonus_roll == 5 or high_dp

    malus_roll = randint(1,6)
    high_gold_cost = malus_roll == 1
    high_sludge_cost = malus_roll == 2
    high_upkeep = malus_roll == 3
    low_op = malus_roll == 4
    low_dp = malus_roll == 5

    if high_gold_cost and low_gold_cost:
        high_gold_cost = False
        low_gold_cost = False

    if high_sludge_cost and low_sludge_cost:
        high_sludge_cost = False
        low_sludge_cost = False

    if high_upkeep and low_upkeep:
        high_upkeep = False
        low_upkeep = False

    if high_op and low_op:
        high_op = False
        low_op = False

    if high_dp and low_dp:
        high_dp = False
        low_dp = False

    min_roll_for_extra_power = 1

    for _ in range(past_experiments):
            min_roll_for_extra_power += (100 - min_roll_for_extra_power) / 75

    min_roll_for_extra_power = int(min_roll_for_extra_power)

    op = randint(1,10)
    extra_op = randint(1,2) == 1

    if extra_op and past_experiments >= 10:
        roll = randint(min_roll_for_extra_power, 100)

        while roll >= 100 and extra_op:
            op += randint(1, 4)
            roll = randint(min_roll_for_extra_power, 100)
            extra_op = randint(1,2) == 1

    dp = randint(1,10)
    extra_dp = randint(1,2) == 1

    if extra_dp and past_experiments >= 10:
        roll = randint(min_roll_for_extra_power, 100)

        while roll >= 100 and extra_dp:
            dp += randint(1, 4)
            roll = randint(min_roll_for_extra_power, 100)
            extra_dp = randint(1,2) == 1

    if high_op:
        op *= 2
    elif low_op:
        op = int(op/2)
    
    if high_dp:
        dp *= 2
    elif low_dp:
        dp = int(dp/2)

    perk_dict = {}
    has_perks = False

    if "Speedlings" in dominion.learned_discoveries and randint(1,100) <= 33:
        perk_dict["returns_in_ticks"] = 8
        has_perks = True
    
    # Toughlings and Cheaplings modify the same perk, so we randomize which order to check in because we're too lazy to do this intelligently
    if randint(1,2) == 1:
        if "Cheaplings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 2
            has_perks = True

        if "Toughlings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 0.5
            has_perks = True
    else:
        if "Toughlings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 0.5
            has_perks = True

        if "Cheaplings" in dominion.learned_discoveries and randint(1,100) <= 33:
            perk_dict["casualty_multiplier"] = 2
            has_perks = True

    cost_type = random.choice(["gold", "other", "hybrid"])
    cost_basis_power = max(op * 1.3, dp)
    is_offensive_unit = cost_basis_power != dp

    goldunit_gold_cost = (cost_basis_power * 300) - 600
    goldunit_sludge_cost = cost_basis_power * 70 * 1.5
    otherunit_sludge_cost = (cost_basis_power * 6 * 70) - (10 * 70)

    if cost_basis_power < 3:
        goldunit_gold_cost = cost_basis_power * 100
        otherunit_sludge_cost = cost_basis_power * 186

    if cost_type == "gold":
        gold_cost = goldunit_gold_cost
        sludge_cost = goldunit_sludge_cost
    elif cost_type == "other":
        gold_cost = 0
        sludge_cost = otherunit_sludge_cost
    else:
        gold_cost = int(goldunit_gold_cost / 2)
        sludge_cost = int((goldunit_sludge_cost + otherunit_sludge_cost) / 2)

    dont_divide_by_zero = 1 if dp == 0 else dp
    bad_turtle_multiplier = (op / 200) / dont_divide_by_zero

    if op > (dp * 2):
        gold_cost *= 1 - (bad_turtle_multiplier)

    multiplier = randint(1,15)
    high_mult = 1 + (multiplier/100)
    low_mult = 1 - (multiplier/100)

    if high_gold_cost:
        gold_cost = int(gold_cost * high_mult)
    elif low_gold_cost:
        gold_cost = int(gold_cost * low_mult)

    if high_sludge_cost:
        sludge_cost = int(sludge_cost * high_mult)
    elif low_sludge_cost:
        sludge_cost = int(sludge_cost * low_mult)

    if "returns_in_ticks" in perk_dict:
        multiplier_base = randint(10, 20) / 100
        gold_cost *= 1 + multiplier_base
        sludge_cost *= 1 + multiplier_base

    if "casualty_multiplier" in perk_dict:
        casualty_based_multiplier = 1

        if perk_dict["casualty_multiplier"] == 2:
            if is_offensive_unit:
                dp_op_ratio = dp / op
                base_discount = int(randint(40, 50) * (1 - dp_op_ratio))
                casualty_based_multiplier = min((1 - (base_discount / 100)), randint(90, 95))
            else:
                casualty_based_multiplier = randint(90, 95) / 100
        elif perk_dict["casualty_multiplier"] == 0.5:
            if is_offensive_unit:
                casualty_based_multiplier = 1 + randint(20, 30) / 100
            else:
                casualty_based_multiplier = 1 + randint(5, 10) / 100

        gold_cost *= casualty_based_multiplier
        sludge_cost *= casualty_based_multiplier

    # No more cost modifiers after this. It's time to start rounding off.
    if gold_cost > 1000:
        gold_cost = round_x_to_nearest_y(gold_cost, 50)
    else:
        gold_cost = round_x_to_nearest_y(gold_cost, 25)

    if sludge_cost > 1000:
        sludge_cost = round_x_to_nearest_y(sludge_cost, 50)
    else:
        sludge_cost = round_x_to_nearest_y(sludge_cost, 25)

    gold_cost = int(gold_cost)
    sludge_cost = int(sludge_cost)

    if high_upkeep:
        if randint(1,2) == 1:
            upkeep_dict = {
                "gold": 4,
                "food": 1,
            }
        else:
            upkeep_dict = {
                "gold": 3,
                "food": 3,
            }
    elif low_upkeep:
        if randint(1,2) == 1:
            upkeep_dict = {
                "gold": 2,
                "food": 1,
                "sludge": 1,
            }
        else:
            upkeep_dict = {
                "gold": 3,
            }
    else:
        upkeep_dict = {
                "gold": 3,
                "food": 1,
            }
    
    current_names = []

    for unit in Unit.objects.filter(ruler=dominion):
        current_names.append(unit.name)

    name = get_sludgeling_name()

    while name in current_names:
        name = get_sludgeling_name()

    cost_per_op = int(((gold_cost * 1.08) + sludge_cost) / max(op, 1))
    cost_per_dp = int(((gold_cost * 1.08) + sludge_cost) / max(dp, 1))

    op_per_normalized_upkeep = (op * 3) / upkeep_dict["gold"]
    dp_per_normalized_upkeep = (dp * 3) / upkeep_dict["gold"]

    if gold_cost == 0:
        cost_dict = {
            "sludge": sludge_cost,
        }
    else:
        cost_dict = {
            "gold": gold_cost,
            "sludge": sludge_cost,
        }

    timer_template = {
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
    }

    latest_experiment = Unit.objects.create(
        name=name,
        op=op,
        dp=dp,
        cost_dict=cost_dict,
        upkeep_dict=upkeep_dict,
        perk_dict=perk_dict,
        training_dict=timer_template,
        returning_dict=timer_template,
    )

    dominion.perk_dict["latest_experiment_id"] = latest_experiment.id

    dominion.perk_dict["latest_experiment"] = {
        "should_display": True,
        "name": name,
        "op": op,
        "dp": dp,
        "cost_dict": cost_dict,
        "upkeep_dict": upkeep_dict,
        "perk_dict": perk_dict,
        "has_perks": has_perks,
        "cost_per_op": cost_per_op,
        "cost_per_dp": cost_per_dp,
        "op_per_normalized_upkeep": op_per_normalized_upkeep,
        "dp_per_normalized_upkeep": dp_per_normalized_upkeep,
    }

    dominion.perk_dict["experiments_done"] += 1
    dominion.save()

    return redirect("experimentation")


def approve_experiment(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("experimentation")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("experimentation")

    if dominion.faction_name != "sludgeling":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    elif dominion.perk_dict["custom_units"] >= dominion.perk_dict["max_custom_units"]:
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    dominion.perk_dict["latest_experiment"]["should_display"] = False
    dominion.perk_dict["custom_units"] += 1
    dominion.save()

    try:
        old_experiment = Unit.objects.get(id=dominion.perk_dict["latest_experiment_id"])
        old_experiment.delete()
    except:
        pass

    unit_data = dominion.perk_dict["latest_experiment"]

    if unit_data["name"] == "":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")

    timer_template = {
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
    }

    Unit.objects.create(
        name=unit_data["name"],
        op=unit_data["op"],
        dp=unit_data["dp"],
        cost_dict=unit_data["cost_dict"],
        upkeep_dict=unit_data["upkeep_dict"],
        perk_dict=unit_data["perk_dict"],
        ruler=dominion,
        training_dict=timer_template,
        returning_dict=timer_template,
    )

    return redirect("experimentation")


def terminate_experiment(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("experimentation")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("experimentation")

    if dominion.faction_name != "sludgeling":
        messages.error(request, f"Go swim in a cesspool")
        return redirect("buildings")
    
    unit = Unit.objects.get(id=request.POST["experiment_to_terminate"])

    if unit.quantity_returning > 0:
        messages.error(request, f"Can't terminate experiments while units are returning")
        return redirect("experimentation")
    elif unit.quantity_in_training > 0:
        messages.error(request, f"Can't terminate experiments while units are in training")
        return redirect("experimentation")

    gold_refund = 0
    sludge_refund = 0

    if "gold" in unit.cost_dict:
        gold_refund = int(unit.quantity_at_home * unit.cost_dict["gold"] * dominion.perk_dict["recycling_refund"])

    if "sludge" in unit.cost_dict:
        sludge_refund = int(unit.quantity_at_home * unit.cost_dict["sludge"] * dominion.perk_dict["recycling_refund"])
    
    gold = Resource.objects.get(ruler=dominion, name="gold")
    gold.quantity += gold_refund
    gold.save()

    sludge = Resource.objects.get(ruler=dominion, name="sludge")
    sludge.quantity += sludge_refund
    sludge.save()

    messages.success(request, f"Terminated the {unit.name} experiment, regained {gold_refund:2,} gold and {sludge_refund:2,} sludge from recycling {unit.quantity_at_home:2,} units")

    unit.ruler = None
    unit.save()

    dominion.perk_dict["custom_units"] -= 1
    dominion.save()
    
    return redirect("experimentation")


def submit_masterpiece(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    try:
        masterpieces_available = dominion.perk_dict["masterpieces_to_create"]
    except:
        return redirect("world")
    
    if masterpieces_available < 1:
        messages.error(request, f"Don't be greedy")
        return redirect("experimentation")

    unit_dict, _ = create_unit_dict(request.POST, "combine_")

    is_encore = False

    for unit in Unit.objects.filter(ruler=dominion):
        if "is_more_glorious" in unit.perk_dict:
            messages.error(request, f"Don't be greedy")
            return redirect("experimentation")
        elif "is_glorious" in unit.perk_dict:
            is_encore = True

    create_magnum_goopus(dominion, unit_dict, is_encore)

    messages.success(request, f"Behold your masterpiece!")
    return redirect("military")
