"""
GitMetrics module - Refactored to use service architecture.
Main facade class that coordinates all analysis services.
"""

import logging
from typing import Any, Dict, Optional

import plotly.graph_objects as go

from .core import GitRepository
from .models.analysis import AnalysisConfig, AnalysisResults
from .models.repository import RepositoryInfo, RepositorySummary
from .services.advanced_analytics import AdvancedAnalytics
from .services.dashboard_generator import DashboardGenerator
from .services.data_aggregator import DataAggregator
from .services.export_service import ExportService
from .services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class GitMetrics:
    """
    Comprehensive metrics and visualization class for Git repository analysis.

    This class acts as a facade, coordinating various analysis services to provide
    a unified interface for repository insights and visualizations.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize GitMetrics with all service components.

        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo

        # Initialize core services
        self.data_aggregator = DataAggregator(git_repo)
        self.dashboard_generator = DashboardGenerator(git_repo)
        self.report_generator = ReportGenerator(git_repo)
        self.export_service = ExportService(git_repo)
        self.advanced_analytics = AdvancedAnalytics(git_repo)

        # Keep references to analyzers for backward compatibility
        self.commit_analyzer = self.data_aggregator.commit_analyzer
        self.file_analyzer = self.data_aggregator.file_analyzer
        self.contributor_analyzer = self.data_aggregator.contributor_analyzer
        self.branch_analyzer = self.data_aggregator.branch_analyzer
        self.advanced_metrics = self.data_aggregator.advanced_metrics

    # Data Aggregation Methods (delegate to DataAggregator)

    def get_enhanced_repository_summary(self) -> Dict[str, Any]:
        """Get enhanced repository summary with advanced metrics."""
        return self.data_aggregator.get_enhanced_repository_summary()

    def generate_repository_summary(self) -> Dict[str, Any]:
        """Generate basic repository summary."""
        return self.data_aggregator.generate_repository_summary()

    # Visualization Methods (delegate to DashboardGenerator)

    def create_commit_activity_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """Create commit activity dashboard."""
        return self.dashboard_generator.create_commit_activity_dashboard(save_path)

    def create_contributor_analysis_charts(self, save_path: Optional[str] = None) -> go.Figure:
        """Create contributor analysis charts."""
        return self.dashboard_generator.create_contributor_analysis_charts(save_path)

    def create_file_analysis_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """Create file analysis visualization."""
        return self.dashboard_generator.create_file_analysis_visualization(save_path)

    def create_enhanced_file_analysis_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """Create enhanced file analysis dashboard."""
        return self.dashboard_generator.create_enhanced_file_analysis_dashboard(save_path)

    # Export Methods (delegate to ExportService)

    def export_metrics_to_csv(self, output_dir: str) -> Dict[str, str]:
        """Export metrics to CSV files."""
        return self.export_service.export_metrics_to_csv(output_dir)

    # Report Generation Methods (delegate to ReportGenerator)

    def generate_all_visualizations(self, output_dir: str):
        """Generate all visualizations and save to output directory."""
        return self.report_generator.generate_all_visualizations(output_dir)

    def create_index_page_only(self, output_dir: str):
        """Create index page only."""
        # Create the main index page
        self.report_generator.create_index_page_only(output_dir)
        # Also create the CSV data page
        self.report_generator.create_csv_data_page(output_dir)
        return None

    def create_executive_summary_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create executive summary report."""
        return self.report_generator.create_executive_summary_report(save_path)

    def create_comprehensive_report(self, output_path: str) -> bool:
        """Create comprehensive HTML report."""
        return self.report_generator.create_comprehensive_report(output_path)

    # Advanced Analytics Methods (delegate to AdvancedAnalytics)

    def create_technical_debt_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """Create technical debt dashboard."""
        return self.advanced_analytics.create_technical_debt_dashboard(save_path)

    def create_repository_health_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """Create repository health dashboard."""
        return self.advanced_analytics.create_repository_health_dashboard(save_path)

    def create_predictive_maintenance_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create predictive maintenance report."""
        return self.advanced_analytics.create_predictive_maintenance_report(save_path)

    def create_velocity_forecasting_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """Create velocity forecasting dashboard."""
        return self.advanced_analytics.create_velocity_forecasting_dashboard(save_path)

    def generate_all_advanced_reports(self, output_dir: str = "advanced_reports") -> Dict[str, str]:
        """Generate all advanced reports."""
        return self.advanced_analytics.generate_all_advanced_reports(output_dir)

    # Model Integration Methods (delegate to DataAggregator)

    def get_repository_info(self) -> RepositoryInfo:
        """Get repository information as a structured model."""
        return self.data_aggregator.get_repository_info()

    def get_repository_summary(self) -> RepositorySummary:
        """Get repository summary as a structured model."""
        return self.data_aggregator.get_repository_summary()

    def get_comprehensive_analysis(self, config: Optional[AnalysisConfig] = None) -> AnalysisResults:
        """Get comprehensive analysis results."""
        return self.data_aggregator.get_comprehensive_analysis(config)
