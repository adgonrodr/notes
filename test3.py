from typing import Tuple, Dict, Any
import re
import yaml

def to_display_name(name: str) -> str:
    """
    Convert identifiers to human titles:
      - snake_case / kebab-case → title with spaces
      - camelCase / PascalCase → split on case changes
      - collapse whitespace, title case words
    """
    s = name.strip()

    # Replace non-alnum (underscore, dash, dot, etc.) with spaces
    s = re.sub(r"[^0-9A-Za-z]+", " ", s)

    # Insert spaces between camelCase boundaries: aB -> a B, or digitLetter
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    # Handle acronym followed by word: URLId -> URL Id
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)

    # Normalize spaces and title case
    s = re.sub(r"\s+", " ", s).strip()
    return s.title()

def normalize_models_and_extract_db_schema(
    contract_yaml: str,
    *,
    overwrite: bool = False
) -> Tuple[str, str, Dict[str, Any]]:
    """
    - Ensures all model keys look like "<db>.<schema>.<rest>"
    - Ensures all models share the same <db> and <schema>
    - Strips "<db>.<schema>." from model keys
    - Adds `dmg_display_name` to each model (based on table name) and to each field (based on field key).
      Use overwrite=True to replace existing dmg_display_name values.
    Returns: (db, schema, new_contract)
    """
    contract = yaml.safe_load(contract_yaml)
    if "models" not in contract or not isinstance(contract["models"], dict):
        raise ValueError("Contract must contain a 'models' mapping.")

    models = contract["models"]
    dbs, schemas = set(), set()
    new_models: Dict[str, Any] = {}

    for full_name, model_def in models.items():
        parts = full_name.split(".")
        if len(parts) < 3:
            raise ValueError(f"Model name '{full_name}' must be '<db>.<schema>.<name>' (at least 3 segments).")

        db, schema = parts[0], parts[1]
        short_path = parts[2:]                  # may be multi-segment
        short_name = ".".join(short_path)       # keep nested path if present
        table_name = short_path[-1]             # last segment is the table's simple name

        dbs.add(db)
        schemas.add(schema)

        if short_name in new_models:
            raise ValueError(
                f"Model key collision after stripping db/schema: '{short_name}' already exists "
                f"(originating from '{full_name}')."
            )

        # Copy model_def so we don't mutate the original
        md = dict(model_def) if isinstance(model_def, dict) else {"_raw": model_def}

        # Add/keep model-level display name
        model_disp = to_display_name(table_name)
        if overwrite or "dmg_display_name" not in md:
            md["dmg_display_name"] = model_disp

        # Add/keep field-level display names
        fields = md.get("fields")
        if isinstance(fields, dict):
            new_fields = {}
            for field_name, field_def in fields.items():
                fd = dict(field_def) if isinstance(field_def, dict) else {"_raw": field_def}
                field_disp = to_display_name(field_name)
                if overwrite or "dmg_display_name" not in fd:
                    fd["dmg_display_name"] = field_disp
                new_fields[field_name] = fd
            md["fields"] = new_fields

        new_models[short_name] = md

    if len(dbs) != 1 or len(schemas) != 1:
        raise ValueError(
            f"Mixed database/schema detected. Databases={sorted(dbs)}, Schemas={sorted(schemas)}. "
            "All models must share the same database and schema."
        )

    new_contract = dict(contract)
    new_contract["models"] = new_models

    db = next(iter(dbs))
    schema = next(iter(schemas))
    return db, schema, new_contract


# --------- Example usage ---------
example = r"""
models:
  db.schema.orders:
    description: One record per order. Includes cancelled and deleted orders.
    type: table
    fields:
      order_id:
        $ref: '#/definitions/order_id'
        required: true
        unique: true
        primaryKey: true
      order_timestamp:
        description: The business timestamp in UTC when the order was successfully registered in the source system and the payment was successful.
        type: timestamp
        required: true
        examples:
          - "2024-09-09T08:30:00Z"
        tags: ["business-timestamp"]
      order_total:
        description: Total amount the smallest monetary unit (e.g., cents).
        type: long
        required: true
        examples:
          - 9999
        quality:
          - type: sql
            description: 95% of all order total values are expected to be between 10 and 499 EUR.
            query: |
              SELECT quantile_cont(order_total, 0.95) AS percentile_95
              FROM orders
            mustBeBetween: [1000, 49900]
"""

if __name__ == "__main__":
    db, schema, new_contract = normalize_models_and_extract_db_schema(example, overwrite=False)
    print("DB =", db)          # -> db
    print("Schema =", schema)  # -> schema
    print(yaml.safe_dump(new_contract, sort_keys=False))