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

# Note: flake8 does not have auto-fixing capabilities for all issues.
# It is primarily for checking. Running it here to show any remaining errors.
echo "Running flake8 to check for remaining style issues..."
flake8 $TARGET_DIRS --max-line-length=120 --extend-ignore=E203,W503,F401,E402,W291,W293,F841,E722,E501,F541,F406 || true # Continue even if flake8 finds errors
echo "flake8 check complete."
echo ""

echo "✨ Lint fixing process completed!"
echo ""
echo "Summary:"
echo "  ✓ Code formatted with black"
echo "  ✓ Imports organized with isort"
echo "  ⚠ Please review any remaining flake8 errors manually"
echo ""
echo "💡 Tip: Run './scripts/check_lint.sh' to verify all checks pass"
