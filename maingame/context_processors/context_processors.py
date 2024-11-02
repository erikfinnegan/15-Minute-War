from maingame.models import Dominion, Round, UserSettings


def dominion_context_processor(request):
    active_dominion = None

    if request.user.is_authenticated:
        active_dominion = Dominion.objects.filter(associated_user=request.user).first()
        active_user_settings = UserSettings.objects.filter(associated_user=request.user).first()
    elif UserSettings.objects.filter(associated_user=None).exists():
        active_dominion = False
        active_user_settings = UserSettings.objects.filter(associated_user=None).first()
    else:
        active_dominion = False
        active_user_settings = UserSettings.objects.create(theme="OpenDominion")
        
    return {
        "active_dominion": active_dominion,
        "active_user_settings": active_user_settings,
        "round": Round.objects.first(),
    }