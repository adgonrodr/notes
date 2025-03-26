import random
from typing import Dict, Any, List


def sort_yaml_obj(obj: Dict[str, Any], key_order: List[str]) -> Dict[str, Any]:
    """
    Sort a dictionary according to a specified key order. Any keys in the dictionary that are not
    included in key_order will be appended in a random order at the end.

    :param obj: The dictionary (YAML object) to sort.
    :type obj: dict
    :param key_order: A list of keys defining the desired order.
                      Keys in obj that are not in this list will be appended randomly.
    :type key_order: list of str
    :return: A new dictionary sorted according to key_order, with remaining keys in random order.
    :rtype: dict
    """
    sorted_dict = {}

    # Add keys that are specified in key_order in the given order.
    for key in key_order:
        if key in obj:
            sorted_dict[key] = obj[key]

    # Collect keys not in key_order.
    remaining_keys = [k for k in obj if k not in key_order]
    random.shuffle(remaining_keys)  # Randomize the order of remaining keys.

    # Append the remaining keys.
    for key in remaining_keys:
        sorted_dict[key] = obj[key]

    return sorted_dict


# --- Example usage ---
if __name__ == "__main__":
    # Simulate a YAML-loaded dictionary.
    yaml_obj = {
        "b": 2,
        "a": 1,
        "d": 4,
        "c": 3,
    }
    desired_order = ["a", "b"]

    sorted_yaml = sort_yaml_obj(yaml_obj, desired_order)
    print("Sorted YAML object:")
    print(sorted_yaml)