"""
Command Line Interface for GitDecomposer.
"""

import argparse
import sys
import os
from pathlib import Path

# Add the package to Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer import GitRepository, GitMetrics


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="GitDecomposer - Analyze Git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitdecomposer /path/to/repo
  gitdecomposer . --output ./analysis
  gitdecomposer /path/to/repo --format csv
        """
    )
    
    parser.add_argument(
        "repository",
        help="Path to the Git repository to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="./gitdecomposer_output",
        help="Output directory for analysis results (default: ./gitdecomposer_output)"
    )
    
    parser.add_argument(
        "--format",
        choices=["html", "csv", "both"],
        default="both",
        help="Output format (default: both)"
    )
    
    parser.add_argument(
        "--no-visualizations",
        action="store_true",
        help="Skip creating visualization files (faster analysis)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate repository path
    repo_path = Path(args.repository).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path '{repo_path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not (repo_path / ".git").exists():
        print(f"Error: '{repo_path}' is not a Git repository", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize repository and metrics
        if args.verbose:
            print(f"Initializing repository: {repo_path}")
        
        git_repo = GitRepository(str(repo_path))
        metrics = GitMetrics(git_repo)
        
        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if args.verbose:
            print(f"Output directory: {output_dir.resolve()}")
        
        # Generate summary
        print("Generating repository analysis...")
        summary = metrics.generate_repository_summary()
        
        # Print basic stats
        print("\n" + "="*50)
        print("REPOSITORY ANALYSIS SUMMARY")
        print("="*50)
        
        repo_info = summary.get('repository_info', {})
        print(f"Repository: {repo_info.get('path', 'Unknown')}")
        print(f"Active Branch: {repo_info.get('active_branch', 'Unknown')}")
        
        commits_info = summary.get('commits', {})
        print(f"Total Commits: {commits_info.get('total_commits', 0)}")
        
        contributors_info = summary.get('contributors', {})
        print(f"Contributors: {contributors_info.get('total_contributors', 0)}")
        
        branches_info = summary.get('branches', {})
        print(f"Branches: {branches_info.get('total_branches', 0)}")
        print(f"Branching Model: {branches_info.get('branching_model', 'Unknown')}")
        
        # Export data
        if args.format in ["csv", "both"]:
            print("\nExporting CSV files...")
            csv_files = metrics.export_metrics_to_csv(str(output_dir))
            print(f"Exported {len(csv_files)} CSV files")
        
        # Create visualizations
        if args.format in ["html", "both"] and not args.no_visualizations:
            print("\nCreating visualizations...")
            
            try:
                # Create individual dashboards
                commit_path = output_dir / "commit_activity.html"
                metrics.create_commit_activity_dashboard(str(commit_path))
                
                contributor_path = output_dir / "contributor_analysis.html"
                metrics.create_contributor_analysis_charts(str(contributor_path))
                
                file_path = output_dir / "file_analysis.html"
                metrics.create_file_analysis_visualization(str(file_path))
                
                # Create enhanced file analysis dashboard
                enhanced_file_path = output_dir / "enhanced_file_analysis.html"
                metrics.create_enhanced_file_analysis_dashboard(str(enhanced_file_path))
                
                # Create comprehensive report
                report_path = output_dir / "comprehensive_report.html"
                metrics.create_comprehensive_report(str(report_path))
                
                print("Created visualization files:")
                print(f"  - {commit_path}")
                print(f"  - {contributor_path}")
                print(f"  - {file_path}")
                print(f"  - {enhanced_file_path}")
                print(f"  - {report_path}")
                
            except ImportError:
                print("Warning: Visualization libraries not available. Install with: pip install matplotlib plotly")
            except Exception as e:
                print(f"Warning: Could not create visualizations: {e}")
        
        # Show recommendations
        recommendations = branches_info.get('recommendations', [])
        if recommendations:
            print("\nRECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print(f"\nAnalysis complete! Results saved to: {output_dir.resolve()}")
        
        # Cleanup
        git_repo.close()
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
