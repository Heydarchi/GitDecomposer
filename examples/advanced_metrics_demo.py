#!/usr/bin/env python3
"""
Example usage of the advanced repository metrics.

This script demonstrates how to use the new advanced metrics analyzers
to gain deep insights into repository health, team productivity, and
development patterns.
"""

import sys
import os
from datetime import datetime

# Add the gitdecomposer package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.analyzers.advanced_metrics import (
    create_metric_analyzer,
    get_available_metrics,
    METRIC_ANALYZERS
)


def run_advanced_metrics_analysis(repo_path: str):
    """
    Run a comprehensive analysis using all advanced metrics.
    
    Args:
        repo_path: Path to the Git repository to analyze
    """
    print(f"🔍 Analyzing repository: {repo_path}")
    print("=" * 80)
    
    try:
        # Initialize the repository
        repository = GitRepository(repo_path)
        
        # Get all available metrics
        available_metrics = get_available_metrics()
        print(f"📊 Running {len(available_metrics)} advanced metrics:")
        print(f"   {', '.join(available_metrics)}")
        print("-" * 80)
        
        results = {}
        
        # Run each metric analysis
        for metric_name in available_metrics:
            print(f"\n🔬 Analyzing: {metric_name.replace('_', ' ').title()}")
            
            try:
                # Create analyzer instance
                analyzer = create_metric_analyzer(metric_name, repository)
                
                # Print metric description
                print(f"   Description: {analyzer.get_description()}")
                
                # Run the analysis
                result = analyzer.calculate()
                results[metric_name] = result
                
                # Print summary
                print_metric_summary(metric_name, result)
                
            except Exception as e:
                print(f"   ❌ Error analyzing {metric_name}: {str(e)}")
                results[metric_name] = {'error': str(e)}
        
        # Print overall summary
        print_overall_summary(results)
        
        return results
        
    except Exception as e:
        print(f"❌ Failed to analyze repository: {str(e)}")
        return None


def print_metric_summary(metric_name: str, result: dict):
    """Print a summary of a metric analysis result."""
    if 'error' in result:
        print(f"   ❌ {result['error']}")
        return
    
    if metric_name == 'bus_factor':
        bus_factor = result.get('bus_factor', 0)
        risk_level = result.get('risk_level', 'UNKNOWN')
        total_contributors = result.get('total_contributors', 0)
        print(f"   🚌 Bus Factor: {bus_factor} (Risk: {risk_level})")
        print(f"   👥 Total Contributors: {total_contributors}")
        
    elif metric_name == 'knowledge_distribution':
        gini = result.get('gini_coefficient', 0)
        quality = result.get('distribution_quality', 'UNKNOWN')
        print(f"   📈 Gini Coefficient: {gini:.3f} (Quality: {quality})")
        
    elif metric_name == 'critical_files':
        critical_count = result.get('critical_file_count', 0)
        total_files = result.get('total_files_analyzed', 0)
        print(f"   🎯 Critical Files: {critical_count} out of {total_files}")
        
    elif metric_name == 'single_point_failure':
        spof_count = result.get('spof_count', 0)
        risk_level = result.get('risk_level', 'UNKNOWN')
        print(f"   ⚠️  SPOF Files: {spof_count} (Risk: {risk_level})")
        
    elif metric_name == 'flow_efficiency':
        analysis = result.get('analysis', {})
        overall_efficiency = analysis.get('overall_efficiency', 0)
        performance = analysis.get('performance_category', 'UNKNOWN')
        print(f"   ⚡ Flow Efficiency: {overall_efficiency:.1%} ({performance})")
        
    elif metric_name == 'branch_lifecycle':
        analysis = result.get('analysis', {})
        total_branches = analysis.get('total_branches_analyzed', 0)
        phase_analysis = analysis.get('phase_analysis', {})
        total_lifecycle = phase_analysis.get('total_lifecycle', {})
        avg_days = total_lifecycle.get('avg_days', 0)
        print(f"   🔄 Branches Analyzed: {total_branches}")
        print(f"   ⏱️  Avg Lifecycle: {avg_days:.1f} days")
        
    elif metric_name == 'velocity_trend':
        overall_health = result.get('overall_health', {})
        status = overall_health.get('overall_status', 'unknown')
        health_level = overall_health.get('health_level', 'unknown')
        print(f"   📊 Velocity Trend: {status.title()} ({health_level.title()})")
        
    elif metric_name == 'cycle_time':
        statistics = result.get('statistics', {})
        mean_days = statistics.get('mean_days', 0)
        median_days = statistics.get('median_days', 0)
        count = statistics.get('count', 0)
        print(f"   🔄 Features Analyzed: {count}")
        print(f"   ⏰ Mean Cycle Time: {mean_days:.1f} days")
        print(f"   📊 Median Cycle Time: {median_days:.1f} days")
    
    # Print top recommendations
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"   💡 Top Recommendations:")
        for i, rec in enumerate(recommendations[:2], 1):
            print(f"      {i}. {rec}")


def print_overall_summary(results: dict):
    """Print an overall summary of all metrics."""
    print("\n" + "=" * 80)
    print("📋 OVERALL ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Count successful vs failed analyses
    successful = sum(1 for r in results.values() if 'error' not in r)
    failed = len(results) - successful
    
    print(f"✅ Successful Analyses: {successful}")
    print(f"❌ Failed Analyses: {failed}")
    
    # Identify high-priority concerns
    concerns = []
    strengths = []
    
    for metric_name, result in results.items():
        if 'error' in result:
            continue
            
        if metric_name == 'bus_factor':
            risk_level = result.get('risk_level', '')
            if risk_level in ['CRITICAL', 'HIGH']:
                concerns.append(f"Bus factor risk is {risk_level.lower()}")
            elif risk_level == 'LOW':
                strengths.append("Good knowledge distribution (bus factor)")
        
        elif metric_name == 'single_point_failure':
            risk_level = result.get('risk_level', '')
            if risk_level in ['CRITICAL', 'HIGH']:
                concerns.append(f"Single point of failure risk is {risk_level.lower()}")
        
        elif metric_name == 'flow_efficiency':
            analysis = result.get('analysis', {})
            performance = analysis.get('performance_category', '')
            if performance in ['VERY_POOR', 'POOR']:
                concerns.append(f"Flow efficiency is {performance.lower().replace('_', ' ')}")
            elif performance in ['EXCELLENT', 'GOOD']:
                strengths.append(f"Flow efficiency is {performance.lower()}")
    
    if concerns:
        print(f"\n🚨 HIGH PRIORITY CONCERNS:")
        for concern in concerns:
            print(f"   • {concern}")
    
    if strengths:
        print(f"\n💪 STRENGTHS IDENTIFIED:")
        for strength in strengths:
            print(f"   • {strength}")
    
    print(f"\n📅 Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main function to run the advanced metrics example."""
    # Default to current directory if no argument provided
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print("🚀 GitDecomposer Advanced Metrics Analysis")
    print("=" * 80)
    
    # Run the analysis
    results = run_advanced_metrics_analysis(repo_path)
    
    if results:
        print("\n✨ Analysis complete! Check the results above for insights.")
    else:
        print("\n❌ Analysis failed. Please check the repository path and try again.")


if __name__ == '__main__':
    main()
