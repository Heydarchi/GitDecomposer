# Analysis Capabilities

## Commit Analysis
- Commit frequency patterns (daily, weekly, monthly)
- Commit message analysis and common patterns
- Merge commit detection and patterns
- Commit size distribution (lines added/deleted)
- Activity timeline visualization

## Contributor Analysis
- Contributor statistics and rankings
- Impact analysis and scoring
- Collaboration patterns between contributors
- Contributor specialization (file types, directories)
- Activity consistency and timeline analysis

## File Analysis
- File extension distribution
- Most frequently changed files
- File lifecycle analysis
- Directory activity patterns
- File complexity metrics
- File churn analysis
- **File change frequency analysis** (commit-based and line-based)
- **Commit size distribution** (lines and files)
- **File hotspot detection** with risk assessment

## Branch Analysis
- Branch statistics and lifecycle
- Branching strategy detection (Git Flow, GitHub Flow, etc.)
- Branch divergence analysis
- Merge pattern analysis
- Stale branch detection

## Visualization Examples

GitDecomposer creates interactive HTML dashboards including:

- **Commit Activity Dashboard**: Timeline charts, hourly/daily patterns, commit size distribution
- **Contributor Analysis**: Activity heatmaps, collaboration networks, impact scoring
- **File Analysis**: Extension distribution, most changed files, directory activity
- **Enhanced File Analysis**: File change frequency, commit size analysis, hotspot detection
- **Comprehensive Report**: All-in-one HTML report with key insights and recommendations

## Output Examples

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
   - Most common commit words: fix, add, update, refactor, improve
   - Merge commits: 12.4% of total commits

Analyzing contributors...
   - Total contributors: 8
   - Top contributor: john.doe: 423 commits, +12,847/-8,234 lines
```

### Generated Files
- `commit_activity_dashboard.html` - Interactive commit timeline and patterns
- `contributor_analysis.html` - Contributor metrics and collaboration charts  
- `file_analysis.html` - File change patterns and directory activity
- `enhanced_file_analysis.html` - Advanced file frequency and hotspot analysis
- `comprehensive_report.html` - Complete analysis with recommendations
- `*.csv` files - Raw data for further analysis including:
  - `file_change_frequency.csv` - Detailed file change metrics
  - `file_hotspots.csv` - File hotspot risk assessment
  - `commit_size_analysis.csv` - Commit size distribution data

## Use Cases

- **Code Review Insights**: Identify frequently changed files and contributors
- **Team Analysis**: Understand collaboration patterns and contributor impact
- **Repository Health**: Detect stale branches and maintenance needs  
- **Development Patterns**: Analyze commit frequency and development cycles
- **Quality Metrics**: Track file complexity and change patterns
- **Onboarding**: Help new team members understand repository structure and history

## Example Analysis Insights

GitDecomposer can help answer questions like:

- Which files are changed most frequently and might need refactoring?
- Who are the most active contributors and what's their expertise?  
- What's the team's commit pattern throughout the day/week?
- Are there stale branches that should be cleaned up?
- What branching strategy is the team following?
- How consistent are contributors in their activity?
- Which directories see the most development activity?
- **What's the typical commit size in your project (lines vs files)?**
- **Which files are hotspots that require immediate attention?**
- **How do file change frequencies correlate with code quality issues?**
- **Are developers making appropriately sized commits?**
- **Which files have the highest risk of bugs based on change patterns?**
