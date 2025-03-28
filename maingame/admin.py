from django.contrib import admin

from .models import Faction, Unit, Dominion, Deity, Building, Round, Event, Battle, Resource, Discovery, Spell, UserSettings, Theme, MechModule, Sludgene

class FooAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)

admin.site.register(Faction)
admin.site.register(Resource)
admin.site.register(Dominion)
admin.site.register(Unit)
admin.site.register(MechModule)
admin.site.register(Deity)
admin.site.register(Discovery)
admin.site.register(Event, FooAdmin)
admin.site.register(Battle)
admin.site.register(Building)
admin.site.register(Spell)
admin.site.register(Round)
admin.site.register(UserSettings)
admin.site.register(Theme)
admin.site.register(Sludgene)