def compare_dicts(dict1, dict2):
    """
    Compares two dictionaries, including nested lists and dictionaries.

    :param dict1: The first dictionary to compare.
    :param dict2: The second dictionary to compare.
    :return: A tuple (is_equal, differences), where:
             - is_equal is True if the dictionaries are equal, False otherwise.
             - differences is a dictionary containing the differences.
    """
    differences = {}

    def normalize(value):
        """Normalize values to ensure consistent comparison."""
        return None if value in [None, "None"] else value

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

    def compare_lists(list1, list2, path):
        """Helper function to compare lists."""
        list_diff = []
        max_length = max(len(list1), len(list2))
        equal = True

        for i in range(max_length):
            if i >= len(list1):
                equal = False
                list_diff.append({"index": i, "value1": None, "value2": normalize(list2[i])})
            elif i >= len(list2):
                equal = False
                list_diff.append({"index": i, "value1": normalize(list1[i]), "value2": None})
            else:
                normalized_value1 = normalize(list1[i])
                normalized_value2 = normalize(list2[i])

                if isinstance(normalized_value1, dict) and isinstance(normalized_value2, dict):
                    nested_equal, nested_diff = compare_dicts(normalized_value1, normalized_value2)
                    if not nested_equal:
                        equal = False
                        list_diff.append({"index": i, "difference": nested_diff})
                elif normalized_value1 != normalized_value2:
                    equal = False
                    list_diff.append({"index": i, "value1": normalized_value1, "value2": normalized_value2})

        return equal, list_diff

    keys = set(dict1.keys()).union(set(dict2.keys()))
    equal = True

    for key in keys:
        value1 = dict1.get(key)
        value2 = dict2.get(key)
        path = key
        if normalize(value1) is None and normalize(value2) is None:
            continue
        if normalize(value1) is None:
            equal = False
            differences[path] = {"value1": None, "value2": value2}
        elif normalize(value2) is None:
            equal = False
            differences[path] = {"value1": value1, "value2": None}
        else:
            compare_values(key, value1, value2, path)

    return equal and not differences, differences


# Example usage
dict1 = {
    "name": "Alice",
    "age": None,
    "addresses": [
        {"city": "London", "postcode": None},
        {"city": "Paris", "postcode": "75000"}
    ],
    "skills": ["Python", None]
}

dict2 = {
    "name": "Alice",
    "age": "None",
    "addresses": [
        {"city": "London", "postcode": "None"},
        {"city": "Paris", "postcode": "75000"}
    ],
    "skills": ["Python", "None"]
}

is_equal, diff = compare_dicts(dict1, dict2)

import json
print("Equal:", is_equal)
print("Differences:", json.dumps(diff, indent=4))