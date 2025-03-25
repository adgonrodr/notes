import os
import yaml
import copy


def get_nested_value(d: dict, field_str: str, default=None):
    """
    Retrieve the nested value from a dictionary using a dot-separated key string.

    Args:
        d (dict): The dictionary to search.
        field_str (str): A dot-separated string representing the nested keys (e.g., "info.test.field").
        default: The value to return if the nested keys don't exist (default is None).

    Returns:
        The value found at the nested key path if it exists, otherwise the default value.
    """
    keys = field_str.split('.')
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def create_dict_with_field(field_str: str, value):
    """
    Create a nested dictionary with the specified value using a dot-separated key string.

    Args:
        field_str (str): A dot-separated string representing nested keys (e.g., "info.test.field").
        value: The value to set at the nested field.

    Returns:
        dict: A dictionary with the nested structure and value.

    Example:
        create_dict_with_field("info.test.field", "value") returns:
        {
            "info": {
                "test": {
                    "field": "value"
                }
            }
        }
    """
    keys = field_str.split('.')
    nested_dict = current = {}

    for i, key in enumerate(keys):
        # If we're at the last key, assign the value
        if i == len(keys) - 1:
            current[key] = value
        else:
            # Create a new dictionary for the current key and move deeper
            current[key] = {}
            current = current[key]

    return nested_dict
def merge_pattern(merged, new, tokens):
    """
    Recursively merge a subtree of 'merged' with 'new' following the pattern tokens.

    The tokens list represents the path (which may include wildcards, "*").

    - For a literal token:
      * If the token exists in the new data, we update that branch recursively.
      * If it’s the final token, its value is replaced (while leaving siblings untouched).
      * If the token is missing in new, the original branch is left unchanged.

    - For a wildcard token ("*"):
      * If both merged and new are dictionaries, we take the union of keys (preserving the order:
        first the keys in the original, then any extra keys from the new data).
      * For each key in the union:
          - If the key exists in both, we recursively merge using the remaining tokens.
          - Otherwise, we take whichever value exists.
      * A similar strategy is used for lists.
    """
    if not tokens:
        return new

    token = tokens[0]
    rest = tokens[1:]

    if token != "*":
        # Literal token: work on a dictionary branch.
        if isinstance(merged, dict):
            if token in new:
                if rest:
                    # Descend recursively, using {} as default if the branch doesn't exist.
                    merged[token] = merge_pattern(merged.get(token, {}), new[token], rest)
                else:
                    # Final token: override with new value.
                    merged[token] = new[token]
            # If token not in new, leave merged[token] as is.
            return merged
        else:
            # Not a dict – cannot descend, so return new.
            return new
    else:
        # Wildcard token: merge dictionaries or lists.
        if isinstance(merged, dict) and isinstance(new, dict):
            # Build union of keys (preserve order: old keys first, then new keys not in old).
            union_keys = list(merged.keys())
            for key in new.keys():
                if key not in union_keys:
                    union_keys.append(key)
            new_merged = {}
            for key in union_keys:
                if key in merged and key in new:
                    new_merged[key] = merge_pattern(merged[key], new[key], rest)
                elif key in merged:
                    new_merged[key] = merged[key]
                else:
                    if not rest:
                        new_merged[key] = new[key]
                    elif rest and get_nested_value(new, f"{key}.{'.'.join(rest)}"):
                        new_merged[key] = create_dict_with_field('.'.join(rest), get_nested_value(new, '.'.join(rest)))

            return new_merged
        elif isinstance(merged, list) and isinstance(new, list):
            merged_list = []
            for i in range(max(len(merged), len(new))):
                if i < len(merged) and i < len(new):
                    merged_list.append(merge_pattern(merged[i], new[i], rest))
                elif i < len(merged):
                    merged_list.append(merged[i])
                else:
                    merged_list.append(new[i])
            return merged_list
        else:
            # If not both dicts or lists, simply return new.
            return new


def merge_yaml(old_data, new_data, merge_keys):
    """
    Merge new_data into old_data for only the paths specified in merge_keys.

    For each merge key pattern (e.g. "models.*.type" or "info.product_name"),
    the corresponding branch in old_data is updated by recursively merging
    with new_data using the rules defined in merge_pattern().

    Branches not mentioned in merge_keys remain unchanged.
    """
    merged = copy.deepcopy(old_data)
    for pattern in merge_keys:
        tokens = pattern.split('.')
        merged = merge_pattern(merged, new_data, tokens)
    return merged


def write_yaml_to_file(yaml_string, file_path, merge_keys):
    """
    Write a YAML string to a file.
    If file_path exists, load the original YAML, merge it with the new YAML using merge_keys,
    and then write the merged result.
    """
    new_data = yaml.safe_load(yaml_string)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            old_data = yaml.safe_load(f)
        merged_data = merge_yaml(old_data, new_data, merge_keys)
    else:
        merged_data = new_data
    with open(file_path, 'w') as f:
        yaml.dump(merged_data, f)
    return merged_data  # returning merged data for further use if needed


# --- Testing the merge function ---
if __name__ == '__main__':
    old_yaml_str = """
info:
  product_name: "OldProduct"
  version: "1.0"
models:
  modela:
    type: "A"
    description: "Original model A"
  modelb:
    type: "B"
    description: "Original model B"
    fields:
      field1:
        name: a
other_config:
  key1: "value1"
"""
    new_yaml_str = """
info:
  product_name: "NewProduct"
models:
  modelb:
    type: "B_new"
    fields:
      field1:
        name: b
  modelc:
    type: "C"
    description: "Original model A"
"""
    merge_keys = ["info.product_name", "models.*.type", "models.*.fields.*.name"]

    old_data = yaml.safe_load(old_yaml_str)
    new_data = yaml.safe_load(new_yaml_str)

    merged = merge_yaml(old_data, new_data, merge_keys)

    print("Merged YAML output:")
    print(yaml.dump(merged, default_flow_style=False))

    # Optionally, write to file (for demonstration we use 'merged.yaml').
    file_path = "merged.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(merged, f)
    print(f"\nYAML written to {file_path}:")
    print(yaml.dump(merged, default_flow_style=False))