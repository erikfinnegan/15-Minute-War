from maingame.models import Building, Round


def get_trade_value(resource_name):
    building = Building.objects.get(resource_produced_name=resource_name, ruler=None)
    return 1000 / building.amount_produced

    this_round = Round.objects.first()
    total_production = 0

    for dominion in Dominion.objects.all():
        total_production += dominion.get_production(resource_name)
    
    price_modifier = 1

    if total_production > 0 and resource_name in this_round.resource_bank_dict:
        price_modifier = 1 + ((this_round.resource_bank_dict[resource_name] / (total_production * 9)) * -0.2)

    if resource_name == "gold":
        trade_value = 10 * price_modifier
    else:
        building = Building.objects.get(resource_produced_name=resource_name, ruler=None)
        trade_value = (500 / building.amount_produced) * price_modifier

    trade_value = round(trade_value, 2)

    # if resource_name == "gems":
    #     trade_value *= 1.3

    return max(1, trade_value)


def update_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        if resource_name in round.trade_price_dict:
            current_value = round.trade_price_dict[resource_name]
            goal_value = get_trade_value(resource_name)
            
            if goal_value > current_value:
                new_value = min(goal_value, current_value * 1.01)
                round.trade_price_dict[resource_name] = new_value
                round.save()
            elif goal_value < current_value:
                new_value = max(goal_value, current_value / 1.01)
                round.trade_price_dict[resource_name] = new_value
                round.save()
        else:
            round.trade_price_dict[resource_name] = get_trade_value(resource_name)

        if resource_name not in round.base_price_dict:
            round.base_price_dict[resource_name] = get_trade_value(resource_name)

    round.save()