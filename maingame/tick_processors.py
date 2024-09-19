from maingame.models import Player, Region, Building, Terrain

def do_resource_production():
    beautiful_terrain = Terrain.objects.get(name="beautiful")

    for player in Player.objects.all():
        player.gold += 5000
        
        for region in Region.objects.filter(ruler=player):
            if region.primary_terrain == beautiful_terrain:
                player.gold += 1500
            elif region.secondary_terrain == beautiful_terrain:
                player.gold += 1000
            else:
                player.gold += 500

        for building in Building.objects.filter(ruler=player):
            if building.type.amount_produced > 0:
                amount_produced = building.type.amount_produced
                
                if building.built_on_ideal_terrain:
                    amount_produced *= 2
                
                elif building.type.resource_produced == "ore":
                    player.ore += amount_produced
                elif building.type.resource_produced == "lumber":
                    player.lumber += amount_produced
                elif building.type.resource_produced == "mana":
                    player.mana += amount_produced
                elif building.type.resource_produced == "gems":
                    player.gems += amount_produced
                elif building.type.resource_produced == "food":
                    player.food += amount_produced

        player.save()