#!/bin/bash
# Test execution script for GitDecomposer

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}GitDecomposer Test Suite${NC}"
echo "=========================="

# Check if we're in the right directory
if [ ! -f "gitdecomposer/__init__.py" ]; then
    echo -e "${RED}Error: Please run this script from the GitDecomposer root directory${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "gitdecomposer-env" ]; then
    echo "Activating virtual environment..."
    source gitdecomposer-env/bin/activate
fi

# Function to run tests
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo -e "\n${YELLOW}Running $test_name...${NC}"
    echo "----------------------------------------"
    
    if python -m pytest "$test_file" -v; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        return 1
    fi
}

# Function to run tests with unittest
run_unittest() {
    local test_file=$1
    local test_name=$2
    
    echo -e "\n${YELLOW}Running $test_name...${NC}"
    echo "----------------------------------------"
    
    if python "$test_file"; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        return 1
    fi
}

# Check for pytest, fall back to unittest if not available
if command -v pytest &> /dev/null; then
    echo "Using pytest for test execution"
    TEST_RUNNER="pytest"
else
    echo "pytest not found, using unittest"
    TEST_RUNNER="unittest"
fi

# Track test results
FAILED_TESTS=()
PASSED_TESTS=()

# Run individual test files
if [ "$TEST_RUNNER" = "pytest" ]; then
    # Run with pytest
    test_files=(
        "tests/test_gitdecomposer.py:Core GitRepository Tests"
        "tests/test_analyzers.py:Analyzer Tests"
        "tests/test_commit_analyzer_detailed.py:Detailed CommitAnalyzer Tests"
    )
    
    for test_entry in "${test_files[@]}"; do
        IFS=':' read -r test_file test_name <<< "$test_entry"
        if [ -f "$test_file" ]; then
            if run_test "$test_file" "$test_name"; then
                PASSED_TESTS+=("$test_name")
            else
                FAILED_TESTS+=("$test_name")
            fi
        else
            echo -e "${YELLOW}Warning: $test_file not found, skipping${NC}"
        fi
    done
else
    # Run with unittest
    test_files=(
        "tests/test_gitdecomposer.py:Core GitRepository Tests"
        "tests/test_analyzers.py:Analyzer Tests" 
        "tests/test_commit_analyzer_detailed.py:Detailed CommitAnalyzer Tests"
    )
    
    for test_entry in "${test_files[@]}"; do
        IFS=':' read -r test_file test_name <<< "$test_entry"
        if [ -f "$test_file" ]; then
            if run_unittest "$test_file" "$test_name"; then
                PASSED_TESTS+=("$test_name")
            else
                FAILED_TESTS+=("$test_name")
            fi
        else
            echo -e "${YELLOW}Warning: $test_file not found, skipping${NC}"
        fi
    done
fi

# Print summary
echo -e "\n${YELLOW}Test Summary${NC}"
echo "============"

if [ ${#PASSED_TESTS[@]} -gt 0 ]; then
    echo -e "${GREEN}Passed Tests (${#PASSED_TESTS[@]}):${NC}"
    for test in "${PASSED_TESTS[@]}"; do
        echo -e "  ${GREEN}✓${NC} $test"
    done
fi

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo -e "\n${RED}Failed Tests (${#FAILED_TESTS[@]}):${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  ${RED}✗${NC} $test"
    done
fi

TOTAL_TESTS=$((${#PASSED_TESTS[@]} + ${#FAILED_TESTS[@]}))
echo -e "\nTotal: $TOTAL_TESTS tests, ${GREEN}${#PASSED_TESTS[@]} passed${NC}, ${RED}${#FAILED_TESTS[@]} failed${NC}"

# Exit with appropriate code
if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    exit 1
fi
