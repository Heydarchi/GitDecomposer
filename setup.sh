#!/bin/bash
#
# This script sets up the development environment for the GitDecomposer project.
# It creates a virtual environment, installs dependencies, and installs the
# package in editable mode.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
VENV_NAME="gitdecomposer-env"
PYTHON_CMD="python3"

# --- Check for Python ---
if ! command -v ${PYTHON_CMD} &> /dev/null
then
    echo "Error: ${PYTHON_CMD} could not be found. Please install Python 3."
    exit 1
fi

echo "Found Python at: $(command -v ${PYTHON_CMD})"

# --- Create Virtual Environment ---
if [ ! -d "${VENV_NAME}" ]; then
    echo "Creating virtual environment '${VENV_NAME}'..."
    ${PYTHON_CMD} -m venv ${VENV_NAME}
else
    echo "Virtual environment '${VENV_NAME}' already exists."
fi

# --- Activate Virtual Environment and Install Dependencies ---
echo "Activating virtual environment and installing dependencies..."

# Activate the environment
source "${VENV_NAME}/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements files
if [ -f "requirements.txt" ]; then
    echo "   - Installing production dependencies from requirements.txt"
    pip install -r requirements.txt
else
    echo "   - Warning: requirements.txt not found."
fi

if [ -f "requirements-dev.txt" ]; then
    echo "   - Installing development dependencies from requirements-dev.txt"
    pip install -r requirements-dev.txt
else
    echo "   - Warning: requirements-dev.txt not found."
fi

# --- Install Package in Editable Mode ---
echo "Installing 'gitdecomposer' in editable mode..."
pip install -e .

# --- Announce Completion ---
echo ""
echo "Development setup complete!"
echo "   To activate the virtual environment, run:"
echo "   source ${VENV_NAME}/bin/activate"
echo ""
