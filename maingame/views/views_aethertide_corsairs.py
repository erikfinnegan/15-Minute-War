from django.shortcuts import redirect, render
from django.contrib import messages

from maingame.models import Dominion, Resource


def captains_quarters(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    try:
        press_gangers = Resource.objects.get(ruler=dominion, name="press gangers").quantity
    except:
        press_gangers = 0
    
    context = {
        "press_gangers": press_gangers,
    }
    
    return render(request, "maingame/faction_pages/captains_quarters.html", context)


def corpsify_press_gangers(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    print(request.POST)
    quantity_corpsified = int(request.POST.get("quantity_corpsified"))
    
    try:
        press_gangers = Resource.objects.get(ruler=dominion, name="press gangers")
        
        if quantity_corpsified > press_gangers.quantity:
            messages.error(request, "Walk the timeplank")
            return redirect("captains_quarters")
        
        press_gangers.spend(quantity_corpsified)
        Resource.objects.get(ruler=dominion, name="corpses").gain(quantity_corpsified)
        messages.success(request, f"Corpsified {quantity_corpsified} press gangers.")
    except:
        messages.error(request, f"Something went wrong when trying to corpsify {quantity_corpsified} press gangers.")
    
    return redirect("captains_quarters")