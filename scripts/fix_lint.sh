#!/bin/bash

# Script to automatically fix linting issues.
# This script applies formatting changes and can be run locally.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Define the directories to fix.
# Add or remove directories as needed.
TARGET_DIRS="gitdecomposer tests examples"
echo "Targeting directories for fixing: $TARGET_DIRS"
echo ""

# --- Fixing Steps ---

echo "Running black to format code..."
black $TARGET_DIRS
echo "Black formatting applied."
echo ""

echo "Running isort to organize imports..."
isort $TARGET_DIRS
echo "isort import organization applied."
echo ""

# Note: flake8 and mypy do not have auto-fixing capabilities for all issues.
# They are primarily for checking. Running them here to show any remaining errors.
echo "Running flake8 to check for remaining style issues..."
flake8 $TARGET_DIRS || true # Continue even if flake8 finds errors
echo "flake8 check complete."
echo ""

echo "Running mypy to check for type errors..."
mypy $TARGET_DIRS || true # Continue even if mypy finds errors
echo "mypy check complete."
echo ""

echo "Lint fixing process completed!"
echo "Please review the changes and manually fix any remaining flake8 or mypy errors."
