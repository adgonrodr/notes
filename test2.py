import yaml
from snowflake.snowpark import Session

# --- 1. Load YAML and pull out the field names for a given model ---
def load_contract_fields(yaml_path: str, model_name: str) -> set:
    with open(yaml_path, 'r') as f:
        spec = yaml.safe_load(f)
    model = spec['models'].get(model_name)
    if not model:
        raise ValueError(f"Model '{model_name}' not found in spec")
    return set(model['fields'].keys())

# --- 2. Use Snowpark to get the column names of the table/view ---
def fetch_snowflake_columns_snowpark(
    connection_params: dict,
    database: str,
    schema: str,
    view_name: str,
) -> set:
    """
    connection_params should include keys:
      user, password, account, role, warehouse, database, schema
    """
    # 2A. Create a Snowpark Session
    session = Session.builder.configs(connection_params).create()
    
    # 2B. Load the table/view as a DataFrame and read its schema
    df = session.table(f"{database}.{schema}.{view_name}")
    
    # 2C. Extract the field names
    cols = {field.name.lower() for field in df.schema.fields}
    
    session.close()
    return cols

# --- 3. Compare the two sets and print differences ---
def compare_fields(contract_fields: set, actual_columns: set):
    only_in_contract = sorted(contract_fields - actual_columns)
    only_in_db       = sorted(actual_columns - contract_fields)

    if only_in_contract:
        print("Fields defined in data contract but missing in Snowflake:")
        for f in only_in_contract:
            print(f"  – {f}")
    else:
        print("✅ All contract fields are present in Snowflake.")
    
    if only_in_db:
        print("\nColumns in Snowflake but not in the data contract:")
        for c in only_in_db:
            print(f"  – {c}")
    else:
        print("✅ No extra columns in Snowflake.")

# --- 4. Put it all together ---
if __name__ == "__main__":
    # 4A. YAML and model
    YAML_PATH  = "path/to/contract.yaml"
    MODEL_NAME = "orders"

    # 4B. Snowflake connection params
    SF_CONN = {
        "account":   "<your_account>",
        "user":      "<your_username>",
        "password":  "<your_password>",
        "role":      "<your_role>",
        "warehouse": "<your_warehouse>",
        "database":  "<your_database>",
        "schema":    "<your_schema>",
    }

    VIEW_NAME = "ORDERS"  # Upper‐case or as defined in Snowflake

    # 4C. Run comparison
    contract_fields = load_contract_fields(YAML_PATH, MODEL_NAME)
    db_columns      = fetch_snowflake_columns_snowpark(
                          SF_CONN,
                          SF_CONN["database"],
                          SF_CONN["schema"],
                          VIEW_NAME
                      )
    compare_fields(contract_fields, db_columns)