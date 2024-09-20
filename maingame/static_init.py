from maingame.models import BuildingType, Terrain, Deity, Faction, Region, Player, Building, Unit, Journey

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
            "name": "mine",
            "resource_produced": "💎",
            "amount_produced": 20,
            "ideal_terrain": Terrain.objects.get(name="cavernous")
        },
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
        {
            "name": "home",
            "housing": 20,
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
        BuildingType.objects.get(name="mine"),
        BuildingType.objects.get(name="tower"),
        BuildingType.objects.get(name="stronghold"),
        BuildingType.objects.get(name="home"),
    ]

    # grassy = Terrain.objects.get(name="grassy")
    # mountainous = Terrain.objects.get(name="mountainous")
    # coastal = Terrain.objects.get(name="coastal")
    # densely_forested = Terrain.objects.get(name="forested")
    # cavernous = Terrain.objects.get(name="cavernous")
    # swampy = Terrain.objects.get(name="swampy")
    # beautiful = Terrain.objects.get(name="beautiful")
    # defensible = Terrain.objects.get(name="defensible")
    # barren = Terrain.objects.get(name="barren")

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
        op=5,
        dp=6,
        faction_for_which_is_default=humans,
        cost_dict={
            "🪙": 300,
            "🪨": 30,
        }
    )
    Unit.objects.create(
        name="trebuchet",
        op=10,
        dp=0,
        faction_for_which_is_default=humans,
        cost_dict={
            "🪙": 200,
            "🪵": 40,
        }
    )

    humans.starter_building_types.add(*generic_building_types)


def initialize_terrain():
    Terrain.objects.create(
        name="grassy",
        emoji="🌾",
        unit_op_dp_ratio=0.9,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="mountainous",
        emoji="⛰",
        unit_op_dp_ratio=0.4,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="coastal",
        emoji="🌊",
        unit_op_dp_ratio=0.6,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="forested",
        emoji="🌳",
        unit_op_dp_ratio=1,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="cavernous",
        emoji="🕳",
        unit_op_dp_ratio=1.3,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="swampy",
        emoji="🦟",
        unit_op_dp_ratio=1.1,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="defensible",
        emoji="🏰",
        unit_op_dp_ratio=0,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="barren",
        emoji="🏜",
        unit_op_dp_ratio=2,
        unit_perk_options="",
    )
    Terrain.objects.create(
        name="beautiful",
        emoji="🏞️",
        unit_op_dp_ratio=0.7,
        unit_perk_options="",
    )


def initialize_deities():
    Deity.objects.create(name="Hunger Without End")
    Deity.objects.create(name="Rubecus")
    Deity.objects.create(name="The Many Who Are One")


def initialize_game_pieces():
    Journey.objects.all().delete()
    Building.objects.all().delete()
    Region.objects.all().delete()
    Unit.objects.all().delete()
    BuildingType.objects.all().delete()
    Player.objects.all().delete()
    Faction.objects.all().delete()
    Terrain.objects.all().delete()
    Deity.objects.all().delete()

    initialize_terrain()
    initialize_deities()
    initialize_building_types()
    initialize_factions()
