from maingame.models import BuildingType, Terrain, Deity, Faction, Region, Player, Building, Unit, Journey, Round, Battle, Event

def initialize_building_types():
    building_type_templates = [
        {
            "name": "farm",
            "resource_produced": "🍞",
            "amount_produced": 100,
            "ideal_terrain": Terrain.objects.get(name="grassy")
        },
        {
            "name": "quarry",
            "resource_produced": "🪨",
            "amount_produced": 50,
            "ideal_terrain": Terrain.objects.get(name="mountainous")
        },
        {
            "name": "embassy",
            "trade_multiplier": 30,
            "ideal_terrain": Terrain.objects.get(name="coastal")
        },
        {
            "name": "lumberyard",
            "resource_produced": "🪵",
            "amount_produced": 100,
            "ideal_terrain": Terrain.objects.get(name="forested")
        },
        {
            "name": "school",
            "resource_produced": "📜",
            "amount_produced": 20,
            "ideal_terrain": Terrain.objects.get(name="grassy")
        },
        # {
        #     "name": "mine",
        #     "resource_produced": "💎",
        #     "amount_produced": 20,
        #     "ideal_terrain": Terrain.objects.get(name="cavernous")
        # },
        {
            "name": "tower",
            "resource_produced": "🔮",
            "amount_produced": 10,
            "ideal_terrain": Terrain.objects.get(name="swampy")
        },
        {
            "name": "stronghold",
            "defense_multiplier": 50,
            "ideal_terrain": Terrain.objects.get(name="defensible")
        },
    ]

    for building_template in building_type_templates:
        BuildingType.objects.create(**building_template)


def initialize_factions():
    generic_building_types = [
        BuildingType.objects.get(name="farm"),
        BuildingType.objects.get(name="quarry"),
        BuildingType.objects.get(name="embassy"),
        BuildingType.objects.get(name="lumberyard"),
        BuildingType.objects.get(name="tower"),
        BuildingType.objects.get(name="stronghold"),
        BuildingType.objects.get(name="school"),
    ]

    humans = Faction.objects.create(name="human")
    Unit.objects.create(
        name="archer",
        op=2,
        dp=4,
        faction_for_which_is_default=humans,
        cost_dict={
            "🪙": 150,
            "🪵": 30,
        }
    )
    Unit.objects.create(
        name="knight",
        op=6,
        dp=5,
        faction_for_which_is_default=humans,
        cost_dict={
            "🪙": 275,
            "🪨": 25,
        }
    )
    humans.starter_building_types.add(*generic_building_types)

    undead = Faction.objects.create(name="undead")
    Unit.objects.create(
        name="skeleton",
        op=3,
        dp=3,
        faction_for_which_is_default=undead,
        cost_dict={
            "🪙": 125,
            "🔮": 2,
        }
    )
    Unit.objects.create(
        name="necromancer",
        op=6,
        dp=5,
        faction_for_which_is_default=undead,
        cost_dict={
            "🪙": 1400,
            "📜": 50,
        }
    )
    undead.starter_building_types.add(*generic_building_types)


def initialize_terrain():
    Terrain.objects.create(
        name="grassy",
        icon="🌾",
        unit_op_dp_ratio=0.9,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="mountainous",
        icon="⛰",
        unit_op_dp_ratio=0.4,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="coastal",
        icon="🌊",
        unit_op_dp_ratio=0.6,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="forested",
        icon="🌳",
        unit_op_dp_ratio=1,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="cavernous",
        icon="🕳",
        unit_op_dp_ratio=1.3,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="swampy",
        icon="🦟",
        unit_op_dp_ratio=1.1,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="defensible",
        icon="🏰",
        unit_op_dp_ratio=0,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="barren",
        icon="🏜",
        unit_op_dp_ratio=1.8,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="beautiful",
        icon="🏞️",
        unit_op_dp_ratio=0.7,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="influential",
        icon="👑",
        unit_op_dp_ratio=2,
        unit_perk_options="",
    )


def initialize_deities():
    Deity.objects.create(name="Hunger Without End", icon="🪙")
    Deity.objects.create(name="Rubecus", icon="🪺")
    Deity.objects.create(name="The Many Who Are One", icon="🍄")


def initialize_game_pieces():
    Battle.objects.all().delete()
    Event.objects.all().delete()
    Round.objects.all().delete()
    Journey.objects.all().delete()
    Building.objects.all().delete()
    Region.objects.all().delete()
    Unit.objects.all().delete()
    BuildingType.objects.all().delete()
    Player.objects.all().delete()
    Faction.objects.all().delete()
    Terrain.objects.all().delete()
    Deity.objects.all().delete()

    Round.objects.create()

    initialize_terrain()
    initialize_deities()
    initialize_building_types()
    initialize_factions()
