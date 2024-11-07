import yaml
import subprocess
import sys
import os

# Load the YAML data contract
def load_data_contract(yaml_path):
    with open(yaml_path, 'r') as file:
        try:
            data_contract = yaml.safe_load(file)
            return data_contract
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            sys.exit(1)

# Run DataContract CLI to test the data contract against Snowflake
def test_data_contract(data_contract_path, snowflake_connection_string):
    # Load the data contract to confirm the path
    data_contract = load_data_contract(data_contract_path)
    print(f"Data contract loaded: {data_contract}")

    # Construct the DataContract CLI command
    command = [
        "datacontract", "test",  # or 'validate' based on your CLI
        "--config", data_contract_path,
        "--connection", snowflake_connection_string  # Adjust this based on CLI options
    ]

    try:
        # Execute the DataContract CLI command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"DataContract CLI Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error running DataContract CLI: {e.stderr}")
        sys.exit(1)

# Path to your data contract YAML file and Snowflake connection string
data_contract_path = "path/to/your/data_contract.yaml"
snowflake_connection_string = "snowflake://<user>:<password>@<account>/<database>/<schema>?warehouse=<warehouse>&role=<role>"

# Test the data contract against Snowflake
if __name__ == "__main__":
    test_data_contract(data_contract_path, snowflake_connection_string)