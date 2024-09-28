from random import randint
from maingame.formatters import create_or_add_to_key
from maingame.models import Player, Region, Round, Unit, Building, Battle, Event, Deity
from maingame.utils import generate_region
from django.db.models import Q


def check_victory():
    for player in Player.objects.all():
        if player.resource_dict["👑"] >= 1000:
            round = Round.objects.first()
            round.winner = player
            round.has_ended = True
            round.save()


def do_invasion(region: Region):
    ruler_power = {}
    unit_casualties_dict = {}

    for unit_id, quantity in region.units_here_dict.items():
        unit = Unit.objects.get(id=unit_id)

        if unit.ruler == region.ruler:
            create_or_add_to_key(ruler_power, str(unit.ruler.id), (quantity * unit.dp) + 0.01)  # Ties go to defender
        else:
            create_or_add_to_key(ruler_power, str(unit.ruler.id), (quantity * unit.op))

    if region.ruler == None and len(ruler_power.keys()) == 1:
        new_ruler_id = int(list(ruler_power)[0])
        player = Player.objects.get(id=new_ruler_id)
        region.ruler = player
        region.invasion_this_tick = False
        region.save()
        event = Event.objects.create(reference_id=region.id, reference_type="colonize", icon="🚩")
        event.notified_players.add(player)
        event.save()
        player.has_unread_events = True
        player.save()
        return

    battle = Battle.objects.create(target=region, units_involved_dict=region.units_here_dict.copy(), original_ruler=region.ruler, dp=region.defense)
    event = Event.objects.create(reference_id=battle.id, reference_type="battle", extra_text=f"{battle.dp} DP")

    winner_id = 0
    highest_power = 0
    highest_invader_power = 0

    for ruler_id, power in ruler_power.items():
        player = Player.objects.get(id=ruler_id)
        event.notified_players.add(player)
        player.has_unread_events = True
        player.save()

        if power > highest_power:
            winner_id = ruler_id
            highest_power = power

        if ruler_id != region.ruler.id and power > highest_invader_power:
            highest_invader_power = power

        if int(ruler_id) != region.ruler.id:
            battle.attackers.add(player)

    winner = Player.objects.get(id=winner_id)
    units_here_dict_clone = region.units_here_dict.copy()

    for unit_id, quantity in units_here_dict_clone.items():
        unit = Unit.objects.get(id=unit_id)
        defensive_casualties_for_this_unit = int(0.05 * region.units_here_dict[unit_id])
        offensive_casualties_for_this_unit = int(0.1 * region.units_here_dict[unit_id])

        if unit.ruler == region.ruler and ruler_power[str(unit.ruler.id)] <= 1.25 * highest_invader_power:
            unit_casualties_dict[unit.id] = defensive_casualties_for_this_unit
            region.units_here_dict[unit_id] -= defensive_casualties_for_this_unit
        else:
            unit_casualties_dict[unit.id] = offensive_casualties_for_this_unit
            region.units_here_dict[unit_id] -= offensive_casualties_for_this_unit

        if unit.ruler != winner:
            survivors_to_each_region = int((quantity - defensive_casualties_for_this_unit) / Region.objects.filter(~Q(id=region.id), ruler=unit.ruler).count())

            for retreat_region in Region.objects.filter(ruler=unit.ruler):
                retreat_region.units_here_dict = create_or_add_to_key(retreat_region.units_here_dict, unit_id, survivors_to_each_region)
                retreat_region.save()
            
            del region.units_here_dict[unit_id]

    for building in Building.objects.filter(region=region):
        building.ruler = winner
        building.save()

    battle.casualties_dict = unit_casualties_dict
    battle.winner = winner
    battle.save()

    if battle.winner == region.ruler:
        event.icon = "🛡"
    else:
        event.icon = "🗡"

    event.save()

    region.ruler = winner
    region.invasion_this_tick = False
    region.save()


def discover_regions():
    total_defense = 0
    
    for region in Region.objects.all():
        total_defense += region.defense

    average_defense = total_defense / Region.objects.count()
    low_defense_regions = 0
    
    for region in Region.objects.all():
        if region.defense < average_defense / 3:
            low_defense_regions += 1

        if region.ruler and region.ruler.protection_ticks_remaining > 0:
            low_defense_regions -= 1

    if randint(1,100) <= 20 / (low_defense_regions + 1):
        generate_region()


def do_deities():
    for deity in Deity.objects.all():
        if deity.favored_player:
            favored_player = deity.favored_player
            if deity.icon == "📈" and deity.favored_player.resource_dict["🪙"]:
                favored_player.resource_dict["🪙"] = int(favored_player.resource_dict["🪙"] * 1.01)
                favored_player.save()
            elif deity.icon == "🍄":
                if Unit.objects.filter(name="tendril of unity", ruler=favored_player).count() == 0:
                    base_tendril_unit = Unit.objects.get(name="tendril of unity", ruler=None)
                    players_unit = base_tendril_unit
                    players_unit.pk = None
                    players_unit.ruler = favored_player
                    players_unit.save()
                
                players_tendril = Unit.objects.get(name="tendril of unity", ruler=favored_player)
                sacred_sites = Region.objects.filter(ruler=favored_player, deity=deity).count()
                players_tendril.quantity_marshaled += int(sacred_sites / 2)
                players_tendril.save()


def do_global_tick():
    check_victory()

    if Round.objects.first().allow_ticks:
        for player in Player.objects.all():
            if player.protection_ticks_remaining == 0:
                player.do_tick()

    for region in Region.objects.filter(invasion_this_tick=True):
        do_invasion(region)

    do_deities()
    discover_regions()