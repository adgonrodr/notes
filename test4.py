from typing import Tuple, Dict, Any
import yaml

def normalize_models_and_extract_db_schema(contract_yaml: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    - Ensures all model keys look like "<db>.<schema>.<rest>"
    - Ensures all models share the same <db> and <schema>
    - Returns (db, schema, new_contract) with model keys stripped of "<db>.<schema>."
    """
    contract = yaml.safe_load(contract_yaml)
    if "models" not in contract or not isinstance(contract["models"], dict):
        raise ValueError("Contract must contain a 'models' mapping.")

    models = contract["models"]

    dbs, schemas = set(), set()
    new_models = {}

    for full_name, model_def in models.items():
        parts = full_name.split(".")
        if len(parts) < 3:
            raise ValueError(f"Model name '{full_name}' must be '<db>.<schema>.<name>' (at least 3 segments).")

        db, schema, short_name = parts[0], parts[1], ".".join(parts[2:])
        dbs.add(db)
        schemas.add(schema)

        if short_name in new_models:
            # Collision after stripping db.schema — make the issue explicit
            raise ValueError(
                f"Model key collision after stripping db/schema: '{short_name}' already exists. "
                f"Originals: '{full_name}' and another model share the same short name."
            )

        new_models[short_name] = model_def

    if len(dbs) != 1 or len(schemas) != 1:
        raise ValueError(
            f"Mixed database/schema detected. Databases={sorted(dbs)}, Schemas={sorted(schemas)}. "
            "All models must share the same database and schema."
        )

    # Build a transformed contract (preserve everything else)
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
    db, schema, new_contract = normalize_models_and_extract_db_schema(example)
    print("DB =", db)          # -> db
    print("Schema =", schema)  # -> schema
    print(yaml.safe_dump(new_contract, sort_keys=False))


    # Ensure the 'servers' dict exists
dc.setdefault("servers", {})

for env in envs:
    # Ensure each env dict exists
    env_cfg = dc["servers"].setdefault(env, {})

    # --- Option A: upsert (overwrite existing values) ---
    env_cfg["database"] = db
    env_cfg["schema"]   = schema

    # --- Option B: only set if missing (append semantics) ---
    # env_cfg.setdefault("database", db)
    # env_cfg.setdefault("schema", schema)