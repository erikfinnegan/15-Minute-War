from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from maingame.models import Dominion, Unit, Faction, UserSettings, Round
from maingame.tick_processors import do_global_tick
from maingame.utils.dominion_controls import initialize_dominion, delete_dominion, abandon_dominion


@login_required
def register(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        return redirect("buildings")
    except:
        pass

    context = {
        "factions": Faction.objects.all(),
    }

    return render(request, "maingame/register.html", context)


@login_required
def submit_register(request):
    display_name = request.POST["dominionName"]
    faction = Faction.objects.get(name=request.POST["factionChoice"].lower())

    if Dominion.objects.filter(name=display_name).exists():
        messages.error(request, "A dominion with that name already exists")
        return redirect("register")

    initialize_dominion(user=request.user, faction=faction, display_name=display_name)

    return redirect("buildings")


def protection_tick(request, quantity):
    if quantity <= 96:
        try:
            dominion = Dominion.objects.get(associated_user=request.user)
            user_settings = UserSettings.objects.get(associated_user=request.user)
        except:
            return redirect("register")
        
        if user_settings.tutorial_step == 1:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step == 2 and dominion.protection_ticks_remaining - quantity != 71:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step == 3 and quantity != 12:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step == 10 and dominion.protection_ticks_remaining - quantity < 1:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            return redirect("buildings")
        elif user_settings.tutorial_step < 999 and user_settings.tutorial_step not in [1, 2, 3, 5, 10, 11]:
            messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
            if user_settings.tutorial_step in [4]:
                return redirect("upgrades")
            elif user_settings.tutorial_step in [6, 7, 10]:
                return redirect("military")
            elif user_settings.tutorial_step in [8]:
                return redirect("discoveries")
            else:
                return redirect("buildings")
        
        if dominion.protection_ticks_remaining - quantity < 12:
            forgot_units = True

            for unit in Unit.objects.filter(ruler=dominion):
                if unit.quantity_at_home + unit.quantity_in_training > 0:
                    forgot_units = False

            if forgot_units:
                messages.error(request, f"You may not leave protection without units and they take 12 ticks to train. You'll want at least a few hundred total defense.")
            else:
                for _ in range(quantity):
                    if dominion.protection_ticks_remaining > 0:
                        dominion.do_tick()
                        dominion.protection_ticks_remaining -= 1
                        dominion.save()
        else:
            for _ in range(quantity):
                if dominion.protection_ticks_remaining > 0:
                    dominion.do_tick()
                    dominion.protection_ticks_remaining -= 1
                    dominion.save()
    else:
        messages.error(request, f"Knock it off")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def protection_restart(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if dominion.is_oop and Round.objects.first().has_started:
        messages.error(request, f"I just saved your life.")
        return redirect("world")
    
    display_name = dominion.name
    faction = Faction.objects.get(name=dominion.faction_name)

    delete_dominion(dominion)
    initialize_dominion(user=request.user, faction=faction, display_name=display_name)

    if faction.name == "sludgeling":
        return redirect("experimentation")    

    return redirect("buildings")


def abandon(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("overview", dominion.id)
    
    if "abandon" in request.POST and request.POST["confirm_abandon"] == "REALLY DO IT":
        if Round.objects.first().has_started:
            abandon_dominion(dominion)
        else:
            delete_dominion(dominion)

        return redirect("register")

    return redirect("overview", dominion.id)



def run_tick_view(request, quantity):
    if request.user.username != "test":
        messages.error(request, f"Ticky tick tick")
        return redirect("buildings")

    round = Round.objects.first()
    round.has_started = True
    round.save()

    for _ in range(quantity):
        do_global_tick()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
