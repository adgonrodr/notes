#!/bin/bash

# Define variables
RUN_FOLDER=".run"
VENV_FOLDER="$RUN_FOLDER/venv"
DEPENDENCY="requests" # Replace with your desired pip dependency

# Create the .run folder if it doesn't exist
if [ ! -d "$RUN_FOLDER" ]; then
    echo "Creating folder: $RUN_FOLDER"
    mkdir "$RUN_FOLDER"
fi

# Change directory to .run
cd "$RUN_FOLDER" || exit

# Create a Python virtual environment if it doesn't exist
if [ ! -d "$VENV_FOLDER" ]; then
    echo "Creating Python virtual environment in $VENV_FOLDER"
    python3 -m venv venv
fi

# Activate the virtual environment
source "$VENV_FOLDER/bin/activate"

# Install the pip dependency
echo "Installing pip dependency: $DEPENDENCY"
pip install "$DEPENDENCY"

echo "Setup complete. Dependency '$DEPENDENCY' installed in virtual environment."


@echo off
set RUN_FOLDER=.run
set VENV_FOLDER=%RUN_FOLDER%\venv
set DEPENDENCY=requests

REM Create the .run folder if it doesn't exist
if not exist "%RUN_FOLDER%" (
    echo Creating folder: %RUN_FOLDER%
    mkdir %RUN_FOLDER%
)

REM Change directory to .run
cd %RUN_FOLDER%

REM Create a Python virtual environment if it doesn't exist
if not exist "%VENV_FOLDER%" (
    echo Creating Python virtual environment in %VENV_FOLDER%
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Install the pip dependency
echo Installing pip dependency: %DEPENDENCY%
pip install %DEPENDENCY%

echo Setup complete. Dependency '%DEPENDENCY%' installed in virtual environment.