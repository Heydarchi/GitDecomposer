"""
Plotting functions for technical debt visualizations.
"""

from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .base import BasePlotter


class TechnicalDebtPlotter(BasePlotter):
    """Plotter for technical debt visualizations."""

    @property
    def title(self) -> str:
        return "Technical Debt Analysis"

    @property
    def description(self) -> str:
        return "Comprehensive analysis of technical debt accumulation, maintainability, and debt hotspots."

    def get_subplot_descriptions(self, visualization_type: str = "default") -> dict[str, str]:
        """
        Returns a dictionary of subplot titles and their descriptions.
        """
        return {
            "Debt Accumulation Trend": "Shows how technical debt has accumulated over time in the repository. Rising trends indicate areas where code quality may be declining and require attention.",
            "Debt Distribution by Type": "Displays the breakdown of different types of technical debt (e.g., complexity, duplication, maintainability issues) to help prioritize refactoring efforts.",
            "Maintainability vs Debt Correlation": "Illustrates the relationship between code maintainability scores and technical debt levels. Lower maintainability typically correlates with higher debt.",
            "Debt Hotspots (Top 10 Files)": "Identifies the files with the highest technical debt scores, helping teams focus their refactoring efforts on the most problematic areas.",
            "Monthly Debt Rate": "Shows the monthly accumulation rate of technical debt, helping to track whether debt is being addressed or growing over time.",
            "Debt Resolution Priority Matrix": "Provides a prioritization framework for addressing technical debt based on impact and effort required for resolution.",
        }

    def create_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive technical debt analysis dashboard.

        Args:
            save_path (Optional[str]): Path to save the HTML file

        Returns:
            go.Figure: Technical debt dashboard
        """
        try:
            debt_analysis = self.metrics_coordinator.advanced_metrics.calculate_technical_debt_accumulation()
            maintainability = self.metrics_coordinator.advanced_metrics.calculate_maintainability_index()

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

            if debt_analysis and "debt_over_time" in debt_analysis:
                debt_df = pd.DataFrame(debt_analysis["debt_over_time"])
                if not debt_df.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=debt_df["date"],
                            y=debt_df["cumulative_debt"],
                            mode="lines",
                            name="Debt Trend",
                        ),
                        row=1,
                        col=1,
                    )

            if debt_analysis and "debt_by_type" in debt_analysis:
                debt_types = debt_analysis["debt_by_type"]
                if debt_types:
                    fig.add_trace(
                        go.Pie(
                            labels=list(debt_types.keys()),
                            values=list(debt_types.values()),
                            name="Debt Types",
                        ),
                        row=1,
                        col=2,
                    )

            if maintainability and "maintainability_scores" in maintainability:
                mi_df = pd.DataFrame(maintainability["maintainability_scores"])
                if not mi_df.empty and debt_analysis and "debt_hotspots" in debt_analysis:
                    debt_hotspots_df = pd.DataFrame(debt_analysis["debt_hotspots"])
                    if not debt_hotspots_df.empty:
                        merged_df = pd.merge(mi_df, debt_hotspots_df, on="file")
                        if not merged_df.empty:
                            fig.add_trace(
                                go.Scatter(
                                    x=merged_df["maintainability_index"],
                                    y=merged_df["debt_score"],
                                    mode="markers",
                                    text=merged_df["file"],
                                    name="MI vs Debt",
                                ),
                                row=2,
                                col=1,
                            )

                        fig.add_trace(
                            go.Bar(
                                x=debt_hotspots_df["file"][:10],
                                y=debt_hotspots_df["debt_score"][:10],
                                name="Debt Hotspots",
                            ),
                            row=2,
                            col=2,
                        )

            if debt_analysis and "debt_over_time" in debt_analysis:
                debt_df = pd.DataFrame(debt_analysis["debt_over_time"])
                if not debt_df.empty and "date" in debt_df.columns and "debt_score" in debt_df.columns:
                    debt_df["month"] = pd.to_datetime(debt_df["date"]).dt.to_period("M")
                    monthly_debt = debt_df.groupby("month")["debt_score"].sum().reset_index()
                    monthly_debt["month"] = monthly_debt["month"].astype(str)
                    fig.add_trace(
                        go.Bar(
                            x=monthly_debt["month"],
                            y=monthly_debt["debt_score"],
                            name="Monthly Debt",
                        ),
                        row=3,
                        col=1,
                    )

            fig.update_layout(title_text="Technical Debt Analysis Dashboard", height=1200, showlegend=False)

            if save_path:
                self.save_html(fig, save_path)

            return fig
        except Exception:
            return go.Figure()


# Backwards compatibility function
def create_technical_debt_dashboard(metrics_coordinator, save_path: Optional[str] = None) -> go.Figure:
    """
    Backwards compatibility function for technical debt dashboard.

    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the HTML file

    Returns:
        go.Figure: Technical debt dashboard
    """
    plotter = TechnicalDebtPlotter(metrics_coordinator)
    return plotter.create_visualization(save_path)
