from random import randint
from maingame.models import Dominion, Round
from datetime import datetime
from zoneinfo import ZoneInfo

from maingame.utils.invasion import do_biclops_partner_attack, do_forced_attack

def normalize_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        round.resource_bank_dict[resource_name] *= 0.99

    round.save()


def do_global_tick():
    print("Start global tick", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))
    round = Round.objects.first()
    round.is_ticking = True
    round.save()

    if not round.has_ended:
        # print("Starting trade prices", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))

        # update_trade_prices()
        # normalize_trade_prices()

        # print("Trade prices done, starting dominion ticks", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))

        if Round.objects.first().allow_ticks:
            for dominion in Dominion.objects.all():
                if dominion.is_oop and not dominion.is_abandoned:
                    dominion.do_tick()

            # This has to be a separate loop or else multiple auto attacks against the same target get fucked up
            for dominion in Dominion.objects.all().order_by("?"):
                if dominion.faction_name == "biclops" and not dominion.is_abandoned: 
                    do_biclops_partner_attack(dominion)

                if "biclopean_ambition_ticks_remaining" in dominion.perk_dict and dominion.can_attack:
                    do_forced_attack(dominion, use_always_dies_units=False)
            
            print("Dominions done", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))

        now = datetime.now(ZoneInfo('America/New_York'))

        if not round.start_time:
            pass
        elif now > round.start_time and not round.has_started:
            round.has_started = True
        elif round.has_started:
            round.ticks_passed += 1

            if round.ticks_passed >= round.ticks_to_end:
                round.has_ended = randint(1,100) <= round.percent_chance_for_round_end

        round.save()

        if round.has_ended:
            for dominion in Dominion.objects.all():
                dominion.acres += dominion.incoming_acres
                dominion.incoming_acres_dict = {
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
                dominion.save()

        print("Round management done", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))

    round.is_ticking = False
    round.save()