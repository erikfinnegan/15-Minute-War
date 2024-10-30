from maingame.models import Dominion, Round, UserSettings


def dominion_context_processor(request):
    active_dominion = None

    if request.user.is_authenticated:
        print("aaa")
        active_dominion = Dominion.objects.filter(associated_user=request.user).first()
        active_user_settings = UserSettings.objects.filter(associated_user=request.user).first()
    elif UserSettings.objects.filter(associated_user=None).exists():
        print("bbb")
        active_dominion = False
        active_user_settings = UserSettings.objects.filter(associated_user=None).first()
    else:
        print("ccc")
        active_dominion = False
        active_user_settings = UserSettings.objects.create()
        
    return {
        "active_dominion": active_dominion,
        "active_user_settings": active_user_settings,
        "round": Round.objects.first(),
    }