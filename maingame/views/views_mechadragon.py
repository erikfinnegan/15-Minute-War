from django.shortcuts import redirect, render

from maingame.models import Dominion


def mech_hangar(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    components = []

    components.append(
        {
            "id": "asuidona",
            "name": "XV-8 Rocket Pods",
            "durability_percent": 15,
            "op": 4,
            "capacity": 5,
            "equipped": True,
        }
    )

    components.append(
        {
            "id": "sdfgsd",
            "name": "B-99 Heavy Cannon",
            "durability_percent": 30,
            "op": 7,
            "capacity": 7,
            "equipped": False,
        }
    )

    components.append(
        {
            "id": "hdfgsdfgs",
            "name": "XII Scrapper Claws",
            "durability_percent": 55,
            "op": 8,
            "capacity": 9,
            "equipped": False,
        }
    )

    components.append(
        {
            "id": "ccvbsdr",
            "name": "Fire Breath MkII",
            "durability_percent": 85,
            "op": 12,
            "capacity": 12,
            "equipped": True,
        }
    )

    context = {
        "max_capacity": 30,
        "components": components,
    }
    
    return render(request, "maingame/faction_pages/mech_hangar.html", context)


def submit_mech_hangar(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    print()
    print()
    print(request.POST)
    print()
    print()

    return redirect("mech_hangar")