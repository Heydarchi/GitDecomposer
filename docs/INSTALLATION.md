# Installation Guide

## Prerequisites
- Python 3.8 or higher
- Git repository to analyze

## Create Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with other Python packages:

```bash
# Create virtual environment
python -m venv gitdecomposer-env

# Activate virtual environment
# On Windows:
gitdecomposer-env\Scripts\activate
# On macOS/Linux:
source gitdecomposer-env/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Install as Package (Optional)

```bash
pip install -e .
```

## Testing

Run the test suite to verify functionality:

```bash
python tests/test_gitdecomposer.py
```

## Contributing

Contributions are welcome! This project is designed with extensibility in mind:

1. **Adding New Metrics**: Extend existing analyzer classes
2. **New Visualizations**: Add methods to `GitMetrics` class
3. **Additional Analyzers**: Create new analyzer classes following the established pattern
4. **Output Formats**: Add new export capabilities
