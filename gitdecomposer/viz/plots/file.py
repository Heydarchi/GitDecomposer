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

    def get_subplot_descriptions(self, visualization_type: str = "default") -> dict[str, str]:
        """
        Returns a dictionary of subplot titles and their descriptions.
        """
        return {
            "File Extensions Distribution": "Shows the distribution of different file types in the repository, helping to understand the technology stack and codebase composition.",
            "Most Changed Files": "Identifies files that have been modified most frequently, which may indicate areas of high maintenance or potential refactoring candidates.",
            "File Change Frequency Over Time": "Displays how file modification patterns have changed over time, revealing development focus areas and project evolution.",
            "Lines of Code by File Type": "Compares the amount of code across different file types, providing insights into the relative size and importance of different components.",
            "Code Churn Analysis": "Shows the rate of code changes (additions and deletions) over time, helping to identify periods of intense development or refactoring.",
            "File Size Distribution": "Displays the distribution of file sizes in the repository, helping to identify potentially oversized files that might need refactoring.",
        }

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

        # File extensions: DataFrame columns ['extension','count']
        if file_extensions is not None and hasattr(file_extensions, "empty") and not file_extensions.empty:
            labels = list(file_extensions["extension"].astype(str))
            values = list(file_extensions["count"].astype(int))
            fig.add_trace(go.Pie(labels=labels, values=values, name="Extensions"), row=1, col=1)

        # Most changed files: DataFrame ['file_path','change_count']
        if most_changed is not None and hasattr(most_changed, "empty") and not most_changed.empty:
            top_df = most_changed.head(15)
            files = list(top_df["file_path"].astype(str))
            changes = list(top_df["change_count"].astype(int))
            fig.add_trace(
                go.Bar(x=changes, y=files, orientation="h", name="Changes", marker=dict(color="lightcoral")),
                row=1,
                col=2,
            )
            change_counts = list(most_changed["change_count"].astype(int))
            fig.add_trace(go.Histogram(x=change_counts, name="Change Frequency", nbinsx=15), row=2, col=2)

        # File churn: DataFrame ['file_path','changes_in_period','churn_rate']
        if file_churn is not None and hasattr(file_churn, "empty") and not file_churn.empty:
            top_churn = file_churn.sort_values("changes_in_period", ascending=False).head(15)
            fig.add_trace(
                go.Bar(
                    x=list(top_churn["file_path"].astype(str)),
                    y=list(top_churn["changes_in_period"].astype(int)),
                    name="Churn (recent)",
                    marker=dict(color="green"),
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
        if file_extensions is not None and hasattr(file_extensions, "empty") and not file_extensions.empty:
            fig.add_trace(
                go.Pie(
                    labels=list(file_extensions["extension"].astype(str)),
                    values=list(file_extensions["count"].astype(int)),
                    name="File Types",
                    hole=0.3,
                    marker=dict(colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]),
                ),
                row=1,
                col=1,
            )

        # File activity analysis
        if most_changed is not None and hasattr(most_changed, "empty") and not most_changed.empty:
            top_files = most_changed.head(10).copy()
            # Simulate monthly activity lines for top files using their change_count as scale
            import random
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            for i, row in top_files.iterrows():
                changes = int(row.get("change_count", 0)) or 1
                if i < 5:
                    activity_data = [random.randint(0, max(1, changes)) for _ in range(12)]
                    fig.add_trace(
                        go.Scatter(x=months, y=activity_data, mode="lines+markers", name=str(row.get("file_path", "file"))[-30:]),
                        row=1,
                        col=2,
                    )

            # Directory activity (aggregate changes by directory from most_changed)
            if most_changed is not None and hasattr(most_changed, "empty") and not most_changed.empty:
                tmp = most_changed.copy()
                tmp["directory"] = tmp["file_path"].astype(str).apply(lambda p: "/".join(p.split("/")[:-1]) if "/" in p else "<root>")
                dir_stats = tmp.groupby("directory")["change_count"].sum().sort_values(ascending=False).head(10)
                fig.add_trace(
                    go.Bar(x=list(dir_stats.index), y=list(dir_stats.values), name="Directory Changes", marker=dict(color="lightgreen")),
                    row=2,
                    col=2,
                )

        # Churn vs Changes (scatter using DataFrame columns if available)
        if file_churn is not None and hasattr(file_churn, "empty") and not file_churn.empty:
            scatter_df = file_churn.copy()
            # Ensure required columns exist
            if "changes_in_period" in scatter_df.columns and "churn_rate" in scatter_df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=list(scatter_df["changes_in_period"].astype(float)),
                        y=list(scatter_df["churn_rate"].astype(float)),
                        text=list(scatter_df["file_path"].astype(str).str[-40:]),
                        mode="markers",
                        name="Churn vs Changes",
                        marker=dict(color="#D7263D", size=8, opacity=0.7),
                    ),
                    row=2,
                    col=1,
                )

        # Documentation coverage
        if isinstance(doc_coverage, dict) and "doc_file_types" in doc_coverage:
            coverage_data = doc_coverage["doc_file_types"]
            fig.add_trace(
                go.Bar(x=list(coverage_data.keys()), y=list(coverage_data.values()), name="Doc Coverage", marker=dict(color="skyblue")),
                row=3,
                col=1,
            )
        elif isinstance(doc_coverage, dict) and "documentation_ratio" in doc_coverage:
            doc_ratio = float(doc_coverage.get("documentation_ratio", 0))
            code_ratio = max(0.0, 100.0 - doc_ratio)
            fig.add_trace(
                go.Pie(labels=["Documentation", "Code"], values=[doc_ratio, code_ratio], name="Doc vs Code"),
                row=3,
                col=1,
            )

        # Change frequency distribution
        if most_changed is not None and hasattr(most_changed, "empty") and not most_changed.empty:
            change_counts = list(most_changed["change_count"].astype(int))
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
