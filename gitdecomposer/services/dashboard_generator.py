"""
Dashboard Generator Service for GitDecomposer.

This service handles creating interactive dashboard visualizations
for repository analysis data.
"""

import logging
from typing import Optional

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
from ..viz import VisualizationEngine

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """
    Service for generating interactive dashboard visualizations.
    
    This class handles dashboard creation responsibilities previously managed
    by GitMetrics, providing clean separation of concerns.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize DashboardGenerator with analyzer and visualization instances.

        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self.commit_analyzer = CommitAnalyzer(git_repo)
        self.file_analyzer = FileAnalyzer(git_repo)
        self.contributor_analyzer = ContributorAnalyzer(git_repo)
        self.branch_analyzer = BranchAnalyzer(git_repo)
        self.advanced_metrics = AdvancedMetrics(git_repo)
        # Initialize visualization engine with self as metrics coordinator
        self.visualization = VisualizationEngine(git_repo, self)

        logger.info("DashboardGenerator initialized with all analyzers and visualization engine")

    def create_commit_activity_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create an interactive dashboard showing commit activity patterns.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Interactive dashboard
        """
        try:
            return self.visualization.create_commit_activity_dashboard(save_path)
        except Exception as e:
            logger.error(f"Error creating commit activity dashboard: {e}")
            return self._create_error_figure("Error creating commit activity dashboard")

    def create_contributor_analysis_charts(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create charts analyzing contributor patterns.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Contributor analysis charts
        """
        try:
            return self.visualization.create_contributor_analysis_charts(save_path)
        except Exception as e:
            logger.error(f"Error creating contributor analysis charts: {e}")
            return self._create_error_figure("Error creating contributor analysis charts")

    def create_file_analysis_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create visualizations for file analysis.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: File analysis visualizations
        """
        try:
            # Get data
            extensions_dist = self.file_analyzer.get_file_extensions_distribution()
            most_changed = self.file_analyzer.get_most_changed_files(15)
            directory_analysis = self.file_analyzer.get_directory_analysis()

            # Create subplots
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=[
                    "File Extensions Distribution",
                    "Most Changed Files",
                    "Directory Activity",
                    "File Change Patterns",
                ],
                specs=[
                    [{"type": "pie"}, {"secondary_y": False}],
                    [{"secondary_y": False}, {"secondary_y": False}],
                ],
            )

            # File extensions pie chart
            if not extensions_dist.empty:
                fig.add_trace(
                    go.Pie(
                        labels=extensions_dist["extension"],
                        values=extensions_dist["count"],
                        name="File Extensions",
                    ),
                    row=1, col=1
                )

            # Most changed files bar chart
            if not most_changed.empty:
                fig.add_trace(
                    go.Bar(
                        x=most_changed["file_path"][:10],  # Top 10
                        y=most_changed["change_count"],
                        name="Changes",
                        marker_color="lightblue",
                    ),
                    row=1, col=2
                )

            # Directory activity
            if not directory_analysis.empty:
                dir_stats = directory_analysis
                fig.add_trace(
                    go.Bar(
                        x=dir_stats["directory"][:10],
                        y=dir_stats["unique_files"][:10],
                        name="File Count",
                        marker_color="lightgreen",
                    ),
                    row=2, col=1
                )

            # File change patterns (timeline)
            try:
                file_timeline = self.file_analyzer.get_file_change_frequency_analysis()
                if not file_timeline.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=file_timeline["file_path"][:10] if "file_path" in file_timeline.columns else file_timeline.index[:10],
                            y=file_timeline["change_intensity"][:10] if "change_intensity" in file_timeline.columns else file_timeline["commit_count"][:10],
                            mode="lines+markers",
                            name="Files Changed",
                            line=dict(color="orange"),
                        ),
                        row=2, col=2
                    )
            except Exception as e:
                logger.warning(f"Could not add file change timeline: {e}")

            # Update layout
            fig.update_layout(
                title="File Analysis Dashboard",
                showlegend=True,
                height=800,
                template="plotly_white",
            )

            if save_path:
                fig.write_html(save_path)
                logger.info(f"File analysis visualization saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating file analysis visualization: {e}")
            return self._create_error_figure("Error creating file analysis visualization")

    def create_enhanced_file_analysis_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create an enhanced file analysis dashboard with advanced metrics.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Enhanced file analysis dashboard
        """
        try:
            # Get enhanced data
            hotspots = self.file_analyzer.get_file_hotspots_analysis()
            churn_analysis = self.file_analyzer.get_code_churn_analysis()
            size_analysis = self.file_analyzer.get_commit_size_distribution_analysis()
            doc_coverage = self.file_analyzer.get_documentation_coverage_analysis()

            # Create subplots
            fig = make_subplots(
                rows=3,
                cols=2,
                subplot_titles=[
                    "File Hotspots",
                    "Code Churn Rate",
                    "Commit Size Distribution",
                    "Documentation Coverage",
                    "File Change Frequency",
                    "Directory Health",
                ],
                specs=[
                    [{"secondary_y": False}, {"secondary_y": False}],
                    [{"type": "histogram"}, {"type": "pie"}],
                    [{"secondary_y": False}, {"secondary_y": False}],
                ],
            )

            # File hotspots
            if not hotspots.empty:
                fig.add_trace(
                    go.Scatter(
                        x=hotspots["total_lines_changed"][:15] if "total_lines_changed" in hotspots.columns else range(len(hotspots[:15])),
                        y=hotspots["hotspot_score"][:15] if "hotspot_score" in hotspots.columns else hotspots.index[:15],
                        mode="markers",
                        marker=dict(
                            size=hotspots["commit_count"][:15] if "commit_count" in hotspots.columns else 10,
                            color=hotspots["total_lines_changed"][:15] if "total_lines_changed" in hotspots.columns else range(len(hotspots[:15])),
                            colorscale="Reds",
                            showscale=True,
                        ),
                        text=hotspots.index[:15],  # Use index as file names
                        name="Hotspots",
                    ),
                    row=1, col=1
                )

            # Code churn rate
            if "file_churn_rates" in churn_analysis and not churn_analysis["file_churn_rates"].empty:
                churn_data = churn_analysis["file_churn_rates"]
                fig.add_trace(
                    go.Bar(
                        x=churn_data["file_path"][:10],
                        y=churn_data["churn_rate"],
                        name="Churn Rate",
                        marker_color="coral",
                    ),
                    row=1, col=2
                )

            # Commit size distribution
            if "size_distribution" in size_analysis:
                sizes = list(size_analysis["size_distribution"].keys())
                counts = list(size_analysis["size_distribution"].values())
                fig.add_trace(
                    go.Histogram(
                        x=sizes,
                        y=counts,
                        name="Size Distribution",
                        marker_color="lightblue",
                    ),
                    row=2, col=1
                )

            # Documentation coverage
            doc_ratio = doc_coverage.get("documentation_ratio", 0)
            code_ratio = 100 - doc_ratio
            fig.add_trace(
                go.Pie(
                    labels=["Documentation", "Code"],
                    values=[doc_ratio, code_ratio],
                    name="Doc Coverage",
                ),
                row=2, col=2
            )

            # File change frequency
            try:
                freq_analysis = self.file_analyzer.get_file_change_frequency_analysis()
                if not freq_analysis.empty:
                    fig.add_trace(
                        go.Bar(
                            x=freq_analysis["file_path"][:10],
                            y=freq_analysis["change_intensity"][:10],
                            name="Change Frequency",
                            marker_color="purple",
                        ),
                        row=3, col=1
                    )
            except Exception as e:
                logger.warning(f"Could not add file change frequency: {e}")

            # Directory health metrics
            try:
                dir_analysis = self.file_analyzer.get_directory_analysis()
                if not dir_analysis.empty:
                    dir_stats = dir_analysis
                    fig.add_trace(
                        go.Scatter(
                            x=dir_stats["unique_files"][:10],
                            y=dir_stats["avg_changes_per_file"][:10],
                            mode="markers",
                            marker=dict(size=12, color="green"),
                            text=dir_stats["directory"][:10],
                            name="Directory Health",
                        ),
                        row=3, col=2
                    )
            except Exception as e:
                logger.warning(f"Could not add directory health: {e}")

            # Update layout
            fig.update_layout(
                title="Enhanced File Analysis Dashboard",
                showlegend=True,
                height=1200,
                template="plotly_white",
            )

            if save_path:
                fig.write_html(save_path)
                logger.info(f"Enhanced file analysis dashboard saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating enhanced file analysis dashboard: {e}")
            return self._create_error_figure("Error creating enhanced file analysis dashboard")

    def create_branch_analysis_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a dashboard for branch analysis.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Branch analysis dashboard
        """
        try:
            # Get branch data
            branch_stats = self.branch_analyzer.get_branch_statistics()
            active_branches = self.branch_analyzer.get_branch_statistics()
            
            # Create basic branch visualization
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=[
                    "Branch Activity",
                    "Branch Age Distribution", 
                    "Commits per Branch",
                    "Branch Status",
                ],
            )

            if not branch_stats.empty:
                # Branch activity over time
                fig.add_trace(
                    go.Bar(
                        x=branch_stats["branch"][:10],
                        y=branch_stats["commits"],
                        name="Commits",
                        marker_color="skyblue",
                    ),
                    row=1, col=1
                )

            fig.update_layout(
                title="Branch Analysis Dashboard",
                showlegend=True,
                height=800,
                template="plotly_white",
            )

            if save_path:
                fig.write_html(save_path)
                logger.info(f"Branch analysis dashboard saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating branch analysis dashboard: {e}")
            return self._create_error_figure("Error creating branch analysis dashboard")

    def _create_error_figure(self, error_message: str) -> go.Figure:
        """Create a simple error figure when visualization fails."""
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Visualization Error",
            template="plotly_white",
        )
        return fig
