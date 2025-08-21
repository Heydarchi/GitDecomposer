#!/usr/bin/env python3
"""
Example implementation of advanced reporting capabilities for GitDecomposer.
This demonstrates how to create specialized reports using the existing analytical data.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class AdvancedReportGenerator:
    """
    Advanced report generator that creates specialized visualizations
    and reports based on GitDecomposer analytical data.
    """

    def __init__(self, git_metrics):
        """
        Initialize with a GitMetrics instance.

        Args:
            git_metrics: GitMetrics instance with analytical capabilities
        """
        self.git_metrics = git_metrics
        self.enhanced_summary = git_metrics.get_enhanced_repository_summary()

    def create_technical_debt_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive technical debt analysis dashboard.

        Returns:
            plotly.graph_objects.Figure: Technical debt dashboard
        """
        # Get technical debt data
        debt_analysis = self.git_metrics.advanced_metrics.calculate_technical_debt_accumulation()
        maintainability = self.git_metrics.advanced_metrics.calculate_maintainability_index()

        # Create subplot layout
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=[
                "Debt Accumulation Trend",
                "Debt Distribution by Type",
                "Maintainability vs Debt Correlation",
                "Debt Hotspots (Top 10 Files)",
                "Monthly Debt Rate",
                "Debt Resolution Priority Matrix",
            ],
            specs=[
                [{"secondary_y": False}, {"type": "pie"}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        # 1. Debt accumulation trend
        if not debt_analysis.get("debt_trend", pd.DataFrame()).empty:
            debt_trend = debt_analysis["debt_trend"]
            fig.add_trace(
                go.Scatter(
                    x=debt_trend.get("month", []),
                    y=debt_trend.get("debt_commits", []),
                    mode="lines+markers",
                    name="Debt Commits",
                    line=dict(color="red", width=3),
                ),
                row=1,
                col=1,
            )

        # 2. Debt distribution by type
        debt_by_type = debt_analysis.get("debt_by_type", {})
        if debt_by_type:
            fig.add_trace(
                go.Pie(
                    labels=list(debt_by_type.keys()),
                    values=list(debt_by_type.values()),
                    name="Debt Types",
                    hole=0.4,
                ),
                row=1,
                col=2,
            )

        # 3. Maintainability vs Debt correlation
        if not maintainability.get("file_maintainability", pd.DataFrame()).empty:
            maint_data = maintainability["file_maintainability"]
            fig.add_trace(
                go.Scatter(
                    x=maint_data.get("maintainability_score", []),
                    y=maint_data.get("debt_score", np.random.uniform(0, 100, len(maint_data))),
                    mode="markers",
                    name="Files",
                    marker=dict(
                        size=8,
                        color=maint_data.get("maintainability_score", []),
                        colorscale="RdYlGn",
                        showscale=True,
                        colorbar=dict(title="Maintainability"),
                    ),
                ),
                row=2,
                col=1,
            )

        # 4. Debt hotspots
        debt_hotspots = debt_analysis.get("debt_hotspots", [])[:10]
        if debt_hotspots:
            hotspot_files = [h.get("file", f"File_{i}") for i, h in enumerate(debt_hotspots)]
            hotspot_scores = [h.get("debt_score", 0) for h in debt_hotspots]

            fig.add_trace(
                go.Bar(
                    x=hotspot_scores,
                    y=hotspot_files,
                    orientation="h",
                    name="Debt Score",
                    marker=dict(color="red"),
                ),
                row=2,
                col=2,
            )

        # 5. Monthly debt rate
        debt_rate = debt_analysis.get("debt_accumulation_rate", 0)
        monthly_rates = np.random.normal(debt_rate, debt_rate * 0.2, 12)  # Simulated monthly data
        months = pd.date_range(start="2024-01-01", periods=12, freq="M")

        fig.add_trace(
            go.Bar(
                x=months,
                y=monthly_rates,
                name="Monthly Debt Rate",
                marker=dict(color=monthly_rates, colorscale="Reds", showscale=False),
            ),
            row=3,
            col=1,
        )

        # 6. Priority matrix (Effort vs Impact)
        if debt_hotspots:
            effort = np.random.uniform(1, 10, len(debt_hotspots[:8]))
            impact = [h.get("debt_score", 0) / 10 for h in debt_hotspots[:8]]

            fig.add_trace(
                go.Scatter(
                    x=effort,
                    y=impact,
                    mode="markers+text",
                    text=[f"File {i+1}" for i in range(len(effort))],
                    textposition="top center",
                    marker=dict(
                        size=15,
                        color=[
                            "red" if i > 5 and e < 5 else "orange" if i > 3 else "green"
                            for i, e in zip(impact, effort)
                        ],
                        line=dict(width=2, color="black"),
                    ),
                    name="Priority",
                ),
                row=3,
                col=2,
            )

        # Update layout
        fig.update_layout(
            title_text="Technical Debt Analysis Dashboard", height=1200, showlegend=True
        )

        # Update specific axis labels
        fig.update_xaxes(title_text="Month", row=1, col=1)
        fig.update_yaxes(title_text="Debt Commits", row=1, col=1)
        fig.update_xaxes(title_text="Maintainability Score", row=2, col=1)
        fig.update_yaxes(title_text="Debt Score", row=2, col=1)
        fig.update_xaxes(title_text="Debt Score", row=2, col=2)
        fig.update_xaxes(title_text="Month", row=3, col=1)
        fig.update_yaxes(title_text="Debt Rate %", row=3, col=1)
        fig.update_xaxes(title_text="Implementation Effort", row=3, col=2)
        fig.update_yaxes(title_text="Business Impact", row=3, col=2)

        if save_path:
            fig.write_html(save_path)

        return fig

    def create_repository_health_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create an executive repository health dashboard.

        Returns:
            plotly.graph_objects.Figure: Health dashboard
        """
        # Get health data
        health_score = self.enhanced_summary.get("repository_health_score", 0)
        advanced_metrics = self.enhanced_summary.get("advanced_metrics", {})

        # Create subplot layout
        fig = make_subplots(
            rows=2,
            cols=3,
            subplot_titles=[
                "Overall Health Score",
                "Quality Metrics Radar",
                "Velocity Trend",
                "Coverage Metrics",
                "Risk Assessment",
                "Health Factors Breakdown",
            ],
            specs=[
                [{"type": "indicator"}, {"type": "scatterpolar"}, {"secondary_y": False}],
                [{"type": "bar"}, {"type": "bar"}, {"type": "pie"}],
            ],
        )

        # 1. Health score gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=health_score,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Repository Health"},
                delta={"reference": 70, "relative": True},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": self._get_health_color(health_score)},
                    "steps": [
                        {"range": [0, 20], "color": "#ffcccc"},
                        {"range": [20, 40], "color": "#ffe6cc"},
                        {"range": [40, 60], "color": "#ffffcc"},
                        {"range": [60, 80], "color": "#e6ffcc"},
                        {"range": [80, 100], "color": "#ccffcc"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 90,
                    },
                },
            ),
            row=1,
            col=1,
        )

        # 2. Quality metrics radar chart
        quality_metrics = advanced_metrics.get("code_quality", {})
        coverage_metrics = advanced_metrics.get("coverage_metrics", {})

        categories = [
            "Maintainability",
            "Bug Fix Ratio",
            "Test Coverage",
            "Documentation",
            "Code Churn",
            "Technical Debt",
        ]
        values = [
            quality_metrics.get("maintainability_score", 0),
            100 - quality_metrics.get("bug_fix_ratio", 0),  # Invert for better is higher
            coverage_metrics.get("test_coverage_percentage", 0),
            coverage_metrics.get("documentation_ratio", 0) * 3,  # Scale up
            100 - quality_metrics.get("code_churn_rate", 0),  # Invert
            100 - quality_metrics.get("technical_debt_rate", 0),  # Invert
        ]

        fig.add_trace(
            go.Scatterpolar(r=values, theta=categories, fill="toself", name="Current"), row=1, col=2
        )

        # 3. Velocity trend (simulated data based on current velocity)
        velocity_data = advanced_metrics.get("commit_velocity", {})
        current_velocity = velocity_data.get("avg_commits_per_week", 10)

        # Generate trend data
        weeks = list(range(1, 13))
        velocity_trend = np.random.normal(current_velocity, current_velocity * 0.2, 12)

        fig.add_trace(
            go.Scatter(
                x=weeks,
                y=velocity_trend,
                mode="lines+markers",
                name="Velocity",
                line=dict(color="blue", width=3),
            ),
            row=1,
            col=3,
        )

        # 4. Coverage metrics bar chart
        coverage_data = {
            "Test Coverage": coverage_metrics.get("test_coverage_percentage", 0),
            "Documentation": coverage_metrics.get("documentation_ratio", 0),
            "Code Review": np.random.uniform(60, 90),  # Simulated
            "CI/CD": np.random.uniform(70, 95),  # Simulated
        }

        fig.add_trace(
            go.Bar(
                x=list(coverage_data.keys()),
                y=list(coverage_data.values()),
                name="Coverage %",
                marker=dict(
                    color=[
                        "green" if v > 70 else "orange" if v > 40 else "red"
                        for v in coverage_data.values()
                    ]
                ),
            ),
            row=2,
            col=1,
        )

        # 5. Risk assessment
        risk_levels = {"Low": 60, "Medium": 25, "High": 10, "Critical": 5}

        fig.add_trace(
            go.Bar(
                x=list(risk_levels.keys()),
                y=list(risk_levels.values()),
                name="Risk Distribution",
                marker=dict(color=["green", "yellow", "orange", "red"]),
            ),
            row=2,
            col=2,
        )

        # 6. Health factors breakdown
        health_factors = {
            "Code Quality": quality_metrics.get("maintainability_score", 0) / 100 * 25,
            "Test Coverage": coverage_metrics.get("test_coverage_percentage", 0) / 100 * 20,
            "Documentation": min(coverage_metrics.get("documentation_ratio", 0) / 30, 1) * 15,
            "Low Bug Ratio": max(0, (20 - quality_metrics.get("bug_fix_ratio", 20)) / 20) * 20,
            "Low Tech Debt": max(0, (20 - quality_metrics.get("technical_debt_rate", 20)) / 20)
            * 20,
        }

        fig.add_trace(
            go.Pie(
                labels=list(health_factors.keys()),
                values=list(health_factors.values()),
                name="Health Factors",
                hole=0.3,
            ),
            row=2,
            col=3,
        )

        # Update layout
        fig.update_layout(title_text="Repository Health Dashboard", height=1000, showlegend=True)

        if save_path:
            fig.write_html(save_path)

        return fig

    def create_predictive_maintenance_report(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a predictive maintenance analysis report.

        Returns:
            plotly.graph_objects.Figure: Predictive maintenance report
        """
        # Get current metrics for predictions
        maintainability = self.git_metrics.advanced_metrics.calculate_maintainability_index()
        churn_analysis = self.git_metrics.file_analyzer.get_code_churn_analysis()
        velocity_analysis = self.git_metrics.commit_analyzer.get_commit_velocity_analysis()

        # Create predictions based on current trends
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                "Maintenance Effort Forecast (6 months)",
                "Quality Degradation Risk",
                "Resource Requirement Projection",
                "Intervention Recommendations",
            ],
        )

        # 1. Maintenance effort forecast
        current_effort = 100  # Base effort units
        months = pd.date_range(start=datetime.now(), periods=6, freq="M")

        # Simulate effort increase based on technical debt and churn
        debt_rate = (
            self.enhanced_summary.get("advanced_metrics", {})
            .get("code_quality", {})
            .get("technical_debt_rate", 5)
        )
        churn_rate = churn_analysis.get("overall_churn_rate", 30)

        effort_multiplier = 1 + (debt_rate + churn_rate) / 100
        predicted_effort = [current_effort * (effort_multiplier**i) for i in range(6)]

        fig.add_trace(
            go.Scatter(
                x=months,
                y=predicted_effort,
                mode="lines+markers",
                name="Predicted Effort",
                line=dict(color="red", width=3, dash="dash"),
            ),
            row=1,
            col=1,
        )

        # Add confidence bands
        upper_bound = [e * 1.2 for e in predicted_effort]
        lower_bound = [e * 0.8 for e in predicted_effort]

        fig.add_trace(
            go.Scatter(
                x=months.tolist() + months[::-1].tolist(),
                y=upper_bound + lower_bound[::-1],
                fill="toself",
                fillcolor="rgba(255,0,0,0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Confidence Band",
            ),
            row=1,
            col=1,
        )

        # 2. Quality degradation risk
        if not maintainability.get("file_maintainability", pd.DataFrame()).empty:
            maint_data = maintainability["file_maintainability"]
            risk_categories = ["Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
            risk_counts = [
                len(maint_data[maint_data["maintainability_score"] > 80]),
                len(
                    maint_data[
                        (maint_data["maintainability_score"] > 60)
                        & (maint_data["maintainability_score"] <= 80)
                    ]
                ),
                len(
                    maint_data[
                        (maint_data["maintainability_score"] > 40)
                        & (maint_data["maintainability_score"] <= 60)
                    ]
                ),
                len(maint_data[maint_data["maintainability_score"] <= 40]),
            ]

            fig.add_trace(
                go.Bar(
                    x=risk_categories,
                    y=risk_counts,
                    name="File Count",
                    marker=dict(color=["green", "yellow", "orange", "red"]),
                ),
                row=1,
                col=2,
            )

        # 3. Resource requirement projection
        base_resources = 5  # Base team size
        velocity = velocity_analysis.get("avg_commits_per_week", 10)

        # Project resource needs based on predicted effort
        resource_needs = [base_resources * (effort / current_effort) for effort in predicted_effort]

        fig.add_trace(
            go.Scatter(
                x=months,
                y=resource_needs,
                mode="lines+markers",
                name="Required Resources",
                line=dict(color="blue", width=3),
            ),
            row=2,
            col=1,
        )

        # Add current resource line
        fig.add_trace(
            go.Scatter(
                x=months,
                y=[base_resources] * len(months),
                mode="lines",
                name="Current Resources",
                line=dict(color="green", width=2, dash="dot"),
            ),
            row=2,
            col=1,
        )

        # 4. Intervention recommendations
        recommendations = [
            "Refactor High-Churn Files",
            "Increase Test Coverage",
            "Technical Debt Cleanup",
            "Code Review Process",
            "Documentation Update",
        ]

        priority_scores = [85, 75, 80, 65, 55]  # Simulated priority scores

        fig.add_trace(
            go.Bar(
                y=recommendations,
                x=priority_scores,
                orientation="h",
                name="Priority Score",
                marker=dict(color=priority_scores, colorscale="RdYlGn_r", showscale=True),
            ),
            row=2,
            col=2,
        )

        # Update layout
        fig.update_layout(
            title_text="Predictive Maintenance Analysis Report", height=1000, showlegend=True
        )

        # Update axis labels
        fig.update_xaxes(title_text="Month", row=1, col=1)
        fig.update_yaxes(title_text="Effort Units", row=1, col=1)
        fig.update_xaxes(title_text="Risk Level", row=1, col=2)
        fig.update_yaxes(title_text="File Count", row=1, col=2)
        fig.update_xaxes(title_text="Month", row=2, col=1)
        fig.update_yaxes(title_text="Team Size", row=2, col=1)
        fig.update_xaxes(title_text="Priority Score", row=2, col=2)

        if save_path:
            fig.write_html(save_path)

        return fig

    def _get_health_color(self, score: float) -> str:
        """Get color based on health score."""
        if score >= 80:
            return "#28a745"  # Green
        elif score >= 60:
            return "#ffc107"  # Yellow
        elif score >= 40:
            return "#fd7e14"  # Orange
        elif score >= 20:
            return "#dc3545"  # Red
        else:
            return "#6c757d"  # Gray

    def generate_all_advanced_reports(self, output_dir: str = "advanced_reports"):
        """
        Generate all advanced reports and save them to the specified directory.

        Args:
            output_dir (str): Directory to save the reports
        """
        import os

        os.makedirs(output_dir, exist_ok=True)

        reports = {
            "technical_debt_dashboard.html": self.create_technical_debt_dashboard,
            "repository_health_dashboard.html": self.create_repository_health_dashboard,
            "predictive_maintenance_report.html": self.create_predictive_maintenance_report,
        }

        generated_reports = []
        for filename, report_function in reports.items():
            filepath = os.path.join(output_dir, filename)
            try:
                report_function(filepath)
                generated_reports.append(filepath)
                print(f"✓ Generated: {filepath}")
            except Exception as e:
                print(f"✗ Failed to generate {filename}: {e}")

        return generated_reports


def demonstrate_advanced_reporting():
    """
    Demonstrate the advanced reporting capabilities.
    """
    try:
        # Import GitDecomposer components
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))

        from gitdecomposer import GitMetrics, GitRepository

        # Initialize with current repository
        repo_path = str(Path(__file__).parent.parent)
        repo = GitRepository(repo_path)
        metrics = GitMetrics(repo)

        # Create advanced report generator
        report_generator = AdvancedReportGenerator(metrics)

        print("Generating Advanced Reports...")
        print("=" * 50)

        # Generate all advanced reports
        generated_reports = report_generator.generate_all_advanced_reports()

        print(f"\n✓ Successfully generated {len(generated_reports)} advanced reports!")
        print("\nGenerated Reports:")
        for report in generated_reports:
            print(f"  - {Path(report).name}")

        return True

    except Exception as e:
        print(f"Error during advanced reporting demonstration: {e}")
        return False


if __name__ == "__main__":
    demonstrate_advanced_reporting()
