def smart_comma(base, addition):
    if len(base) > 0:
        return f", {addition}"
    else:
        return addition
    
    
def get_resource_name(resource_icon):
    match resource_icon:
        case "🪙":
            return "gold"
        case "🪨":
            return "ore"
        case "🪵":
            return "wood"
        case "🔮":
            return "mana"
        case "💎":
            return "gems"
        case "🍞":
            return "food"
        case "📜":
            return "research points"
        case _:
            return "Erik forgot the tooltip"