from django.shortcuts import render, redirect
from django.contrib import messages

from maingame.models import Dominion, Round


def other_head(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if dominion.faction_name != "biclops":
        messages.error(request, f"You don't have access to this page")
        return redirect("buildings")
    
    return render(request, "maingame/faction_pages/other_head.html")


def submit_other_head(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("other_head")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("other_head")
    
    if dominion.faction_name != "biclops" or "partner_attack_on_sight" not in dominion.perk_dict:
        messages.error(request, f"You don't have access to this page")
        return redirect("buildings")
    
    dominion.perk_dict["partner_attack_on_sight"] = "partner_attack_on_sight" in request.POST
    dominion.save()
    
    messages.success(request, "Scheming with your other head successful")
    return redirect("other_head")
