"""
Plotting functions for contributor-related visualizations.
"""

from typing import Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .base import BasePlotter


class ContributorPlotter(BasePlotter):
    """Plotter for contributor-related visualizations."""

    @property
    def title(self) -> str:
        return "Contributor Analysis"

    @property
    def description(self) -> str:
        return "Analysis of contributor patterns, activity over time, and impact on the repository."

    def get_subplot_descriptions(self, visualization_type: str = "default") -> dict[str, str]:
        """
        Returns a dictionary of subplot titles and their descriptions.
        """
        return {
            "Commits by Author": "Shows the distribution of commits across different contributors, helping to identify the most active contributors and understand team dynamics.",
            "Contributor Activity Timeline": "Displays when each contributor has been active in the project over time, revealing patterns of engagement and periods of high activity.",
            "Lines Added/Removed by Author": "Compares the amount of code added versus removed by each contributor, providing insights into their coding patterns and impact on the codebase.",
            "Author Contribution Distribution": "Pie chart showing the relative contribution of each author to the overall project, helping to understand team composition and workload distribution.",
        }

    def create_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create contributor analysis visualization.

        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        # Get data from metrics coordinator
        contributors = self.metrics_coordinator.contributor_analyzer.get_top_contributors()

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Top Contributors by Commits",
                "Top Contributors by Lines Added",
                "Contributor Activity Over Time",
                "Contributors by Impact",
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        if not contributors.empty:
            top_10_commits = contributors.head(10)

            fig.add_trace(
                go.Bar(
                    x=top_10_commits["author"], y=top_10_commits["total_commits"], name="Commits"
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Bar(
                    x=top_10_commits["author"],
                    y=top_10_commits["total_insertions"],
                    name="Lines Added",
                    marker=dict(color="lightgreen"),
                ),
                row=1,
                col=2,
            )

            fig.add_trace(
                go.Scatter(
                    x=contributors["total_commits"],
                    y=contributors["total_insertions"],
                    mode="markers",
                    text=contributors["author"],
                    name="Impact",
                    marker=dict(size=8, opacity=0.7),
                ),
                row=2,
                col=2,
            )

        # Activity over time for top 5 contributors
        if not contributors.empty:
            top_5_contributors = contributors.head(5)
            for index, author_data in top_5_contributors.iterrows():
                author = author_data["author"]
                first_commit = author_data["first_commit_date"]
                last_commit = author_data["last_commit_date"]

                fig.add_trace(
                    go.Scatter(
                        x=[first_commit, last_commit],
                        y=[author, author],
                        mode="lines+markers",
                        name=author,
                        showlegend=False,  # Avoid cluttering legend
                    ),
                    row=2,
                    col=1,
                )

        fig.update_layout(
            title="Repository Contributor Analysis",
            height=800,
            showlegend=True,
            yaxis2=dict(title_text="Contributor"),  # Label for the activity timeline
        )

        if save_path:
            self.save_html(fig, save_path)

        return fig


# Backwards compatibility function
def create_contributor_analysis_charts(
    metrics_coordinator, save_path: Optional[str] = None
) -> go.Figure:
    """
    Backwards compatibility function for contributor analysis charts.

    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the dashboard HTML file

    Returns:
        go.Figure: Plotly figure object
    """
    plotter = ContributorPlotter(metrics_coordinator)
    return plotter.create_visualization(save_path)
