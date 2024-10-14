from random import randint
from maingame.models import Player, Round, Unit, Building, Battle, Event, Deity
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
        for player in Player.objects.all():
            if player.protection_ticks_remaining == 0:
                player.do_tick()
