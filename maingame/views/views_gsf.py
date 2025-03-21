from django.shortcuts import redirect
from django.contrib import messages

from maingame.models import Dominion, Unit


def recall_red_beret(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    try:
        red_beret = Unit.objects.get(ruler=dominion, name="Red Beret")
        
        if red_beret.quantity_returning == 1:
            red_beret.returning_dict["12"] = 1
            red_beret.quantity_in_void -= 1
            red_beret.perk_dict["subverted_target_id"] = 0
            red_beret.save()
    except:
        messages.error(request, "Don't make me send a red beret after YOU.")
        pass
    
    return redirect("world")
