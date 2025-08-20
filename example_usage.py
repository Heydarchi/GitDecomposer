#!/usr/bin/env python3
"""
Example usage script for GitDecomposer.

This script demonstrates how to use all the classes in the GitDecomposer package
to analyze a Git repository.
"""

import os
import sys
import logging
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gitdecomposer import (
    GitRepository, 
    CommitAnalyzer, 
    FileAnalyzer, 
    ContributorAnalyzer, 
    BranchAnalyzer, 
    GitMetrics
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def analyze_repository(repo_path: str, output_dir: str = "analysis_output"):
    """
    Perform comprehensive analysis of a Git repository.
    
    Args:
        repo_path (str): Path to the Git repository
        output_dir (str): Directory to save analysis results
    """
    try:
        print(f"🔍 Analyzing repository: {repo_path}")
        print("=" * 60)
        
        # Initialize the repository
        print("\n📂 Initializing repository connection...")
        git_repo = GitRepository(repo_path)
        
        # Display basic repository info
        repo_stats = git_repo.get_repository_stats()
        print(f"✅ Repository loaded successfully!")
        print(f"   - Active branch: {repo_stats.get('active_branch', 'Unknown')}")
        print(f"   - Total commits: {repo_stats.get('total_commits', 0)}")
        print(f"   - Total branches: {repo_stats.get('total_branches', 0)}")
        print(f"   - Total tags: {repo_stats.get('total_tags', 0)}")
        
        # Initialize analyzers
        print("\n🔧 Initializing analyzers...")
        commit_analyzer = CommitAnalyzer(git_repo)
        file_analyzer = FileAnalyzer(git_repo)
        contributor_analyzer = ContributorAnalyzer(git_repo)
        branch_analyzer = BranchAnalyzer(git_repo)
        metrics = GitMetrics(git_repo)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. COMMIT ANALYSIS
        print("\n📊 Analyzing commits...")
        
        # Commit frequency analysis
        daily_commits = commit_analyzer.get_commit_frequency_by_date()
        print(f"   - Analyzed {len(daily_commits)} days of commit activity")
        
        # Commit messages analysis
        message_analysis = commit_analyzer.get_commit_messages_analysis()
        print(f"   - Average commit message length: {message_analysis.get('avg_message_length', 0):.1f} characters")
        print(f"   - Most common commit words: {', '.join([word for word, _ in message_analysis.get('common_words', [])[:5]])}")
        
        # Merge analysis
        merge_analysis = commit_analyzer.get_merge_commit_analysis()
        print(f"   - Merge commits: {merge_analysis.get('merge_percentage', 0):.1f}% of total commits")
        
        # 2. FILE ANALYSIS
        print("\n📁 Analyzing files...")
        
        # File extensions
        extensions = file_analyzer.get_file_extensions_distribution()
        print(f"   - Found {len(extensions)} different file extensions")
        if not extensions.empty:
            top_ext = extensions.head(3)
            for _, row in top_ext.iterrows():
                print(f"     • {row['extension']}: {row['count']} files")
        
        # Most changed files
        most_changed = file_analyzer.get_most_changed_files(5)
        print(f"   - Top 5 most changed files:")
        if not most_changed.empty:
            for _, row in most_changed.iterrows():
                filename = Path(row['file_path']).name
                print(f"     • {filename}: {row['change_count']} changes")
        
        # 3. CONTRIBUTOR ANALYSIS
        print("\n👥 Analyzing contributors...")
        
        contributor_stats = contributor_analyzer.get_contributor_statistics()
        print(f"   - Total contributors: {len(contributor_stats)}")
        
        if not contributor_stats.empty:
            # Top contributors
            top_contributors = contributor_stats.head(5)
            print("   - Top 5 contributors:")
            for _, row in top_contributors.iterrows():
                print(f"     • {row['author']}: {row['total_commits']} commits, "
                      f"+{row['total_insertions']}/-{row['total_deletions']} lines")
            
            # Impact analysis
            impact_analysis = contributor_analyzer.get_contributor_impact_analysis()
            if not impact_analysis.empty:
                top_impact = impact_analysis.head(3)
                print("   - Top contributors by impact:")
                for _, row in top_impact.iterrows():
                    print(f"     • {row['author']}: Impact score {row['impact_score']:.1f}")
        
        # 4. BRANCH ANALYSIS
        print("\n🌿 Analyzing branches...")
        
        branch_stats = branch_analyzer.get_branch_statistics()
        print(f"   - Total branches: {len(branch_stats)}")
        
        # Branching strategy insights
        branching_insights = branch_analyzer.get_branching_strategy_insights()
        print(f"   - Detected branching model: {branching_insights.get('branching_model', 'Unknown')}")
        print(f"   - Average branch lifetime: {branching_insights.get('avg_branch_lifetime_days', 0):.1f} days")
        
        # Recommendations
        recommendations = branching_insights.get('recommendations', [])
        if recommendations:
            print("   - Recommendations:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"     • {rec}")
        
        # 5. GENERATE COMPREHENSIVE REPORT
        print("\n📈 Generating comprehensive analysis...")
        
        # Create visualizations and reports
        try:
            # Export metrics to CSV
            csv_files = metrics.export_metrics_to_csv(output_dir)
            print(f"   - Exported {len(csv_files)} CSV files to {output_dir}/")
            
            # Create interactive dashboards
            commit_dashboard_path = os.path.join(output_dir, "commit_activity_dashboard.html")
            metrics.create_commit_activity_dashboard(commit_dashboard_path)
            print(f"   - Created commit activity dashboard: {commit_dashboard_path}")
            
            contributor_charts_path = os.path.join(output_dir, "contributor_analysis.html")
            metrics.create_contributor_analysis_charts(contributor_charts_path)
            print(f"   - Created contributor analysis charts: {contributor_charts_path}")
            
            file_viz_path = os.path.join(output_dir, "file_analysis.html")
            metrics.create_file_analysis_visualization(file_viz_path)
            print(f"   - Created file analysis visualization: {file_viz_path}")
            
            # Create comprehensive report
            report_path = os.path.join(output_dir, "comprehensive_report.html")
            if metrics.create_comprehensive_report(report_path):
                print(f"   - Created comprehensive report: {report_path}")
            
        except Exception as e:
            print(f"   ⚠️  Warning: Could not create some visualizations: {e}")
            print("   (This is normal if matplotlib/plotly packages are not installed)")
        
        # 6. SUMMARY
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 60)
        
        summary = metrics.generate_repository_summary()
        print("\n📋 REPOSITORY SUMMARY:")
        print(f"   Repository: {repo_stats.get('path', 'Unknown')}")
        print(f"   Total Commits: {summary.get('commits', {}).get('total_commits', 0)}")
        print(f"   Contributors: {summary.get('contributors', {}).get('total_contributors', 0)}")
        print(f"   Branches: {summary.get('branches', {}).get('total_branches', 0)}")
        print(f"   File Extensions: {summary.get('files', {}).get('total_unique_extensions', 0)}")
        print(f"   Branching Model: {summary.get('branches', {}).get('branching_model', 'Unknown')}")
        
        print(f"\n📁 Analysis results saved to: {os.path.abspath(output_dir)}")
        
        # Close repository connection
        git_repo.close()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    
    return True

def main():
    """Main function with example usage."""
    
    print("🚀 GitDecomposer - Git Repository Analysis Tool")
    print("=" * 60)
    
    # Example usage - you can modify this path
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        # Use current directory if no argument provided
        repo_path = "."
        print("💡 No repository path provided, using current directory")
        print("   Usage: python example_usage.py <path_to_git_repository>")
    
    # Check if path exists and is a git repository
    if not os.path.exists(repo_path):
        print(f"❌ Error: Path '{repo_path}' does not exist")
        return
    
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print(f"❌ Error: '{repo_path}' is not a Git repository")
        return
    
    # Perform analysis
    success = analyze_repository(repo_path)
    
    if success:
        print("\n🎉 Analysis completed successfully!")
        print("\nNext steps:")
        print("• Open the HTML files in your browser to view interactive charts")
        print("• Review the CSV files for detailed data analysis")
        print("• Use the insights to improve your development workflow")
    else:
        print("\n❌ Analysis failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
