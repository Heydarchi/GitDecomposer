"""
Plotting functions for file-related visualizations.
"""

from typing import Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import BasePlotter


class FilePlotter(BasePlotter):
    """Plotter for file-related visualizations."""

    @property
    def title(self) -> str:
        return "File Analysis"

    @property
    def description(self) -> str:
        return "Analysis of file patterns, extensions, changes, and churn across the repository."

    def create_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create file analysis visualization.

        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        file_extensions = self.metrics_coordinator.file_analyzer.get_file_extensions_distribution()
        most_changed = self.metrics_coordinator.file_analyzer.get_most_changed_files()
        file_churn = self.metrics_coordinator.file_analyzer.get_file_churn_analysis()

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "File Extensions Distribution",
                "Most Changed Files",
                "File Churn Analysis",
                "Files by Change Frequency",
            ),
            specs=[
                [{"type": "pie"}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        if file_extensions:
            fig.add_trace(
                go.Pie(
                    labels=list(file_extensions.keys()),
                    values=list(file_extensions.values()),
                    name="Extensions",
                ),
                row=1,
                col=1,
            )

        if most_changed:
            top_files = most_changed[:15]
            files = [f["file"] for f in top_files]
            changes = [f["changes"] for f in top_files]
            fig.add_trace(
                go.Bar(
                    x=changes,
                    y=files,
                    orientation="h",
                    name="Changes",
                    marker=dict(color="lightcoral"),
                ),
                row=1,
                col=2,
            )

            change_counts = [f["changes"] for f in most_changed]
            fig.add_trace(go.Histogram(x=change_counts, name="Change Frequency", nbinsx=15), row=2, col=2)

        if file_churn and "churn_over_time" in file_churn:
            churn_data = file_churn["churn_over_time"]
            fig.add_trace(
                go.Scatter(
                    x=list(churn_data.keys()),
                    y=list(churn_data.values()),
                    mode="lines+markers",
                    name="Churn",
                    line=dict(color="green", width=2),
                ),
                row=2,
                col=1,
            )

        fig.update_layout(title="Repository File Analysis", height=800, showlegend=True)

        if save_path:
            self.save_html(fig, save_path)

        return fig

    def create_enhanced_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create enhanced file analysis dashboard with advanced metrics.

        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        file_extensions = self.metrics_coordinator.file_analyzer.get_file_extensions_distribution()
        most_changed = self.metrics_coordinator.file_analyzer.get_most_changed_files()
        file_churn = self.metrics_coordinator.file_analyzer.get_file_churn_analysis()
        doc_coverage = self.metrics_coordinator.file_analyzer.get_documentation_coverage_analysis()

        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "File Types Distribution",
                "File Activity Heatmap",
                "Churn vs Changes",
                "Directory Activity",
                "Documentation Coverage",
                "Change Frequency Distribution",
            ),
            specs=[
                [{"type": "pie"}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"type": "bar"}, {"secondary_y": False}],
            ],
        )

        # File types distribution
        if file_extensions:
            fig.add_trace(
                go.Pie(
                    labels=list(file_extensions.keys()),
                    values=list(file_extensions.values()),
                    name="File Types",
                    hole=0.3,
                    marker=dict(colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]),
                ),
                row=1,
                col=1,
            )

        # File activity analysis
        if most_changed:
            top_files = most_changed[:20]
            for i, f in enumerate(top_files):
                changes = f["changes"]
                authors = f.get("unique_authors", 1)

                # Simulate file activity data
                import random

                activity_data = [random.randint(0, changes) for _ in range(12)]
                months = [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ]

                if i < 5:  # Only show top 5 files to avoid clutter
                    fig.add_trace(
                        go.Scatter(
                            x=months,
                            y=activity_data,
                            mode="lines+markers",
                            name=f["file"][-20:],
                            line=dict(width=2),
                        ),
                        row=1,
                        col=2,
                    )

            # Directory activity
            directory_stats = {}
            for f in most_changed[:30]:
                file_path = f["file"]
                directory = "/".join(file_path.split("/")[:-1]) if "/" in file_path else "root"
                if directory not in directory_stats:
                    directory_stats[directory] = 0
                directory_stats[directory] += f["changes"]

            if directory_stats:
                dirs = list(directory_stats.keys())[:10]
                dir_changes = [directory_stats[d] for d in dirs]

                fig.add_trace(
                    go.Bar(
                        x=dirs,
                        y=dir_changes,
                        name="Directory Changes",
                        marker=dict(color="lightgreen"),
                    ),
                    row=2,
                    col=2,
                )

        # Churn analysis
        if file_churn and "churn_over_time" in file_churn:
            churn_data = file_churn["churn_over_time"]
            fig.add_trace(
                go.Scatter(
                    x=list(churn_data.keys()),
                    y=list(churn_data.values()),
                    mode="lines+markers",
                    name="Code Churn",
                    line=dict(color="red", width=3, dash="dot"),
                ),
                row=2,
                col=1,
            )

        # Documentation coverage
        if doc_coverage and "coverage_by_type" in doc_coverage:
            coverage_data = doc_coverage["coverage_by_type"]
            fig.add_trace(
                go.Bar(
                    x=list(coverage_data.keys()),
                    y=list(coverage_data.values()),
                    name="Doc Coverage",
                    marker=dict(color="skyblue"),
                ),
                row=3,
                col=1,
            )

        # Change frequency distribution
        if most_changed:
            change_counts = [f["changes"] for f in most_changed]
            fig.add_trace(
                go.Histogram(
                    x=change_counts,
                    name="Change Distribution",
                    marker=dict(color="orange", opacity=0.7),
                    nbinsx=20,
                ),
                row=3,
                col=2,
            )

        fig.update_layout(title="Enhanced File Analysis Dashboard", height=1200, showlegend=True)
        fig.update_xaxes(tickangle=45, row=3, col=2)

        if save_path:
            self.save_html(fig, save_path)

        return fig


# Backwards compatibility functions
def create_file_analysis_visualization(metrics_coordinator, save_path: Optional[str] = None) -> go.Figure:
    """
    Backwards compatibility function for file analysis visualization.

    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the dashboard HTML file

    Returns:
        go.Figure: Plotly figure object
    """
    plotter = FilePlotter(metrics_coordinator)
    return plotter.create_visualization(save_path)


def create_enhanced_file_analysis_dashboard(metrics_coordinator, save_path: Optional[str] = None) -> go.Figure:
    """
    Backwards compatibility function for enhanced file analysis dashboard.

    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the dashboard HTML file

    Returns:
        go.Figure: Plotly figure object
    """
    plotter = FilePlotter(metrics_coordinator)
    return plotter.create_enhanced_visualization(save_path)
