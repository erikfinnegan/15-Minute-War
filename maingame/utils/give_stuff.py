from maingame.models import Unit, Dominion, Spell, Building, Resource, MechModule


def give_dominion_unit(dominion: Dominion, unit: Unit):
    try:
        dominions_unit = Unit.objects.get(ruler=dominion, name=unit.name)
    except:
        dominions_unit = unit
        dominions_unit.pk = None
        dominions_unit.ruler = dominion
        dominions_unit.save()

        for resource in unit.cost_dict:
            create_resource_for_dominion(resource, dominion)

        for resource in unit.upkeep_dict:
            create_resource_for_dominion(resource, dominion)
            
        if unit.op > unit.dp and dominion.faction_name == "aether confederacy":
            dominions_unit.upkeep_dict = {}
            dominions_unit.save()

    return dominions_unit


def give_dominion_module(dominion: Dominion, module: MechModule):
    try:
        dominions_module = MechModule.objects.get(ruler=dominion, name=module.name)
    except:
        dominions_module = module
        dominions_module.pk = None
        dominions_module.ruler = dominion
        dominions_module.save()

        for resource in module.base_upgrade_cost_dict:
            create_resource_for_dominion(resource, dominion)

        for resource in module.base_repair_cost_dict:
            create_resource_for_dominion(resource, dominion)

    return dominions_module


def give_dominion_spell(dominion: Dominion, spell: Spell):
    dominions_spell = spell
    dominions_spell.pk = None
    dominions_spell.ruler = dominion
    dominions_spell.save()

    return dominions_spell


def give_dominion_building(dominion: Dominion, building: Building):
    dominions_building = building
    dominions_building.pk = None
    dominions_building.ruler = dominion
    dominions_building.save()

    if building.amount_produced > 0:
        create_resource_for_dominion(building.resource_produced_name, dominion)

    return dominions_building


def create_resource_for_dominion(resource_identifier, dominion: Dominion) -> Resource:
    resource_name = resource_identifier

    try:
        resource_name = Resource.objects.get(name=resource_identifier, ruler=None).name

        if not Resource.objects.filter(ruler=dominion, name=resource_name).exists():
            base_resource = Resource.objects.get(name=resource_name, ruler=None)
            dominions_resource = base_resource
            dominions_resource.pk = None
            dominions_resource.ruler = dominion
            dominions_resource.save()

            return dominions_resource
        else:
            return None
    except:
        return None