from maingame.models import Player


def player_context_processor(request):
    active_player = None

    if request.user.is_authenticated:
        active_player = Player.objects.get(associated_user=request.user)
        
    return {
        "active_player": active_player,
    }