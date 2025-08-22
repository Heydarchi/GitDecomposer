#!/bin/bash

# Simple test runner for the corrected analyzer tests
echo "Running Corrected Analyzer Tests..."
echo "=================================="

cd /home/mhh/Projects/GitDecomposer

# Activate virtual environment
source gitdecomposer-env/bin/activate

# Run the specific test file
python -m pytest tests/test_analyzers_final.py -v

echo ""
echo "Test run completed!"
