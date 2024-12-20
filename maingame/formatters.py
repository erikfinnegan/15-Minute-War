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


def get_goblin_name():
    name_base = random.choice(["Tok", "Gor", "Grum", "Grim", "Gut", "Kork", "Mux", "Buzzz", "Ruk", "Tuk", "Zu", "Zew", "Bok", "Wok", "Rik", "Yux", "Pox",
                               "Sik", "Dux", "Fum", "Hog", "Juk", "Lug", "Zug", "Xix", "Cug", "Vit", "Nox", "Mud"])
    
    return f"{name_base}-{name_base}"


def get_goblin_title():
    roll = random.randint(1,103)

    if roll <= 50:
        return "Queen"
    elif roll <= 100:
        return "King"
    elif roll <= 101:
        return "Arch-arsonist"
    elif roll <= 102:
        return "Supreme Chancellor"
    elif roll <= 103:
        return "Almightiest"

    return "Scumbucket"


def get_goblin_ruler():
    return f"{get_goblin_title()} {get_goblin_name()}"