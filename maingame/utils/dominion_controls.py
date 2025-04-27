import random
from maingame.formatters import generate_countdown_dict, get_goblin_ruler
from maingame.models import Dominion, Faction, Spell, Resource, Unit, Event, User, Building, UserSettings, MechModule
from maingame.utils.give_stuff import create_resource_for_dominion, give_dominion_module, give_dominion_spell, give_dominion_unit
from maingame.utils.utils import get_random_resource, update_available_discoveries


def create_faction_perk_dict(dominion: Dominion, faction: Faction):
    # dominion.perk_dict["book_of_grudges"] = {}
    dominion.perk_dict["aethertide_roll_history"] = []
    dominion.perk_dict["aethertide_net_ticks"] = 0

    if faction.name == "dwarf":
        dominion.perk_dict["book_of_grudges"] = {}
        # dominion.perk_dict["grudge_page_multiplier"] = 1.5
    elif faction.name == "blessed order":
        dominion.perk_dict["heretics_per_hundred_acres_per_tick"] = 1
        dominion.perk_dict["inquisition_rate"] = 0
        dominion.perk_dict["order_cant_attack_ticks_left"] = 0
        dominion.perk_dict["martyr_cost"] = 500
        dominion.perk_dict["corruption"] = 0
    elif faction.name == "sludgeling":
        dominion.perk_dict["splices"] = 3
        dominion.perk_dict["custom_units"] = 1
        dominion.perk_dict["max_custom_units"] = 5
        # dominion.perk_dict["experiments_done"] = 0
        dominion.perk_dict["recycling_refund"] = 0.8
        dominion.perk_dict["masterpieces_to_create"] = 0
        dominion.perk_dict["get_sludgenes"] = True
    elif faction.name == "goblin":
        dominion.perk_dict["rats_per_acre_per_tick"] = 0.3334
        dominion.perk_dict["goblin_ruler"] = get_goblin_ruler()
        dominion.perk_dict["rulers_favorite_resource"] = get_random_resource(dominion).name
    elif faction.name == "biclops":
        dominion.perk_dict["partner_patience"] = 36
        dominion.perk_dict["partner_attack_on_sight"] = False
        dominion.perk_dict["bonus_determination"] = 0
        dominion.perk_dict["percent_complacency_to_determination_when_hit"] = 50
    elif faction.name == "gnomish special forces":
        dominion.perk_dict["infiltration_dict"] = {}
    elif faction.name == "mecha-dragon":
        dominion.perk_dict["capacity_max"] = 1
        dominion.perk_dict["capacity_used"] = 0
        dominion.perk_dict["capacity_upgrade_cost"] = 100000
    elif faction.name == "aethertide corsairs":
        dominion.perk_dict["aethertide_coefficient"] = 0
        dominion.perk_dict["aethertide_coefficient_max"] = 18 + random.randint(-3, 3)
        dominion.perk_dict["aethertide_max_chance"] = 50
        dominion.perk_dict["aethertide_increase_next_tick"] = True
        dominion.perk_dict["double_ticks_and_op_penalty"] = True
        dominion.perk_dict["ticks_until_next_share_change"] = 0

    dominion.save()


def initialize_dominion(user: User, faction: Faction, display_name):
    dominion = Dominion.objects.create(
        associated_user=user, 
        name=display_name, 
        faction_name=faction.name,
        invasion_consequences=faction.invasion_consequences,
    )

    update_available_discoveries(dominion)

    for unit in Unit.objects.filter(ruler=None, faction=faction):
        give_dominion_unit(dominion, unit)

    for module in MechModule.objects.filter(ruler=None, faction=faction):
        give_dominion_module(dominion, module)

    for building_name in faction.starting_buildings:
        base_building = Building.objects.get(name=building_name, ruler=None)
        dominions_building = base_building
        dominions_building.pk = None
        dominions_building.ruler = dominion
        dominions_building.save()

        if dominions_building.resource_produced_name:
            create_resource_for_dominion(dominions_building.resource_produced_name, dominion)

    for unit in Unit.objects.filter(ruler=dominion):
        for perk_name in unit.perk_dict:
            if perk_name[-9:] == "_per_tick":
                create_resource_for_dominion(perk_name[:-9], dominion)

    if dominion.faction_name == "blessed order":
        create_resource_for_dominion("heretics", dominion)
    elif dominion.faction_name == "goblin":
        create_resource_for_dominion("rats", dominion)
    elif dominion.faction_name == "mecha-dragon":
        mechadragon = Unit.objects.get(ruler=dominion, name="Mecha-Dragon")
        mechadragon.gain(1)
    elif dominion.faction_name == "aethertide corsairs":
        plunder = Resource.objects.get(ruler=dominion, name="plunder")
        plunder.gain(7777)

    for spell in Spell.objects.filter(ruler=None, is_starter=True):
        give_dominion_spell(dominion, spell)

    dominion.primary_resource_name = faction.primary_resource_name
    dominion.primary_resource_per_acre = faction.primary_resource_per_acre
    dominion.incoming_acres_dict = generate_countdown_dict()

    user_settings, _ = UserSettings.objects.get_or_create(associated_user=user)

    event = Event.objects.create(
        reference_id=dominion.id, 
        reference_type="signup", 
        category="Signup",
        message_override=f"{user_settings.display_name} has created a {faction} dominion named {dominion}"
    )

    dominion.save()

    create_faction_perk_dict(dominion, faction)

    return dominion


def abandon_dominion(dominion: Dominion):
    event = Event.objects.create(
        reference_id=dominion.id, 
        reference_type="abandon", 
        category="Abandon",
        message_override=f"{dominion} has been abandoned by {dominion.rulers_display_name}"
    )

    dominion.is_abandoned = True
    dominion.associated_user = None
    dominion.name += " (abandoned)"
    dominion.save()


def delete_dominion(dominion: Dominion):
    Resource.objects.filter(ruler=dominion).delete()
    Building.objects.filter(ruler=dominion).delete()
    Unit.objects.filter(ruler=dominion).delete()
    MechModule.objects.filter(ruler=dominion).delete()
    Spell.objects.filter(ruler=dominion).delete()
    Event.objects.filter(reference_id=dominion.id, reference_type="signup").delete()
    
    dominion.delete()