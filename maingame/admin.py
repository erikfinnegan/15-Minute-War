from django.contrib import admin

from .models import Terrain, Region, Unit, Player, Deity, BuildingType, Building, Faction, Journey, Rule

admin.site.register(Terrain)
admin.site.register(Player)
admin.site.register(Region)
admin.site.register(Unit)
admin.site.register(Deity)
admin.site.register(Journey)

admin.site.register(BuildingType)
admin.site.register(Building)
admin.site.register(Faction)

admin.site.register(Rule)