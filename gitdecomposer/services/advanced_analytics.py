"""
Advanced Analytics Service for GitDecomposer.

This service handles advanced metrics and analytical capabilities
including technical debt, repository health, and predictive analytics.
"""

import logging
from typing import Dict, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..analyzers import (
    AdvancedMetrics,
    BranchAnalyzer,
    CommitAnalyzer,
    ContributorAnalyzer,
    FileAnalyzer,
)
from ..core import GitRepository

logger = logging.getLogger(__name__)


class AdvancedAnalytics:
    """
    Service for advanced analytics and predictive metrics.

    This class handles advanced analytics responsibilities previously managed
    by GitMetrics, providing clean separation of concerns.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize AdvancedAnalytics with analyzer instances.

        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self.commit_analyzer = CommitAnalyzer(git_repo)
        self.file_analyzer = FileAnalyzer(git_repo)
        self.contributor_analyzer = ContributorAnalyzer(git_repo)
        self.branch_analyzer = BranchAnalyzer(git_repo)
        self.advanced_metrics = AdvancedMetrics(git_repo)

        logger.info("AdvancedAnalytics initialized with all analyzers")

    def create_technical_debt_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive technical debt analysis dashboard.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Technical debt dashboard
        """
        try:
            # Get technical debt data
            debt_analysis = self.advanced_metrics.calculate_technical_debt_accumulation()
            maintainability = self.advanced_metrics.calculate_maintainability_index()
            test_ratio = self.advanced_metrics.calculate_test_to_code_ratio()
            churn_analysis = self.file_analyzer.get_code_churn_analysis()

            # Create subplots for technical debt dashboard
            fig = make_subplots(
                rows=3,
                cols=2,
                subplot_titles=[
                    "Technical Debt Trend",
                    "Maintainability Score",
                    "Test Coverage",
                    "Code Churn Analysis",
                    "Debt Distribution",
                    "Risk Assessment",
                ],
                specs=[
                    [{"secondary_y": False}, {"type": "indicator"}],
                    [{"type": "pie"}, {"secondary_y": False}],
                    [{"secondary_y": False}, {"type": "indicator"}],
                ],
            )

            # Technical debt trend
            if "debt_trend" in debt_analysis and not debt_analysis["debt_trend"].empty:
                debt_trend = debt_analysis["debt_trend"]
                fig.add_trace(
                    go.Scatter(
                        x=debt_trend["date"] if "date" in debt_trend.columns else list(range(len(debt_trend))),
                        y=debt_trend["debt_score"] if "debt_score" in debt_trend.columns else [0] * len(debt_trend),
                        mode="lines+markers",
                        name="Debt Trend",
                        line=dict(color="red", width=3),
                    ),
                    row=1,
                    col=1,
                )

            # Maintainability indicator
            overall_maintainability = maintainability.get("overall_maintainability_score", 0)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=overall_maintainability,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Maintainability"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 50], "color": "lightgray"},
                            {"range": [50, 80], "color": "gray"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 90,
                        },
                    },
                ),
                row=1,
                col=2,
            )

            # Test coverage pie chart
            test_coverage = test_ratio.get("test_coverage_percentage", 0)
            untested_percentage = 100 - test_coverage
            fig.add_trace(
                go.Pie(
                    labels=["Tested", "Untested"],
                    values=[test_coverage, untested_percentage],
                    name="Test Coverage",
                    marker_colors=["green", "red"],
                ),
                row=2,
                col=1,
            )

            # Code churn analysis
            if "file_churn_rates" in churn_analysis and not churn_analysis["file_churn_rates"].empty:
                churn_data = churn_analysis["file_churn_rates"]
                fig.add_trace(
                    go.Bar(
                        x=churn_data["file_path"][:10],
                        y=churn_data["churn_rate"][:10],
                        name="Churn Rate",
                        marker_color="orange",
                    ),
                    row=2,
                    col=2,
                )

            # Debt distribution by file type
            debt_by_type = debt_analysis.get("debt_by_file_type", {})
            if debt_by_type:
                fig.add_trace(
                    go.Bar(
                        x=list(debt_by_type.keys())[:10],
                        y=list(debt_by_type.values())[:10],
                        name="Debt by Type",
                        marker_color="purple",
                    ),
                    row=3,
                    col=1,
                )

            # Overall risk indicator
            debt_rate = debt_analysis.get("debt_accumulation_rate", 0)
            risk_score = min(100, debt_rate * 5)  # Convert to 0-100 scale
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=risk_score,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Risk Level"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "red"},
                        "steps": [
                            {"range": [0, 30], "color": "green"},
                            {"range": [30, 70], "color": "yellow"},
                            {"range": [70, 100], "color": "red"},
                        ],
                    },
                ),
                row=3,
                col=2,
            )

            # Update layout
            fig.update_layout(
                title="Technical Debt Dashboard",
                showlegend=True,
                height=1200,
                template="plotly_white",
            )

            if save_path:
                fig.write_html(save_path)
                logger.info(f"Technical debt dashboard saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating technical debt dashboard: {e}")
            return self._create_error_figure("Error creating technical debt dashboard")

    def create_repository_health_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a repository health monitoring dashboard.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Repository health dashboard
        """
        try:
            # Get health metrics
            velocity_analysis = self.commit_analyzer.get_commit_velocity_analysis()
            bug_fix_analysis = self.commit_analyzer.get_bug_fix_ratio_analysis()
            maintainability = self.advanced_metrics.calculate_maintainability_index()
            test_ratio = self.advanced_metrics.calculate_test_to_code_ratio()
            doc_coverage = self.file_analyzer.get_documentation_coverage_analysis()

            # Create health dashboard
            fig = make_subplots(
                rows=2,
                cols=3,
                subplot_titles=[
                    "Commit Velocity",
                    "Bug Fix Ratio",
                    "Test Coverage",
                    "Documentation Ratio",
                    "Maintainability Trend",
                    "Overall Health Score",
                ],
                specs=[
                    [{"secondary_y": False}, {"type": "indicator"}, {"type": "indicator"}],
                    [{"type": "indicator"}, {"secondary_y": False}, {"type": "indicator"}],
                ],
            )

            # Commit velocity trend
            if "weekly_velocity" in velocity_analysis and not velocity_analysis["weekly_velocity"].empty:
                velocity_data = velocity_analysis["weekly_velocity"]
                fig.add_trace(
                    go.Scatter(
                        x=velocity_data["week"] if "week" in velocity_data.columns else list(range(len(velocity_data))),
                        y=velocity_data["commits"] if "commits" in velocity_data.columns else [0] * len(velocity_data),
                        mode="lines+markers",
                        name="Velocity",
                        line=dict(color="blue"),
                    ),
                    row=1,
                    col=1,
                )

            # Bug fix ratio indicator
            bug_ratio = bug_fix_analysis.get("bug_fix_ratio", 0)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=bug_ratio,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Bug Fix %"},
                    gauge={
                        "axis": {"range": [0, 50]},
                        "bar": {"color": "orange"},
                        "steps": [
                            {"range": [0, 10], "color": "green"},
                            {"range": [10, 25], "color": "yellow"},
                            {"range": [25, 50], "color": "red"},
                        ],
                    },
                ),
                row=1,
                col=2,
            )

            # Test coverage indicator
            test_coverage = test_ratio.get("test_coverage_percentage", 0)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=test_coverage,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Test Coverage %"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "green"},
                        "steps": [
                            {"range": [0, 50], "color": "red"},
                            {"range": [50, 80], "color": "yellow"},
                            {"range": [80, 100], "color": "green"},
                        ],
                    },
                ),
                row=1,
                col=3,
            )

            # Documentation ratio indicator
            doc_ratio = doc_coverage.get("documentation_ratio", 0)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=doc_ratio,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Documentation %"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "purple"},
                        "steps": [
                            {"range": [0, 20], "color": "red"},
                            {"range": [20, 50], "color": "yellow"},
                            {"range": [50, 100], "color": "green"},
                        ],
                    },
                ),
                row=2,
                col=1,
            )

            # Maintainability trend (if available)
            if "file_maintainability" in maintainability and not maintainability["file_maintainability"].empty:
                maint_data = maintainability["file_maintainability"]
                avg_scores = [maint_data["maintainability_score"].mean()] * 10  # Simplified trend
                fig.add_trace(
                    go.Scatter(
                        x=list(range(10)),
                        y=avg_scores,
                        mode="lines",
                        name="Maintainability",
                        line=dict(color="darkgreen"),
                    ),
                    row=2,
                    col=2,
                )

            # Overall health score
            health_factors = self._calculate_health_score(
                bug_ratio, test_coverage, doc_ratio, maintainability.get("overall_maintainability_score", 0)
            )
            overall_health = sum(health_factors.values()) / len(health_factors) * 100

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=overall_health,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Health Score"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 40], "color": "red"},
                            {"range": [40, 70], "color": "yellow"},
                            {"range": [70, 100], "color": "green"},
                        ],
                    },
                ),
                row=2,
                col=3,
            )

            # Update layout
            fig.update_layout(
                title="Repository Health Dashboard",
                showlegend=True,
                height=800,
                template="plotly_white",
            )

            if save_path:
                fig.write_html(save_path)
                logger.info(f"Repository health dashboard saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating repository health dashboard: {e}")
            return self._create_error_figure("Error creating repository health dashboard")

    def create_predictive_maintenance_report(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a predictive maintenance report with forecasting.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Predictive maintenance dashboard
        """
        try:
            # Get predictive data
            velocity_analysis = self.commit_analyzer.get_commit_velocity_analysis()
            churn_analysis = self.file_analyzer.get_code_churn_analysis()
            debt_analysis = self.advanced_metrics.calculate_technical_debt_accumulation()

            # Create predictive dashboard
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=[
                    "Velocity Forecast",
                    "Debt Accumulation Prediction",
                    "High-Risk Files",
                    "Maintenance Recommendations",
                ],
            )

            # Velocity forecast (simplified)
            if "weekly_velocity" in velocity_analysis and not velocity_analysis["weekly_velocity"].empty:
                velocity_data = velocity_analysis["weekly_velocity"]
                # Simple trend prediction
                recent_weeks = velocity_data.tail(4)
                if not recent_weeks.empty:
                    avg_velocity = recent_weeks["commits"].mean() if "commits" in recent_weeks.columns else 0
                    forecast_weeks = list(range(len(velocity_data), len(velocity_data) + 4))
                    forecast_values = [avg_velocity] * 4

                    # Historical data
                    fig.add_trace(
                        go.Scatter(
                            x=(
                                velocity_data.index
                                if hasattr(velocity_data, "index")
                                else list(range(len(velocity_data)))
                            ),
                            y=(
                                velocity_data["commits"]
                                if "commits" in velocity_data.columns
                                else [0] * len(velocity_data)
                            ),
                            mode="lines+markers",
                            name="Historical Velocity",
                            line=dict(color="blue"),
                        ),
                        row=1,
                        col=1,
                    )

                    # Forecast
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_weeks,
                            y=forecast_values,
                            mode="lines+markers",
                            name="Forecast",
                            line=dict(color="red", dash="dash"),
                        ),
                        row=1,
                        col=1,
                    )

            # Debt accumulation prediction
            debt_rate = debt_analysis.get("debt_accumulation_rate", 0)
            current_debt = debt_analysis.get("current_debt_score", 0)
            future_months = list(range(1, 7))  # 6 months forecast
            predicted_debt = [current_debt + (debt_rate * month) for month in future_months]

            fig.add_trace(
                go.Scatter(
                    x=future_months,
                    y=predicted_debt,
                    mode="lines+markers",
                    name="Debt Forecast",
                    line=dict(color="orange"),
                ),
                row=1,
                col=2,
            )

            # High-risk files
            if "file_churn_rates" in churn_analysis and not churn_analysis["file_churn_rates"].empty:
                high_risk_files = churn_analysis["file_churn_rates"].head(10)
                fig.add_trace(
                    go.Bar(
                        x=high_risk_files["file_path"] if "file_path" in high_risk_files.columns else [],
                        y=high_risk_files["churn_rate"] if "churn_rate" in high_risk_files.columns else [],
                        name="Risk Score",
                        marker_color="red",
                    ),
                    row=2,
                    col=1,
                )

            # Maintenance recommendations (text summary)
            recommendations = self._generate_maintenance_recommendations(
                velocity_analysis, debt_analysis, churn_analysis
            )

            fig.add_annotation(
                text=recommendations,
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=12),
                row=2,
                col=2,
            )

            # Update layout
            fig.update_layout(
                title="Predictive Maintenance Report",
                showlegend=True,
                height=800,
                template="plotly_white",
            )

            if save_path:
                fig.write_html(save_path)
                logger.info(f"Predictive maintenance report saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating predictive maintenance report: {e}")
            return self._create_error_figure("Error creating predictive maintenance report")

    def create_velocity_forecasting_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a velocity forecasting dashboard.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Velocity forecasting dashboard
        """
        try:
            # Get velocity data
            velocity_analysis = self.commit_analyzer.get_commit_velocity_analysis()

            # Create velocity dashboard
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=[
                    "Historical Velocity",
                    "Velocity Trend",
                    "Sprint Predictions",
                    "Capacity Planning",
                ],
            )

            # Simple implementation for velocity forecasting
            # In a real implementation, this would use more sophisticated forecasting models

            fig.update_layout(
                title="Velocity Forecasting Dashboard",
                showlegend=True,
                height=800,
                template="plotly_white",
            )

            if save_path:
                fig.write_html(save_path)
                logger.info(f"Velocity forecasting dashboard saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating velocity forecasting dashboard: {e}")
            return self._create_error_figure("Error creating velocity forecasting dashboard")

    def generate_all_advanced_reports(self, output_dir: str = "advanced_reports") -> Dict[str, str]:
        """
        Generate all advanced analytics reports.

        Args:
            output_dir (str): Directory to save reports

        Returns:
            Dict[str, str]: Mapping of report names to file paths
        """
        import os

        os.makedirs(output_dir, exist_ok=True)
        generated_files = {}

        try:
            # Generate advanced reports
            reports = [
                ("technical_debt", "technical_debt_dashboard.html", self.create_technical_debt_dashboard),
                ("repository_health", "repository_health_dashboard.html", self.create_repository_health_dashboard),
                (
                    "predictive_maintenance",
                    "predictive_maintenance_report.html",
                    self.create_predictive_maintenance_report,
                ),
                (
                    "velocity_forecasting",
                    "velocity_forecasting_dashboard.html",
                    self.create_velocity_forecasting_dashboard,
                ),
            ]

            for report_name, filename, generator_func in reports:
                try:
                    file_path = os.path.join(output_dir, filename)
                    generator_func(file_path)
                    generated_files[report_name] = file_path
                    logger.info(f"Generated {report_name} report: {file_path}")
                except Exception as e:
                    logger.error(f"Error generating {report_name} report: {e}")

            logger.info(f"Generated {len(generated_files)} advanced reports in {output_dir}")
            return generated_files

        except Exception as e:
            logger.error(f"Error generating advanced reports: {e}")
            return generated_files

    def _calculate_health_score(
        self, bug_ratio: float, test_coverage: float, doc_ratio: float, maintainability: float
    ) -> Dict[str, float]:
        """Calculate health score factors."""
        return {
            "low_bug_ratio": max(0, (20 - bug_ratio) / 20),  # Lower bug ratio is better
            "test_coverage": min(test_coverage / 100, 1.0),
            "documentation": min(doc_ratio / 50, 1.0),  # 50% doc ratio = perfect
            "maintainability": maintainability / 100,
        }

    def _generate_maintenance_recommendations(
        self, velocity_analysis: dict, debt_analysis: dict, churn_analysis: dict
    ) -> str:
        """Generate maintenance recommendations based on analysis."""
        recommendations = []

        # Velocity recommendations
        velocity_trend = velocity_analysis.get("velocity_trend", "stable")
        if velocity_trend == "declining":
            recommendations.append("• Consider team capacity planning")

        # Debt recommendations
        debt_rate = debt_analysis.get("debt_accumulation_rate", 0)
        if debt_rate > 10:
            recommendations.append("• Schedule technical debt reduction")

        # Churn recommendations
        high_churn_files = churn_analysis.get("high_churn_files", [])
        if len(high_churn_files) > 5:
            recommendations.append("• Review high-churn files for refactoring")

        if not recommendations:
            recommendations.append("• Repository health is good")
            recommendations.append("• Continue current practices")

        return "\n".join(recommendations)

    def _create_error_figure(self, error_message: str) -> go.Figure:
        """Create a simple error figure when visualization fails."""
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="red"),
        )
        fig.update_layout(
            title="Advanced Analytics Error",
            template="plotly_white",
        )
        return fig
