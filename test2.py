import os
import yaml
import copy
from typing import Any, List, Dict

class YamlMerger:
    def __init__(self, merge_keys: List[str]) -> None:
        """
        Initialize YamlMerger with a list of merge key patterns.

        :param merge_keys: A list of merge key patterns (e.g., "models.*.type" or "info.product_name").
        :type merge_keys: list of str
        """
        self.merge_keys = merge_keys

    @staticmethod
    def get_nested_value(d: Dict[Any, Any], field_str: str, default: Any = None) -> Any:
        """
        Retrieve the nested value from a dictionary using a dot-separated key string.

        :param d: The dictionary to search.
        :type d: dict
        :param field_str: A dot-separated string representing the nested keys (e.g., "info.test.field").
        :type field_str: str
        :param default: The value to return if the nested keys don't exist.
        :type default: Any
        :return: The value found at the nested key path if it exists, otherwise the default value.
        :rtype: Any
        """
        keys = field_str.split('.')
        current = d
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    @staticmethod
    def create_dict_with_field(field_str: str, value: Any) -> Dict[str, Any]:
        """
        Create a nested dictionary with the specified value using a dot-separated key string.

        :param field_str: A dot-separated string representing nested keys (e.g., "info.test.field").
        :type field_str: str
        :param value: The value to set at the nested field.
        :type value: Any
        :return: A dictionary with the nested structure and value.
        :rtype: dict

        Example:
            >>> YamlMerger.create_dict_with_field("info.test.field", "value")
            {'info': {'test': {'field': 'value'}}}
        """
        keys = field_str.split('.')
        nested_dict = current = {}
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                current[key] = value
            else:
                current[key] = {}
                current = current[key]
        return nested_dict

    @classmethod
    def merge_pattern(cls, merged: Any, new: Any, tokens: List[str]) -> Any:
        """
        Recursively merge a subtree of 'merged' with 'new' following the pattern tokens.

        :param merged: The original data structure (dict or list) to merge into.
        :type merged: Any
        :param new: The new data structure (dict or list) to merge from.
        :type new: Any
        :param tokens: A list of tokens representing the path, which may include wildcards ("*").
        :type tokens: list of str
        :return: The merged data structure.
        :rtype: Any

        The tokens list represents the path (which may include wildcards, "*").

        - For a literal token:
          * If the token exists in the new data, update that branch recursively.
          * If it’s the final token, override its value (leaving siblings untouched).
          * If the token is missing in new, the original branch is left unchanged.

        - For a wildcard token ("*"):
          * If both merged and new are dictionaries, take the union of keys (preserving order:
            keys in the original first, then any extra keys from the new data).
          * For each key in the union:
              - If the key exists in both, recursively merge using the remaining tokens.
              - Otherwise, take whichever value exists.
          * A similar strategy is used for lists.
        """
        if not tokens:
            return new

        token = tokens[0]
        rest = tokens[1:]

        if token != "*":
            if isinstance(merged, dict):
                if token in new:
                    if rest:
                        merged[token] = cls.merge_pattern(merged.get(token, {}), new[token], rest)
                    else:
                        merged[token] = new[token]
                return merged
            else:
                return new
        else:
            if isinstance(merged, dict) and isinstance(new, dict):
                # Build union of keys (preserve order: original keys first, then new keys).
                union_keys = list(merged.keys())
                for key in new.keys():
                    if key not in union_keys:
                        union_keys.append(key)
                new_merged = {}
                for key in union_keys:
                    if key in merged and key in new:
                        new_merged[key] = cls.merge_pattern(merged[key], new[key], rest)
                    elif key in merged:
                        new_merged[key] = merged[key]
                    else:
                        if not rest:
                            new_merged[key] = new[key]
                        elif rest and cls.get_nested_value(new, f"{key}.{'.'.join(rest)}"):
                            new_merged[key] = cls.create_dict_with_field(
                                '.'.join(rest),
                                cls.get_nested_value(new, f"{key}.{'.'.join(rest)}")
                            )
                return new_merged
            elif isinstance(merged, list) and isinstance(new, list):
                merged_list = []
                for i in range(max(len(merged), len(new))):
                    if i < len(merged) and i < len(new):
                        merged_list.append(cls.merge_pattern(merged[i], new[i], rest))
                    elif i < len(merged):
                        merged_list.append(merged[i])
                    else:
                        merged_list.append(new[i])
                return merged_list
            else:
                return new

    def merge_yaml(self, old_data: Dict[Any, Any], new_data: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Merge new_data into old_data for only the paths specified in self.merge_keys.

        :param old_data: The original YAML data as a dictionary.
        :type old_data: dict
        :param new_data: The new YAML data as a dictionary.
        :type new_data: dict
        :return: The merged YAML data as a dictionary.
        :rtype: dict

        For each merge key pattern, the corresponding branch in old_data is updated by recursively merging
        with new_data using the rules defined in merge_pattern().

        Branches not mentioned in merge_keys remain unchanged.
        """
        merged = copy.deepcopy(old_data)
        for pattern in self.merge_keys:
            tokens = pattern.split('.')
            merged = self.merge_pattern(merged, new_data, tokens)
        return merged

    def write_yaml_to_file(self, yaml_string: str, file_path: str) -> Dict[Any, Any]:
        """
        Write a YAML string to a file, merging with existing YAML data if the file exists.

        :param yaml_string: The YAML data as a string.
        :type yaml_string: str
        :param file_path: The path to the YAML file.
        :type file_path: str
        :return: The merged YAML data as a dictionary.
        :rtype: dict

        If the file at file_path exists, load the original YAML, merge it with the new YAML using self.merge_keys,
        and then write the merged result to the file. If the file does not exist, the new YAML data is written directly.
        """
        new_data = yaml.safe_load(yaml_string)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                old_data = yaml.safe_load(f)
            merged_data = self.merge_yaml(old_data, new_data)
        else:
            merged_data = new_data
        with open(file_path, 'w') as f:
            yaml.dump(merged_data, f)
        return merged_data


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

    merger = YamlMerger(merge_keys)
    merged = merger.merge_yaml(old_data, new_data)

    print("Merged YAML output:")
    print(yaml.dump(merged, default_flow_style=False))

    # Optionally, write to file (for demonstration we use 'merged.yaml').
    file_path = "merged.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(merged, f)
    print(f"\nYAML written to {file_path}:")
    print(yaml.dump(merged, default_flow_style=False))