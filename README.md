```bash
├── cli                                       # Command-line interface (CLI) utilities
│   ├── lib                                   # Library for CLI operations
│   │   ├── templating                        # Folder for templating utilities
│   │   │   ├── target                        # Target folder for build artifacts
│   │   │   ├── venv                          # Virtual environment folder for Python dependencies
│   │   │   ├── .gitignore                    # Git ignore file to exclude files and directories
│   │   │   ├── .pre-commit-config.yaml       # Pre-commit hook configuration
│   │   │   ├── generate_schema_docs.sh       # Script to generate schema documentation
│   │   │   ├── README.md                     # Project documentation and overview
│   │   │   ├── requirements.txt              # Python project dependencies
│   │   │   ├── templating-engine.py          # Python script for the templating engine
│   │   │   ├── tenant_schema.json            # JSON schema file for the tenant configuration
│   │   │   └── tenant_schema.md              # Markdown file for the tenant schema documentation
```


```bash
├── cli                                      # Command-line interface (CLI) utilities
│   ├── lib                                  # Library for CLI operations
│   │   ├── collibra                         # Collibra module for interacting with Collibra API and workflows
│   │   │   ├── adapter                      # Adapter for connecting with Collibra API
│   │   │   ├── venv                         # Virtual environment for Python dependencies
│   │   │   ├── __init__.py                  # Initialization file for the Collibra package
│   │   │   ├── all_dataproduct_req_body.json # JSON file for all data product request body
│   │   │   ├── collibra.py                  # Main script for Collibra-related functions
│   │   │   ├── collibra_linking.py          # Script for linking metadata in Collibra
│   │   │   ├── collibra_original.py         # Script for original Collibra metadata handling
│   │   │   ├── collibra_utils.py            # Utility functions for Collibra interactions
│   │   │   ├── CollibraWorkflowOrchestrator.py # Orchestrator script for Collibra workflows
│   │   │   ├── dev.env_mapping.json         # Development environment mapping JSON
│   │   │   ├── enum_action.py               # Enum definitions for various actions
│   │   │   ├── env_mapping.json             # General environment mapping JSON
│   │   │   ├── EnvConfigReader.py           # Configuration reader for environment settings
│   │   │   ├── logger.ini                   # Logger configuration file
│   │   │   ├── prod.env_mapping.json        # Production environment mapping JSON
│   │   │   ├── README.md                    # Project documentation and overview
│   │   │   ├── requirements.txt             # Python dependencies
│   │   │   ├── Test.py                      # Test script for Collibra functions
│   │   │   └── uat.env_mapping.json         # UAT environment mapping JSON
```

1. Templating Engine - README Overview

The Templating Engine is designed to streamline the extraction and transformation of metadata from DMG configurations into a format compatible with downstream systems like Collibra. This engine supports various metadata formats, enabling organizations to automate the creation of data contracts and governance artifacts based on predefined templates.

By utilizing this engine, users can reduce manual metadata handling, maintain consistency across environments, and accelerate the integration of data governance processes into their workflows. The engine is highly customizable, with support for templating systems such as Jinja2, ensuring flexibility in metadata management and transformation.

Key features:

	•	Extracts metadata from DMG configurations.
	•	Transforms metadata into data contracts.
	•	Supports integration with Collibra for metadata management.
	•	Customizable templates for diverse use cases.

2. Collibra Tenant Engine Module - README Overview

The Collibra Tenant Engine Module facilitates proactive, federated data governance by automating metadata management within Collibra. This module ensures that logical and physical metadata are synced across different environments, promoting consistency and reducing the risk of discrepancies during deployments.

The engine empowers tenants to self-govern their data by validating business metadata prior to deployment and automatically syncing technical metadata post-deployment. With integrated workflow orchestration and environment mapping, the module ensures that both business and technical metadata remain aligned and compliant with governance policies. The engine also performs critical checks that flag issues in earlier environments to prevent problematic production deployments.

Key features:

	•	Automates the syncing of logical and physical metadata in Collibra.
	•	Supports pre-deployment validation of business metadata.
	•	Enables automatic technical metadata synchronization po