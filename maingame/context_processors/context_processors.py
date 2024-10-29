from maingame.models import Dominion, Round


def dominion_context_processor(request):
    active_dominion = None

    if request.user.is_authenticated:
        active_dominion = Dominion.objects.filter(associated_user=request.user).first()
        
    return {
        "active_dominion": active_dominion,
        "round": Round.objects.first(),
    }