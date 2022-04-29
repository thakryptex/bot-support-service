import re


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def uncapitalize(string):
    string = string.strip()
    return string[0].lower() + string[1:]


def remove_redundant_symbols(string):
    string = re.sub(r'[^\w\s,.?!\-:/]', '', string)
    return uncapitalize(string)


def deactivate_default_factory(default_dict):
    # <хак для templates>
    default_dict.default_factory = None
    # </хак для templates>
