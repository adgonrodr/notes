# Collibra Tenant Engine

## Overview

The Collibra Tenant Engine is a comprehensive toolkit designed to simplify integration with Collibra, enabling proactive federated data governance. This engine populates logical metadata, ensures consistency across environments, and triggers Collibra workflows to synchronize and link physical and logical metadata.

The tool supports various input formats, including DM configurations, data contracts, and Snowflake tags, facilitating metadata management within Collibra. It provides pipelines to automate the end-to-end process and includes a Docker image for simplified deployment.

## Features

* Metadata Population: Supports the ingestion of DM configurations, data contracts, and Snowflake tags into Collibra.
* Metadata Consistency Validation: Ensures logical and physical metadata are consistently aligned across different environments.
* Workflow Automation: Triggers Collibra workflows for syncing physical and logical metadata.
* Automated Pipelines: Provides GitHub Actions and CI/CD pipelines to automate the end-to-end process.
* Dockerized Deployment: Includes a Docker image for easy deployment.
* DMG Config to Data Contract Translation: Translates DMG configurations into Data Contracts, improving transparency and reducing ambiguity.

## Proactive Federated Data Governance

This engine enables tenants to self-govern their data by defining and approving business metadata before deployment, ensuring alignment with business outcomes. Post-deployment, technical metadata is synced directly from the data platform and linked to the business metadata to maintain consistency.

The engine performs validation checks to ensure metadata consistency across environments. Any discrepancies flagged are addressed before reaching production, blocking non-compliant deployments and reducing the risk of errors and misalignment.

## Repository Structure
```md
├── docs
│   ├── dmg_datacontract.schema.md      # DMG Data Contract specification
│   ├── original_datacontract.schema.md # Original Data Contract specification from datacontract-cli
│   ├── platform_schema.md              # Tenant platform config specification
│   ├── task_schema.md                  # Tenant task configuration specification
│   ├── tenant_schema.md                # Tenant DMG config specification
│   └── snowflake_tasks.json            # Snowflake tasks JSON specification
├── scripts
│   ├── generate_schema_docs.sh         # Script to auto-generate schema documentation
├── src
│   ├── data_contract_engine
│   │   ├── __init__.py                 # Data Contract Engine module
│   │   ├── common
│   │   │   └── cli.py                  # Common CLI utilities
│   │   ├── collibra_to_data_contract
│   │   │   ├── __init__.py             # Collibra to Data Contract translation module
│   │   │   └── dc_templates            # Jinja2 templates for data contract
│   │   ├── dmg_config_to_data_contract
│   │   │   └── __init__.py             # DMG Config to Data Contract translation module
├── tests
│   ├── integration_test
│   │   └── test_collibra_integration.py # Integration tests (Work in progress)
│   ├── unit_test
│   │   └── test_data_contract_engine.py # Unit tests for Data Contract Engine
├── docker_build_scripts
│   ├── Dockerfile                      # Dockerfile to build the Docker image for the engine
│   ├── build.sh                        # Script to build the project
├── notebooks
│   └── data_contract_engine.ipynb       # Jupyter notebook for testing and prototyping
├── .github
│   └── workflows
│       ├── build_docker_image.yml       # GitHub action to build Docker image
│       ├── deploy_version.yml           # GitHub action to deploy versions
│       ├── pull_request_validate.yml    # GitHub action for PR validation
│       ├── reusable_collibra_utils.yml  # Reusable Collibra utilities in workflows
│       ├── reusable_deploy.yml          # Reusable deploy utilities in workflows
│       ├── reusable_pull_request_validate.yml # Reusable PR validation tasks
│       └── tag_artifact.yml             # GitHub action to tag build artifacts
├── .gitignore                           # Ignore specific files in Git
├── requirements.in                      # Project main dependencies
├── requirements.txt                     # Exact dependencies auto-generated from requirements.in
├── setup.py                             # Installation script for the project
├── README.md                            # Project documentation
└── test-requirements.txt                # Test dependencies
```

## Build