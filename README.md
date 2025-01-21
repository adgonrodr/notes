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

    def compare_values(key, value1, value2, path):
        """Helper function to compare values."""
        if isinstance(value1, dict) and isinstance(value2, dict):
            nested_equal, nested_diff = compare_dicts(value1, value2)
            if not nested_equal:
                differences[path] = nested_diff
        elif isinstance(value1, list) and isinstance(value2, list):
            list_equal, list_diff = compare_lists(value1, value2, path)
            if not list_equal:
                differences[path] = list_diff
        elif value1 != value2:
            # Handle None and 'None' comparison
            if value1 is None and value2 == 'None':
                return
            if value2 is None and value1 == 'None':
                return
            differences[path] = {"value1": value1, "value2": value2}

    def compare_lists(list1, list2, path):
        """Helper function to compare lists."""
        list_diff = []
        max_length = max(len(list1), len(list2))
        equal = True

        for i in range(max_length):
            if i >= len(list1):
                equal = False
                list_diff.append({"index": i, "value1": None, "value2": list2[i]})
            elif i >= len(list2):
                equal = False
                list_diff.append({"index": i, "value1": list1[i], "value2": None})
            else:
                if isinstance(list1[i], dict) and isinstance(list2[i], dict):
                    nested_equal, nested_diff = compare_dicts(list1[i], list2[i])
                    if not nested_equal:
                        equal = False
                        list_diff.append({"index": i, "difference": nested_diff})
                elif list1[i] != list2[i]:
                    # Handle None and 'None' comparison
                    if list1[i] is None and list2[i] == 'None':
                        continue
                    if list2[i] is None and list1[i] == 'None':
                        continue
                    equal = False
                    list_diff.append({"index": i, "value1": list1[i], "value2": list2[i]})

        return equal, list_diff

    keys = set(dict1.keys()).union(set(dict2.keys()))
    equal = True

    for key in keys:
        value1 = dict1.get(key)
        value2 = dict2.get(key)
        path = key
        if value1 is None and value2 is None:
            continue
        if value1 is None:
            equal = False
            differences[path] = {"value1": None, "value2": value2}
        elif value2 is None:
            equal = False
            differences[path] = {"value1": value1, "value2": None}
        else:
            compare_values(key, value1, value2, path)

    return equal and not differences, differences