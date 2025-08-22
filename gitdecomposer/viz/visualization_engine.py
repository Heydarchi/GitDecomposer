"""
VisualizationEngine module for creating charts and dashboards.
Refactored to use modular plotting functions from the plots directory.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns

# Import plotting functions from the plots module
from .plots import (
    create_commit_activity_dashboard,
    create_contributor_analysis_charts,
    create_file_analysis_visualization,
    create_enhanced_file_analysis_dashboard,
    create_technical_debt_dashboard,
    create_index_page,
)

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Handles all chart and dashboard generation for GitDecomposer.

    This class now acts as a coordinator that delegates to specialized
    plotting functions in the plots module.
    """

    def __init__(self, git_repo, metrics_coordinator):
        """
        Initialize visualization engine.

        Args:
            git_repo: GitRepository instance
            metrics_coordinator: GitMetrics instance (for data access)
        """
        self.git_repo = git_repo
        self.metrics = metrics_coordinator

        # Set style for matplotlib
        plt.style.use("default")
        sns.set_palette("husl")

    def create_commit_activity_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create comprehensive commit activity dashboard.

        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        return create_commit_activity_dashboard(self.metrics, save_path)

    def create_contributor_analysis_charts(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create contributor analysis visualization.

        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        return create_contributor_analysis_charts(self.metrics, save_path)

    def create_file_analysis_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create file analysis visualization.

        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        return create_file_analysis_visualization(self.metrics, save_path)

    def create_enhanced_file_analysis_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create enhanced file analysis dashboard with advanced metrics.

        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        return create_enhanced_file_analysis_dashboard(self.metrics, save_path)

    def create_technical_debt_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive technical debt analysis dashboard.

        Args:
            save_path (Optional[str]): Path to save the HTML file

        Returns:
            go.Figure: Technical debt dashboard
        """
        return create_technical_debt_dashboard(self.metrics, save_path)

    def create_index_page(
        self,
        output_path: str,
        report_links: Dict[str, str],
        csv_links: Dict[str, str],
        summary: Dict,
    ):
        """
        Creates a main index.html page with links to all reports and CSVs.

        Args:
            output_path (str): The path to save the index.html file.
            report_links (dict): A dictionary of report names to their file paths.
            csv_links (dict): A dictionary of CSV file names to their paths.
            summary (dict): The repository summary data.
        """
        return create_index_page(output_path, report_links, csv_links, summary)

    def generate_all_visualizations(self, output_dir: str = "visualizations") -> Dict[str, str]:
        """
        Generate all visualizations and save them to the specified directory.

        Args:
            output_dir (str): Directory to save the visualizations

        Returns:
            Dict[str, str]: Mapping of visualization names to file paths
        """
        import os

        os.makedirs(output_dir, exist_ok=True)
        generated_reports = {}

        visualizations = {
            "commit_activity_dashboard": self.create_commit_activity_dashboard,
            "contributor_analysis_charts": self.create_contributor_analysis_charts,
            "file_analysis_visualization": self.create_file_analysis_visualization,
            "enhanced_file_analysis_dashboard": self.create_enhanced_file_analysis_dashboard,
            "technical_debt_dashboard": self.create_technical_debt_dashboard,
        }

        for viz_name, viz_function in visualizations.items():
            try:
                filepath = os.path.join(output_dir, f"{viz_name}.html")
                viz_function(filepath)
                generated_reports[viz_name] = filepath
                logger.info(f"Generated {viz_name} at {filepath}")
            except Exception as e:
                logger.error(f"Failed to generate {viz_name}: {e}")

        return generated_reports

    def _add_explanation_to_html(self, save_path: str, explanation_html: str):
        """Appends explanation section to the end of a Plotly HTML file."""
        if not save_path:
            return
        try:
            with open(save_path, "a") as f:
                f.write(explanation_html)
            logger.info(f"Appended explanation to {save_path}")
        except Exception as e:
            logger.error(f"Could not append explanation to {save_path}: {e}")
