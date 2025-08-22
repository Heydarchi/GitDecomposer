"""
Report Generator Service for GitDecomposer.

This service handles generating HTML reports and comprehensive
analysis documentation.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional

import plotly.graph_objects as go

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


class ReportGenerator:
    """
    Service for generating comprehensive HTML reports and documentation.

    This class handles report generation responsibilities previously managed
    by GitMetrics, providing clean separation of concerns.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize ReportGenerator with analyzer instances.

        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self.commit_analyzer = CommitAnalyzer(git_repo)
        self.file_analyzer = FileAnalyzer(git_repo)
        self.contributor_analyzer = ContributorAnalyzer(git_repo)
        self.branch_analyzer = BranchAnalyzer(git_repo)
        # Advanced metrics can be accessed via advanced_metrics.create_metric_analyzer()
        # Initialize visualization engine with self as metrics coordinator
        self.visualization = VisualizationEngine(git_repo, self)

        logger.info("ReportGenerator initialized with all analyzers and visualization engine")

    def generate_all_visualizations(self, output_dir: str) -> Dict[str, str]:
        """
        Generate all HTML visualization reports and an index page.

        Args:
            output_dir (str): Directory to save reports

        Returns:
            Dict[str, str]: Mapping of report names to file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "HTML"), exist_ok=True)

        generated_files = {}

        try:
            # Generate individual reports
            reports = [
                ("commit_activity", "commit_analysis.html", self._create_commit_activity_dashboard),
                ("contributor_analysis", "contributor_analysis.html", self._create_contributor_analysis_charts),
                ("file_analysis", "file_analysis.html", self._create_file_analysis_visualization),
                (
                    "enhanced_file_analysis",
                    "enhanced_file_analysis.html",
                    self._create_enhanced_file_analysis_dashboard,
                ),
                ("executive_summary", "executive_summary.html", self._create_executive_summary_report),
            ]

            for report_name, filename, generator_func in reports:
                try:
                    file_path = os.path.join(output_dir, "HTML", filename)
                    generator_func(file_path)
                    generated_files[report_name] = file_path
                    logger.info(f"Generated {report_name} report: {file_path}")
                except Exception as e:
                    logger.error(f"Error generating {report_name} report: {e}")

            # Generate index page
            index_path = os.path.join(output_dir, "index.html")
            self.create_index_page_only(output_dir)
            generated_files["index"] = index_path

            logger.info(f"Generated {len(generated_files)} visualization reports in {output_dir}")
            return generated_files

        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return generated_files

    def create_index_page_only(self, output_dir: str) -> None:
        """
        Create just the index.html page that links to existing reports.

        Args:
            output_dir (str): Directory containing the reports
        """
        try:
            # Define the expected report files
            report_files = [
                ("commit_activity.html", "Commit Activity Analysis", "Analysis of commit patterns over time"),
                ("contributor_analysis.html", "Contributor Analysis", "Insights into contributor behavior"),
                ("file_analysis.html", "File Analysis", "File change patterns and statistics"),
                ("enhanced_file_analysis.html", "Enhanced File Analysis", "Advanced file metrics and hotspots"),
                ("executive_summary.html", "Executive Summary", "High-level repository overview"),
                ("technical_debt.html", "Technical Debt Analysis", "Code quality and technical debt metrics"),
                ("repository_health.html", "Repository Health", "Overall repository health indicators"),
                ("predictive_maintenance.html", "Predictive Maintenance", "Predictive analytics for code maintenance"),
                ("velocity_forecasting.html", "Velocity Forecasting", "Development velocity predictions and trends"),
            ]

            # Generate index HTML
            index_html = self._generate_index_html(output_dir, report_files)

            # Save index page
            index_path = os.path.join(output_dir, "index.html")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_html)

            logger.info(f"Index page created: {index_path}")

        except Exception as e:
            logger.error(f"Error creating index page: {e}")

    def create_csv_data_page(self, output_dir: str) -> None:
        """
        Create a CSV data page that lists all available CSV files.

        Args:
            output_dir (str): Directory containing the CSV files
        """
        try:
            # Define the CSV files and their descriptions
            csv_files = [
                ("branch_statistics.csv", "Branch Statistics", "Statistics about repository branches"),
                ("bug_fix_analysis.csv", "Bug Fix Analysis", "Analysis of bug fix patterns"),
                ("code_churn_analysis.csv", "Code Churn Analysis", "Code churn metrics and analysis"),
                ("commit_frequency.csv", "Commit Frequency", "Frequency of commits over time"),
                ("commit_size_analysis.csv", "Commit Size Analysis", "Analysis of commit sizes"),
                ("commit_velocity.csv", "Commit Velocity", "Development velocity metrics"),
                ("contributor_statistics.csv", "Contributor Statistics", "Detailed contributor metrics"),
                ("documentation_files.csv", "Documentation Files", "Documentation coverage analysis"),
                ("file_change_frequency.csv", "File Change Frequency", "How often files are changed"),
                ("file_extensions.csv", "File Extensions", "Distribution of file types"),
                ("file_hotspots.csv", "File Hotspots", "Most frequently changed files"),
                ("maintainability_analysis.csv", "Maintainability Analysis", "Code maintainability metrics"),
                ("most_changed_files.csv", "Most Changed Files", "Files with most modifications"),
                ("technical_debt_analysis.csv", "Technical Debt Analysis", "Technical debt indicators"),
                ("test_coverage_analysis.csv", "Test Coverage Analysis", "Test coverage metrics"),
            ]

            # Generate CSV data page HTML
            csv_html = self._generate_csv_data_html(output_dir, csv_files)

            # Save CSV data page
            csv_page_path = os.path.join(output_dir, "csv_data.html")
            with open(csv_page_path, "w", encoding="utf-8") as f:
                f.write(csv_html)

            logger.info(f"CSV data page created: {csv_page_path}")

        except Exception as e:
            logger.error(f"Error creating CSV data page: {e}")

    def _generate_csv_data_html(self, output_dir: str, csv_files: list) -> str:
        """
        Generate HTML content for the CSV data page.

        Args:
            output_dir (str): Output directory path
            csv_files (list): List of tuples with (filename, title, description)

        Returns:
            str: Generated HTML content
        """
        csv_dir = os.path.join(output_dir, "CSV")
        existing_files = []

        # Check which CSV files actually exist
        for filename, title, description in csv_files:
            file_path = os.path.join(csv_dir, filename)
            if os.path.exists(file_path):
                # Get file size
                file_size = os.path.getsize(file_path)
                file_size_kb = round(file_size / 1024, 1)
                existing_files.append((filename, title, description, file_size_kb))

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitDecomposer CSV Data - Repository Analysis</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3); 
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 40px; 
            border-radius: 15px 15px 0 0; 
            text-align: center; 
        }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1em; }}
        .content {{ padding: 40px; }}
        .nav-links {{ 
            margin-bottom: 30px; 
            padding: 15px; 
            background: #f8f9fa; 
            border-radius: 10px; 
            text-align: center; 
        }}
        .nav-links a {{ 
            background: #667eea; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 0 10px; 
            display: inline-block; 
            transition: background 0.3s ease; 
        }}
        .nav-links a:hover {{ background: #5a6fd8; }}
        .csv-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 20px; 
            margin-top: 30px; 
        }}
        .csv-card {{ 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 25px; 
            border-left: 4px solid #28a745; 
            transition: transform 0.3s ease; 
        }}
        .csv-card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 5px 20px rgba(0,0,0,0.1); 
        }}
        .csv-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .csv-card p {{ color: #666; margin: 0 0 15px 0; }}
        .csv-card .file-info {{ 
            font-size: 0.9em; 
            color: #888; 
            margin-bottom: 15px; 
        }}
        .csv-card a {{ 
            background: #28a745; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
            display: inline-block; 
            transition: background 0.3s ease; 
        }}
        .csv-card a:hover {{ background: #218838; }}
        .footer {{ 
            text-align: center; 
            padding: 20px; 
            color: #666; 
            border-top: 1px solid #eee; 
        }}
        .summary {{ 
            background: #e8f4f8; 
            padding: 20px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
        }}
        .summary h3 {{ margin-top: 0; color: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CSV Data Export</h1>
            <p>GitDecomposer Repository Analysis - Raw Data</p>
        </div>
        
        <div class="content">
            <div class="nav-links">
                <a href="index.html">← Back to Main Dashboard</a>
                <a href="HTML/" target="_blank">View HTML Reports</a>
            </div>
            
            <div class="summary">
                <h3>Data Export Summary</h3>
                <p>This page provides access to all the raw data generated during the repository analysis. 
                Each CSV file contains detailed metrics that can be imported into spreadsheet applications, 
                data analysis tools, or custom dashboards for further analysis.</p>
                <p><strong>Total Files Available:</strong> {len(existing_files)} CSV files</p>
            </div>

            <h2>Available CSV Data Files</h2>
            <div class="csv-grid">
"""

        # Add CSV file cards
        for filename, title, description, file_size_kb in existing_files:
            html_content += f"""
                <div class="csv-card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <div class="file-info">
                        📄 {filename} • {file_size_kb} KB
                    </div>
                    <a href="CSV/{filename}" download>Download CSV</a>
                </div>
"""

        html_content += """
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by GitDecomposer - Repository Analysis Tool</p>
            <p>Tip: Right-click on download links and select "Save As" to save files to your computer</p>
        </div>
    </div>
</body>
</html>"""

        return html_content

    def create_executive_summary_report(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create an executive summary report with key metrics.

        Args:
            save_path (str, optional): Path to save the HTML file

        Returns:
            plotly.graph_objects.Figure: Executive summary visualization
        """
        try:
            # Get summary data
            from .data_aggregator import DataAggregator

            aggregator = DataAggregator(self.git_repo)
            enhanced_summary = aggregator.get_enhanced_repository_summary()
            basic_summary = aggregator.generate_repository_summary()

            # Create executive summary visualization
            fig = self._create_executive_summary_figure(enhanced_summary, basic_summary)

            if save_path:
                # Generate full HTML report
                html_content = self._generate_executive_summary_html(enhanced_summary, basic_summary, fig)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"Executive summary report saved to {save_path}")

            return fig

        except Exception as e:
            logger.error(f"Error creating executive summary report: {e}")
            return self._create_error_figure("Error creating executive summary")

    def create_comprehensive_report(self, output_path: str) -> bool:
        """
        Create a comprehensive HTML report with all analysis results.

        Args:
            output_path (str): Path to save the comprehensive report

        Returns:
            bool: True if report was created successfully, False otherwise
        """
        try:
            # Get all analysis data
            from .data_aggregator import DataAggregator

            aggregator = DataAggregator(self.git_repo)

            enhanced_summary = aggregator.get_enhanced_repository_summary()
            basic_summary = aggregator.generate_repository_summary()

            # Create comprehensive HTML content
            html_content = self._generate_comprehensive_html(enhanced_summary, basic_summary)

            # Save the report
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Comprehensive report created: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating comprehensive report: {e}")
            return False

    def _create_commit_activity_dashboard(self, save_path: str) -> None:
        """Create commit activity dashboard."""
        from .dashboard_generator import DashboardGenerator

        dashboard = DashboardGenerator(self.git_repo)
        dashboard.create_commit_activity_dashboard(save_path)

    def _create_contributor_analysis_charts(self, save_path: str) -> None:
        """Create contributor analysis charts."""
        from .dashboard_generator import DashboardGenerator

        dashboard = DashboardGenerator(self.git_repo)
        dashboard.create_contributor_analysis_charts(save_path)

    def _create_file_analysis_visualization(self, save_path: str) -> None:
        """Create file analysis visualization."""
        from .dashboard_generator import DashboardGenerator

        dashboard = DashboardGenerator(self.git_repo)
        dashboard.create_file_analysis_visualization(save_path)

    def _create_enhanced_file_analysis_dashboard(self, save_path: str) -> None:
        """Create enhanced file analysis dashboard."""
        from .dashboard_generator import DashboardGenerator

        dashboard = DashboardGenerator(self.git_repo)
        dashboard.create_enhanced_file_analysis_dashboard(save_path)

    def _create_executive_summary_report(self, save_path: str) -> None:
        """Create executive summary report."""
        self.create_executive_summary_report(save_path)

    def _generate_index_html(self, output_dir: str, report_files: list) -> str:
        """Generate HTML content for index page."""
        # Get basic repository info
        repo_name = getattr(self.git_repo.repo, "name", "Repository")
        repo_path = str(self.git_repo.repo_path)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitDecomposer Analysis - {repo_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px 15px 0 0; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1em; }}
        .content {{ padding: 40px; }}
        .reports-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }}
        .report-card {{ background: #f8f9fa; border-radius: 10px; padding: 25px; border-left: 4px solid #667eea; transition: transform 0.3s ease; }}
        .report-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        .report-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .report-card p {{ color: #666; margin: 0 0 15px 0; }}
        .report-card a {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; transition: background 0.3s ease; }}
        .report-card a:hover {{ background: #5a6fd8; }}
        .footer {{ text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>GitDecomposer Analysis</h1>
            <p>Repository: {repo_name}</p>
            <p>Path: {repo_path}</p>
        </div>
        
        <div class="content">
            <h2>Available Reports</h2>
            <div class="reports-grid">
"""

        # Add report cards
        for filename, title, description in report_files:
            file_path = os.path.join(output_dir, "HTML", filename)
            if os.path.exists(file_path):
                html_content += f"""
                <div class="report-card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <a href="HTML/{filename}">View Report</a>
                </div>
"""

        html_content += """
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background: #e8f4f8; border-radius: 10px;">
                <h3 style="margin-top: 0; color: #0056b3;">📊 Raw Data Export</h3>
                <p style="margin-bottom: 15px;">Access detailed CSV data files for custom analysis and reporting.</p>
                <a href="csv_data.html" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; transition: background 0.3s ease;">View CSV Data Files</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by GitDecomposer - Repository Analysis Tool</p>
        </div>
    </div>
</body>
</html>"""

        return html_content

    def _create_executive_summary_figure(self, enhanced_summary: dict, basic_summary: dict) -> go.Figure:
        """Create executive summary figure."""
        # Create a simple metrics figure
        fig = go.Figure()

        # Add key metrics as annotations
        health_score = enhanced_summary.get("repository_health_score", 0)
        total_commits = basic_summary.get("commits", {}).get("total_commits", 0)
        total_contributors = basic_summary.get("contributors", {}).get("total_contributors", 0)

        fig.add_annotation(
            text=f"Repository Health Score: {health_score:.1f}/100<br>"
            f"Total Commits: {total_commits:,}<br>"
            f"Total Contributors: {total_contributors}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16),
        )

        fig.update_layout(
            title="Executive Summary",
            template="plotly_white",
        )

        return fig

    def _generate_executive_summary_html(self, enhanced_summary: dict, basic_summary: dict, fig: go.Figure) -> str:
        """Generate executive summary HTML content."""
        health_score = enhanced_summary.get("repository_health_score", 0)
        health_category = enhanced_summary.get("repository_health_category", "Unknown")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Summary</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2em; }}
        .health-score {{ font-size: 3em; font-weight: bold; margin: 10px 0; }}
        .content {{ padding: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Executive Summary</h1>
            <div class="health-score">{health_score:.1f}/100</div>
            <div>Repository Health: {health_category}</div>
        </div>
        
        <div class="content">
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value">{basic_summary.get('commits', {}).get('total_commits', 0):,}</div>
                    <div class="metric-label">Total Commits</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{basic_summary.get('contributors', {}).get('total_contributors', 0)}</div>
                    <div class="metric-label">Contributors</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{basic_summary.get('files', {}).get('total_files', 0):,}</div>
                    <div class="metric-label">Total Files</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{basic_summary.get('branches', {}).get('total_branches', 0)}</div>
                    <div class="metric-label">Branches</div>
                </div>
            </div>
            
            <div id="chart"></div>
        </div>
    </div>
    
    <script>
        var chartData = {fig.to_json()};
        Plotly.newPlot('chart', chartData.data, chartData.layout);
    </script>
</body>
</html>"""

        return html_content

    def _generate_comprehensive_html(self, enhanced_summary: dict, basic_summary: dict) -> str:
        """Generate comprehensive report HTML content."""
        # This would be a much more detailed HTML report
        # For now, return a simplified version
        return self._generate_executive_summary_html(
            enhanced_summary, basic_summary, self._create_executive_summary_figure(enhanced_summary, basic_summary)
        )

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
