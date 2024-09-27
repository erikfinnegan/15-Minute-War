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
