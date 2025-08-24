#!/bin/bash

# Advanced script to fix linting issues automatically
# This script handles more complex flake8 issues

set -e

TARGET_DIRS="gitdecomposer tests examples"
echo "Advanced lint fixing for directories: $TARGET_DIRS"
echo ""

# Step 1: Run basic formatting
echo "Step 1: Basic formatting..."
black $TARGET_DIRS --line-length=120
isort $TARGET_DIRS
echo "✓ Basic formatting complete"
echo ""

# Step 2: Fix long lines with autopep8
echo "Step 2: Fixing long lines with autopep8..."
autopep8 --in-place --aggressive --aggressive --max-line-length=120 --recursive $TARGET_DIRS
echo "✓ Long lines fixed"
echo ""

# Step 3: Run autoflake to remove unused variables and imports
echo "Step 3: Removing unused variables and imports..."
autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive $TARGET_DIRS
echo "✓ Unused variables and imports removed"
echo ""

# Step 4: Check remaining issues
echo "Step 4: Checking remaining issues..."
echo "Running flake8 to check for any remaining style issues..."
flake8 $TARGET_DIRS --max-line-length=120 --extend-ignore=E203,W503 || true
echo ""

echo "Advanced lint fixing completed!"
echo ""
echo "Summary:"
echo "  ✓ Code formatted with black"
echo "  ✓ Imports organized with isort"
echo "  ✓ Long lines fixed with autopep8"
echo "  ✓ Unused variables removed with autoflake"
echo ""
echo "If any errors remain, they may need manual fixing"
