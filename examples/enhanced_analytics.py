#!/usr/bin/env python3
"""
Enhanced Analytics Example: Demonstrating new analytical capabilities

This example shows how to use the new advanced metrics including:
- Commit velocity analysis
- Code churn rate analysis  
- Bug fix ratio analysis
- Documentation coverage analysis
- Maintainability index calculation
- Technical debt accumulation analysis
- Test-to-code ratio analysis
"""

import os
import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer import GitRepository, GitMetrics

def analyze_enhanced_metrics(repo_path: str):
    """
    Demonstrate the new analytical capabilities.
    
    Args:
        repo_path (str): Path to the Git repository
    """
    print(f"Enhanced Analytics Demo: {repo_path}")
    print("=" * 60)
    
    # Initialize repository and metrics
    repo = GitRepository(repo_path)
    metrics = GitMetrics(repo)
    
    # Get enhanced repository summary
    print("\n1. ENHANCED REPOSITORY SUMMARY")
    print("-" * 40)
    enhanced_summary = metrics.get_enhanced_repository_summary()
    
    # Display repository health score
    health_score = enhanced_summary.get('repository_health_score', 0)
    health_category = enhanced_summary.get('repository_health_category', 'Unknown')
    print(f"Repository Health Score: {health_score:.1f}/100 ({health_category})")
    
    # Display advanced metrics
    advanced_metrics = enhanced_summary.get('advanced_metrics', {})
    
    print("\n2. COMMIT VELOCITY ANALYSIS")
    print("-" * 40)
    velocity = advanced_metrics.get('commit_velocity', {})
    print(f"Average commits per week: {velocity.get('avg_commits_per_week', 0):.1f}")
    print(f"Velocity trend: {velocity.get('velocity_trend', 'unknown')}")
    print(f"Velocity change: {velocity.get('velocity_change_percentage', 0):.1f}%")
    
    print("\n3. CODE QUALITY METRICS")
    print("-" * 40)
    quality = advanced_metrics.get('code_quality', {})
    print(f"Bug fix ratio: {quality.get('bug_fix_ratio', 0):.1f}%")
    print(f"Code churn rate: {quality.get('code_churn_rate', 0):.1f}%")
    print(f"Maintainability score: {quality.get('maintainability_score', 0):.1f}/100")
    print(f"Technical debt rate: {quality.get('technical_debt_rate', 0):.1f}%")
    
    print("\n4. COVERAGE METRICS")
    print("-" * 40)
    coverage = advanced_metrics.get('coverage_metrics', {})
    print(f"Documentation ratio: {coverage.get('documentation_ratio', 0):.1f}%")
    print(f"Test-to-code ratio: {coverage.get('test_to_code_ratio', 0):.2f}")
    print(f"Test coverage percentage: {coverage.get('test_coverage_percentage', 0):.1f}%")
    
    # Detailed analysis of individual components
    print("\n5. DETAILED VELOCITY ANALYSIS")
    print("-" * 40)
    velocity_analysis = metrics.commit_analyzer.get_commit_velocity_analysis()
    weekly_velocity = velocity_analysis.get('weekly_velocity')
    if not weekly_velocity.empty:
        print(f"Weeks analyzed: {len(weekly_velocity)}")
        print(f"Current week velocity: {velocity_analysis.get('current_week_velocity', 0)} commits")
        print("Recent weekly velocities:")
        for _, row in weekly_velocity.tail(5).iterrows():
            print(f"  {row['week_start']}: {row['commit_count']} commits")
    
    print("\n6. BUG FIX RATIO ANALYSIS")
    print("-" * 40)
    bug_fix_analysis = metrics.commit_analyzer.get_bug_fix_ratio_analysis()
    print(f"Total commits: {bug_fix_analysis.get('total_commits', 0)}")
    print(f"Bug fix commits: {bug_fix_analysis.get('bug_fix_commits', 0)}")
    print(f"Bug fix ratio: {bug_fix_analysis.get('bug_fix_ratio', 0):.1f}%")
    
    common_keywords = bug_fix_analysis.get('common_bug_keywords', [])
    if common_keywords:
        print(f"Common bug keywords: {', '.join(common_keywords[:5])}")
    
    print("\n7. CODE CHURN ANALYSIS")
    print("-" * 40)
    churn_analysis = metrics.file_analyzer.get_code_churn_analysis()
    print(f"Overall churn rate: {churn_analysis.get('overall_churn_rate', 0):.2f}%")
    print(f"Total lines changed: {churn_analysis.get('total_lines_changed', 0):,}")
    print(f"Estimated total lines: {churn_analysis.get('estimated_total_lines', 0):,}")
    
    high_churn_files = churn_analysis.get('high_churn_files', [])
    if high_churn_files:
        print("High churn files (top 5):")
        for file_info in high_churn_files[:5]:
            file_name = Path(file_info['file_path']).name
            print(f"  {file_name}: {file_info['churn_rate']:.1f}% churn rate")
    
    print("\n8. MAINTAINABILITY INDEX")
    print("-" * 40)
    maintainability = metrics.advanced_metrics.calculate_maintainability_index()
    print(f"Overall maintainability score: {maintainability.get('overall_maintainability_score', 0):.1f}/100")
    
    factors = maintainability.get('maintainability_factors', {})
    print(f"Average commits per file: {factors.get('avg_commits_per_file', 0):.1f}")
    print(f"Average authors per file: {factors.get('avg_authors_per_file', 0):.1f}")
    print(f"Files needing attention: {factors.get('files_needing_attention', 0)}")
    print(f"Excellent files: {factors.get('excellent_files', 0)}")
    
    print("\n9. TECHNICAL DEBT ANALYSIS")
    print("-" * 40)
    debt_analysis = metrics.advanced_metrics.calculate_technical_debt_accumulation()
    print(f"Debt accumulation rate: {debt_analysis.get('debt_accumulation_rate', 0):.1f}%")
    print(f"Total debt commits: {debt_analysis.get('total_debt_commits', 0)}")
    
    debt_by_type = debt_analysis.get('debt_by_type', {})
    if debt_by_type:
        print("Debt types found:")
        for debt_type, count in sorted(debt_by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  {debt_type}: {count} occurrences")
    
    print("\n10. TEST COVERAGE ANALYSIS")
    print("-" * 40)
    test_analysis = metrics.advanced_metrics.calculate_test_to_code_ratio()
    print(f"Test-to-code ratio: {test_analysis.get('test_to_code_ratio', 0):.2f}")
    print(f"Test files: {test_analysis.get('test_files_count', 0)}")
    print(f"Code files: {test_analysis.get('code_files_count', 0)}")
    print(f"Test coverage: {test_analysis.get('test_coverage_percentage', 0):.1f}%")
    
    untested_dirs = test_analysis.get('untested_directories', [])
    if untested_dirs:
        print("Directories without tests:")
        for dir_info in untested_dirs[:5]:
            print(f"  {dir_info['directory']}: {dir_info['file_count']} files")
    
    print("\n11. DOCUMENTATION COVERAGE")
    print("-" * 40)
    doc_analysis = metrics.file_analyzer.get_documentation_coverage_analysis()
    print(f"Documentation ratio: {doc_analysis.get('documentation_ratio', 0):.1f}%")
    print(f"Documentation files: {doc_analysis.get('doc_files_count', 0)}")
    print(f"Total files: {doc_analysis.get('total_files_count', 0)}")
    
    doc_types = doc_analysis.get('doc_file_types', {})
    if doc_types:
        print("Documentation file types:")
        for file_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {file_type}: {count} files")
    
    # Display recommendations
    print("\n12. ENHANCED RECOMMENDATIONS")
    print("-" * 40)
    recommendations = enhanced_summary.get('enhanced_recommendations', [])
    if recommendations:
        for i, rec in enumerate(recommendations[:10], 1):
            print(f"{i:2d}. {rec}")
    else:
        print("No specific recommendations at this time.")
    
    print("\n" + "=" * 60)
    print("ENHANCED ANALYTICS COMPLETE!")
    print("=" * 60)
    print(f"Repository Health: {health_score:.1f}/100 ({health_category})")
    print("\nKey Insights:")
    print(f"• Velocity: {velocity.get('avg_commits_per_week', 0):.1f} commits/week ({velocity.get('velocity_trend', 'stable')})")
    print(f"• Quality: {quality.get('maintainability_score', 0):.1f}/100 maintainability")
    print(f"• Testing: {coverage.get('test_coverage_percentage', 0):.1f}% test coverage")
    print(f"• Documentation: {coverage.get('documentation_ratio', 0):.1f}% doc coverage")
    
    # Close repository connection
    repo.close()

if __name__ == "__main__":
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Check if path exists and is a git repository
    if not os.path.exists(repo_path):
        print(f"Error: Path '{repo_path}' does not exist")
        sys.exit(1)
    
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print(f"Error: '{repo_path}' is not a Git repository")
        sys.exit(1)
    
    analyze_enhanced_metrics(repo_path)
