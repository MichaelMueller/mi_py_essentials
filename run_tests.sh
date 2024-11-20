#!/bin/bash

# Fail early on error
set -e

# Change to the directory of the current script
cd "$(dirname "$0")"

# 1. Ensure Python is installed
PYTHON=$(command -v python3 || command -v python)
if [[ -z "$PYTHON" ]]; then
    echo "Python 3 is not installed. Please install Python 3.10 or higher to continue."
    exit 1
fi

# Ensure Python version is 3.10+
if ! $PYTHON -c 'import sys; assert sys.version_info >= (3, 10)' &> /dev/null; then
    echo "Python version must be 3.10 or higher. Please upgrade Python."
    exit 1
fi

echo "Python 3.10 or higher is installed."

# Create and activate a virtual environment
if [ ! -d "venv" ]; then
    echo "Creating a virtual environment..."
    $PYTHON -m venv venv
    echo "Virtual environment created."

    source venv/bin/activate

    # Install requirements if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements from requirements.txt..."
        pip install -r requirements.txt
        pip install -e .

        echo "Requirements installed."
    else
        echo "No requirements.txt found. Skipping dependency installation."
    fi        
fi

source venv/bin/activate

# Execute Python script with parameters passed to this shell script
echo "Executing ..."
$PYTHON mi_py_essentials/tests.py "$@"
exit_code=$?

# Deactivate the virtual environment
deactivate
exit $exit_code
