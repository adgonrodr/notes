#!/usr/bin/env python3
"""
Script to uppercase all field names under the `models.*.fields` section in a YAML file,
preserving the rest of the structure, comments, and formatting.

Usage:
    python convert_fields_uppercase.py input.yaml -o output.yaml
If -o/--output is omitted, the result is printed to stdout.
"""
import sys
import argparse
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

def uppercase_fields(stream_in, stream_out):
    yaml = YAML()
    yaml.preserve_quotes = True
    data = yaml.load(stream_in)

    # Traverse models and uppercase field names
    models = data.get('models')
    if not isinstance(models, dict):
        yaml.dump(data, stream_out)
        return

    for model_name, model in models.items():
        if not isinstance(model, dict):
            continue
        fields = model.get('fields')
        if not isinstance(fields, dict):
            continue

        # Build a new mapping with uppercase keys
        new_fields = type(fields)()
        for field_name, value in fields.items():
            new_fields[field_name.upper()] = value
        # Replace the old mapping
        model['fields'] = new_fields

    yaml.dump(data, stream_out)


def main():
    parser = argparse.ArgumentParser(
        description="Uppercase field names in YAML models while preserving formatting."
    )
    parser.add_argument('input', help='Path to the input YAML file')
    parser.add_argument('-o', '--output', help='Path to write the modified YAML (defaults to stdout)')
    args = parser.parse_args()

    # Open input and output streams
    with open(args.input, 'r') as stream_in:
        if args.output:
            with open(args.output, 'w') as stream_out:
                uppercase_fields(stream_in, stream_out)
        else:
            uppercase_fields(stream_in, sys.stdout)

if __name__ == '__main__':
    main()
