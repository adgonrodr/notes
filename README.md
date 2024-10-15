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
├── .github
│   └── workflows
│       ├── build_docker_image.yml              # GitHub action to build Docker image
│       ├── deploy_version.yml                  # GitHub action to deploy versions
│       ├── pull_request_validate.yml           # GitHub action for PR validation
│       ├── reusable_collibra_utils.yml         # Reusable Collibra-related utilities in workflows
│       ├── reusable_deploy.yml                 # Reusable deploy utilities in workflows
│       ├── reusable_pull_request_validate.yml  # Reusable PR validation tasks
│       └── tag_artifact.yml                    # GitHub action to tag build artifacts
├── .idea                                       # IDE configuration files
├── .venv                                       # Virtual environment for Python dependencies
├── build_scripts
│   ├── create_venv.sh                          # Script to create virtual environment
│   ├── github_download_release_file.sh         # Script to download release files from GitHub
│   └── ZscalerRootCertificate-2048-SHA256.crt  # Zscaler certificate for secure connections
├── cli
│   ├── actions                                 # CLI actions and utilities
│   ├── lib
│   │   ├── collibra                            # Collibra integration library
│   │   └── templating                          # Templating resources for metadata operations
│   └── datamesh-shim                           # DataMesh integration shim
├── k8s                                         # Kubernetes deployment configuration (if needed)
├── target                                      # Target build directory for compiled artifacts
├── .gitignore                                  # List of files and directories to ignore in Git
├── .pre-commit-config.yaml                     # Pre-commit hooks configuration
├── build.sh                                    # Build script to compile and package the engine
├── demo_tenant_run.sh                          # Demo script for running tenant examples
├── Dockerfile                                  # Dockerfile to build the Docker image for the engine
├── package-lock.json                           # Package lock file for NPM (if applicable)
├── README.md                                   # Project documentation and overview
└── test-requirements.txt                       # Testing dependencies
```

## Build