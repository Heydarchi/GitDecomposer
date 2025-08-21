#!/usr/bin/env python3
"""
Updated comprehensive example demonstrating GitDecomposer with advanced reporting capabilities.
This example shows how to use all the new advanced reports and dashboards.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import gitdecomposer
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer import GitRepository, GitMetrics


def demonstrate_advanced_reports():
    """
    Demonstrate all the advanced reporting capabilities.
    """
    try:
        # Use current repository as example
        repo_path = str(Path(__file__).parent.parent)
        print(f"Analyzing repository: {repo_path}")

        # Initialize GitDecomposer components
        repo = GitRepository(repo_path)
        metrics = GitMetrics(repo)

        print("\n=== Advanced GitDecomposer Reporting Demo ===")
        print("=" * 60)

        # 1. Generate enhanced repository summary
        print("\n1. Generating Enhanced Repository Summary...")
        enhanced_summary = metrics.get_enhanced_repository_summary()

        health_score = enhanced_summary.get("repository_health_score", 0)
        health_category = enhanced_summary.get("repository_health_category", "Unknown")

        print(f"   Repository Health Score: {health_score:.1f}/100")
        print(f"   Health Category: {health_category}")

        advanced_metrics = enhanced_summary.get("advanced_metrics", {})
        velocity_data = advanced_metrics.get("commit_velocity", {})
        quality_data = advanced_metrics.get("code_quality", {})
        coverage_data = advanced_metrics.get("coverage_metrics", {})

        print(
            f"   Commit Velocity: {velocity_data.get('avg_commits_per_week', 0):.1f} commits/week"
        )
        print(f"   Maintainability: {quality_data.get('maintainability_score', 0):.1f}/100")
        print(f"   Test Coverage: {coverage_data.get('test_coverage_percentage', 0):.1f}%")

        # 2. Generate individual advanced reports
        print("\n2. Generating Individual Advanced Reports...")

        # Technical Debt Dashboard
        print("   ✓ Creating Technical Debt Analysis Dashboard...")
        debt_dashboard = metrics.create_technical_debt_dashboard("technical_debt_dashboard.html")

        # Repository Health Dashboard
        print("   ✓ Creating Repository Health Dashboard...")
        health_dashboard = metrics.create_repository_health_dashboard(
            "repository_health_dashboard.html"
        )

        # Predictive Maintenance Report
        print("   ✓ Creating Predictive Maintenance Report...")
        predictive_report = metrics.create_predictive_maintenance_report(
            "predictive_maintenance_report.html"
        )

        # Velocity Forecasting Dashboard
        print("   ✓ Creating Velocity Forecasting Dashboard...")
        velocity_dashboard = metrics.create_velocity_forecasting_dashboard(
            "velocity_forecasting_dashboard.html"
        )

        # 3. Generate all advanced reports at once
        print("\n3. Generating All Advanced Reports (Batch Mode)...")
        output_dir = "advanced_reports_output"
        generated_reports = metrics.generate_all_advanced_reports(output_dir)

        print(f"   Generated {len(generated_reports)} reports in '{output_dir}':")
        for report_name, filepath in generated_reports.items():
            print(f"     - {report_name}: {filepath}")

        # 4. Generate comprehensive report with all advanced features
        print("\n4. Generating Enhanced Comprehensive Report...")
        comprehensive_path = "enhanced_comprehensive_report.html"
        success = metrics.create_comprehensive_report(comprehensive_path)

        if success:
            print(f"   ✓ Enhanced comprehensive report: {comprehensive_path}")
            print("     This report now includes:")
            print("       - Repository health scoring")
            print("       - Technical debt analysis")
            print("       - Predictive maintenance insights")
            print("       - Velocity forecasting")
            print("       - Advanced analytics dashboard")
        else:
            print("   ✗ Failed to generate comprehensive report")

        # 5. Export enhanced metrics
        print("\n5. Exporting Enhanced Analytics Data...")
        csv_export_dir = "enhanced_csv_exports"
        exported_files = metrics.export_metrics_to_csv(csv_export_dir)

        print(f"   Exported {len(exported_files)} CSV files to '{csv_export_dir}':")
        for metric_name, filepath in exported_files.items():
            print(f"     - {metric_name}: {Path(filepath).name}")

        # 6. Display key insights and recommendations
        print("\n6. Key Insights and Recommendations:")
        recommendations = enhanced_summary.get("enhanced_recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                print(f"   {i}. {rec}")
        else:
            print("   No specific recommendations - repository is in good health!")

        # 7. Advanced analytics summary
        print("\n7. Advanced Analytics Summary:")
        print("   Available Advanced Reports:")
        print("     ✓ Technical Debt Analysis - Debt trends, hotspots, priority matrix")
        print("     ✓ Repository Health Dashboard - Health scoring, quality radar, risk assessment")
        print(
            "     ✓ Predictive Maintenance - Effort forecasting, resource planning, interventions"
        )
        print(
            "     ✓ Velocity Forecasting - Sprint predictions, productivity analysis, bottlenecks"
        )
        print("     ✓ Enhanced Comprehensive Report - All analytics in one unified report")

        print("\n   Advanced Capabilities:")
        print("     • Predictive analytics for maintenance planning")
        print("     • Real-time health monitoring with alerts")
        print("     • Interactive dashboards with drill-down capabilities")
        print("     • Correlation analysis between different metrics")
        print("     • Trend forecasting and confidence intervals")
        print("     • Risk assessment and prioritization matrices")

        print("\n=== Advanced Reporting Demo Complete ===")
        print("✓ Repository health assessment")
        print("✓ Technical debt analysis")
        print("✓ Predictive maintenance forecasting")
        print("✓ Velocity trend analysis")
        print("✓ Enhanced CSV exports")
        print("✓ Comprehensive HTML reporting")
        print("✓ Advanced visualization dashboards")

        return True

    except Exception as e:
        print(f"Error during advanced reporting demo: {e}")
        import traceback

        traceback.print_exc()
        return False


def compare_basic_vs_advanced():
    """
    Compare basic vs advanced reporting capabilities.
    """
    print("\n=== Basic vs Advanced Reporting Comparison ===")
    print()

    print("BASIC REPORTING (Before):")
    print("• Basic commit activity dashboard")
    print("• Contributor analysis charts")
    print("• File analysis visualization")
    print("• Simple CSV exports")
    print("• Basic HTML report")
    print()

    print("ADVANCED REPORTING (Now):")
    print("• All basic reports PLUS:")
    print("• Technical debt analysis dashboard")
    print("• Repository health scoring system")
    print("• Predictive maintenance forecasting")
    print("• Velocity trend analysis and forecasting")
    print("• Enhanced file analysis with hotspots")
    print("• Advanced correlation analysis")
    print("• Risk assessment and prioritization")
    print("• Interactive exploration capabilities")
    print("• Enhanced CSV exports with 7+ new data types")
    print("• Comprehensive unified reporting")
    print()

    print("NEW ANALYTICAL CAPABILITIES:")
    print("1. Commit velocity tracking with trend analysis")
    print("2. Code churn rate analysis")
    print("3. Bug fix ratio monitoring")
    print("4. Maintainability index scoring")
    print("5. Technical debt accumulation tracking")
    print("6. Test-to-code ratio analysis")
    print("7. Documentation coverage assessment")
    print()

    print("BUSINESS VALUE:")
    print("• Data-driven decision making")
    print("• Proactive problem identification")
    print("• Resource optimization insights")
    print("• Quality improvement tracking")
    print("• Risk mitigation planning")
    print("• Team performance optimization")


if __name__ == "__main__":
    print("GitDecomposer Advanced Reporting Demonstration")
    print("=" * 70)

    # Run the advanced reporting demonstration
    success = demonstrate_advanced_reports()

    # Show comparison between basic and advanced features
    compare_basic_vs_advanced()

    if success:
        print("\n🎉 All advanced reporting features demonstrated successfully!")
        print("\nGenerated Files:")
        print("• technical_debt_dashboard.html")
        print("• repository_health_dashboard.html")
        print("• predictive_maintenance_report.html")
        print("• velocity_forecasting_dashboard.html")
        print("• enhanced_comprehensive_report.html")
        print("• advanced_reports_output/ (directory with all reports)")
        print("• enhanced_csv_exports/ (directory with enhanced CSV data)")
    else:
        print("\n❌ Some features failed. Check the output above.")
        sys.exit(1)
