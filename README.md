import yaml
import subprocess
import sys

def load_data_contract(yaml_path):
    """
    Loads a data contract from a YAML file.

    :param yaml_path: The path to the YAML file containing the data contract.
    :return: A dictionary representation of the data contract.
    :raises SystemExit: If there is an error loading the YAML file.
    """
    with open(yaml_path, 'r') as file:
        try:
            data_contract = yaml.safe_load(file)
            return data_contract
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            sys.exit(1)

def test_data_contract(data_contract_path, snowflake_connection_string):
    """
    Tests a data contract against Snowflake using the DataContract CLI.

    This function uses the DataContract CLI to validate the data contract
    specified in the YAML file against a Snowflake instance. The connection
    string for Snowflake must be formatted as expected by the CLI.

    :param data_contract_path: The path to the YAML file containing the data contract.
    :param snowflake_connection_string: The Snowflake connection string, including user, password,
                                        account, database, schema, warehouse, and role.
    :return: None
    :raises SystemExit: If the DataContract CLI command fails to execute.
    """
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

if __name__ == "__main__":
    # Path to your data contract YAML file and Snowflake connection string
    data_contract_path = "path/to/your/data_contract.yaml"
    snowflake_connection_string = "snowflake://<user>:<password>@<account>/<database>/<schema>?warehouse=<warehouse>&role=<role>"

    # Test the data contract against Snowflake
    test_data_contract(data_contract_path, snowflake_connection_string)