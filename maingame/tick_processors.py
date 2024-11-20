from maingame.models import Dominion, Round
from datetime import datetime
from zoneinfo import ZoneInfo

def normalize_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        round.resource_bank_dict[resource_name] *= 0.99

    round.save()


def do_global_tick():
    print("Start global tick", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))
    round = Round.objects.first()

    if not round.has_ended:
        now = datetime.now(ZoneInfo('America/New_York'))

        if not round.start_time:
            pass
        elif now > round.start_time and not round.has_started:
            round.has_started = True
        elif round.has_started:
            round.ticks_passed += 1

            if round.ticks_passed >= round.ticks_to_end:
                round.has_ended = True

        round.save()

        print("Round management done, starting trade prices", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))

        normalize_trade_prices()

        print("Trade prices done, starting dominion ticks", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))

        if Round.objects.first().allow_ticks:
            for dominion in Dominion.objects.all():
                print(f"Starting {dominion.name}", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))
                if dominion.protection_ticks_remaining == 0:
                    dominion.do_tick()
            
            print("Dominions done", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))
