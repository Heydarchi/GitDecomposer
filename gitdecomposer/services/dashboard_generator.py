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
    BranchAnalyzer,
    CommitAnalyzer,
    ContributorAnalyzer,
    FileAnalyzer,
    advanced_metrics,
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
        # Advanced metrics module for creating metric analyzers
        self.advanced_metrics = advanced_metrics
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
                    row=1,
                    col=1,
                )

            # Most changed files bar chart
            if not most_changed.empty:
                fig.add_trace(
                    go.Bar(
                        x=most_changed["file_path"][:25],  # Top 25
                        y=most_changed["change_count"],
                        name="Changes",
                        marker_color="lightblue",
                    ),
                    row=1,
                    col=2,
                )

            # Directory activity
            if not directory_analysis.empty:
                dir_stats = directory_analysis
                fig.add_trace(
                    go.Bar(
                        x=dir_stats["directory"][:25],
                        y=dir_stats["unique_files"][:25],
                        name="File Count",
                        marker_color="lightgreen",
                    ),
                    row=2,
                    col=1,
                )

            # File change patterns (timeline)
            try:
                file_timeline = self.file_analyzer.get_file_change_frequency_analysis()
                if not file_timeline.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=(
                                file_timeline["file_path"][:25]
                                if "file_path" in file_timeline.columns
                                else file_timeline.index[:25]
                            ),
                            y=(
                                file_timeline["change_intensity"][:25]
                                if "change_intensity" in file_timeline.columns
                                else file_timeline["commit_count"][:25]
                            ),
                            mode="lines+markers",
                            name="Files Changed",
                            line=dict(color="orange"),
                        ),
                        row=2,
                        col=2,
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
                # Generate HTML with custom description  
                html_content = self._generate_file_analysis_html(fig)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
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
                        x=(
                            hotspots["total_lines_changed"][:30]
                            if "total_lines_changed" in hotspots.columns
                            else range(len(hotspots[:30]))
                        ),
                        y=(
                            hotspots["hotspot_score"][:30]
                            if "hotspot_score" in hotspots.columns
                            else hotspots.index[:30]
                        ),
                        mode="markers",
                        marker=dict(
                            size=hotspots["commit_count"][:30] if "commit_count" in hotspots.columns else 10,
                            color=(
                                hotspots["total_lines_changed"][:30]
                                if "total_lines_changed" in hotspots.columns
                                else range(len(hotspots[:30]))
                            ),
                            colorscale="Reds",
                            showscale=True,
                        ),
                        text=hotspots.index[:30],  # Use index as file names
                        name="Hotspots",
                    ),
                    row=1,
                    col=1,
                )

            # Code churn rate
            if "file_churn_rates" in churn_analysis and not churn_analysis["file_churn_rates"].empty:
                churn_data = churn_analysis["file_churn_rates"]
                fig.add_trace(
                    go.Bar(
                        x=churn_data["file_path"][:25],
                        y=churn_data["churn_rate"],
                        name="Churn Rate",
                        marker_color="coral",
                    ),
                    row=1,
                    col=2,
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
                    row=2,
                    col=1,
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
                row=2,
                col=2,
            )

            # File change frequency
            try:
                freq_analysis = self.file_analyzer.get_file_change_frequency_analysis()
                if not freq_analysis.empty:
                    fig.add_trace(
                        go.Bar(
                            x=freq_analysis["file_path"][:25],
                            y=freq_analysis["change_intensity"][:25],
                            name="Change Frequency",
                            marker_color="purple",
                        ),
                        row=3,
                        col=1,
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
                            x=dir_stats["unique_files"][:25],
                            y=dir_stats["avg_changes_per_file"][:25],
                            mode="markers",
                            marker=dict(size=12, color="green"),
                            text=dir_stats["directory"][:10],
                            name="Directory Health",
                        ),
                        row=3,
                        col=2,
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
                # Generate HTML with custom description
                html_content = self._generate_enhanced_file_analysis_html(fig)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Enhanced file analysis dashboard saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating enhanced file analysis dashboard: {e}")
            return self._create_error_figure("Error creating enhanced file analysis dashboard")

    def _generate_enhanced_file_analysis_html(self, fig: go.Figure) -> str:
        """Generate HTML content for enhanced file analysis report with description."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced File Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ padding: 30px; }}
        .description {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #28a745; }}
        .calculation {{ background: #e9ecef; padding: 15px; border-radius: 6px; margin: 10px 0; }}
        .section-title {{ color: #28a745; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }}
        .metric-formula {{ font-family: 'Courier New', monospace; background: #f1f3f4; padding: 8px; border-radius: 4px; }}
        .component-box {{ background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 6px; margin: 8px 0; }}
        .insight-box {{ background: #d4edda; border-left: 4px solid #28a745; padding: 12px; border-radius: 4px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enhanced File Analysis Dashboard</h1>
            <p>Advanced file metrics with risk assessment and hotspot analysis</p>
        </div>
        
        <div class="content">
            <div id="chart"></div>
            
            <div class="description">
                <h3 class="section-title">Dashboard Overview</h3>
                <p><strong>Enhanced File Analysis</strong> provides deep insights into your codebase files, identifying hotspots, technical debt, and maintenance patterns. This advanced analysis goes beyond basic file statistics to reveal actionable insights for code quality improvement and technical debt management.</p>
                
                <h4 class="section-title">Key Metrics and Calculations</h4>
                
                <div class="component-box">
                    <strong>Hotspot Score Calculation:</strong>
                    <div class="metric-formula">Score = (Change Frequency × 0.3) + (Lines Changed × 0.4) + (Contributors × 0.3)</div>
                    <p>Combines multiple factors to identify files requiring immediate attention due to high maintenance burden and complexity.</p>
                </div>

                <div class="component-box">
                    <strong>Code Churn Rate:</strong>
                    <div class="metric-formula">Churn = (Lines Added + Lines Deleted) / Total Commits</div>
                    <p>Measures code instability by tracking how much code is rewritten, indicating potential design issues or active development areas.</p>
                </div>

                <div class="component-box">
                    <strong>Change Intensity Score:</strong>
                    <div class="metric-formula">Intensity = Weighted Sum(Recent Changes) / Time Period</div>
                    <p>Evaluates recent activity patterns with higher weight on newer changes to identify current development hotspots.</p>
                </div>

                <div class="component-box">
                    <strong>Directory Health Index:</strong>
                    <div class="metric-formula">Health = Average Changes per File / Total File Count</div>
                    <p>Assesses module organization and stability by comparing file count with change distribution across directories.</p>
                </div>

                <h4 class="section-title">Dashboard Components Analysis</h4>
                
                <div class="calculation">
                    <strong>File Hotspots (Top Left):</strong>
                    <ul>
                        <li>Bubble chart showing files by lines changed vs hotspot score</li>
                        <li>Bubble size indicates number of commits</li>
                        <li>Color intensity shows change frequency</li>
                        <li>Identifies files requiring immediate attention</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>Code Churn Rate (Top Right):</strong>
                    <ul>
                        <li>Files with highest churn (lines added + deleted)</li>
                        <li>Indicates unstable or actively developed areas</li>
                        <li>High churn may suggest design issues</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>Commit Size Distribution (Middle Left):</strong>
                    <ul>
                        <li>Histogram of commit sizes (XS, S, M, L, XL)</li>
                        <li>Helps identify development patterns</li>
                        <li>Large commits may indicate poor practices</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>Documentation Coverage (Middle Right):</strong>
                    <ul>
                        <li>Ratio of documentation vs code files</li>
                        <li>Shows project maintainability level</li>
                        <li>Helps identify documentation gaps</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>File Change Frequency (Bottom Left):</strong>
                    <ul>
                        <li>Files by change intensity over time</li>
                        <li>Identifies maintenance hotspots</li>
                        <li>Helps prioritize refactoring efforts</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>Directory Health (Bottom Right):</strong>
                    <ul>
                        <li>Scatter plot of files vs average changes per file</li>
                        <li>Shows module stability and organization</li>
                        <li>Identifies problematic directories</li>
                    </ul>
                </div>

                <h4 class="section-title">Practical Applications</h4>
                <ul>
                    <li><strong>Refactoring Prioritization:</strong> Focus on files with high hotspot scores for immediate code improvement</li>
                    <li><strong>Code Review Strategy:</strong> Intensify reviews for files with high churn rates to prevent quality degradation</li>
                    <li><strong>Development Practices:</strong> Use commit size distribution to encourage smaller, more focused commits</li>
                    <li><strong>Documentation Planning:</strong> Identify areas lacking documentation coverage for knowledge management</li>
                    <li><strong>Architecture Assessment:</strong> Use directory health metrics to evaluate module organization effectiveness</li>
                    <li><strong>Technical Debt Management:</strong> Systematically address files showing signs of accumulated complexity</li>
                    <li><strong>Team Allocation:</strong> Assign experienced developers to high-maintenance files and hotspot areas</li>
                </ul>

                <h4 class="section-title">Risk Assessment Guidelines</h4>
                <div class="calculation">
                    <h5>Hotspot Score Interpretation:</h5>
                    <ul>
                        <li><strong>Low Risk (0-3):</strong> Stable files with minimal maintenance needs</li>
                        <li><strong>Medium Risk (4-6):</strong> Moderate activity requiring regular attention</li>
                        <li><strong>High Risk (7-8):</strong> Intensive maintenance areas needing careful management</li>
                        <li><strong>Critical Risk (9-10):</strong> Immediate refactoring candidates with high technical debt</li>
                    </ul>
                </div>

                <div class="calculation">
                    <h5>Churn Rate Categories:</h5>
                    <ul>
                        <li><strong>Stable (<20% churn):</strong> Well-established code with minimal changes</li>
                        <li><strong>Active (20-50% churn):</strong> Normal development activity and evolution</li>
                        <li><strong>Volatile (50-80% churn):</strong> High rewrite activity, potential design issues</li>
                        <li><strong>Unstable (>80% churn):</strong> Excessive rework indicating fundamental problems</li>
                    </ul>
                </div>

                <div class="insight-box">
                    <h4 class="section-title">Key Insights and Actions</h4>
                    <ul>
                        <li><strong>High Hotspot Score:</strong> Files needing immediate refactoring or enhanced testing coverage</li>
                        <li><strong>High Churn Rate:</strong> Investigate for design issues, unclear requirements, or architectural problems</li>
                        <li><strong>Large Commits:</strong> Encourage smaller, focused commits through development process improvements</li>
                        <li><strong>Low Documentation:</strong> Add comprehensive documentation for complex areas and domain knowledge</li>
                        <li><strong>Frequent Changes:</strong> Implement stronger code reviews and stability measures</li>
                        <li><strong>Unhealthy Directories:</strong> Consider module restructuring or architectural refactoring</li>
                        <li><strong>Pattern Recognition:</strong> Use trends to predict future maintenance needs and resource allocation</li>
                    </ul>
                </div>
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

    def _generate_file_analysis_html(self, fig: go.Figure) -> str:
        """Generate HTML content for basic file analysis report with description."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Analysis Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ padding: 30px; }}
        .description {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #007bff; }}
        .calculation {{ background: #e9ecef; padding: 15px; border-radius: 6px; margin: 10px 0; }}
        .section-title {{ color: #007bff; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }}
        .metric-formula {{ font-family: 'Courier New', monospace; background: #f1f3f4; padding: 8px; border-radius: 4px; }}
        .component-box {{ background: #ffffff; border: 1px solid #e9ecef; padding: 12px; border-radius: 6px; margin: 8px 0; }}
        .action-box {{ background: #cce5ff; border-left: 4px solid #007bff; padding: 12px; border-radius: 4px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>File Analysis Dashboard</h1>
            <p>File change patterns and repository structure analysis</p>
        </div>
        
        <div class="content">
            <div id="chart"></div>
            
            <div class="description">
                <h3 class="section-title">Dashboard Overview</h3>
                <p><strong>File Analysis</strong> provides fundamental insights into your repository's file structure, change patterns, and development activity. This analysis helps understand the codebase composition, identify areas of high activity, and assess project organization effectiveness.</p>
                
                <h4 class="section-title">Key Metrics and Calculations</h4>
                
                <div class="component-box">
                    <strong>File Change Count:</strong>
                    <div class="metric-formula">Change Count = Number of Commits Modifying File</div>
                    <p>Tracks how frequently each file has been modified, indicating development activity levels and potential maintenance hotspots.</p>
                </div>

                <div class="component-box">
                    <strong>File Type Distribution:</strong>
                    <div class="metric-formula">Type Analysis = Count by Extension / Total Files</div>
                    <p>Shows the percentage distribution of different file types in your codebase, revealing technology stack composition and diversity.</p>
                </div>

                <div class="component-box">
                    <strong>Directory File Count:</strong>
                    <div class="metric-formula">Directory Size = Total Unique Files per Directory</div>
                    <p>Measures the size and complexity of each directory, helping assess module organization and potential restructuring needs.</p>
                </div>

                <div class="component-box">
                    <strong>Change Intensity Score:</strong>
                    <div class="metric-formula">Intensity = Weighted Changes over Time Period</div>
                    <p>Evaluates the frequency and recency of modifications to identify current development focus areas and activity patterns.</p>
                </div>

                <h4 class="section-title">Dashboard Components Analysis</h4>
                
                <div class="calculation">
                    <strong>File Extensions Distribution (Top Left):</strong>
                    <ul>
                        <li>Pie chart showing proportion of different file types</li>
                        <li>Helps understand technology stack composition</li>
                        <li>Identifies dominant programming languages and frameworks</li>
                        <li>Reveals project complexity and technical diversity</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>Most Changed Files (Top Right):</strong>
                    <ul>
                        <li>Bar chart of files with highest commit counts</li>
                        <li>Shows which files receive most development attention</li>
                        <li>Helps identify potential hotspots or critical system components</li>
                        <li>Indicates files that may need additional testing or documentation</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>Directory Activity (Bottom Left):</strong>
                    <ul>
                        <li>Number of unique files per directory</li>
                        <li>Shows project structure and module organization effectiveness</li>
                        <li>Identifies largest and most complex directories</li>
                        <li>Helps assess if code organization follows best practices</li>
                    </ul>
                </div>

                <div class="calculation">
                    <strong>File Change Patterns (Bottom Right):</strong>
                    <ul>
                        <li>Timeline of file changes and modification intensity</li>
                        <li>Shows development activity patterns over time</li>
                        <li>Identifies periods of high development activity</li>
                        <li>Reveals seasonal or cyclical development patterns</li>
                    </ul>
                </div>

                <h4 class="section-title">File Analysis Insights</h4>
                
                <div class="calculation">
                    <h5>Technology Stack Assessment:</h5>
                    <ul>
                        <li><strong>Language Diversity:</strong> Balanced distribution indicates healthy multi-technology approach</li>
                        <li><strong>Dominant Types:</strong> High concentration in specific file types shows specialization</li>
                        <li><strong>Configuration Files:</strong> Proportion of config files indicates deployment complexity</li>
                        <li><strong>Documentation Ratio:</strong> Adequate documentation files support maintainability</li>
                    </ul>
                </div>

                <div class="calculation">
                    <h5>Change Pattern Interpretation:</h5>
                    <ul>
                        <li><strong>High Change Files (>50 commits):</strong> Core system components or problematic areas</li>
                        <li><strong>Medium Change Files (10-50 commits):</strong> Regular development focus areas</li>
                        <li><strong>Low Change Files (<10 commits):</strong> Stable or recently added components</li>
                        <li><strong>Unchanged Files:</strong> Potential technical debt or abandoned features</li>
                    </ul>
                </div>

                <h4 class="section-title">Practical Applications</h4>
                <ul>
                    <li><strong>Code Review Prioritization:</strong> Focus reviews on frequently changed files to maintain quality</li>
                    <li><strong>Testing Strategy:</strong> Increase test coverage for files with high change frequency</li>
                    <li><strong>Documentation Planning:</strong> Ensure critical and frequently-changed files have adequate documentation</li>
                    <li><strong>Refactoring Opportunities:</strong> Large directories or highly-changed files may benefit from restructuring</li>
                    <li><strong>Developer Onboarding:</strong> Use file change patterns to identify key areas new team members should understand</li>
                    <li><strong>Architecture Assessment:</strong> Directory structure and file distribution reflect architectural decisions</li>
                    <li><strong>Maintenance Planning:</strong> Allocate resources based on file change intensity and complexity</li>
                </ul>

                <div class="action-box">
                    <h4 class="section-title">Recommended Actions</h4>
                    <ul>
                        <li><strong>Monitor Hotspots:</strong> Frequently changed files require extra attention for stability and quality</li>
                        <li><strong>Ensure Test Coverage:</strong> Critical and high-change files need comprehensive testing strategies</li>
                        <li><strong>Review Large Directories:</strong> Directories with many files may benefit from subdivision or reorganization</li>
                        <li><strong>Balance Development Effort:</strong> Ensure development attention is appropriately distributed across modules</li>
                        <li><strong>Optimize File Organization:</strong> Consider restructuring based on change patterns and logical groupings</li>
                        <li><strong>Documentation Maintenance:</strong> Keep documentation current for files with frequent changes</li>
                        <li><strong>Performance Monitoring:</strong> Large or frequently-changed files may impact build and runtime performance</li>
                    </ul>
                </div>
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
                    row=1,
                    col=1,
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
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="red"),
        )
        fig.update_layout(
            title="Visualization Error",
            template="plotly_white",
        )
        return fig

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
            title="Dashboard Generation Error",
            template="plotly_white",
        )
        return fig
