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