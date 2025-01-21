def compare_dicts(dict1, dict2):
    """
    Compares two dictionaries, including nested lists and dictionaries.
    Order of lists and dictionaries does not matter.

    :param dict1: The first dictionary to compare.
    :param dict2: The second dictionary to compare.
    :return: A tuple (is_equal, differences), where:
             - is_equal is True if the dictionaries are equal, False otherwise.
             - differences is a dictionary containing the differences.
    """
    differences = {}

    def normalize(value):
        """Normalize values to ensure consistent comparison."""
        if value in [None, "None"]:
            return None
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            # Recursively normalize and sort lists
            return sorted([normalize(v) for v in value], key=lambda x: str(x))
        return value

    def compare_lists(list1, list2, path):
        """Compares two lists, ignoring order and accounting for nested structures."""
        normalized_list1 = sorted([normalize(item) for item in list1], key=str)
        normalized_list2 = sorted([normalize(item) for item in list2], key=str)

        if normalized_list1 != normalized_list2:
            return False, {
                "value1": list1,
                "value2": list2,
                "normalized_value1": normalized_list1,
                "normalized_value2": normalized_list2,
            }
        return True, None

    def compare_values(key, value1, value2, path):
        """Helper function to compare values."""
        value1 = normalize(value1)
        value2 = normalize(value2)

        if isinstance(value1, dict) and isinstance(value2, dict):
            nested_equal, nested_diff = compare_dicts(value1, value2)
            if not nested_equal:
                differences[path] = nested_diff
        elif isinstance(value1, list) and isinstance(value2, list):
            list_equal, list_diff = compare_lists(value1, value2, path)
            if not list_equal:
                differences[path] = list_diff
        elif value1 != value2:
            differences[path] = {"value1": value1, "value2": value2}

    keys = set(dict1.keys()).union(set(dict2.keys()))
    equal = True

    for key in keys:
        value1 = dict1.get(key)
        value2 = dict2.get(key)
        path = key
        if normalize(value1) != normalize(value2):
            equal = False
            compare_values(key, value1, value2, path)

    return equal and not differences, differences


