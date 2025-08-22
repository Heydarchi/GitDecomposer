# Examples

This directory contains various examples demonstrating how to use GitDecomposer to analyze Git repositories.

## Available Examples

### 1. Basic Analysis (`basic_analysis.py`)
The simplest way to get started with GitDecomposer. This example shows:
- How to initialize a repository
- Generate a summary report
- Create basic visualizations
- Export data to CSV

**Usage:**
```bash
python basic_analysis.py /path/to/repository
```

### 2. Advanced Analysis (`advanced_analysis.py`)
Demonstrates using individual analyzer classes for specific types of analysis:
- Detailed commit analysis
- Enhanced file analysis with hotspot detection
- Contributor impact analysis
- Individual analyzer usage patterns

**Usage:**
```bash
python advanced_analysis.py /path/to/repository
```

### 3. Comprehensive Analysis (`comprehensive_analysis.py`)
Full-featured example that performs complete repository analysis:
- All analyzer types
- Complete visualization suite
- Detailed reporting
- CSV exports
- Error handling and logging

**Usage:**
```bash
python comprehensive_analysis.py /path/to/repository
```

### 4. Enhanced Analytics (`enhanced_analytics.py`) **NEW**
Demonstrates the latest analytical capabilities including:
- **Commit velocity analysis** (commits/week trends)
- **Code churn rate** (lines changed vs total lines)
- **Bug fix ratio** (fix commits vs total commits) 
- **Maintainability index** calculation
- **Technical debt accumulation** rate
- **Test-to-code ratio** analysis
- **Documentation coverage** metrics
- **Repository health score** (0-100)

**Features Showcased:**
- Repository health scoring system
- Trend analysis and velocity tracking
- Quality metrics and recommendations
- Coverage analysis (tests and documentation)
- Technical debt identification
- Maintainability assessment

**Usage:**
```bash
python enhanced_analytics.py /path/to/repository
```

## Running the Examples

1. **Prerequisites:**
   ```bash
   # Install dependencies
   pip install -r ../requirements.txt
   ```

2. **Run any example:**
   ```bash
   # From the examples directory
   cd examples
   python basic_analysis.py /path/to/your/git/repo
   
   # Or use current directory if it's a Git repository
   python basic_analysis.py .
   ```

3. **Output:**
   - HTML files with interactive visualizations
   - CSV files with raw data
   - Console output with key insights

## Example Output

When you run any of these examples, you'll get:

### Console Output
```
Analyzing repository: /path/to/repo
==========================================

Repository loaded successfully!
   - Active branch: main
   - Total commits: 1,247
   - Total branches: 15
   - Total tags: 8

Analyzing commits...
   - Analyzed 342 days of commit activity
   - Average commit message length: 52.3 characters
```

### Generated Files
- `commit_activity_dashboard.html` - Interactive commit timeline
- `contributor_analysis.html` - Contributor metrics and charts
- `file_analysis.html` - File change patterns
- `comprehensive_report.html` - Complete analysis report
- Various `.csv` files with detailed data

## Customization

Feel free to modify these examples to suit your needs:
- Change output directories
- Adjust analysis parameters
- Add custom visualizations
- Filter by date ranges or specific contributors

## Next Steps

After running the examples:
1. Open the HTML files in your browser
2. Review the CSV data for deeper analysis
3. Use the insights to improve your development workflow
4. Customize the code for your specific use cases
