# GitDecomposer Makefile

.PHONY: help install install-dev test clean lint format example

help:  ## Show this help message
	@echo "GitDecomposer Development Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:  ## Install package dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

test:  ## Run tests
	python tests/test_gitdecomposer.py

example:  ## Run example analysis on current repository
	python example_usage.py .

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build dist analysis_output gitdecomposer_output

lint:  ## Run linting (if flake8 is installed)
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 gitdecomposer/ --count --select=E9,F63,F7,F82 --show-source --statistics; \
	else \
		echo "flake8 not installed, skipping lint"; \
	fi

format:  ## Format code (if black is installed)
	@if command -v black >/dev/null 2>&1; then \
		black gitdecomposer/ tests/ example_usage.py; \
	else \
		echo "black not installed, skipping format"; \
	fi

setup:  ## Set up development environment
	@echo "Setting up GitDecomposer development environment..."
	pip install --upgrade pip
	$(MAKE) install-dev
	@echo "Setup complete! Try running: make example"

package:  ## Build package
	python setup.py sdist bdist_wheel

# Windows-specific commands
install-windows:  ## Install on Windows
	python -m pip install -r requirements.txt

test-windows:  ## Run tests on Windows
	python tests\\test_gitdecomposer.py

example-windows:  ## Run example on Windows
	python example_usage.py .
