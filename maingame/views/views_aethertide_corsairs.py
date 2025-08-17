from django.shortcuts import redirect, render
from django.contrib import messages

from maingame.models import Dominion, Resource, Unit


def captains_quarters(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    try:
        pirate_crews = Unit.objects.get(ruler=dominion, name="Pirate Crew")
        shares = pirate_crews.upkeep_dict["plunder"]
        min_shares = max(0, shares - 2)
        max_shares = min(10, shares + 2)
    except:
        shares = 0
        messages.error(request, "You are sentenced to walk the timeplank")
        return redirect("world")
    
    try:
        press_gangers = Resource.objects.get(ruler=dominion, name="press gangers").quantity
    except:
        press_gangers = 0
        
    try:
        ticks_until_next_share_change = dominion.perk_dict["ticks_until_next_share_change"]
    except:
        ticks_until_next_share_change = 99999
        
    context = {
        "press_gangers": press_gangers,
        "shares": shares,
        "min_shares": min_shares,
        "max_shares": max_shares,
        "ticks_until_next_share_change": ticks_until_next_share_change,
        "can_change_shares": ticks_until_next_share_change == 0,
        "no_changing_shares": ticks_until_next_share_change > 0,
    }
    
    return render(request, "maingame/faction_pages/captains_quarters.html", context)


def corpsify_press_gangers(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    quantity_corpsified = int(request.POST.get("quantity_corpsified"))
    
    if quantity_corpsified < 0:
        messages.error(request, "You are sentenced to walk the timeplank")
        return redirect("captains_quarters")
    
    try:
        press_gangers = Resource.objects.get(ruler=dominion, name="press gangers")
        
        if quantity_corpsified > press_gangers.quantity:
            messages.error(request, "You are sentenced to walk the timeplank")
            return redirect("captains_quarters")
        
        press_gangers.spend(quantity_corpsified)
        Resource.objects.get(ruler=dominion, name="corpses").gain(quantity_corpsified)
        messages.success(request, f"Corpsified {quantity_corpsified} press gangers.")
    except:
        messages.error(request, f"Something went wrong when trying to corpsify {quantity_corpsified} press gangers.")
    
    return redirect("captains_quarters")


def submit_plunder_shares(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if "shares_per_pirate" not in request.POST or request.POST.get("shares_per_pirate") == "":
        messages.error(request, "You must enter an amount.")
        return redirect("captains_quarters")
    
    shares = int(request.POST.get("shares_per_pirate"))
    
    if shares < 0:
        messages.error(request, "You can't allocate negative shares")
        return redirect("captains_quarters")
    
    if shares != 0 and not shares:
        messages.error(request, "You are sentenced to walk the timeplank")
        return redirect("captains_quarters")
    
    if dominion.perk_dict["ticks_until_next_share_change"] > 0:
        messages.error(request, "You must wait longer to change your crews' cut of the plunder")
        return redirect("captains_quarters")
    
    try:
        pirate_crews = Unit.objects.get(ruler=dominion, name="Pirate Crew")
        template_pirate_crews = Unit.objects.get(ruler=None, name="Pirate Crew")
        pirate_crews.upkeep_dict["plunder"] = shares
        
        pirate_crews.op = template_pirate_crews.op + (2 * (shares - 1))
        pirate_crews.dp = template_pirate_crews.dp + (2 * (shares - 1))
        pirate_crews.save()
        
        dominion.perk_dict["ticks_until_next_share_change"] = 36
        dominion.save()
    except:
        messages.error(request, "You are sentenced to walk the timeplank")
        return redirect("world")
    
    return redirect("captains_quarters")