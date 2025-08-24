#!/bin/bash

# GitDecomposer Build and Validation Script
# This script performs all the necessary steps for building, checking, and validating the package

set -e  # Exit immediately if a command exits with a non-zero status

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="gitdecomposer"
SOURCE_DIRS="gitdecomposer tests examples"
DIST_DIR="dist"
BUILD_DIR="build"

# Helper functions
print_step() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Clean previous builds
cleanup() {
    print_step "Cleaning previous builds"
    rm -rf ${DIST_DIR} ${BUILD_DIR} *.egg-info
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    print_success "Cleanup completed"
}

# Install development dependencies
install_deps() {
    print_step "Installing development dependencies"
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        print_success "Development dependencies installed"
    else
        print_warning "requirements-dev.txt not found, skipping dependency installation"
    fi
}

# Code formatting and linting
lint_code() {
    print_step "Running code formatting and linting"
    
    echo "Running black formatter..."
    black --check --diff ${SOURCE_DIRS} || {
        print_warning "Code formatting issues found. Run 'black ${SOURCE_DIRS}' to fix them."
        read -p "Would you like to auto-fix formatting issues? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            black ${SOURCE_DIRS}
            print_success "Code formatting applied"
        else
            print_error "Code formatting check failed"
            return 1
        fi
    }
    print_success "Black formatting check passed"
    
    echo "Running isort import sorting..."
    isort --check-only --diff ${SOURCE_DIRS} || {
        print_warning "Import sorting issues found. Run 'isort ${SOURCE_DIRS}' to fix them."
        read -p "Would you like to auto-fix import sorting? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            isort ${SOURCE_DIRS}
            print_success "Import sorting applied"
        else
            print_error "Import sorting check failed"
            return 1
        fi
    }
    print_success "Import sorting check passed"
    
    echo "Running flake8 linter..."
    flake8 ${SOURCE_DIRS} --max-line-length=120 --extend-ignore=E203,W503
    print_success "Flake8 linting passed"
}

# Run tests
run_tests() {
    print_step "Running tests"
    if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
        pytest tests/ -v --cov=${PACKAGE_NAME} --cov-report=term-missing --cov-report=html
        print_success "Tests completed"
    else
        print_warning "No tests found, skipping test execution"
    fi
}

# Type checking
type_check() {
    print_step "Running type checking"
    if command -v mypy &> /dev/null; then
        mypy ${PACKAGE_NAME} --ignore-missing-imports || {
            print_warning "Type checking found issues, but continuing..."
        }
        print_success "Type checking completed"
    else
        print_warning "mypy not available, skipping type checking"
    fi
}

# Validate manifest
check_manifest() {
    print_step "Validating MANIFEST.in"
    if [ -f "MANIFEST.in" ]; then
        check-manifest
        print_success "Manifest validation passed"
    else
        print_warning "MANIFEST.in not found, skipping manifest check"
    fi
}

# Build package
build_package() {
    print_step "Building package"
    python -m build
    print_success "Package build completed"
    
    echo "Built files:"
    ls -la ${DIST_DIR}/
}

# Validate package
validate_package() {
    print_step "Validating package with twine"
    twine check ${DIST_DIR}/*
    print_success "Package validation passed"
}

# Install package locally for testing
test_install() {
    print_step "Testing local installation"
    
    # Create a temporary virtual environment for testing
    TEMP_VENV="temp_test_env"
    python -m venv ${TEMP_VENV}
    source ${TEMP_VENV}/bin/activate
    
    # Install the built package
    pip install ${DIST_DIR}/*.whl
    
    # Test the CLI command
    echo "Testing CLI command..."
    ${PACKAGE_NAME} --help || {
        print_error "CLI command test failed"
        deactivate
        rm -rf ${TEMP_VENV}
        return 1
    }
    
    # Test import
    echo "Testing package import..."
    python -c "import ${PACKAGE_NAME}; print('Import successful')" || {
        print_error "Package import test failed"
        deactivate
        rm -rf ${TEMP_VENV}
        return 1
    }
    
    deactivate
    rm -rf ${TEMP_VENV}
    print_success "Local installation test passed"
}

# Generate package info
package_info() {
    print_step "Package Information"
    if [ -f "${DIST_DIR}/*.whl" ]; then
        echo "Package contents:"
        python -m zipfile -l ${DIST_DIR}/*.whl | head -20
        echo "..."
        echo ""
        echo "Package size:"
        ls -lh ${DIST_DIR}/
    fi
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              GitDecomposer Build & Validation                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Parse command line arguments
    SKIP_CLEANUP=false
    SKIP_DEPS=false
    SKIP_LINT=false
    SKIP_TESTS=false
    SKIP_BUILD=false
    SKIP_INSTALL_TEST=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-cleanup)
                SKIP_CLEANUP=true
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-lint)
                SKIP_LINT=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-install-test)
                SKIP_INSTALL_TEST=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-cleanup      Skip cleanup of previous builds"
                echo "  --skip-deps         Skip dependency installation"
                echo "  --skip-lint         Skip linting and formatting checks"
                echo "  --skip-tests        Skip running tests"
                echo "  --skip-build        Skip package building"
                echo "  --skip-install-test Skip local installation test"
                echo "  --help              Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute build pipeline
    [ "$SKIP_CLEANUP" = false ] && cleanup
    [ "$SKIP_DEPS" = false ] && install_deps
    [ "$SKIP_LINT" = false ] && lint_code
    [ "$SKIP_TESTS" = false ] && run_tests
    type_check
    check_manifest
    [ "$SKIP_BUILD" = false ] && build_package
    [ "$SKIP_BUILD" = false ] && validate_package
    [ "$SKIP_INSTALL_TEST" = false ] && test_install
    package_info
    
    print_step "Build Pipeline Completed Successfully!"
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ALL CHECKS PASSED!                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Your package is ready for:"
    echo "  • Distribution to PyPI (using: twine upload dist/*)"
    echo "  • Local installation (using: pip install dist/*.whl)"
    echo "  • Sharing with others"
    echo ""
    echo "Next steps:"
    echo "  1. Commit your changes: git add . && git commit -m 'Package ready for release'"
    echo "  2. Tag the release: git tag v1.0.0"
    echo "  3. Push to repository: git push --tags"
}

# Run main function with all arguments
main "$@"
