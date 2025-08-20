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
# Create virtual environment (recommended)
python -m venv gitdecomposer-env
gitdecomposer-env\Scripts\activate  # Windows
# source gitdecomposer-env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
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

**Option 1: Direct script execution (recommended for development):**

```bash
# Analyze current directory
python gitdecomposer/cli.py .

# Analyze specific repository
python gitdecomposer/cli.py /path/to/repository

# Specify output directory
python gitdecomposer/cli.py /path/to/repository --output ./my_analysis
```

**Option 2: After installing as package (`pip install -e .`):**

```bash
gitdecomposer /path/to/repository --output ./my_analysis
```

## Examples

See the [`examples/`](examples/) directory for detailed usage examples:

- **[Basic Analysis](examples/basic_analysis.py)** - Simple repository analysis
- **[Advanced Analysis](examples/advanced_analysis.py)** - Using individual analyzers  
- **[Comprehensive Analysis](examples/comprehensive_analysis.py)** - Full-featured analysis

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Features & Capabilities](docs/FEATURES.md)** - Complete feature overview
- **[API Reference](docs/API_REFERENCE.md)** - Class documentation and examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
python gitdecomposer/cli.py /path/to/repository

# Specify output directory
python gitdecomposer/cli.py /path/to/repository --output ./my_analysis

# Export only CSV files
python gitdecomposer/cli.py /path/to/repository --format csv

# Skip visualizations (faster)
python gitdecomposer/cli.py /path/to/repository --no-visualizations
```

**Option 2: After installing as package (`pip install -e .`):**

```bash
gitdecomposer /path/to/repository --output ./my_analysis
```

## Examples

See the [`examples/`](examples/) directory for detailed usage examples:

- **[Basic Analysis](examples/basic_analysis.py)** - Simple repository analysis
- **[Advanced Analysis](examples/advanced_analysis.py)** - Using individual analyzers  
- **[Comprehensive Analysis](examples/comprehensive_analysis.py)** - Full-featured analysis

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Features & Capabilities](docs/FEATURES.md)** - Complete feature overview
- **[API Reference](docs/API_REFERENCE.md)** - Class documentation and examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
