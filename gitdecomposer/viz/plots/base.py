"""
Base class for all plotting modules in GitDecomposer.
"""

from abc import ABC, abstractmethod
from typing import Optional

import plotly.graph_objects as go


class BasePlotter(ABC):
    """
    Abstract base class for all plotting modules.

    This class defines the common interface that all plotting classes should implement.
    """

    def __init__(self, metrics_coordinator):
        """
        Initialize the plotter with a metrics coordinator.

        Args:
            metrics_coordinator: GitMetrics instance for data access.
        """
        self.metrics_coordinator = metrics_coordinator

    @abstractmethod
    def create_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create the main visualization for this plotter.

        Args:
            save_path (Optional[str]): Path to save the HTML file

        Returns:
            go.Figure: Plotly figure object
        """
        pass

    def save_html(
        self, fig: go.Figure, save_path: str, visualization_type: str = "default"
    ) -> None:
        """
        Save the figure as an HTML file with an explanation section.

        Args:
            fig (go.Figure): The plotly figure to save
            save_path (str): Path to save the HTML file
            visualization_type (str): The type of visualization to get descriptions for.
        """
        html = fig.to_html(full_html=True, include_plotlyjs="cdn")

        # Create the explanation HTML
        descriptions = self.get_subplot_descriptions(visualization_type)
        if descriptions:
            explanation_html = """
            <div style="font-family: sans-serif; padding: 20px; margin: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="border-bottom: 1px solid #ddd; padding-bottom: 10px;">Chart Explanations</h2>
            """
            for title, desc in descriptions.items():
                explanation_html += f"""
                <div style="margin-bottom: 15px;">
                    <h3 style="color: #333;">{title}</h3>
                    <p style="color: #555;">{desc}</p>
                </div>
                """
            explanation_html += "</div>"

            # Inject the explanation before the closing body tag
            if "</body>" in html:
                html = html.replace("</body>", explanation_html + "</body>")
            else:
                html += explanation_html

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(html)

    @property
    @abstractmethod
    def title(self) -> str:
        """Return the title of this visualization."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this visualization shows."""
        pass

    @abstractmethod
    def get_subplot_descriptions(self) -> dict:
        """Return a dictionary of subplot titles to their descriptions."""
        pass
