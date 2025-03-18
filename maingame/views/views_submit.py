from django.shortcuts import redirect
from django.contrib import messages

from maingame.formatters import create_or_add_to_key
from maingame.models import Building, Dominion, Unit, Round, Resource, Discovery, Spell, UserSettings, Theme
from maingame.utils.invasion import do_gsf_infiltration, do_invasion, get_op_and_dp_left
from maingame.utils.utils import create_unit_dict, unlock_discovery, cast_spell


def submit_discovery(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("discoveries")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("discoveries")
    
    discovery_name = request.POST["discovery_name"]

    if user_settings.tutorial_step < 999 and discovery_name != "Palisades":
        messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
        return redirect("discoveries")
    
    if dominion.discovery_points < 50:
        messages.error(request, f"Insufficient discovery points")
        return redirect("discoveries")
    elif not Discovery.objects.filter(name=discovery_name).exists():
        messages.error(request, f"That discovery doesn't exist")
        return redirect("discoveries")
    elif dominion.faction_name in Discovery.objects.get(name=discovery_name).not_for_factions:
        messages.error(request, f"Your faction doesn't have access to that discovery")
        return redirect("discoveries")
    else:
        dominion.discovery_points -= 50
        new_discoveries_message = unlock_discovery(dominion, discovery_name)
        messages.success(request, f"Discovered {discovery_name}")
        
        if new_discoveries_message:
            messages.success(request, f"New discoveries unlocked: {new_discoveries_message}")

    return redirect("discoveries")


def submit_building(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("buildings")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("buildings")
    
    user_settings = UserSettings.objects.get(associated_user=dominion.associated_user)

    total_new_percent = 0

    for building in Building.objects.filter(ruler=dominion):
        if request.POST.get(f"build_{building.id}") != "":
            string_percent = request.POST.get(f"build_{building.id}")
            total_new_percent += int(string_percent)

            if user_settings.tutorial_step == 1:
                if building.name == "farm" and int(string_percent) != 5:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "quarry" and int(string_percent) != 45:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "lumberyard" and int(string_percent) != 11:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "school" and int(string_percent) != 39:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")
                elif building.name == "tower" and int(string_percent) != 0:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("buildings")

    if total_new_percent != 100:
        messages.error(request, f"Building allocation must add up to exactly 100%")
        return redirect("buildings")
    
    for building in Building.objects.filter(ruler=dominion):
        if request.POST.get(f"build_{building.id}") != "":
            string_percent = request.POST.get(f"build_{building.id}")
            building.percent_of_land = int(string_percent)
        else:
            building.percent_of_land = 0

        building.save()

    # for key, string_percent in request.POST.items():
    #     if "build_" in key and string_percent != "":
    #         building = Building.objects.get(id=key[6:])
    #         building.percent_of_land = int(string_percent)
    #         building.save()

    messages.success(request, f"Building allocation successful")
    
    return redirect("buildings")


def submit_training(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("military")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("military")
    
    total_trained = 0
    total_cost_dict = {}

    for key, string_amount in request.POST.items():
        # key is like "train_123" where 123 is the ID of the Unit
        if "train_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[6:])

            if user_settings.tutorial_step < 999:
                if user_settings.tutorial_step <= 5:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                if unit.name == "Stoneshield" and int(string_amount) != 500 and user_settings.tutorial_step <= 6:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                elif unit.name == "Hammerer" and int(string_amount) != 720 and user_settings.tutorial_step <= 7:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                elif unit.name == "Palisade" and int(string_amount) != 147 and user_settings.tutorial_step <= 9:
                    messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
                    return redirect("military")
                

            if unit.is_trainable:
                amount = int(string_amount)
                total_trained += amount

                for resource, cost in unit.cost_dict.items():
                    total_of_this_resource = cost * amount
                    total_cost_dict = create_or_add_to_key(total_cost_dict, resource, total_of_this_resource)
            else:
                messages.error(request, f"Knock it off")
                return redirect("military")

    if total_trained < 1:
        messages.error(request, f"Zero units trained")
        return redirect("military")

    training_succeeded = True

    for resource, amount in total_cost_dict.items():
        dominions_resource = Resource.objects.get(ruler=dominion, name=resource)

        if dominions_resource.quantity < amount:
            training_succeeded = False
            messages.error(request, f"This would cost {f'{amount:,}'} {resource}. You have {f'{dominions_resource.quantity:,}'}. You're {f'{amount - dominions_resource.quantity:,}'} short.")

    if training_succeeded:
        for resource, amount in total_cost_dict.items():
            dominions_resource = Resource.objects.get(ruler=dominion, name=resource)
            dominions_resource.spend(amount)

        for key, string_amount in request.POST.items():
            if "train_" in key and string_amount != "":
                unit = Unit.objects.get(ruler=dominion, id=key[6:])
                amount = int(string_amount)

                if "unit_training_time" in dominion.perk_dict:
                    unit_training_time = dominion.perk_dict["unit_training_time"]
                    unit.put_into_training(amount, unit_training_time)
                else:
                    unit.put_into_training(amount, 12)

                unit.save()

        messages.success(request, f"Training of {total_trained} units successful")
    
    return redirect("military")


def submit_release(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("military")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("military")
    
    total_released = 0

    for key, string_amount in request.POST.items():
        # key is like "release_123" where 123 is the ID of the Unit
        if "release_" in key and string_amount != "":
            unit = Unit.objects.get(id=key[8:])
            amount = int(string_amount)

            if total_released > unit.quantity_at_home:
                messages.error(request, f"You can't release more units than you have at home.")
                return redirect("military")

            unit.lose(max(0, amount))
            total_released += amount

    if total_released < 1:
        messages.error(request, f"Zero units released")
        return redirect("military")

    messages.success(request, f"{total_released} units released")

    return redirect("military")


def upgrade_building(request, building_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("upgrades")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("upgrades")
    
    building = Building.objects.get(ruler=dominion, id=building_id)
    research_resource = Resource.objects.get(ruler=dominion, name="research")
    available_research_points = research_resource.quantity

    if user_settings.tutorial_step == 4 and building.name != "quarry":
        messages.error(request, f"Please follow the tutorial or disable tutorial mode in the Options page")
        return redirect("upgrades")

    if available_research_points < building.upgrade_cost:
        messages.error(request, f"This would cost {f'{building.upgrade_cost:,}'} research. You have {f'{available_research_points:,}'}. You're {f'{building.upgrade_cost - available_research_points:,}'} short.")
        return redirect("upgrades")

    research_resource.spend(building.upgrade_cost)
    building.upgrades += 1
    
    if building.amount_produced > 0:
        building.amount_produced += 1
    elif building.defense_multiplier > 0:
        building. defense_multiplier += 1
    
    building.save()
    dominion.save()

    return redirect("upgrades")


def submit_spell(request, spell_id):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    target_dominion = None
    spell = Spell.objects.get(id=spell_id)
    mana = Resource.objects.get(ruler=dominion, name="mana")
    round = Round.objects.first()

    try:
        dominion_id = request.POST["target_dominion_id"]
        target_dominion = Dominion.objects.get(id=dominion_id)

        if not target_dominion.is_oop or not dominion.is_oop or not round.has_started or round.has_ended or target_dominion.is_abandoned:
            messages.error(request, f"Illegal target")
            return redirect("spells")
    except:
        pass

    if Round.objects.first().has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("spells")
    
    if Round.objects.first().is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("spells")

    if spell.mana_cost > mana.quantity:
        messages.error(request, f"This would cost {f'{spell.mana_cost:,}'} mana. You have {f'{mana.quantity:,}'}. You're {f'{spell.mana_cost - mana.quantity:,}'} short.")
        return redirect("spells")
    
    if spell.cooldown_remaining > 0:
        messages.error(request, f"This spell is still on cooldown.")
        return redirect("spells")
    
    cast_spell(spell, target_dominion)

    messages.success(request, f"Cast {spell.name}")
    return redirect("spells")


def submit_options(request):
    try:
        user_settings = UserSettings.objects.get(associated_user=request.user)
    except:
        return redirect("index")
    
    user_settings.display_name = request.POST["display_name"]
    user_settings.use_am_pm = "use_am_pm" in request.POST
    user_settings.timezone = request.POST["timezone"]
    user_settings.is_tutorial = "tutorial_mode" in request.POST
    user_settings.hide_zero_resources = "hide_zero_resources" in request.POST
    selected_theme = Theme.objects.get(id=request.POST["theme"])
    user_settings.juicy_target_threshold = request.POST["juicy_target_threshold"]

    header_background = request.POST["header_background"]
    header_text = request.POST["header_text"]
    base_background = request.POST["base_background"]
    base_text = request.POST["base_text"]
    card_background = request.POST["card_background"]
    card_text = request.POST["card_text"]
    input_background = request.POST["input_background"]
    input_text = request.POST["input_text"]

    try:
        my_theme = Theme.objects.get(creator_user_settings_id=user_settings.id)
    except:
        my_theme = Theme.objects.create(
            name=f"{user_settings.display_name}'s Theme",
            creator_user_settings_id=user_settings.id,
            base_background=base_background,
            base_text=base_text,
            header_background=header_background,
            header_text=header_text,
            card_background=card_background,
            card_text=card_text,
            input_background=input_background,
            input_text=input_text,   
        )

    if (
        user_settings.theme_model == selected_theme and
        (
            header_background != selected_theme.header_background or
            header_text != selected_theme.header_text or
            base_background != selected_theme.base_background or
            base_text != selected_theme.base_text or
            card_background != selected_theme.card_background or
            card_text != selected_theme.card_text or
            input_background != selected_theme.input_background or
            input_text != selected_theme.input_text
        )
    ):
        my_theme.header_background = header_background
        my_theme.header_text = header_text
        my_theme.base_background = base_background
        my_theme.base_text = base_text
        my_theme.card_background = card_background
        my_theme.card_text = card_text
        my_theme.input_background = input_background
        my_theme.input_text = input_text
        my_theme.save()
        user_settings.theme_model = my_theme
    else:
        user_settings.theme_model = selected_theme

    user_settings.save()
    messages.success(request, "Options saved")
    return redirect("options")


def submit_void_return(request):
    try:
        dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    round = Round.objects.first()
    
    if round.has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("world")
    
    if round.is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("world")
    
    mana = Resource.objects.get(ruler=dominion, name="mana")
    
    if dominion.void_return_cost > mana.quantity:
        messages.error(request, f"Insufficient mana")
        return redirect("world")
    
    mana.spend(dominion.void_return_cost)
    
    for unit in Unit.objects.filter(ruler=dominion, quantity_in_void__gt=0):
        unit.quantity_at_home += unit.quantity_in_void
        unit.quantity_in_void = 0
        unit.save()
        
    dominion.gain_acres(dominion.acres_in_void)
    dominion.acres_in_void = 0
    dominion.void_return_cost = 0
    dominion.save()

    messages.success(request, f"Your units have returned from a place between realities")
    return redirect("world")


def submit_invasion(request):
    try:
        my_dominion = Dominion.objects.get(associated_user=request.user)
    except:
        return redirect("register")
    
    round = Round.objects.first()
    dominion_id = request.POST["target_dominion_id"]
    this_is_infiltration = "do_infiltration" in request.POST
    
    if round.has_ended:
        messages.error(request, f"The round has already ended")
        return redirect("world")
    
    if round.is_ticking:
        messages.error(request, f"The tick is being processed, try again shortly.")
        return redirect("world")
    
    if not my_dominion.can_attack:
        messages.error(request, f"You can't attack right now")
        return redirect("world")
    
    if dominion_id == "0":
        messages.error(request, f"No target selected")
        return redirect("world")
    
    units_sent_dict, total_units_sent = create_unit_dict(request.POST, "send_")

    if total_units_sent < 1:
        messages.error(request, f"Zero units sent")
        return redirect("world")

    target_dominion = Dominion.objects.get(id=dominion_id)
    
    if target_dominion.protection_ticks_remaining > 0 or my_dominion.protection_ticks_remaining > 0 or not round.has_started or round.has_ended or target_dominion.is_abandoned:
        messages.error(request, f"Illegal invasion")
        return redirect("world")

    if this_is_infiltration:
        infiltration_power_gained, _, _ = get_op_and_dp_left(units_sent_dict, attacker=my_dominion, defender=target_dominion, is_infiltration=True)
        success, message = do_gsf_infiltration(infiltration_power_gained, units_sent_dict, my_dominion, target_dominion)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("world")
    else:
        battle_id, message = do_invasion(units_sent_dict, my_dominion, target_dominion)

        if battle_id == 0:
            messages.error(request, message)
            return redirect("world")

        return redirect("battle_report", battle_id=battle_id)
    
    return redirect("world")