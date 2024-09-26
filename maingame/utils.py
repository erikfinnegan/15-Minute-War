from random import randint, choice

from maingame.formatters import create_or_add_to_key
from maingame.models import Terrain, Unit, BuildingType, Player, Faction, Region, Journey, Building, Deity, Event
from django.contrib.auth.models import User
from django.db.models import Q


def assign_faction(player: Player, faction: Faction):
    for unit in Unit.objects.filter(faction_for_which_is_default=faction, ruler=None):
        players_unit = unit
        players_unit.pk = None
        players_unit.ruler = player
        players_unit.save()

        player.adjust_resource("👑", 0)

        for resource in players_unit.cost_dict:
            player.adjust_resource(resource, 0)

    for building_type in faction.starter_building_types.all():
        players_building_type = building_type
        players_building_type.pk = None
        players_building_type.ruler = player
        players_building_type.save()

        if players_building_type.amount_produced > 0:
            player.adjust_resource(players_building_type.resource_produced, 0)

    player.upgrade_cost = faction.base_upgrade_cost
    player.upgrade_exponent = faction.base_upgrade_exponent

    player.save()


def send_journey(player: Player, unit: Unit, quantity: int, destination: Region):
    try:
        journey = Journey.objects.get(ruler=player, unit=unit, destination=destination, ticks_to_arrive=12)
        journey.quantity += quantity
        journey.save()
    except:
        Journey.objects.create(ruler=player, unit=unit, quantity=quantity, destination=destination)
        
    unit.quantity_marshaled -= quantity
    unit.save()


def marshal_from_location(player: Player, unit: Unit, quantity: int, origin: Region):
    if quantity <= origin.units_here_dict[str(unit.id)] and unit.ruler == player:
        origin.units_here_dict[str(unit.id)] -= quantity
        
        if origin.units_here_dict[str(unit.id)] == 0:
            del origin.units_here_dict[str(unit.id)]

        origin.save()

        unit.quantity_marshaled += quantity
        unit.save()


def construct_building(player, region_id, building_type_id, amount):
    building_type = BuildingType.objects.get(id=building_type_id)
    region = Region.objects.get(id=region_id)

    if region.ruler == player and building_type.ruler == player:
        for _ in range(amount):
            built_on_ideal_terrain = False

            if building_type.ideal_terrain == region.primary_terrain and region.primary_plots_available:
                built_on_ideal_terrain = True
            elif building_type.ideal_terrain == region.secondary_terrain and region.secondary_plots_available:
                built_on_ideal_terrain = True

            Building.objects.create(
                ruler=player,
                type=building_type,
                region=region,
                built_on_ideal_terrain=built_on_ideal_terrain,
            )


def get_journey_output_dict(player: Player, region: Region):
    journey_dict = {}
    output_dict = {}
    incoming_journeys = Journey.objects.filter(ruler=player, destination=region)

    for unit in Unit.objects.filter(ruler=player):
        journey_dict[unit.name] = {}

    for journey in incoming_journeys:
        journey_dict[journey.unit.name] = create_or_add_to_key(journey_dict[journey.unit.name], str(journey.ticks_to_arrive), journey.quantity)

        for x in range(1, 13):
            if str(x) not in journey_dict[journey.unit.name]:
                journey_dict[journey.unit.name][str(x)] = 0

    for unit_name, tick_data in journey_dict.items():
        if len(tick_data) > 0:
            output_dict[unit_name] = []

            for x in range(1, 13):
                output_dict[unit_name].append(tick_data[str(x)])

    return output_dict


def generate_region():
    terrain_count = Terrain.objects.count()
    primary_terrain = Terrain.objects.all()[randint(0, terrain_count - 1)]

    terrain_count = Terrain.objects.count() - 1
    secondary_terrain = Terrain.objects.filter(~Q(id=primary_terrain.id))[randint(0, terrain_count - 1)]

    deity_count = Deity.objects.count()
    deity = Deity.objects.all()[randint(0, deity_count - 1)]

    person_names = ["Caul", "Ratclip", "Thomer", "Vaude", "Andrel", "Poley", "Tert", "Menry", "Wester", "Bragon", "Canter", "Card", "Baston", "Edwall", "Octague",
                    "Micham", "Franter", "Cater", "Catlip", "Carda", "Blance", "Regess", "Archam", "Bastaff", "Erpidge", "Humphin", "Richam", "Priar", "Stalton",
                    "Gober", "Colk", "Shakir", "Amr", "Imad", "Yazid", "Zayd", "Chanda", "Layla", "Razia", "Helder", "Costa", "Branco", "Rosa", "Nuho", "Miko",
                    "Hehomu", "Nimopa", "Hops", "Buzz", "Chuck", "Pallas", "Callisto", "Kirk", "Mbizi", "Lapis"]
    
    class Place:
        def __init__(self, before, after):
            self.before = before
            self.after = after
    
    name_modifiers = [Place("", "town"), Place("", "ton"), Place("", " Meadows"), Place("", " Downs"), Place("", "'s Folly"), Place("", " Priory"), Place("", "wood"),
                      Place("", "'s Gate"), Place("", " Baths"), Place("The ", "marches"), Place("", "ford"), Place("St. ", ""), Place("", "bridge"), Place("", " Corner"),
                      Place("", " Junction"), Place("North ", ""), Place("South ", ""), Place("East ", ""), Place("West ", ""), Place("Old ", ""), Place("New ", ""),
                      Place("", " Heights")]
    
    while True:
        try:
            person = choice(person_names)
            modifier = choice(name_modifiers)
            region_name = f"{modifier.before}{person}{modifier.after}"
            region = Region.objects.create(name=region_name, primary_terrain=primary_terrain, secondary_terrain=secondary_terrain, deity=deity)
            break
        except:
            pass

    event = Event.objects.create(reference_id=region.id, reference_type="discover", icon="🗺️")


def mock_up_player(user: User, faction: Faction):
    player = Player.objects.create(associated_user=user, name=f"P-{user.username}")
    assign_faction(player, faction)

    region_templates = []
    
    for _ in range(4):
        x = str(randint(1,9999))
        name = f"{player.name[2:5]}{x}"

        count = Terrain.objects.count()
        primary_terrain = Terrain.objects.all()[randint(0, count - 1)]

        count = Terrain.objects.count() - 1
        secondary_terrain = Terrain.objects.filter(~Q(id=primary_terrain.id))[randint(0, count - 1)]

        count = Deity.objects.count()
        deity = Deity.objects.all()[randint(0, count - 1)]

        region_templates.append({
            "ruler": player,
            "name": name,
            "primary_terrain": primary_terrain,
            "secondary_terrain": secondary_terrain,
            "deity": deity,
        })

    for template in region_templates:
        Region.objects.create(**template)