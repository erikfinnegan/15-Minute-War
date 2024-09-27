from django import template

register = template.Library()

@register.filter(name='getattr')
def getattrfilter(o, attr):
    try:
        # return getattr(o, attr)
        return o[attr]
    except Exception as e:
        return f"getattr_error {e}"
    

@register.filter(name='hasattr')
def hasattrfilter(o, attr):
    try:
        return hasattr(o, attr)
    except:
        return "hasattr_error"
    

@register.filter(name='times') 
def times(number):
    return range(number)


@register.filter(name='multiply') 
def multiply(value, arg):
    return value * arg

@register.filter(name='involves_player')
def involves_player(event, player_id):
    print()
    print(event)
    print()
    # b_id = int(benefit_id)
    return event.notified_players.filter(id=int(player_id)).count() > 0
    # return user.benefits.filter(id=b_id).count() > 0