> [!WARNING]
> **This project is deprecated and should not be used anymore.** If you have any questions, contact test@test.com.

# Collibra DAG Deployment Repository

## Overview
This repository is used to deploy the DMG Collibra DAG in Astronomer. It contains the necessary Airflow DAGs, configurations, dependencies, and CI/CD workflows to build, test, and deploy a custom Astronomer image for running the Collibra-related data pipelines.

## File Structure
Below is the directory structure of the repository, along with descriptions for each folder and file:
```
collibra-astro/
├── .github/
│   └── workflows/
│       ├── build-collibra-astro-image.yaml    # GitHub Actions workflow to build the custom Docker image for Astronomer deployment.
│       ├── deploy-astro-collibra.yaml         # GitHub Actions workflow to deploy the built image to Astronomer.
│       └── run_tests_and_code_scans.yaml      # GitHub Actions workflow to run unit tests, code scans, and quality checks.
├── cli_lib_astro/                             # Custom CLI library or module for Astronomer-related utilities.
├── .astro/                                    # Astronomer-specific configuration directory, including settings for Airflow deployments.
├── common/
│   └── alerts/
│       ├── tests/
│       │   ├── __init__.py                    # Python package initializer for the alerts tests module.
│       │   └── alert.py                       # Test scripts or utilities related to alert functionalities.
│       └── internal-ca.pem                    # Internal Certificate Authority (CA) PEM file for secure connections (e.g., SSL/TLS).
├── dags/                                      # Main directory for Airflow DAG files, where the DMG Collibra DAG definitions reside.
├── tests/                                     # Directory for integration or end-to-end tests for the project.
├── .coveragerc                                # Configuration file for code coverage reporting (used with tools like pytest-cov).
├── .dockerignore                              # File specifying patterns to ignore when building Docker images.
├── .gitignore                                 # Git configuration file to ignore certain files and directories from version control.
├── cx.config                                  # Custom configuration file (possibly for connections or environment-specific settings).
├── Dockerfile                                 # Main Dockerfile for building the Astronomer-compatible Docker image for Azure 3.0.
├── Dockerfile-A24                             # Main Dockerfile for building the Astronomer-compatible Docker image for Azure 4.0.
├── environment.yml                            # Conda environment specification file for reproducible environments.
├── packages.txt                               # List of OS-level packages required for the Docker image or environment.
├── README.md                                  # This documentation file providing an overview, structure, and instructions.
├── requirements.txt                           # Python dependencies file listing required packages for the project.
└── setup.py                                   # Python setup script for packaging the project as a distributable module.
```

## Build, Test, and Local Deployment
### Build
To build the custom Docker image for the Astronomer deployment:
1.  Ensure Docker is installed and running on your machine.
2.  Navigate to the project root.
3.  Run the following command to build the image using the main Dockerfile:
```
# Azure 3.0
docker build -t collibra-astro-image .
# Azure 3.0
docker build -f Dockerfile-A24 -t collibra-astro-image .
```
4.  The build process installs dependencies from requirements.txt and packages.txt, copies DAGs and other files, and sets up the Airflow environment.
5.  Alternatively, trigger the GitHub Actions workflow (build-collibra-astro-image.yaml) by pushing changes to the repository for automated builds.

### Test
To run tests locally:
1.  Set up a virtual environment (recommended: use Python 3.8+):
	•  For pip: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	•  For Conda: conda env create -f environment.yml && conda activate <env-name>
2.  Install testing dependencies if not included (e.g., pytest, coverage).
3.  Run unit tests:
```
pytest tests/
```
4. For CI/CD testing, the run_tests_and_code_scans.yaml workflow handles automated testing on push/pull requests, including code linting and security scans.

## Local Deployment
To deploy and run Airflow locally using Docker Compose for development/testing:
1.  Build the custom Docker image as described in the Build section (e.g., docker build -t collibra-astro-image .).
2.  Create a docker-compose.yaml file in the project root with the following content (customized for Airflow; adjust versions and paths as needed):
```yaml
```
3.  Start the services with Docker  
    - NOTE: This will spin up PostgreSQL (as metadata backend), Airflow webserver, scheduler, and worker.
```bash
docker-compose up -d
```
4.  Wait for the services to initialize (check logs with docker-compose logs -f if needed). Access the Airflow UI at http://localhost:8080 (default credentials: airflow/airflow).
5.  Set the required Airflow variables via the UI (under Admin > Variables) or CLI (once inside a container, e.g., docker-compose exec airflow-webserver airflow variables set KEY VALUE):  
	- COLLIBRA_API_URL: The base URL for the Collibra API (e.g., https://your-collibra-instance.com).
	- COLLIBRA_USERNAME: Username for Collibra authentication.
	- COLLIBRA_PASSWORD: Password for Collibra authentication (use secure storage like Secrets Backend in production).
6.  Sync or ensure DAGs from the dags/ folder are loaded (they are mounted via volumes).
