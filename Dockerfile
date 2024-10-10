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

# Parameters: Organization name, Team name, GitHub username
ORG_NAME=$1
TEAM_NAME=$2
USER=$3

# Check if the required parameters are provided
if [ -z "$ORG_NAME" ] || [ -z "$TEAM_NAME" ] || [ -z "$USER" ]; then
  echo "Usage: $0 <ORG_NAME> <TEAM_NAME> <GITHUB_USERNAME>"
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
elif [ "$RESPONSE" == "404" ]; then
  echo "Failure: User $USER is NOT a member of the team $TEAM_NAME in organization $ORG_NAME."
  exit 1
else
  echo "Error: Unable to verify team membership. API response code: $RESPONSE"
  exit 1
fi