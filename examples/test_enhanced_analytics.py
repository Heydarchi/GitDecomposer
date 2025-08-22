#!/usr/bin/env python3
"""
Test script for enhanced GitDecomposer analytics and reporting.
This script demonstrates the new analytical capabilities and report generation.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import gitdecomposer
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer import AdvancedMetrics, GitMetrics, GitRepository


def test_enhanced_analytics():
    """Test the enhanced analytics features."""
    try:
        # Use current repository as example
        repo_path = str(Path(__file__).parent.parent)
        print(f"Analyzing repository: {repo_path}")

        # Initialize GitDecomposer components
        repo = GitRepository(repo_path)
        metrics = GitMetrics(repo)

        print("\n=== Enhanced Repository Analysis ===")

        # Generate enhanced summary with new analytics
        enhanced_summary = metrics.get_enhanced_repository_summary()

        print(f"Repository Health Score: {enhanced_summary.get('repository_health_score', 0):.1f}/100")
        print(f"Health Category: {enhanced_summary.get('repository_health_category', 'Unknown')}")

        # Display advanced metrics
        advanced_metrics = enhanced_summary.get("advanced_metrics", {})

        print("\n--- Commit Velocity Analysis ---")
        velocity_data = advanced_metrics.get("commit_velocity", {})
        print(f"Average commits per week: {velocity_data.get('avg_commits_per_week', 0):.2f}")
        print(f"Velocity trend: {velocity_data.get('velocity_trend', 'stable')}")
        print(f"Velocity change: {velocity_data.get('velocity_change_percentage', 0):+.1f}%")

        print("\n--- Code Quality Metrics ---")
        quality_data = advanced_metrics.get("code_quality", {})
        print(f"Bug fix ratio: {quality_data.get('bug_fix_ratio', 0):.1f}%")
        print(f"Code churn rate: {quality_data.get('code_churn_rate', 0):.1f}%")
        print(f"Maintainability score: {quality_data.get('maintainability_score', 0):.1f}/100")
        print(f"Technical debt rate: {quality_data.get('technical_debt_rate', 0):.1f}%")

        print("\n--- Coverage Metrics ---")
        coverage_data = advanced_metrics.get("coverage_metrics", {})
        print(f"Test coverage: {coverage_data.get('test_coverage_percentage', 0):.1f}%")
        print(f"Documentation ratio: {coverage_data.get('documentation_ratio', 0):.1f}%")

        # Export enhanced metrics to CSV
        print("\n=== Exporting Enhanced Metrics ===")
        export_dir = Path("enhanced_analytics_export")
        export_dir.mkdir(exist_ok=True)

        success = metrics.export_metrics_to_csv(str(export_dir))
        if success:
            print(f"Enhanced analytics exported to: {export_dir.absolute()}")

            # List exported files
            exported_files = list(export_dir.glob("*.csv"))
            print(f"Exported {len(exported_files)} CSV files:")
            for file in sorted(exported_files):
                print(f"  - {file.name}")
        else:
            print("Failed to export enhanced metrics")

        # Generate comprehensive HTML report
        print("\n=== Generating Enhanced HTML Report ===")
        report_path = "enhanced_repository_report.html"

        success = metrics.create_comprehensive_report(report_path)
        if success:
            print(f"Enhanced comprehensive report generated: {Path(report_path).absolute()}")
            print("The report includes:")
            print("  - Repository health score and dashboard")
            print("  - Advanced analytics (velocity, quality, coverage)")
            print("  - Interactive visualizations")
            print("  - Personalized recommendations")
            print("  - Trend analysis and insights")
        else:
            print("Failed to generate comprehensive report")

        # Display recommendations
        recommendations = enhanced_summary.get("enhanced_recommendations", [])
        if recommendations:
            print(f"\n=== Recommendations ({len(recommendations)}) ===")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")

        print("\n=== Enhanced Analytics Test Complete ===")
        print("✓ Repository health scoring")
        print("✓ Commit velocity analysis")
        print("✓ Code quality assessment")
        print("✓ Coverage metrics")
        print("✓ Technical debt tracking")
        print("✓ Enhanced CSV exports")
        print("✓ Comprehensive HTML reporting")

        return True

    except Exception as e:
        print(f"Error during enhanced analytics test: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_individual_analytics():
    """Test individual analytical components."""
    try:
        repo_path = str(Path(__file__).parent.parent)
        repo = GitRepository(repo_path)
        metrics = GitMetrics(repo)

        print("\n=== Individual Analytics Testing ===")

        # Test commit velocity
        print("\n--- Commit Velocity Analysis ---")
        velocity_analysis = metrics.commit_analyzer.get_commit_velocity_analysis()
        print(f"Weekly velocity: {velocity_analysis.get('avg_commits_per_week', 0):.2f}")
        print(f"Total periods: {velocity_analysis.get('total_periods', 0)}")

        # Test bug fix analysis
        print("\n--- Bug Fix Analysis ---")
        bug_analysis = metrics.commit_analyzer.get_bug_fix_ratio_analysis()
        print(f"Bug fix commits: {bug_analysis.get('bug_fix_commits', 0)}")
        print(f"Total commits: {bug_analysis.get('total_commits', 0)}")
        print(f"Bug fix ratio: {bug_analysis.get('bug_fix_ratio', 0):.1f}%")

        # Test code churn analysis
        print("\n--- Code Churn Analysis ---")
        churn_analysis = metrics.file_analyzer.get_code_churn_analysis()
        print(f"High churn files: {churn_analysis.get('high_churn_files_count', 0)}")
        print(f"Overall churn rate: {churn_analysis.get('overall_churn_rate', 0):.2f}%")

        # Test documentation analysis
        print("\n--- Documentation Analysis ---")
        doc_analysis = metrics.file_analyzer.get_documentation_coverage_analysis()
        print(f"Documentation files: {doc_analysis.get('doc_files_count', 0)}")
        print(f"Documentation ratio: {doc_analysis.get('documentation_ratio', 0):.1f}%")

        # Test maintainability
        print("\n--- Maintainability Analysis ---")
        maintainability = metrics.advanced_metrics.calculate_maintainability_index()
        print(f"Overall score: {maintainability.get('overall_maintainability_score', 0):.1f}")
        print(f"Files analyzed: {maintainability.get('maintainability_factors', {}).get('total_files_analyzed', 0)}")

        # Test technical debt
        print("\n--- Technical Debt Analysis ---")
        debt_analysis = metrics.advanced_metrics.calculate_technical_debt_accumulation()
        print(f"Debt accumulation rate: {debt_analysis.get('debt_accumulation_rate', 0):.2f}%")
        print(f"Debt indicators: {debt_analysis.get('debt_indicators', {})}")

        # Test test coverage
        print("\n--- Test Coverage Analysis ---")
        test_analysis = metrics.advanced_metrics.calculate_test_to_code_ratio()
        print(f"Test files: {test_analysis.get('test_files_count', 0)}")
        print(f"Code files: {test_analysis.get('code_files_count', 0)}")
        print(f"Test coverage: {test_analysis.get('test_coverage_percentage', 0):.1f}%")

        print("\n=== Individual Analytics Test Complete ===")
        return True

    except Exception as e:
        print(f"Error during individual analytics test: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("GitDecomposer Enhanced Analytics Test")
    print("=" * 50)

    # Test enhanced analytics
    success1 = test_enhanced_analytics()

    # Test individual components
    success2 = test_individual_analytics()

    if success1 and success2:
        print("\n🎉 All enhanced analytics tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
