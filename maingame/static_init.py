from maingame.models import BuildingType, Terrain, Deity, Region, Player, Building, Unit, Journey, Round, Battle, Event
from maingame.formatters import create_or_add_to_key
from maingame.utils import update_trade_prices

def initialize_building_types():
    building_type_templates = [
        {
            "name": "farm",
            "resource_produced": "🍞",
            "amount_produced": 100,
            "ideal_terrain": Terrain.objects.get(name="grassy"),
            "is_starter": True,
        },
        {
            "name": "quarry",
            "resource_produced": "🪨",
            "amount_produced": 50,
            "ideal_terrain": Terrain.objects.get(name="mountainous"),
            "is_starter": True,
        },
        {
            "name": "lumberyard",
            "resource_produced": "🪵",
            "amount_produced": 100,
            "ideal_terrain": Terrain.objects.get(name="forested"),
            "is_starter": True,
        },
        {
            "name": "school",
            "resource_produced": "📜",
            "amount_produced": 1,
            "ideal_terrain": Terrain.objects.get(name="grassy"),
            "is_starter": True,
        },
        {
            "name": "stronghold",
            "defense_multiplier": 20,
            "ideal_terrain": Terrain.objects.get(name="defensible"),
            "is_starter": True,
        },

        {
            "name": "mine",
            "resource_produced": "💎",
            "amount_produced": 20,
            "ideal_terrain": Terrain.objects.get(name="cavernous")
        },
        {
            "name": "tower",
            "resource_produced": "🔮",
            "amount_produced": 10,
            "ideal_terrain": Terrain.objects.get(name="swampy"),
        },
        {
            "name": "embassy",
            "trade_multiplier": 30,
            "ideal_terrain": Terrain.objects.get(name="coastal"),
        },
    ]

    for building_template in building_type_templates:
        BuildingType.objects.create(**building_template)


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
    Deity.objects.create(name="Rubecus Swiftstrike", icon="⚡")
    Deity.objects.create(name="The Many Who Are One", icon="🍄")
    Unit.objects.create(
        name="tendril of unity",
        op=13,
        dp=0,
        is_trainable=False,
    )


def initialize_units():
    Unit.objects.create(
        name="archer",
        op=2,
        dp=4,
        cost_dict={
            "🪙": 150,
            "🪵": 30,
        },
        is_starter=True
    )
    Unit.objects.create(
        name="knight",
        op=6,
        dp=5,
        cost_dict={
            "🪙": 275,
            "🪨": 25,
        },
        is_starter=True
    )


def initialize_trade_prices():
    round = Round.objects.first()

    for building_type in BuildingType.objects.all():
        if building_type.amount_produced > 0:
            round.resource_bank_dict[building_type.resource_produced] = 0

    round.resource_bank_dict["🪙"] = 0
    update_trade_prices()
    round.save()


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
    Terrain.objects.all().delete()
    Deity.objects.all().delete()
    Round.objects.create()

    initialize_terrain()
    initialize_deities()
    initialize_building_types()
    initialize_units()
    initialize_trade_prices()
