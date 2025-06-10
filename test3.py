#!/usr/bin/env python3
"""
Script to uppercase all field names under the `models.*.fields` section in a YAML file using PyYAML,
preserving the rest of the structure (though comments won’t be retained by PyYAML).

Usage:
    python convert_fields_uppercase.py input.yaml -o output.yaml
If -o/--output is omitted, the result is printed to stdout.
"""
import sys
import argparse
import yaml

def uppercase_fields(stream_in, stream_out):
    # Load YAML structure
    data = yaml.safe_load(stream_in)

    models = data.get('models')
    if isinstance(models, dict):
        for model_name, model in models.items():
            if isinstance(model, dict):
                fields = model.get('fields')
                if isinstance(fields, dict):
                    # Uppercase each field key
                    new_fields = {}
                    for field_name, value in fields.items():
                        new_fields[field_name.upper()] = value
                    model['fields'] = new_fields

    # Dump back to YAML
    yaml.safe_dump(data, stream_out, default_flow_style=False, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(
        description="Uppercase field names in YAML models using PyYAML."
    )
    parser.add_argument('input', help='Path to the input YAML file')
    parser.add_argument('-o', '--output', help='Path to write the modified YAML (defaults to stdout)')
    args = parser.parse_args()

    with open(args.input, 'r') as stream_in:
        if args.output:
            with open(args.output, 'w') as stream_out:
                uppercase_fields(stream_in, stream_out)
        else:
            uppercase_fields(stream_in, sys.stdout)

if __name__ == '__main__':
    main()
