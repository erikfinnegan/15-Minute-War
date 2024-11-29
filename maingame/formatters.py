import random
from string import Formatter


def smart_comma(base, addition):
    if len(base) > 0:
        return f", {addition}"
    else:
        return addition
    

def create_or_add_to_key(dict, key, amount):
    if key in dict:
        dict[key] += amount
    else:
        dict[key] = amount

    return dict


def format_minutes(minutes):
    days, minutes = divmod(minutes, 1440) # 1440 minutes in a day
    hours, minutes = divmod(minutes, 60)

    if days > 0:
        return f'{days} day{"s" if days != 1 else ""}, {hours} hour{"s" if hours != 1 else ""}'
    elif hours > 0:
        return f'{hours} hour{"s" if hours != 1 else ""}, {minutes} minute{"s" if minutes != 1 else ""}'
    else:
        return f'{minutes} minute{"s" if minutes != 1 else ""}'


def get_sludgeling_name():
    return random.choice(["Sludger", "Oozeling", "Gooper", "Marshling", "Sogger", "Squishling", "Slimezoid", "Pudling", "Swamper", "Snotling",
                              "Slurpling", "Slopling", "Dampling", "Grossling", "Slurpazoid"])