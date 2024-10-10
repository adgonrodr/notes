# Use Debian 11 base image
FROM debian:bullseye

# Install dependencies and Python 3.11
RUN apt-get update && \
    apt-get install -y software-properties-common wget build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev libffi-dev curl libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev liblzma-dev libgdbm-dev libnss3-dev libssl-dev \
    ca-certificates && \
    wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz && \
    tar -xvf Python-3.11.0.tgz && \
    cd Python-3.11.0 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && rm -rf Python-3.11.0.tgz Python-3.11.0

# Install the required version of pip
RUN python3.11 -m ensurepip --upgrade && \
    python3.11 -m pip install --upgrade pip==20.3.4

# Verify installation
RUN python3.11 --version && \
    python3.11 -m pip --version

# Set python3.11 as default (optional)
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1


#!/bin/bash

# Parameters: GitHub username and the file path to check
USER=$1
TARGET_PATH=$2

# Check if the required parameters are provided
if [ -z "$USER" ] || [ -z "$TARGET_PATH" ]; then
  echo "Usage: $0 <GITHUB_USERNAME> <TARGET_PATH>"
  exit 1
fi

# GitHub Personal Access Token (PAT) with 'read:org' permissions
# Set this as an environment variable before running the script
TOKEN=${GH_TOKEN}

# Check if GH_TOKEN is set
if [ -z "$TOKEN" ]; then
  echo "Error: GitHub Token (GH_TOKEN) not set. Set it as an environment variable."
  exit 1
fi

# Path to the CODEOWNERS file
CODEOWNERS_FILE="CODEOWNERS"

# Check if CODEOWNERS file exists
if [ ! -f "$CODEOWNERS_FILE" ]; then
  echo "Error: CODEOWNERS file not found in the repository."
  exit 1
fi

# Extract the directory from the target path (remove the filename)
TARGET_DIR=$(dirname "$TARGET_PATH")

# Search for the corresponding team entries in CODEOWNERS (allowing multiple teams)
TEAM_ENTRIES=$(grep -E "^${TARGET_DIR}" "$CODEOWNERS_FILE" | awk '{for(i=2;i<=NF;i++) print $i}')

# Check if any teams were found for the target directory
if [ -z "$TEAM_ENTRIES" ]; then
  echo "Error: No teams found in CODEOWNERS for directory $TARGET_DIR."
  exit 1
fi

# Check if the user is part of any of the teams listed for the directory
for TEAM_ENTRY in $TEAM_ENTRIES; do
  # Extract organization and team from the team entry (e.g., @org/team)
  ORG_NAME=$(echo "$TEAM_ENTRY" | cut -d '/' -f1 | sed 's/@//')
  TEAM_NAME=$(echo "$TEAM_ENTRY" | cut -d '/' -f2)

  # Check if both org and team were extracted successfully
  if [ -z "$ORG_NAME" ] || [ -z "$TEAM_NAME" ]; then
    echo "Error: Unable to parse organization and team from CODEOWNERS entry: $TEAM_ENTRY."
    continue
  fi

  echo "Checking if user $USER is part of the team $TEAM_NAME in organization $ORG_NAME..."

  # GitHub API endpoint to check team membership
  API_URL="https://api.github.com/orgs/${ORG_NAME}/teams/${TEAM_NAME}/members/${USER}"

  # Make the API request to check if the user is a member of the team
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "$API_URL")

  # Check the response code
  if [ "$RESPONSE" == "204" ]; then
    echo "Success: User $USER is a member of the team $TEAM_NAME in organization $ORG_NAME."
    exit 0
  elif [ "$RESPONSE" != "404" ]; then
    echo "Error: Unable to verify team membership for $TEAM_ENTRY. API response code: $RESPONSE"
  fi
done

# If no team memberships were validated
echo "Failure: User $USER is NOT a member of any of the teams for directory $TARGET_DIR."
exit 1