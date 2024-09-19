def smart_comma(base, addition):
    if len(base) > 0:
        return f", {addition}"
    else:
        return addition