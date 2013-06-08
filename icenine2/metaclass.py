def enum(name, mro, attributes):
    # Add frozenset of values to the class
    values = []
    for key, value in attributes.items():
        if key.isupper():
            values.append(value)
    attributes['values'] = frozenset(values)

    choices = {}
    for key, value in attributes.items():
        if key.isupper():
            choices[key] = value
    attributes['choices'] = choices

    return type(name, mro, attributes)