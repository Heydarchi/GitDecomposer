"""
Advanced Report Generator Service for GitDecomposer.
This service handles generating HTML reports for advanced metrics.
"""

import logging
import os
from typing import Dict, Optional

import pandas as pd
import plotly.graph_objects as go

from ..analyzers.advanced_metrics import create_metric_analyzer
from ..core import GitRepository

logger = logging.getLogger(__name__)


class AdvancedReportGenerator:
    """
    Service for generating advanced HTML reports.
    """

    def __init__(self, git_repo: GitRepository, advanced_analytics=None):
        self.git_repo = git_repo
        self.advanced_analytics = advanced_analytics

    def create_knowledge_distribution_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create knowledge distribution report."""
        logger.info("Creating knowledge distribution report")
        try:
            analyzer = create_metric_analyzer("knowledge_distribution", self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or "knowledge_distribution" not in data or data["knowledge_distribution"].empty:
                fig.add_annotation(
                    text="Insufficient data for Knowledge Distribution report.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Knowledge Distribution Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            gini_coefficient = data.get("gini_coefficient", 0)
            distribution_df = data.get("knowledge_distribution")

            # Main Gauge for Gini Coefficient
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=gini_coefficient,
                    title={"text": "Knowledge Gini Coefficient"},
                    domain={"x": [0.1, 0.9], "y": [0.6, 0.95]},
                    gauge={
                        "axis": {"range": [0, 1], "tickwidth": 1, "tickcolor": "darkblue"},
                        "bar": {"color": "darkblue"},
                        "bgcolor": "white",
                        "borderwidth": 2,
                        "bordercolor": "gray",
                        "steps": [
                            {"range": [0, 0.3], "color": "rgba(44, 160, 44, 0.5)"},  # green
                            {"range": [0.3, 0.6], "color": "rgba(255, 127, 14, 0.5)"},  # orange
                            {"range": [0.6, 1], "color": "rgba(214, 39, 40, 0.5)"},  # red
                        ],
                        "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 0.6},
                    },
                )
            )

            # Bar chart for distribution
            if distribution_df is not None and not distribution_df.empty:
                distribution_df = distribution_df.sort_values(by="knowledge_percentage", ascending=False).head(15)
                fig.add_trace(
                    go.Bar(
                        x=distribution_df["author"],
                        y=distribution_df["knowledge_percentage"],
                        name="Knowledge Distribution",
                        marker_color="rgba(31, 119, 180, 0.8)",
                    )
                )

            fig.update_layout(
                title_text="Knowledge Distribution Analysis",
                template="plotly_white",
                height=700,
                showlegend=False,
                xaxis_title="Contributor",
                yaxis_title="Knowledge Percentage (%)",
                bargap=0.2,
            )

            if save_path:
                fig.write_html(save_path)
            return fig
        except Exception as e:
            logger.error(f"Error creating knowledge distribution report: {e}")
            return self._create_error_figure("Error creating knowledge distribution report")

    def create_bus_factor_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create bus factor analysis report."""
        logger.info("Creating bus factor report")
        try:
            analyzer = create_metric_analyzer("bus_factor", self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or "bus_factor" not in data:
                fig.add_annotation(
                    text="Insufficient data for Bus Factor report.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Bus Factor Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            bus_factor = data.get("bus_factor", 0)
            risk_level = data.get("risk_level", "Unknown")
            key_contributors = data.get("key_contributors", [])

            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=bus_factor,
                    title={"text": f"Bus Factor (Risk: {risk_level})"},
                    domain={"x": [0.1, 0.9], "y": [0.6, 0.95]},
                    gauge={
                        "shape": "angular",
                        "axis": {"range": [0, 10]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 1], "color": "rgba(214, 39, 40, 0.5)"},  # red
                            {"range": [1, 3], "color": "rgba(255, 127, 14, 0.5)"},  # orange
                            {"range": [3, 5], "color": "rgba(255, 255, 0, 0.5)"},  # yellow
                            {"range": [5, 10], "color": "rgba(44, 160, 44, 0.5)"},  # green
                        ],
                    },
                )
            )

            if key_contributors:
                contributors_df = pd.DataFrame(key_contributors)
                contributors_df = contributors_df.sort_values(by="knowledge_percentage", ascending=False)

                fig.add_trace(
                    go.Bar(
                        x=contributors_df["author"],
                        y=contributors_df["knowledge_percentage"],
                        name="Key Contributors",
                        marker_color="rgba(31, 119, 180, 0.8)",
                    )
                )

            fig.update_layout(
                title_text="Bus Factor Analysis",
                template="plotly_white",
                height=700,
                showlegend=False,
                xaxis_title="Key Contributors",
                yaxis_title="Knowledge Percentage (%)",
                bargap=0.2,
            )

            if save_path:
                # Generate HTML with custom description
                html_content = self._generate_bus_factor_html(fig)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
            return fig
        except Exception as e:
            logger.error(f"Error creating bus factor report: {e}")
            return self._create_error_figure("Error creating bus factor report")

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
            title="Report Generation Error",
            template="plotly_white",
        )
        return fig

    def create_critical_files_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create critical files analysis report."""
        logger.info("Creating critical files report")
        try:
            analyzer = create_metric_analyzer("critical_files", self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or "critical_files" not in data or not data["critical_files"]:
                fig.add_annotation(
                    text="No critical files identified or insufficient data.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Critical Files Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            critical_files = data["critical_files"][:25]  # Top 25 most critical

            # Create bar chart for critical files
            file_names = [file_path.split("/")[-1] for file_path, metrics in critical_files]
            risk_scores = [metrics["criticality_score"] for file_path, metrics in critical_files]

            fig.add_trace(
                go.Bar(
                    x=file_names,
                    y=risk_scores,
                    name="Risk Score",
                    marker_color="red",
                    text=[
                        f"Risk: {score:.1f}<br>Changes: {metrics['change_frequency']}<br>Complexity: {metrics['complexity']:.1f}"
                        for (file_path, metrics), score in zip(critical_files, risk_scores)
                    ],
                    textposition="auto",
                )
            )

            fig.update_layout(
                title="Critical Files Analysis - Top Risk Files",
                xaxis_title="Files",
                yaxis_title="Risk Score",
                template="plotly_white",
                height=600,
                xaxis_tickangle=-45,
            )

            if save_path:
                # Generate HTML with custom description
                html_content = self._generate_critical_files_html(fig)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
            return fig

        except Exception as e:
            logger.error(f"Error creating critical files report: {e}")
            return self._create_error_figure(f"Error generating Critical Files report: {str(e)}")

    def create_velocity_trend_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create velocity trend analysis report."""
        logger.info("Creating velocity trend report")
        try:
            analyzer = create_metric_analyzer("velocity_trend", self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or "weekly_data" not in data or not data["weekly_data"]:
                fig.add_annotation(
                    text="Insufficient data for velocity trend analysis.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Velocity Trend Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            weekly_data = data["weekly_data"]
            weeks = []
            for w in weekly_data:
                if isinstance(w["week_start"], str):
                    weeks.append(w["week_start"])
                elif hasattr(w["week_start"], "strftime"):
                    weeks.append(w["week_start"].strftime("%Y-%m-%d"))
                else:
                    weeks.append(str(w["week_start"]))

            commits = [w["commit_count"] for w in weekly_data]
            lines_changed = [w["total_lines_changed"] for w in weekly_data]

            # Create velocity trend chart
            fig.add_trace(
                go.Scatter(
                    x=weeks,
                    y=commits,
                    mode="lines+markers",
                    name="Commits per Week",
                    line=dict(color="blue", width=2),
                    yaxis="y1",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=weeks,
                    y=lines_changed,
                    mode="lines+markers",
                    name="Lines Changed per Week",
                    line=dict(color="red", width=2),
                    yaxis="y2",
                )
            )

            fig.update_layout(
                title="Development Velocity Trends",
                xaxis_title="Week",
                yaxis=dict(title="Commits", side="left"),
                yaxis2=dict(title="Lines Changed", side="right", overlaying="y"),
                template="plotly_white",
                height=600,
                legend=dict(x=0.02, y=0.98),
            )

            if save_path:
                fig.write_html(save_path)
            return fig

        except Exception as e:
            logger.error(f"Error creating velocity trend report: {e}")
            return self._create_error_figure(f"Error generating Velocity Trend report: {str(e)}")

    def create_cycle_time_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create cycle time analysis report."""
        logger.info("Creating cycle time report")
        try:
            analyzer = create_metric_analyzer("cycle_time", self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or "statistics" not in data or not data["statistics"]:
                fig.add_annotation(
                    text="Insufficient data for cycle time analysis.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Cycle Time Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            metrics = data["statistics"]

            # Create gauge for average cycle time
            avg_cycle_time = metrics.get("average_cycle_time_hours", 0) if isinstance(metrics, dict) else 0

            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=avg_cycle_time,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Average Cycle Time (Hours)"},
                    gauge={
                        "axis": {"range": [None, 168]},  # 1 week in hours
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 24], "color": "lightgreen"},
                            {"range": [24, 72], "color": "yellow"},
                            {"range": [72, 168], "color": "orange"},
                        ],
                        "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 120},
                    },
                )
            )

            fig.update_layout(title="Development Cycle Time Analysis", template="plotly_white", height=600)

            if save_path:
                fig.write_html(save_path)
            return fig

        except Exception as e:
            logger.error(f"Error creating cycle time report: {e}")
            return self._create_error_figure(f"Error generating Cycle Time report: {str(e)}")

    def create_single_point_failure_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create single point of failure analysis report."""
        logger.info("Creating single point failure report")
        try:
            analyzer = create_metric_analyzer("single_point_failure", self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or "spof_files" not in data or not data["spof_files"]:
                fig.add_annotation(
                    text="No single point of failure files identified.",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="green"),
                )
                fig.update_layout(title="Single Point of Failure Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            spof_files = data["spof_files"][:25]  # Top 25 SPOF files

            # Create bar chart for SPOF files
            file_names = [f["file"].split("/")[-1] for f in spof_files]
            dominance_scores = [f["dominance_ratio"] * 100 for f in spof_files]  # Convert to percentage

            fig.add_trace(
                go.Bar(
                    x=file_names,
                    y=dominance_scores,
                    name="Dominance %",
                    marker_color="darkred",
                    text=[
                        f"Dominance: {score:.1f}%<br>Main Author: {f['dominant_author']}"
                        for score, f in zip(dominance_scores, spof_files)
                    ],
                    textposition="auto",
                )
            )

            fig.update_layout(
                title="Single Point of Failure Files - High Risk Areas",
                xaxis_title="Files",
                yaxis_title="Dominance Percentage",
                template="plotly_white",
                height=600,
                xaxis_tickangle=-45,
            )

            if save_path:
                # Generate HTML with custom description
                html_content = self._generate_single_point_failure_html(fig)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
            return fig

        except Exception as e:
            logger.error(f"Error creating single point failure report: {e}")
            return self._create_error_figure(f"Error generating Single Point Failure report: {str(e)}")

    def _generate_critical_files_html(self, fig: go.Figure) -> str:
        """Generate HTML content for critical files report with description."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Critical Files Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ padding: 30px; }}
        .description {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #dc3545; }}
        .calculation {{ background: #e9ecef; padding: 15px; border-radius: 6px; margin: 10px 0; }}
        .section-title {{ color: #dc3545; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }}
        .metric-formula {{ font-family: 'Courier New', monospace; background: #f1f3f4; padding: 8px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Critical Files Analysis</h1>
            <p>High-risk files based on complexity and change frequency</p>
        </div>
        
        <div class="content">
            <div id="chart"></div>
            
            <div class="description">
                <h3 class="section-title">Report Overview</h3>
                <p><strong>Critical Files Analysis</strong> identifies files that pose the highest risk to your project due to their combination of high complexity and frequent changes. This analysis helps prioritize refactoring efforts and increase testing coverage for the most vulnerable parts of your codebase.</p>
                
                <h4 class="section-title">Calculation Methodology</h4>
                <div class="calculation">
                    <div class="metric-formula">Risk Score = (Change Frequency × 0.4) + (Code Complexity × 0.6)</div>
                    <ul>
                        <li><strong>Change Frequency:</strong> Number of commits affecting the file (normalized to 0-100 scale)</li>
                        <li><strong>Code Complexity:</strong> Estimated based on file size, nesting depth, and code patterns</li>
                        <li><strong>Weighting Rationale:</strong> Complexity weighted higher (60%) as it indicates potential technical debt</li>
                    </ul>
                </div>

                <h4 class="section-title">Risk Level Classification</h4>
                <ul>
                    <li><strong>High Risk (Score > 70):</strong> Immediate refactoring and comprehensive testing recommended</li>
                    <li><strong>Medium Risk (Score 40-70):</strong> Monitor closely, add automated tests, schedule code reviews</li>
                    <li><strong>Low Risk (Score < 40):</strong> Stable, well-maintained code with minimal immediate action needed</li>
                </ul>

                <h4 class="section-title">Recommended Actions</h4>
                <ul>
                    <li>Prioritize automated testing for the top 5 critical files</li>
                    <li>Break down large, monolithic files into smaller, focused modules</li>
                    <li>Implement continuous monitoring for files with frequent change patterns</li>
                    <li>Establish mandatory code review processes for all changes to critical files</li>
                    <li>Consider architectural refactoring for consistently high-risk areas</li>
                    <li>Document complex business logic in critical files</li>
                </ul>

                <h4 class="section-title">Best Practices</h4>
                <ul>
                    <li>Aim to keep individual files under 500 lines of code</li>
                    <li>Implement the Single Responsibility Principle to reduce complexity</li>
                    <li>Use design patterns to manage complexity in unavoidably large files</li>
                    <li>Regularly assess and refactor based on changing risk scores</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        var chartData = {fig.to_json()};
        Plotly.newPlot('chart', chartData.data, chartData.layout);
    </script>
</body>
</html>"""
        return html_content

    def _generate_single_point_failure_html(self, fig: go.Figure) -> str:
        """Generate HTML content for single point failure report with description."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Single Point of Failure Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #dc3545 0%, #bd2130 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ padding: 30px; }}
        .description {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #dc3545; }}
        .calculation {{ background: #e9ecef; padding: 15px; border-radius: 6px; margin: 10px 0; }}
        .section-title {{ color: #dc3545; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }}
        .metric-formula {{ font-family: 'Courier New', monospace; background: #f1f3f4; padding: 8px; border-radius: 4px; }}
        .risk-level {{ margin: 8px 0; padding: 8px; border-radius: 4px; }}
        .critical {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        .high {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
        .medium {{ background-color: #d1ecf1; border-left: 4px solid #17a2b8; }}
        .low {{ background-color: #d4edda; border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Single Point of Failure Analysis</h1>
            <p>Files with dangerously low contributor diversity</p>
        </div>
        
        <div class="content">
            <div id="chart"></div>
            
            <div class="description">
                <h3 class="section-title">Report Overview</h3>
                <p><strong>Single Point of Failure (SPOF) Analysis</strong> identifies files where knowledge and maintenance responsibility is concentrated in a single contributor. These files represent significant project risk if that contributor becomes unavailable, creating potential bottlenecks in development and maintenance.</p>
                
                <h4 class="section-title">Calculation Methodology</h4>
                <div class="calculation">
                    <div class="metric-formula">Dominance Ratio = (Main Contributor Commits / Total File Commits) × 100</div>
                    <ul>
                        <li><strong>Main Contributor:</strong> Individual with the highest number of commits to the file</li>
                        <li><strong>SPOF Threshold:</strong> Files with dominance ratio >80% are flagged as single points of failure</li>
                        <li><strong>Risk Assessment:</strong> Higher percentage indicates greater concentration of knowledge</li>
                    </ul>
                </div>

                <h4 class="section-title">Risk Level Classification</h4>
                <div class="risk-level critical">
                    <strong>Critical Risk (>90% dominance):</strong> Single person effectively owns the file with minimal knowledge sharing
                </div>
                <div class="risk-level high">
                    <strong>High Risk (80-90% dominance):</strong> Very limited knowledge distribution among team members
                </div>
                <div class="risk-level medium">
                    <strong>Medium Risk (60-80% dominance):</strong> Some knowledge sharing exists but still concentrated
                </div>
                <div class="risk-level low">
                    <strong>Low Risk (<60% dominance):</strong> Good knowledge distribution across multiple contributors
                </div>

                <h4 class="section-title">Risk Mitigation Strategies</h4>
                <ul>
                    <li><strong>Knowledge Transfer:</strong> Schedule dedicated sessions for primary contributor to share domain knowledge</li>
                    <li><strong>Pair Programming:</strong> Implement regular pair programming sessions for SPOF files</li>
                    <li><strong>Documentation:</strong> Create comprehensive documentation covering business logic and technical decisions</li>
                    <li><strong>Code Review:</strong> Require multiple reviewers for changes to high-risk files</li>
                    <li><strong>Backup Maintainers:</strong> Assign secondary maintainers and rotate responsibilities</li>
                    <li><strong>Cross-Training:</strong> Ensure multiple team members understand critical system components</li>
                </ul>

                <h4 class="section-title">Implementation Guidelines</h4>
                <ul>
                    <li>Start with the highest-risk files and work systematically through the list</li>
                    <li>Establish a knowledge-sharing culture through regular team technical discussions</li>
                    <li>Create architectural decision records (ADRs) for important design choices</li>
                    <li>Monitor improvements over time by tracking dominance ratio changes</li>
                    <li>Include knowledge distribution as a factor in code review processes</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        var chartData = {fig.to_json()};
        Plotly.newPlot('chart', chartData.data, chartData.layout);
    </script>
</body>
</html>"""
        return html_content

    def _generate_bus_factor_html(self, fig: go.Figure) -> str:
        """Generate HTML content for bus factor report with description."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bus Factor Analysis</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #fd7e14 0%, #e8590c 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ padding: 30px; }}
        .description {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #fd7e14; }}
        .calculation {{ background: #e9ecef; padding: 15px; border-radius: 6px; margin: 10px 0; }}
        .section-title {{ color: #fd7e14; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }}
        .metric-formula {{ font-family: 'Courier New', monospace; background: #f1f3f4; padding: 8px; border-radius: 4px; }}
        .risk-indicator {{ margin: 8px 0; padding: 8px; border-radius: 4px; }}
        .critical {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        .high {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
        .medium {{ background-color: #d1ecf1; border-left: 4px solid #17a2b8; }}
        .low {{ background-color: #d4edda; border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bus Factor Analysis</h1>
            <p>Project risk assessment from key person dependencies</p>
        </div>
        
        <div class="content">
            <div id="chart"></div>
            
            <div class="description">
                <h3 class="section-title">Bus Factor Definition</h3>
                <p><strong>Bus Factor</strong> represents the minimum number of team members who would need to become unavailable before the project becomes severely compromised. It measures knowledge concentration and identifies critical dependencies in your development team.</p>
                
                <h4 class="section-title">Calculation Methodology</h4>
                <div class="calculation">
                    <div class="metric-formula">Bus Factor = Minimum contributors needed to account for 50% of total project commits</div>
                    <ul>
                        <li><strong>Knowledge Share Analysis:</strong> Cumulative percentage of commits by each contributor</li>
                        <li><strong>Critical Threshold:</strong> Point where combined contributions reach 50% of total work</li>
                        <li><strong>Risk Assessment:</strong> Lower bus factor indicates higher project vulnerability</li>
                    </ul>
                </div>

                <h4 class="section-title">Risk Level Interpretation</h4>
                <div class="risk-indicator critical">
                    <strong>Bus Factor 1 - Critical Risk:</strong> Project has a single point of failure with catastrophic potential impact
                </div>
                <div class="risk-indicator high">
                    <strong>Bus Factor 2-3 - High Risk:</strong> Limited knowledge sharing creates significant project vulnerability
                </div>
                <div class="risk-indicator medium">
                    <strong>Bus Factor 4-6 - Medium Risk:</strong> Reasonable knowledge distribution with room for improvement
                </div>
                <div class="risk-indicator low">
                    <strong>Bus Factor 7+ - Low Risk:</strong> Well-distributed knowledge across multiple team members
                </div>

                <h4 class="section-title">Knowledge Distribution Improvement Strategies</h4>
                <ul>
                    <li><strong>Cross-Training Programs:</strong> Implement systematic knowledge sharing across team members</li>
                    <li><strong>Pair Programming:</strong> Regular rotation of programming pairs to spread domain knowledge</li>
                    <li><strong>Code Review Culture:</strong> Ensure multiple people understand each part of the codebase</li>
                    <li><strong>Documentation Standards:</strong> Maintain comprehensive documentation of critical processes and architecture</li>
                    <li><strong>Mentorship Programs:</strong> Pair experienced developers with newer team members</li>
                    <li><strong>Technical Presentations:</strong> Regular team sessions where members share knowledge about their areas</li>
                </ul>

                <h4 class="section-title">Organizational Best Practices</h4>
                <ul>
                    <li>Rotate responsibilities for critical system components among multiple team members</li>
                    <li>Identify and proactively train backup experts for specialized knowledge areas</li>
                    <li>Create and maintain up-to-date architectural decision records</li>
                    <li>Establish clear ownership models while ensuring knowledge redundancy</li>
                    <li>Monitor bus factor trends over time to track improvement efforts</li>
                    <li>Include knowledge sharing in performance evaluation criteria</li>
                </ul>

                <h4 class="section-title">Risk Mitigation Timeline</h4>
                <ul>
                    <li><strong>Immediate (1-2 weeks):</strong> Document critical knowledge held by key contributors</li>
                    <li><strong>Short-term (1-3 months):</strong> Implement pair programming and code review processes</li>
                    <li><strong>Medium-term (3-6 months):</strong> Cross-train team members on critical systems</li>
                    <li><strong>Long-term (6+ months):</strong> Achieve sustainable knowledge distribution patterns</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        var chartData = {fig.to_json()};
        Plotly.newPlot('chart', chartData.data, chartData.layout);
    </script>
</body>
</html>"""
        return html_content

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
            title="Report Generation Error",
            template="plotly_white",
        )
        return fig
