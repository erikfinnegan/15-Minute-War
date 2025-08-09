from random import randint
from maingame.formatters import generate_countdown_dict
from maingame.models import Dominion, Round, Resource, Unit, Event
from datetime import datetime
from django.utils.timezone import make_aware
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
    this_round = Round.objects.first()
    resource_bugs = False
    unit_bugs = False
    acre_bugs = False

    for resource in Resource.objects.all():
        if resource.net != resource.quantity:
            resource_bugs = True
            this_round.bugs.append(f"{start_timestamp.strftime('%H:%M:%S')}: {resource.ruler}'s {resource.name} expected {resource.net} -vs- current {resource.quantity}")

    for unit in Unit.objects.all():
        if unit.quantity_total != unit.net:
            unit_bugs = True
            this_round.bugs.append(f"{start_timestamp.strftime('%H:%M:%S')}: {unit.ruler}'s {unit.name} expected {unit.net} -vs- current {unit.quantity_total}")

    for dominion in Dominion.objects.all():
        if dominion.net_acres + 500 != dominion.acres:
            acre_bugs = True
            this_round.bugs.append(f"{start_timestamp.strftime('%H:%M:%S')}: {dominion} acres expected {dominion.net_acres + 500} -vs- current {dominion.acres}")

    has_bugs = resource_bugs or unit_bugs or acre_bugs

    if has_bugs:
        print("We got bugs!")
    else:
        print("No bugs this tick")

    this_round.has_bugs = has_bugs
    this_round.save()
    
    end_timestamp = datetime.now(ZoneInfo('America/New_York'))
    print(f"Bug audit lasted:", round((end_timestamp - start_timestamp).total_seconds(), 3))


def do_global_tick():
    start_timestamp = datetime.now(ZoneInfo('America/New_York'))
    print("Start global tick", start_timestamp.strftime('%H:%M:%S'))
    this_round = Round.objects.first()
    this_round.is_ticking = True
    this_round.save()

    if not this_round.has_ended:
        
        audit_for_bugs()
        all_dominions = Dominion.objects.all()

        if this_round.allow_ticks:
            print("-----")
            for dominion in all_dominions:
                if dominion.is_oop and not dominion.is_abandoned:
                    if dominion.last_tick_played + 96 < this_round.ticks_passed:
                        dominion.protection_ticks_remaining = 1
                        dominion.save()
                    else:
                        number_of_ticks = get_number_of_times_to_tick(dominion, start_timestamp)
                        
                        dominion.perk_dict["aethertide_net_ticks"] += (number_of_ticks - 1)
                        dominion.save()

                        for _ in range(number_of_ticks):
                            start_tick_timestamp = datetime.now(ZoneInfo('America/New_York'))
                            dominion.do_tick()
                            end_tick_timestamp = datetime.now(ZoneInfo('America/New_York'))
                            print(f"{dominion.name} {dominion.faction_name} tick lasted:", round((end_tick_timestamp - start_tick_timestamp).total_seconds(), 3))
            
            print("-----")
            
            # This has to be a separate loop or else multiple auto attacks against the same target get fucked up
            for dominion in all_dominions.order_by("?"):
                if dominion.faction_name == "biclops" and not dominion.is_abandoned: 
                    do_biclops_partner_attack(dominion)

                if "biclopean_ambition_ticks_remaining" in dominion.perk_dict and dominion.can_attack:
                    do_forced_attack(dominion, use_always_dies_units=False)
            
            print("Dominions done", datetime.now(ZoneInfo('America/New_York')).strftime('%H:%M:%S'))

        now = datetime.now(ZoneInfo('America/New_York'))

        if not this_round.start_time:
            pass
        elif now > this_round.start_time and not this_round.has_started:
            this_round.has_started = True
        elif this_round.has_started:
            this_round.ticks_passed += 1

            if this_round.ticks_passed >= this_round.ticks_to_end:
                this_round.has_ended = randint(1,100) <= this_round.percent_chance_for_round_end
                
                if this_round.has_ended:
                    event = Event.objects.create(
                        reference_id=1, 
                        reference_type="round_end", 
                        category="Round end",
                        message_override=f"The round has ended."
                    )

        this_round.save()

        if this_round.has_ended:
            for dominion in all_dominions:
                dominion.gain_acres(dominion.incoming_acres)
                dominion.incoming_acres_dict = generate_countdown_dict()
                dominion.save()

    end_timestamp = datetime.now(ZoneInfo('America/New_York'))
    print("End global tick", end_timestamp.strftime('%H:%M:%S'))

    delta = end_timestamp - start_timestamp
    printable_delta = str(delta)
    print(f"Tick processing time: {printable_delta}")

    this_round.is_ticking = False
    
    if not this_round.has_ended:
        this_round.last_tick_finished = make_aware(datetime.now())
        
    this_round.save()