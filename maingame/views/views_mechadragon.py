from django.contrib import messages
from django.shortcuts import redirect, render

from maingame.models import Dominion, MechModule, Unit, Resource, Event, Battle


def mech_hangar(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    capacity_upgrade_cost = dominion.perk_dict["capacity_upgrade_cost"]
    gold = Resource.objects.get(ruler=dominion, name="gold")
    mechadragon = Unit.objects.get(ruler=dominion, name="Mecha-Dragon")
    mechadragon_not_home = mechadragon.quantity_at_home == 0

    # try:
    #     town_portal = MechModule.objects.get(ruler=dominion, name="Back-#-U Town Portal System")
    #     has_town_portal = True
    #     can_use_town_portal = True
    #     if town_portal.zone == "mech" and mechadragon_not_home:
    #         for module in MechModule.objects.filter(ruler=dominion, zone="mech"):
    #             if module.capacity > town_portal.capacity:
    #                 can_use_town_portal = False
    #     else:
    #         can_use_town_portal = False
    # except:
    #     has_town_portal = False
    #     can_use_town_portal = False
    
    has_town_portal = MechModule.objects.filter(ruler=dominion, name="Back-#-U Town Portal System").exists()
    can_use_town_portal = MechModule.objects.filter(ruler=dominion, name="Back-#-U Town Portal System", zone="mech").exists() and mechadragon_not_home
    dominion.update_capacity()

    context = {
        "capacity_upgrade_cost": capacity_upgrade_cost,
        "capacity_upgrades_affordable": int(gold.quantity / capacity_upgrade_cost),
        "capacity_used": dominion.perk_dict["capacity_used"],
        "max_capacity": dominion.perk_dict["capacity_max"],
        "modules": MechModule.objects.filter(ruler=dominion).order_by("order"),
        "mechadragon": mechadragon,
        "mechadragon_not_home": mechadragon_not_home,
        "has_town_portal": has_town_portal,
        "can_use_town_portal": can_use_town_portal,
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

    dominion.update_capacity()

    if "upgrade" in request.POST:
        id_to_upgrade = request.POST.get("upgrade")
        module = MechModule.objects.get(ruler=dominion, id=id_to_upgrade)
        success, message = module.upgrade()

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        dominion.update_capacity()
    elif "toggle_equip" in request.POST:
        max_capacity = dominion.perk_dict["capacity_max"]
        capacity_used = dominion.perk_dict["capacity_used"]
        id_to_equip = request.POST.get("toggle_equip")
        module = MechModule.objects.get(ruler=dominion, id=id_to_equip)

        if module.zone == "hangar" and capacity_used + module.capacity <= max_capacity:
            module.zone = "mech"
        elif module.zone == "hangar" and capacity_used + module.capacity > max_capacity:
            messages.error(request, f"Insufficient capacity to equip {module.versioned_name}")
        else:
            module.zone = "hangar"
        
        module.save()
        dominion.update_capacity()
    
    return redirect("mech_hangar")


def submit_town_portal(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        mechadragon = Unit.objects.get(ruler=dominion, name="Mecha-Dragon")
        town_portal = MechModule.objects.get(ruler=dominion, name="Back-#-U Town Portal System")
    except:
        return redirect("register")
    
    if mechadragon.quantity_at_home > 0:
        messages.error(request, "Brrr-ZAP! Oh no, misfire :(")
        return redirect("mech_hangar")
    
    for module in MechModule.objects.filter(ruler=dominion, zone="mech"):
        module.durability_current = 0
        module.save()
    
    while mechadragon.quantity_at_home == 0:
        mechadragon.advance_training_and_returning()

    town_portal.delete()
    
    battle = Battle.objects.filter(attacker=dominion).last()
    event = Event.objects.get(reference_id=battle.id)
    event.extra_text = "The mecha-dragon was returned home instantly via town portal."
    event.save()

    messages.success(request, "POOF! The Mecha-Dragon has returned!")
    return redirect("mech_hangar")