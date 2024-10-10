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

name: Main Branch Restriction for Workflow Dispatch

on:
  workflow_dispatch:

jobs:
  run-job:
    runs-on: ubuntu-latest
    if: ${{ github.ref == 'refs/heads/main' }}  # Restrict to the main branch
    steps:
      - name: Run only on the main branch
        run: echo "This workflow is running because it was dispatched on the main branch."