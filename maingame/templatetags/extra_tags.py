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


@register.filter(name='no_zeroes') 
def dash_if_zero(number):
    if number == 0:
        return ""
    else:
        return number


@register.filter(name='subtract') 
def subtract(value, arg):
    return value - arg


@register.filter(name='multiply') 
def multiply(value, arg):
    return value * arg


@register.filter(name='depluralize') 
def depluralize(value, arg):
    if arg == 1 and value[-1] == "s":
        return value[:-1]
    else:
        return value

@register.filter(name='percent_of') 
def percent_of(value, arg):
    return int((value / arg) * 100)