from datetime import datetime
from zoneinfo import ZoneInfo
from django.core.management.base import BaseCommand

from maingame.models import Resource, Round, Dominion, Unit


class Command(BaseCommand):
    help = "Initiates a battle"

    def handle(self, *args, **options):
        print("Auditing bugs")
        
        start_timestamp = datetime.now(ZoneInfo('America/New_York'))
        round = Round.objects.first()
        resource_bugs = False
        unit_bugs = False
        acre_bugs = False

        for resource in Resource.objects.all():
            if resource.net != resource.quantity:
                resource_bugs = True
                msg = f"{start_timestamp.strftime('%H:%M:%S')}: {resource.ruler}'s {resource.name} expected {resource.net} -vs- current {resource.quantity}"
                round.bugs.append(msg)

        for unit in Unit.objects.all():
            if unit.quantity_trained_and_alive != unit.net:
                unit_bugs = True
                msg = f"{start_timestamp.strftime('%H:%M:%S')}: {unit.ruler}'s {unit.name} expected {unit.net} -vs- current {unit.quantity_trained_and_alive}"
                round.bugs.append(msg)

        for dominion in Dominion.objects.all():
            if dominion.net_acres + 500 != dominion.acres:
                acre_bugs = True
                msg = f"{start_timestamp.strftime('%H:%M:%S')}: {dominion} acres expected {dominion.net_acres + 500} -vs- current {dominion.acres}"
                round.bugs.append(msg)

        has_bugs = resource_bugs or unit_bugs or acre_bugs

        if has_bugs:
            print("We got bugs!")
        else:
            print("No bugs right now")

        round.has_bugs = has_bugs