#!/usr/bin/env python3
"""
Basic Example: Simple repository analysis

This example shows the most straightforward way to analyze a Git repository
using GitDecomposer.
"""

import os
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer import GitRepository, GitMetrics


def basic_analysis(repo_path: str):
    """
    Perform basic analysis of a Git repository.

    Args:
        repo_path (str): Path to the Git repository
    """
    print(f"Analyzing repository: {repo_path}")
    print("=" * 40)

    # Initialize repository
    repo = GitRepository(repo_path)

    # Create comprehensive metrics analyzer
    metrics = GitMetrics(repo)

    # Generate summary
    summary = metrics.generate_repository_summary()
    print(f"Total commits: {summary['commits']['total_commits']}")
    print(f"Contributors: {summary['contributors']['total_contributors']}")
    print(f"Branches: {summary['branches']['total_branches']}")

    # Create interactive visualizations
    print("\nGenerating reports...")
    metrics.create_commit_activity_dashboard("commit_analysis.html")
    metrics.create_contributor_analysis_charts("contributor_analysis.html")

    # Export data to CSV
    csv_files = metrics.export_metrics_to_csv("./analysis_output")
    print(f"Exported {len(csv_files)} CSV files")

    # Generate comprehensive report
    metrics.create_comprehensive_report("full_report.html")
    print("Analysis complete! Check the generated HTML files.")

    # Close repository connection
    repo.close()


if __name__ == "__main__":
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    basic_analysis(repo_path)
