from random import randint
from maingame.formatters import generate_countdown_dict
from maingame.models import Dominion, Round, Resource, Unit
from datetime import datetime
from zoneinfo import ZoneInfo

from maingame.utils.invasion import do_biclops_partner_attack, do_forced_attack
from maingame.utils.utils_aethertide_corsairs import get_number_of_times_to_tick

def normalize_trade_prices():
    round = Round.objects.first()

    for resource_name in round.resource_bank_dict:
        round.resource_bank_dict[resource_name] *= 0.99

    round.save()


def audit_for_bugs():
    start_timestamp = datetime.now(ZoneInfo('America/New_York'))
    round = Round.objects.first()
    resource_bugs = False
    unit_bugs = False
    acre_bugs = False

    for resource in Resource.objects.all():
        if resource.net != resource.quantity:
            resource_bugs = True
            round.bugs.append(f"{start_timestamp.strftime('%H:%M:%S')}: {resource.ruler}'s {resource.name} expected {resource.net} -vs- current {resource.quantity}")

    for unit in Unit.objects.all():
        if unit.quantity_trained_and_alive != unit.net:
            unit_bugs = True
            round.bugs.append(f"{start_timestamp.strftime('%H:%M:%S')}: {unit.ruler}'s {unit.name} expected {unit.net} -vs- current {unit.quantity_trained_and_alive}")

    for dominion in Dominion.objects.all():
        if dominion.net_acres + 500 != dominion.acres:
            acre_bugs = True
            round.bugs.append(f"{start_timestamp.strftime('%H:%M:%S')}: {dominion} acres expected {dominion.net_acres + 500} -vs- current {dominion.acres}")

    has_bugs = resource_bugs or unit_bugs or acre_bugs

    if has_bugs:
        print("We got bugs!")
    else:
        print("No bugs this tick")

    round.has_bugs = has_bugs
    round.save()


def do_global_tick():
    start_timestamp = datetime.now(ZoneInfo('America/New_York'))
    print("Start global tick", start_timestamp.strftime('%H:%M:%S'))
    round = Round.objects.first()
    round.is_ticking = True
    round.save()

    if not round.has_ended:
        audit_for_bugs()

        if Round.objects.first().allow_ticks:
            for dominion in Dominion.objects.all():
                if dominion.is_oop and not dominion.is_abandoned:
                    number_of_ticks = get_number_of_times_to_tick(dominion, start_timestamp)

                    for _ in range(number_of_ticks):
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
                dominion.gain_acres(dominion.incoming_acres)
                dominion.incoming_acres_dict = generate_countdown_dict()
                dominion.save()

    end_timestamp = datetime.now(ZoneInfo('America/New_York'))
    print("End global tick", end_timestamp.strftime('%H:%M:%S'))

    delta = end_timestamp - start_timestamp
    printable_delta = str(delta)
    print(f"Tick processing time: {printable_delta}")

    round.is_ticking = False
    round.save()