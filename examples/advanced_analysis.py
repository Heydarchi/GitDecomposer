#!/usr/bin/env python3
"""
Advanced Example: Using individual analyzers

This example demonstrates how to use individual analyzer classes
for specific types of analysis.
"""

import os
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer import GitRepository, CommitAnalyzer, ContributorAnalyzer, FileAnalyzer

def advanced_analysis(repo_path: str):
    """
    Perform detailed analysis using individual analyzers.
    
    Args:
        repo_path (str): Path to the Git repository
    """
    print(f"Advanced analysis of: {repo_path}")
    print("=" * 40)
    
    # Initialize repository
    repo = GitRepository(repo_path)
    
    # Use specific analyzers
    commit_analyzer = CommitAnalyzer(repo)
    contributor_analyzer = ContributorAnalyzer(repo)
    file_analyzer = FileAnalyzer(repo)
    
    # Detailed commit analysis
    print("\nCommit Analysis:")
    daily_commits = commit_analyzer.get_commit_frequency_by_date()
    print(f"Analyzed {len(daily_commits)} days of activity")
    
    message_analysis = commit_analyzer.get_commit_messages_analysis()
    print(f"Average message length: {message_analysis.get('avg_message_length', 0):.1f} chars")
    
    # Enhanced file analysis
    print("\nFile Analysis:")
    frequency_analysis = file_analyzer.get_file_change_frequency_analysis()
    print(f"Analyzed {len(frequency_analysis)} files for change patterns")
    
    hotspots = file_analyzer.get_file_hotspots_analysis()
    print(f"Identified {len(hotspots)} potential hotspot files")
    
    # Top contributors
    print("\nContributor Analysis:")
    contributors = contributor_analyzer.get_contributor_statistics()
    if not contributors.empty:
        top_contributor = contributors.iloc[0]
        print(f"Top contributor: {top_contributor['author']} with {top_contributor['total_commits']} commits")
    
    impact_analysis = contributor_analyzer.get_contributor_impact_analysis()
    print(f"Impact analysis completed for {len(impact_analysis)} contributors")
    
    print("\nAdvanced analysis complete!")
    
    # Close repository connection
    repo.close()

if __name__ == "__main__":
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    advanced_analysis(repo_path)
