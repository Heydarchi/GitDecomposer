# Advanced Repository Metrics

This module provides sophisticated metrics for analyzing repository health, development patterns, and team productivity. These metrics go beyond basic git statistics to provide actionable insights for engineering teams.

## Available Metrics

### Tier 1: Critical High-Impact Metrics

#### 1. Bus Factor Analysis
**Purpose**: Identifies the minimum number of people whose absence would severely impact project continuity.

**Key Insights**:
- Knowledge distribution across team members
- Risk assessment for project continuity
- Individual contributor criticality

**Usage**:
```python
from gitdecomposer.analyzers.advanced_metrics import create_metric_analyzer

analyzer = create_metric_analyzer('bus_factor', repository)
result = analyzer.calculate(lookback_months=6)
print(f"Bus Factor: {result['bus_factor']}")
print(f"Risk Level: {result['risk_level']}")
```

#### 2. Knowledge Distribution Index (Gini Coefficient)
**Purpose**: Measures inequality in knowledge distribution across team members.

**Key Insights**:
- Team knowledge equality (0 = perfect equality, 1 = maximum inequality)
- Target: < 0.6 for healthy distribution
- Identifies knowledge concentration issues

#### 3. Critical File Identification
**Purpose**: Identifies files that pose highest risk due to complexity and change frequency.

**Key Insights**:
- Files with high complexity and frequent changes
- Risk assessment for individual files
- Maintenance hotspots

#### 4. Single Point of Failure Files
**Purpose**: Finds files with dangerously low contributor diversity.

**Key Insights**:
- Files dominated by single contributors
- Knowledge bottlenecks
- Bus factor at file level

### Development Flow & Process Metrics

#### 5. Flow Efficiency
**Purpose**: Measures how much time is spent on active development vs. waiting.

**Key Insights**:
- Development process efficiency
- Bottleneck identification
- Wait time vs. active work ratio

#### 6. Branch Lifecycle Analysis
**Purpose**: Understands how long features take from conception to completion.

**Key Insights**:
- Feature delivery timelines
- Development phase breakdown
- Process optimization opportunities

#### 7. Development Velocity Trend
**Purpose**: Detects if team is speeding up, slowing down, or maintaining steady pace.

**Key Insights**:
- Team productivity trends
- Velocity direction (increasing/decreasing/stable)
- Statistical confidence in trends

#### 8. Cycle Time Distribution
**Purpose**: Analyzes feature delivery time patterns for better planning.

**Key Insights**:
- Delivery time distribution
- Planning percentiles (50%, 75%, 90%)
- Estimation accuracy

## Quick Start

### Basic Usage

```python
from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.analyzers.advanced_metrics import create_metric_analyzer

# Initialize repository
repo = GitRepository('/path/to/your/repo')

# Run bus factor analysis
bus_factor_analyzer = create_metric_analyzer('bus_factor', repo)
result = bus_factor_analyzer.calculate()

print(f"Bus Factor: {result['bus_factor']}")
print("Recommendations:")
for rec in result['recommendations']:
    print(f"  - {rec}")
```

### Running All Metrics

```python
from gitdecomposer.analyzers.advanced_metrics import get_available_metrics, create_metric_analyzer

# Get all available metrics
metrics = get_available_metrics()

# Run all metrics
for metric_name in metrics:
    analyzer = create_metric_analyzer(metric_name, repo)
    result = analyzer.calculate()
    print(f"{metric_name}: {result}")
```

### Using the Demo Script

Run the included demo script to see all metrics in action:

```bash
python examples/advanced_metrics_demo.py /path/to/your/repo
```

## Metric Details

### Bus Factor Analysis

The bus factor calculation uses a sophisticated knowledge weighting system:

1. **Recency Weighting**: Recent contributions weighted more heavily
2. **File Complexity**: Complex files weighted more heavily
3. **File Criticality**: Critical system files weighted more heavily
4. **Coverage Analysis**: Finds minimum set covering 80% of knowledge

**Parameters**:
- `lookback_months`: How many months back to analyze (default: 6)
- `knowledge_threshold`: Coverage threshold (default: 0.8)
- `decay_half_life`: Half-life for recency weight in days (default: 90)

### Knowledge Distribution Index

Uses the Gini coefficient to measure knowledge inequality:

- **0.0**: Perfect equality (everyone has equal knowledge)
- **< 0.3**: Excellent distribution
- **< 0.5**: Good distribution
- **< 0.6**: Acceptable distribution (target threshold)
- **> 0.6**: Concerning concentration
- **> 0.8**: Critical concentration

### Flow Efficiency

Measures the ratio of active development time to total flow time:

- **Active Days**: Days with commits
- **Flow Time**: Total time from start to completion
- **Efficiency**: Active Days / Flow Time Days

**Interpretation**:
- **> 80%**: Excellent efficiency
- **60-80%**: Good efficiency
- **40-60%**: Average efficiency
- **< 40%**: Poor efficiency (investigate bottlenecks)

### Cycle Time Distribution

Provides statistical distribution of feature delivery times:

- **Mean/Median**: Central tendency measures
- **Percentiles**: P50, P75, P90, P95, P99 for planning
- **Categories**: Very Fast (<1d), Fast (1-3d), Normal (3-7d), Slow (7-14d), Very Slow (>14d)

## Configuration Options

Most metrics accept configuration parameters to customize the analysis:

```python
# Bus Factor with custom parameters
result = analyzer.calculate(
    lookback_months=12,        # Analyze last 12 months
    knowledge_threshold=0.85,  # Require 85% coverage
    decay_half_life=60        # 60-day half-life for recency
)

# Flow Efficiency with custom branch patterns
result = analyzer.calculate(
    branch_patterns=['feature/*', 'bugfix/*', 'enhancement/*']
)

# Velocity Trend with custom timeframe
result = analyzer.calculate(weeks_lookback=16)
```

## Interpreting Results

### Risk Levels

Most metrics provide risk level assessments:

- **LOW**: No immediate concerns
- **MEDIUM**: Monitor and consider improvements
- **HIGH**: Address in next planning cycle
- **CRITICAL**: Immediate action required

### Recommendations

Each metric provides actionable recommendations based on the analysis:

```python
result = analyzer.calculate()
for recommendation in result['recommendations']:
    print(f"- {recommendation}")
```

### Trends and Patterns

Trend metrics provide direction indicators:

- **Increasing**: Metric is improving/growing
- **Decreasing**: Metric is declining
- **Stable**: No significant change

## Integration with GitDecomposer

These advanced metrics integrate seamlessly with the existing GitDecomposer ecosystem:

- **Repository Interface**: Uses the same `GitRepository` class
- **Caching**: Supports caching for performance
- **Error Handling**: Robust error handling with graceful degradation
- **Extensible**: Easy to add new metrics following the base interface

## Contributing New Metrics

To add a new metric:

1. Create a new analyzer class inheriting from `BaseMetricAnalyzer`
2. Implement required methods: `calculate()`, `get_metric_name()`, `get_description()`
3. Add to the `METRIC_ANALYZERS` registry in `__init__.py`
4. Write tests and documentation

Example skeleton:

```python
from . import BaseMetricAnalyzer

class MyCustomAnalyzer(BaseMetricAnalyzer):
    def get_metric_name(self) -> str:
        return "My Custom Metric"
    
    def get_description(self) -> str:
        return "Description of what this metric measures"
    
    def calculate(self, **kwargs) -> Dict[str, Any]:
        # Implement your analysis logic here
        return {
            'metric_value': 42,
            'recommendations': ['Do this', 'Do that']
        }
```

## Performance Considerations

- **Caching**: Results are cached to avoid recomputation
- **Incremental Analysis**: Many metrics support date-based filtering
- **Memory Usage**: Large repositories may require chunked processing
- **Computation Time**: Complex metrics may take several minutes on large repositories

## Best Practices

1. **Regular Monitoring**: Run metrics regularly to track trends
2. **Baseline Establishment**: Establish baselines for your team/project
3. **Action-Oriented**: Focus on metrics that drive actionable insights
4. **Context Awareness**: Consider your team size, project phase, and goals
5. **Holistic View**: Use multiple metrics together for comprehensive insights

## Troubleshooting

### Common Issues

1. **"No commits found"**: Check date ranges and repository activity
2. **"Insufficient data"**: Ensure repository has enough history
3. **High computation time**: Consider reducing lookback periods
4. **Import errors**: Ensure GitPython and dependencies are installed

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run analysis with debug output
result = analyzer.calculate()
```
