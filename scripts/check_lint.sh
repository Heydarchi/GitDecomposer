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
black --check $TARGET_DIRS
echo "Black check passed."
echo ""

echo "Running flake8 for style guide enforcement..."
flake8 $TARGET_DIRS
echo "flake8 check passed."
echo ""

echo "Running isort for static type checking..."
isort $TARGET_DIRS
echo "isort check passed."
echo ""

echo "Running pylint for static type checking..."
pylint $TARGET_DIRS
echo "pylint check passed."
echo ""

echo "Running mypy for static type checking..."
mypy $TARGET_DIRS
echo "mypy check passed."
echo ""

echo "🎉 All lint checks passed successfully!"
