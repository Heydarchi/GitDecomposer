"""
Risk Analysis Service for GitDecomposer.

This service is responsible for analyzing and reporting on file-level risks,
including hotspots, critical files, and knowledge silos.
"""

import logging
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..analyzers import FileAnalyzer, advanced_metrics
from ..core import GitRepository

logger = logging.getLogger(__name__)


class RiskAnalysis:
    """
    Service for generating a consolidated risk analysis report.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize RiskAnalysis with a GitRepository instance.

        Args:
            git_repo (GitRepository): GitRepository instance.
        """
        self.git_repo = git_repo
        self.file_analyzer = FileAnalyzer(git_repo)
        self.critical_files_analyzer = advanced_metrics.create_metric_analyzer("critical_files", git_repo)
        self.single_point_failure_analyzer = advanced_metrics.create_metric_analyzer("single_point_failure", git_repo)
        logger.info("RiskAnalysis service initialized.")

    def create_file_insights_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive, tabbed dashboard for file insights.

        This dashboard includes analysis on hotspots, critical files, and knowledge silos.

        Args:
            save_path (str, optional): Path to save the HTML file.

        Returns:
            plotly.graph_objects.Figure: The file insights dashboard.
        """
        fig = go.Figure()

        # Data Acquisition
        hotspots_data = self.file_analyzer.get_code_churn_analysis()
        critical_files_data = self.critical_files_analyzer.calculate()
        silo_data = self.single_point_failure_analyzer.calculate()

        # Create buttons for tabs
        buttons = [
            dict(label="File Hotspots", method="update", args=[{"visible": [True, True, False, False, False, False]}, {"title": "File Insights: Hotspots & Churn"}]),
            dict(label="Critical Files", method="update", args=[{"visible": [False, False, True, True, False, False]}, {"title": "File Insights: Critical Files"}]),
            dict(label="Knowledge Silos", method="update", args=[{"visible": [False, False, False, False, True, True]}, {"title": "File Insights: Knowledge Silos"}])
        ]
        fig.update_layout(updatemenus=[dict(type="buttons", direction="right", x=1, y=1.1, showactive=True, buttons=buttons)])

        # Tab 1: File Hotspots
        churn_df = hotspots_data.get('file_churn_rates', pd.DataFrame())
        if not churn_df.empty:
            top_churn = churn_df.sort_values('churn_rate', ascending=False).head(15)
            fig.add_trace(
                go.Bar(
                    x=top_churn['file_path'],
                    y=top_churn['churn_rate'],
                    name="Churn Rate",
                    marker_color='blue',
                    visible=True,
                )
            )
            # Use total_changes instead of non-existent commit_count
            fig.add_trace(
                go.Bar(
                    x=top_churn['file_path'],
                    y=top_churn.get('total_changes', pd.Series([0]*len(top_churn))),
                    name="Total Changes",
                    marker_color='lightblue',
                    visible=True,
                )
            )

        # Tab 2: Critical Files
        # critical_files is list of (file_path, metrics)
        cf_list = critical_files_data.get('critical_files', []) or []
        if cf_list:
            cf_df = pd.DataFrame([
                {
                    'file_path': fp,
                    'complexity': m.get('complexity'),
                    'change_frequency': m.get('change_frequency'),
                    'criticality_score': m.get('criticality_score'),
                }
                for fp, m in cf_list
            ])
            fig.add_trace(
                go.Scatter(
                    x=cf_df['complexity'],
                    y=cf_df['change_frequency'],
                    mode='markers',
                    text=cf_df['file_path'],
                    name="Critical Files",
                    marker=dict(size=10, color='red'),
                    visible=False,
                )
            )
            fig.add_trace(
                go.Table(
                    header=dict(values=['File', 'Complexity', 'Change Freq', 'Risk Score']),
                    cells=dict(values=[cf_df['file_path'], cf_df['complexity'], cf_df['change_frequency'], cf_df['criticality_score']]),
                    visible=False,
                )
            )

        # Tab 3: Knowledge Silos
        spof_list = silo_data.get('spof_files', []) or []
        if spof_list:
            spof_df = pd.DataFrame([
                {
                    'file_path': item.get('file'),
                    'owner': item.get('dominant_author'),
                    'dominance_%': (item.get('dominance_ratio', 0) or 0) * 100,
                }
                for item in spof_list
            ])
            fig.add_trace(
                go.Bar(
                    x=spof_df['file_path'],
                    y=spof_df['dominance_%'],
                    name="Dominance % by Single Owner",
                    marker_color='purple',
                    visible=False,
                )
            )
            fig.add_trace(
                go.Table(
                    header=dict(values=['File', 'Owner', 'Dominance %']),
                    cells=dict(values=[spof_df['file_path'], spof_df['owner'], spof_df['dominance_%']]),
                    visible=False,
                )
            )

        fig.update_layout(
            title="File Insights: Hotspots & Churn",
            template="plotly_white",
            height=700,
            barmode='stack'
        )

        if save_path:
            fig.write_html(save_path)
            logger.info(f"File insights dashboard saved to {save_path}")

        return fig
