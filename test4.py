import re
import yaml

def clean_yaml_strings(obj):
    """
    Recursively traverse a YAML-loaded object and clean string values.

    If a string matches the pattern of a double-quoted value with extra whitespace/newlines,
    extract and return only the content inside the quotes.

    :param obj: The YAML-loaded object (could be dict, list, or primitive type).
    :type obj: any
    :return: The cleaned object.
    :rtype: any
    """
    if isinstance(obj, dict):
        return {k: clean_yaml_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_yaml_strings(item) for item in obj]
    elif isinstance(obj, str):
        # This regex matches strings that start with optional whitespace, then a double quote,
        # then captures any characters (non-greedily) until the next double quote,
        # and then allows for optional trailing whitespace/newlines.
        pattern = r'^\s*"(.*?)"\s*$'
        match = re.match(pattern, obj, flags=re.DOTALL)
        if match:
            return match.group(1)
        return obj
    else:
        return obj

# --- Example usage ---
yaml_str = '''
description: |
  "fdldj"
'''

data = yaml.safe_load(yaml_str)
print("Before cleaning:")
print(repr(data['description']))  # Likely: '"fdldj"\n'
cleaned = clean_yaml_strings(data)
print("\nAfter cleaning:")
print(repr(cleaned))  # Expected: 'fdldj'