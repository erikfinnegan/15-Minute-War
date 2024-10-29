from random import randint
from maingame.models import Dominion, Round, Unit, Building, Battle, Event, Deity
from django.db.models import Q


def normalize_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        round.resource_bank_dict[resource_name] *= 0.99

    round.save()


def do_global_tick():
    # check_victory()
    normalize_trade_prices()

    if Round.objects.first().allow_ticks:
        for dominion in Dominion.objects.all():
            if dominion.protection_ticks_remaining == 0:
                dominion.do_tick()
