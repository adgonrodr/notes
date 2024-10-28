# Collibra Metadata Publisher

A script to publish metadata into Collibra, configurable for different data sources, including Snowflake and Unity Catalog, based on the `METADATA_SOURCE_TYPE` environment variable.

## Environment Variable Requirements

The required environment variables depend on the `METADATA_SOURCE_TYPE` setting. There are also some common environment variables that must be set regardless of the data source type.

### Common Environment Variables

These variables are required for all configurations:
- `DEBUG_OUTPUT_TO_DISK`: Enables debug output to disk if set.
- `UNSAFE_SKIP_COLLIBRA_VALIDATION`: Skips Collibra validation if set to `true`.
- `COLLIBRA_API_USER`: Collibra API username.
- `COLLIBRA_API_PASSWD`: Collibra API password.
- `COLLIBRA_CONFIG_OVERRIDE`: Optional Collibra configuration override.
- `TENANT_TYPE`: Defines the tenant type.
- `METADATA_SOURCE_TYPE`: Specifies the data source type (`DMCONFIG`, `SNOWFLAKE`, or `UNITYCATALOG`).

### Data Source-Specific Environment Variables

Set `METADATA_SOURCE_TYPE` to determine the required additional environment variables.

1. **`METADATA_SOURCE_TYPE=DMCONFIG`** (default): Requires only the common Collibra API environment variables.

2. **`METADATA_SOURCE_TYPE=SNOWFLAKE`**: Requires the following in addition to the common variables:
   - `SNOWFLAKE_DBNAME`: Snowflake database name.
   - `SNOWFLAKE_DBSCHEMA`: Snowflake schema name.
   - `SNOWFLAKE_SECRET_KEY`: Secret key for Snowflake connection.
   - `TENANT_NAME`: Tenant name for the Snowflake configuration.

3. **`METADATA_SOURCE_TYPE=UNITYCATALOG`**: Requires the following in addition to the common variables:
   - `TENANT_UNITYCATALOG_NAME`: Unity Catalog tenant name.
   - `TENANT_UNITYCATALOG_SCHEMA`: Unity Catalog schema name.
   - `SERVICE_PRINCIPAL_OAUTH_TOKEN`: OAuth token for Unity Catalog service principal authentication.

## Usage

```bash
python <script_name>.py --env <ENV> [options]
```

Required Argument

	•	--env / -e: Specifies the data mesh environment (e.g., dev, prod).

Optional Arguments

	•	--resources-dir / -rd: Directory containing JSON files, columns, and templates. Default: . (current directory).
	•	--log / -log: Logging level (e.g., info, debug). Default: info.
	•	--dry-run / -d: Skips main actions and runs in dry mode. Default: False. Automatically enabled in dev environment.

Examples

Run in production mode with Collibra API:
```bash
export METADATA_SOURCE_TYPE=DMCONFIG
export COLLIBRA_API_USER=<your_collibra_user>
export COLLIBRA_API_PASSWD=<your_collibra_password>
python <script_name>.py --env prod
```

Run with Snowflake as the metadata source:
```bash
export METADATA_SOURCE_TYPE=SNOWFLAKE
export COLLIBRA_API_USER=<your_collibra_user>
export COLLIBRA_API_PASSWD=<your_collibra_password>
export SNOWFLAKE_DBNAME=<your_snowflake_dbname>
export SNOWFLAKE_DBSCHEMA=<your_snowflake_dbschema>
export SNOWFLAKE_SECRET_KEY=<your_snowflake_secret_key>
export TENANT_NAME=<your_tenant_name>
python <script_name>.py --env prod
```

Run with Unity Catalog as the metadata source:
```bash
export METADATA_SOURCE_TYPE=UNITYCATALOG
export COLLIBRA_API_USER=<your_collibra_user>
export COLLIBRA_API_PASSWD=<your_collibra_password>
export TENANT_UNITYCATALOG_NAME=<your_unitycatalog_name>
export TENANT_UNITYCATALOG_SCHEMA=<your_unitycatalog_schema>
export SERVICE_PRINCIPAL_OAUTH_TOKEN=<your_oauth_token>
python <script_name>.py --env prod
```
