# API Reference

## Core Classes

### GitRepository
The foundation class that provides access to Git repository data.

```python
repo = GitRepository("/path/to/repo")
commits = repo.get_all_commits()
branches = repo.get_branches()
stats = repo.get_repository_stats()
```

### CommitAnalyzer
Analyzes commit patterns and trends.

```python
analyzer = CommitAnalyzer(repo)
daily_activity = analyzer.get_commit_frequency_by_date()
message_analysis = analyzer.get_commit_messages_analysis()
merge_patterns = analyzer.get_merge_commit_analysis()
```

### ContributorAnalyzer  
Evaluates contributor behavior and collaboration.

```python
analyzer = ContributorAnalyzer(repo)
contributor_stats = analyzer.get_contributor_statistics()
impact_scores = analyzer.get_contributor_impact_analysis()
collaboration = analyzer.get_collaboration_matrix()
```

### FileAnalyzer
Examines file changes and patterns.

```python
analyzer = FileAnalyzer(repo)
extensions = analyzer.get_file_extensions_distribution()
most_changed = analyzer.get_most_changed_files()
complexity = analyzer.get_file_complexity_metrics()

# Enhanced file analysis features
frequency_analysis = analyzer.get_file_change_frequency_analysis()
commit_size_analysis = analyzer.get_commit_size_distribution_analysis()
hotspots = analyzer.get_file_hotspots_analysis()
```

### BranchAnalyzer
Studies branching strategies and health.

```python
analyzer = BranchAnalyzer(repo)
branch_stats = analyzer.get_branch_statistics()
strategy_insights = analyzer.get_branching_strategy_insights()
lifecycle = analyzer.get_branch_lifecycle_analysis()
```

### GitMetrics
Combines all analyzers with visualization capabilities.

```python
metrics = GitMetrics(repo)
summary = metrics.generate_repository_summary()
dashboard = metrics.create_commit_activity_dashboard()
report = metrics.create_comprehensive_report("report.html")
```

## Package Structure

```
gitdecomposer/
├── __init__.py              # Package initialization
├── git_repository.py        # Core Git repository interface
├── commit_analyzer.py       # Commit pattern analysis
├── file_analyzer.py         # File change analysis  
├── contributor_analyzer.py  # Contributor metrics
├── branch_analyzer.py       # Branch strategy analysis
├── git_metrics.py          # Comprehensive metrics & visualization
└── cli.py                  # Command-line interface
```

## Dependencies

- **GitPython**: Git repository access
- **pandas**: Data manipulation and analysis
- **matplotlib**: Static plotting (optional)
- **seaborn**: Statistical visualization (optional)  
- **plotly**: Interactive visualizations (optional)
- **numpy**: Numerical computations
