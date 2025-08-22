# GitDecomposer Documentation

## Quick Start
- [Installation Guide](#installation) - Get started with GitDecomposer
- [API Reference](#api-reference) - Complete class and method documentation
- [Features Overview](#features) - Comprehensive analysis capabilities

## Installation

### Prerequisites
- Python 3.8 or higher
- Git repository to analyze

### Setup
```bash
# Create virtual environment (recommended)
python -m venv gitdecomposer-env

# Activate virtual environment
gitdecomposer-env\Scripts\activate  # Windows
# source gitdecomposer-env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Optional: Install as package
pip install -e .
```

### Verification
```bash
python tests/test_gitdecomposer.py
```

## API Reference

### Core Classes

#### GitRepository
Main interface to Git repository data.

```python
from gitdecomposer import GitRepository

repo = GitRepository("/path/to/repo")
commits = repo.get_commits()
```

#### GitMetrics
Comprehensive analysis and visualization engine.

```python
from gitdecomposer import GitMetrics

metrics = GitMetrics(repo)
summary = metrics.generate_repository_summary()
```

#### Individual Analyzers
- `CommitAnalyzer` - Commit patterns and frequency analysis
- `ContributorAnalyzer` - Developer activity and collaboration
- `FileAnalyzer` - File changes and hotspot detection
- `BranchAnalyzer` - Branching strategies and lifecycle
- `AdvancedMetrics` - Quality metrics and technical debt

### Quick Examples

```python
# Basic analysis
repo = GitRepository("/path/to/repo")
metrics = GitMetrics(repo)

# Generate reports
metrics.create_comprehensive_report("report.html")
csv_files = metrics.export_metrics_to_csv("./output")

# Individual analyses
commit_analyzer = CommitAnalyzer(repo)
commit_stats = commit_analyzer.analyze_commit_frequency()
```

## Features

### Analysis Capabilities

**Commit Analysis**
- Frequency patterns (daily, weekly, monthly)
- Message analysis and common patterns
- Merge commit detection
- Size distribution and activity timeline

**Contributor Analysis** 
- Statistics and impact scoring
- Collaboration patterns
- Specialization analysis (file types, directories)
- Activity consistency tracking

**File Analysis**
- Extension distribution and lifecycle analysis
- Change frequency and hotspot detection
- Complexity metrics and churn analysis
- Directory activity patterns

**Branch Analysis**
- Statistics and lifecycle tracking
- Strategy detection (Git Flow, GitHub Flow)
- Divergence and merge pattern analysis
- Stale branch identification

### Visualization Outputs

**Interactive Dashboards**
- Commit Activity Dashboard - Timeline charts and patterns
- Contributor Analysis - Heatmaps and collaboration networks
- File Analysis - Distribution charts and hotspot maps
- Comprehensive Report - All-in-one executive summary

**Export Formats**
- CSV files for data analysis
- HTML reports with interactive charts
- Console output for quick insights

### CLI Usage

```bash
# Analyze current directory
python gitdecomposer/cli.py .

# Analyze specific repository
python gitdecomposer/cli.py /path/to/repository

# Custom output directory
python gitdecomposer/cli.py /path/to/repository --output ./analysis

# CSV export only
python gitdecomposer/cli.py /path/to/repository --format csv
```

## Architecture

GitDecomposer follows a modular architecture with clear separation of concerns:

- **Core Layer** - Git repository interface and data models
- **Analyzer Layer** - Specialized analysis engines
- **Visualization Layer** - Chart generation and HTML reporting
- **CLI Layer** - Command-line interface and user interaction

## Contributing

This project is designed for extensibility:

1. **New Metrics** - Extend existing analyzer classes
2. **Visualizations** - Add methods to GitMetrics class  
3. **Analyzers** - Create new analyzer classes
4. **Export Formats** - Add new output capabilities

## License

MIT License - see [LICENSE](../LICENSE) file for details.
