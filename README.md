import os
import snowflake.connector
from snowflake.connector import Error
from cryptography.hazmat.primitives import serialization

class SnowflakeConnection:
    def __init__(self, account=None, warehouse=None, database=None, schema=None, role=None):
        """
        Initialize SnowflakeConnection with connection settings.

        :param account: Snowflake account name. Defaults to environment variable SNOWFLAKE_ACCOUNT.
        :param warehouse: Snowflake warehouse name. Defaults to environment variable SNOWFLAKE_WAREHOUSE.
        :param database: Snowflake database name. Defaults to environment variable SNOWFLAKE_DATABASE.
        :param schema: Snowflake schema name. Defaults to environment variable SNOWFLAKE_SCHEMA.
        :param role: Snowflake role name. Defaults to environment variable SNOWFLAKE_ROLE.
        """
        self.account = account or os.getenv("SNOWFLAKE_ACCOUNT")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        self.role = role or os.getenv("SNOWFLAKE_ROLE")
        self.connection = None

    def connect(self, user=None, password=None, private_key=None, private_key_passphrase=None, authenticator=None):
        """
        Establish a connection to Snowflake using multiple authentication methods.

        :param user: Snowflake username. Defaults to environment variable SNOWFLAKE_USER.
        :param password: Snowflake password. Defaults to environment variable SNOWFLAKE_PASSWORD.
        :param private_key: Path to private key file for key-pair authentication.
        :param private_key_passphrase: Passphrase for the private key, if encrypted.
        :param authenticator: Authentication method. Use 'externalbrowser' for browser-based SSO or 'okta' for Okta.
                              Defaults to None.
        :return: Connection object if successful, or None if connection fails.
        """
        user = user or os.getenv("SNOWFLAKE_USER")
        password = password or os.getenv("SNOWFLAKE_PASSWORD")

        connection_params = {
            "account": self.account,
            "warehouse": self.warehouse,
            "database": self.database,
            "schema": self.schema,
            "role": self.role,
        }

        try:
            if authenticator == "externalbrowser":
                # External Browser Authentication
                connection_params.update({"authenticator": "externalbrowser", "user": user})
            elif private_key:
                # Key Pair Authentication
                with open(private_key, "rb") as key_file:
                    private_key_obj = serialization.load_pem_private_key(
                        key_file.read(),
                        password=private_key_passphrase.encode() if private_key_passphrase else None
                    )
                connection_params.update({"private_key": private_key_obj, "user": user})
            else:
                # Username and Password Authentication
                connection_params.update({"user": user, "password": password})

            # Attempt to connect to Snowflake
            self.connection = snowflake.connector.connect(**connection_params)
            print("Connection to Snowflake established. Testing connection...")

            # Test the connection with a lightweight query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()

            print("Connection test successful.")
            return self.connection

        except Error as e:
            if self.connection:
                self.connection.close()
            print(f"Failed to connect to Snowflake: {e}")
            return None

    def execute_query(self, query):
        """
        Execute a query on the Snowflake database.

        :param query: SQL query string.
        :return: List of query results or None if query fails.
        """
        if not self.connection:
            print("No active connection. Please connect first.")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Failed to execute query: {e}")
            return None

    def close(self):
        """
        Close the Snowflake connection.
        """
        if self.connection:
            self.connection.close()
            print("Snowflake connection closed.")
        else:
            print("No connection to close.")

# Example usage:
if __name__ == "__main__":
    # Define connection details through environment variables or directly
    conn = SnowflakeConnection()

    # Example 1: Username and Password Authentication
    connection = conn.connect(user="your_username", password="your_password")
    
    # Example 2: Key-Pair Authentication
    # connection = conn.connect(user="your_username", private_key="path_to_private_key.pem", private_key_passphrase="your_passphrase")

    # Example 3: External Browser Authentication
    # connection = conn.connect(user="your_username", authenticator="externalbrowser")

    if connection:
        results = conn.execute_query("SELECT CURRENT_DATE;")
        print(results)
        conn.close()