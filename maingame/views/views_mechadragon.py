from django.contrib import messages
from django.shortcuts import redirect, render

from maingame.models import Dominion, MechModule, Unit, Resource
from maingame.utils.utils import update_capacity


def mech_hangar(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    capacity_upgrade_cost = dominion.perk_dict["capacity_upgrade_cost"]
    gold = Resource.objects.get(ruler=dominion, name="gold")
    mechadragon = Unit.objects.get(ruler=dominion, name="Mecha-Dragon")
    mechadragon_not_home = mechadragon.quantity_at_home == 0
    print("mechadragon_not_home", mechadragon_not_home)

    context = {
        "capacity_upgrade_cost": capacity_upgrade_cost,
        "capacity_upgrades_affordable": int(gold.quantity / capacity_upgrade_cost),
        "capacity_used": dominion.perk_dict["capacity_used"],
        "max_capacity": dominion.perk_dict["capacity_max"],
        "modules": MechModule.objects.filter(ruler=dominion).order_by("order"),
        "mechadragon": mechadragon,
        "mechadragon_not_home": mechadragon_not_home,
    }
    
    return render(request, "maingame/faction_pages/mech_hangar.html", context)


def submit_mech_hangar(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    order = 0

    for key, value in request.POST.items():
        if key[:4] == "zone":
            module_id = key[5:]
            module = MechModule.objects.get(ruler=dominion, id=module_id)
            module.zone = value

            order += 1
            module.order = order

            module.save()
        elif key == "capacity_upgrades" and value != "":
            quantity = int(value)
            gold = Resource.objects.get(ruler=dominion, name="gold")
            capacity_upgrade_cost = dominion.perk_dict["capacity_upgrade_cost"]
            upgrades_affordable = int(gold.quantity / capacity_upgrade_cost)

            if quantity > upgrades_affordable:
                messages.error(request, "Insufficient gold for that many capacity upgrades")
            else:
                gold.spend(quantity * capacity_upgrade_cost)
                dominion.perk_dict["capacity_max"] += quantity
                messages.success(request, f"Upgraded capacity {quantity} times")

        # print(f"{key} -- {value}")

    update_capacity(dominion)

    if "upgrade" in request.POST:
        id_to_upgrade = request.POST.get("upgrade")
        module = MechModule.objects.get(ruler=dominion, id=id_to_upgrade)
        # module.version += 1
        # module.save()
        success, message = module.upgrade()

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        update_capacity(dominion)
    
    return redirect("mech_hangar")


def submit_upgrade_capacity(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    quantity = request.POST.get("quantity")

    return redirect("mech_hangar")