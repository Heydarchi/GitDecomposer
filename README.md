# GitDecomposer

A comprehensive Python toolkit for analyzing Git repositories. GitDecomposer provides detailed insights into commit patterns, contributor behavior, file changes, branch strategies, and overall repository health through an intuitive class-based API and interactive visualizations.

## Features

- **Comprehensive Analysis**: Analyze commits, contributors, files, and branches
- **Interactive Visualizations**: Generate HTML dashboards with interactive charts
- **Multiple Output Formats**: Export data as CSV files or HTML reports
- **Modular Design**: Use individual analyzers or the complete metrics suite
- **CLI Interface**: Command-line tool for quick analysis
- **Extensible Architecture**: Well-structured classes for custom analysis

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Heydarchi/GitDecomposer.git
cd GitDecomposer

# Create virtual environment (recommended)
python -m venv gitdecomposer-env

# Activate virtual environment
# Windows:
gitdecomposer-env\Scripts\activate
# macOS/Linux:
# source gitdecomposer-env/bin/activate

# Install in development mode
pip install -e .
```

### Basic Usage

```python
from gitdecomposer import GitRepository, GitMetrics

# Initialize repository
repo = GitRepository("/path/to/your/git/repository")

# Create comprehensive metrics analyzer
metrics = GitMetrics(repo)

# Generate summary
summary = metrics.generate_repository_summary()
print(f"Total commits: {summary['commits']['total_commits']}")
print(f"Contributors: {summary['contributors']['total_contributors']}")

# Create interactive visualizations
metrics.create_commit_activity_dashboard("commit_analysis.html")
metrics.create_contributor_analysis_charts("contributor_analysis.html")

# Export data to CSV
csv_files = metrics.export_metrics_to_csv("./analysis_output")

# Generate comprehensive report
metrics.create_comprehensive_report("full_report.html")
```

### Command Line Interface

```bash
# Analyze current directory
gitdecomposer .

# Analyze specific repository
gitdecomposer /path/to/repository

# Specify output directory
gitdecomposer /path/to/repository --output ./my_analysis
```

**Alternative: Direct script execution:**

```bash
# For development/testing
python gitdecomposer/cli.py /path/to/repository --output ./analysis_output
```

## Examples

See the [`examples/`](examples/) directory for detailed usage examples:

- **[Basic Analysis](examples/basic_analysis.py)** - Simple repository analysis
- **[Advanced Analysis](examples/advanced_analysis.py)** - Using individual analyzers  
- **[Comprehensive Analysis](examples/comprehensive_analysis.py)** - Full-featured analysis
- **[Enhanced Analytics](examples/enhanced_analytics.py)** - Advanced metrics and visualizations
- **[Advanced Reporting Demo](examples/advanced_reporting_demo.py)** - Comprehensive reporting features

## Architecture

See the [Architecture Diagram](docs/architecture.puml) for system design and component relationships.

## Documentation

For detailed documentation, see:
- **[Documentation](docs/README.md)** - Complete guide and API reference
- **[Examples README](examples/README.md)** - Example usage patterns

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/run_tests.py
```

## Development

### Code Quality

```bash
# Check code formatting and style
source scripts/check_lint.sh

# Auto-fix formatting issues
source scripts/fix_lint.sh
```

### Project Structure

```
GitDecomposer/
├── gitdecomposer/          # Main package
│   ├── analyzers/          # Analysis modules
│   ├── core/              # Core functionality
│   ├── models/            # Data models
│   └── viz/               # Visualization components
├── examples/              # Usage examples
├── tests/                 # Test suite
├── docs/                  # Documentation
└── scripts/               # Development scripts
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest tests/ -v`)
5. Run linting (`source scripts/check_lint.sh`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request
