# Tenant Resources Pre-Processor

A script to pre-process tenant resources by loading and validating data from specified directories.

## Usage

```bash
python <script_name>.py --environment <ENV> [options]
```

### Required Argument

	•	--environment / -env: Specifies the environment (e.g., dev, prod).

### Optional Arguments

	•	--resources-dir / -rd: Directory containing JSON files, columns, and templates. Default: . (current directory).
	•	--output-dir / -od: Directory for output files. Default: ./target.
	•	--log / -log: Logging level (e.g., info, debug). Default: info.

### Examples

Run with default directories:
```bash
python <script_name>.py --environment dev
```
Specify all options:
```bash
python <script_name>.py --environment prod --resources-dir ./data --output-dir ./results --log debug
```
**Note:** Replace <script_name>.py with the actual filename.



# Collibra Metadata Publisher

A script to publish metadata into Collibra, configurable for different data mesh environments. This script requires specific environment variables depending on the configuration.

## Environment Variable Requirements

The script needs environment variables set based on the `VAR` variable.

1. **Set `VAR` to specify the data source configuration**:
   - `VAR=dmconfig` (default): Uses Collibra API credentials.
   - `VAR=snowflake`: Requires Snowflake connection details.

2. **Required Environment Variables**:
   - For `DM_CONFIG=dmconfig`:
     - `COLLIBRA_API_USER`: Collibra API username.
     - `COLLIBRA_API_PASSWD`: Collibra API password.

   - For `DM_CONFIG=snowflake`:
     - `SNOWFLAKE_USER`: Snowflake username.
     - `SNOWFLAKE_PASSWORD`: Snowflake password.
     - `SNOWFLAKE_ACCOUNT`: Snowflake account identifier.
     - `SNOWFLAKE_DATABASE`: Snowflake database name.
     - `SNOWFLAKE_WAREHOUSE`: Snowflake warehouse name.

## Usage

```bash
python <script_name>.py --env <ENV> [options]
```

## Required Argument

	•	--env / -e: Specifies the data mesh environment (e.g., dev, prod).

## Optional Arguments

	•	--resources-dir / -rd: Directory containing JSON files, columns, and templates. Default: . (current directory).
	•	--log / -log: Logging level (e.g., info, debug). Default: info.
	•	--dry-run / -d: Skips main actions and runs in dry mode. Default: False. Automatically enabled in dev environment.

## Examples

Run in production mode with Collibra API:
```bash
export DM_CONFIG=dmconfig
export COLLIBRA_API_USER=<your_collibra_user>
export COLLIBRA_API_PASSWD=<your_collibra_password>
python <script_name>.py --env prod```

Run in production mode with Snowflake:
```bash
export DM_CONFIG=snowflake
export SNOWFLAKE_USER=<your_snowflake_user>
export SNOWFLAKE_PASSWORD=<your_snowflake_password>
export SNOWFLAKE_ACCOUNT=<your_snowflake_account>
export SNOWFLAKE_DATABASE=<your_snowflake_database>
export SNOWFLAKE_WAREHOUSE=<your_snowflake_warehouse>
python <script_name>.py --env prod```

**Note:** Replace <script_name>.py with the actual filename and <> secrets by its real values.