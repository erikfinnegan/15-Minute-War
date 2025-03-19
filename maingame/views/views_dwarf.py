from django.shortcuts import redirect
from django.contrib import messages

from maingame.models import Dominion, Faction
from maingame.utils.dominion_controls import initialize_dominion, delete_dominion


# def submit_doom_prospectors(request, resource):
#     try:
#         dominion = Dominion.objects.get(associated_user=request.user)
#     except:
#         return redirect("register")
    
#     print("doom time")
    
#     return redirect("military")
