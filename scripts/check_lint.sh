#!/bin/bash

# Script to check for linting errors without fixing them.
# This is ideal for CI/CD pipelines.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Define the directories to check.
# Add or remove directories as needed.
TARGET_DIRS="gitdecomposer tests examples"
echo "Targeting directories: $TARGET_DIRS"
echo ""

# --- Linting Steps ---

echo "Running black for format checking..."
black --check --diff $TARGET_DIRS
echo "Black check passed."
echo ""

echo "Running isort for import order checking..."
isort --check-only --diff $TARGET_DIRS
echo "isort check passed."
echo ""

echo "Running flake8 for style guide enforcement..."
flake8 $TARGET_DIRS --max-line-length=120 --extend-ignore=E203,W503,F401,E402,W291,W293,F841,E722,E501,F541,F406
echo "flake8 check passed."
echo ""


echo "All lint checks passed successfully!"
