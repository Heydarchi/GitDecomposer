"""
Export Service for GitDecomposer.

This service handles exporting repository metrics and analysis data
to various formats like CSV files.
"""

import logging
import os
from pathlib import Path
from typing import Dict

import pandas as pd

from ..analyzers import (
    BranchAnalyzer,
    CommitAnalyzer,
    ContributorAnalyzer,
    FileAnalyzer,
    advanced_metrics,
    legacy_advanced_metrics,
)
from ..core import GitRepository

logger = logging.getLogger(__name__)


class ExportService:
    """
    Service for exporting repository analysis data to various formats.

    This class handles all data export responsibilities previously managed
    by GitMetrics, providing clean separation of concerns.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize ExportService with analyzer instances.

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
        self.legacy_advanced_metrics = legacy_advanced_metrics.AdvancedMetrics(git_repo)

        logger.info("ExportService initialized with all analyzers")

    def export_metrics_to_csv(self, output_dir: str) -> Dict[str, str]:
        """
        Export all metrics to CSV files.

        Args:
            output_dir (str): Directory to save CSV files

        Returns:
            Dict[str, str]: Mapping of metric names to file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        exported_files = {}

        try:
            # Export basic metrics
            self._export_basic_metrics(output_dir, exported_files)

            # Export enhanced file analysis
            self._export_enhanced_file_analysis(output_dir, exported_files)

            # Export enhanced commit analysis
            self._export_enhanced_commit_analysis(output_dir, exported_files)

            # Export advanced metrics
            self._export_advanced_metrics(output_dir, exported_files)

            logger.info(f"Exported {len(exported_files)} metric files to {output_dir}")
            return exported_files

        except Exception as e:
            logger.error(f"Error exporting metrics to CSV: {e}")
            return exported_files

    def _export_basic_metrics(self, output_dir: str, exported_files: Dict[str, str]) -> None:
        """Export basic metrics from analyzers."""
        try:
            # Export contributor statistics
            contributor_stats = self.contributor_analyzer.get_contributor_statistics()
            if not contributor_stats.empty:
                contributor_path = os.path.join(output_dir, "contributor_statistics.csv")
                contributor_stats.to_csv(contributor_path, index=False)
                exported_files["contributor_statistics"] = contributor_path

            # Export commit frequency
            commit_freq = self.commit_analyzer.get_commit_frequency_by_date()
            if not commit_freq.empty:
                commit_path = os.path.join(output_dir, "commit_frequency.csv")
                commit_freq.to_csv(commit_path, index=False)
                exported_files["commit_frequency"] = commit_path

            # Export file analysis
            file_extensions = self.file_analyzer.get_file_extensions_distribution()
            if not file_extensions.empty:
                files_path = os.path.join(output_dir, "file_extensions.csv")
                file_extensions.to_csv(files_path, index=False)
                exported_files["file_extensions"] = files_path

            most_changed = self.file_analyzer.get_most_changed_files(50)
            if not most_changed.empty:
                changed_path = os.path.join(output_dir, "most_changed_files.csv")
                most_changed.to_csv(changed_path, index=False)
                exported_files["most_changed_files"] = changed_path

            # Export branch statistics
            branch_stats = self.branch_analyzer.get_branch_statistics()
            if not branch_stats.empty:
                branch_path = os.path.join(output_dir, "branch_statistics.csv")
                branch_stats.to_csv(branch_path, index=False)
                exported_files["branch_statistics"] = branch_path

        except Exception as e:
            logger.warning(f"Error exporting basic metrics: {e}")

    def _export_enhanced_file_analysis(self, output_dir: str, exported_files: Dict[str, str]) -> None:
        """Export enhanced file analysis data."""
        try:
            file_frequency = self.file_analyzer.get_file_change_frequency_analysis()
            if not file_frequency.empty:
                freq_path = os.path.join(output_dir, "file_change_frequency.csv")
                file_frequency.to_csv(freq_path, index=False)
                exported_files["file_change_frequency"] = freq_path

            hotspots = self.file_analyzer.get_file_hotspots_analysis()
            if not hotspots.empty:
                hotspots_path = os.path.join(output_dir, "file_hotspots.csv")
                hotspots.to_csv(hotspots_path, index=False)
                exported_files["file_hotspots"] = hotspots_path

            commit_size_analysis = self.file_analyzer.get_commit_size_distribution_analysis()
            if "detailed_data" in commit_size_analysis:
                commit_size_df = pd.DataFrame(commit_size_analysis["detailed_data"])
                size_path = os.path.join(output_dir, "commit_size_analysis.csv")
                commit_size_df.to_csv(size_path, index=False)
                exported_files["commit_size_analysis"] = size_path

            # Export code churn analysis
            churn_analysis = self.file_analyzer.get_code_churn_analysis()
            if not churn_analysis.get("file_churn_rates", pd.DataFrame()).empty:
                churn_path = os.path.join(output_dir, "code_churn_analysis.csv")
                churn_analysis["file_churn_rates"].to_csv(churn_path, index=False)
                exported_files["code_churn_analysis"] = churn_path

            # Export documentation coverage
            doc_coverage = self.file_analyzer.get_documentation_coverage_analysis()
            if doc_coverage.get("doc_files_list"):
                doc_df = pd.DataFrame(
                    {
                        "file_path": doc_coverage["doc_files_list"],
                        "file_type": [Path(f).suffix for f in doc_coverage["doc_files_list"]],
                    }
                )
                doc_path = os.path.join(output_dir, "documentation_files.csv")
                doc_df.to_csv(doc_path, index=False)
                exported_files["documentation_files"] = doc_path

        except Exception as e:
            logger.warning(f"Error exporting enhanced file analysis: {e}")

    def _export_enhanced_commit_analysis(self, output_dir: str, exported_files: Dict[str, str]) -> None:
        """Export enhanced commit analysis data."""
        try:
            velocity_analysis = self.commit_analyzer.get_commit_velocity_analysis()
            if not velocity_analysis.get("weekly_velocity", pd.DataFrame()).empty:
                velocity_path = os.path.join(output_dir, "commit_velocity.csv")
                velocity_analysis["weekly_velocity"].to_csv(velocity_path, index=False)
                exported_files["commit_velocity"] = velocity_path

            bug_fix_analysis = self.commit_analyzer.get_bug_fix_ratio_analysis()
            if not bug_fix_analysis.get("bug_fix_trend", pd.DataFrame()).empty:
                bug_fix_path = os.path.join(output_dir, "bug_fix_analysis.csv")
                bug_fix_analysis["bug_fix_trend"].to_csv(bug_fix_path, index=False)
                exported_files["bug_fix_analysis"] = bug_fix_path

        except Exception as e:
            logger.warning(f"Error exporting enhanced commit analysis: {e}")

    def _export_advanced_metrics(self, output_dir: str, exported_files: Dict[str, str]) -> None:
        """Export advanced metrics data."""
        try:
            # Export legacy advanced metrics
            maintainability = self.legacy_advanced_metrics.calculate_maintainability_index()
            if not maintainability.get("file_maintainability", pd.DataFrame()).empty:
                maint_path = os.path.join(output_dir, "maintainability_analysis.csv")
                maintainability["file_maintainability"].to_csv(maint_path, index=False)
                exported_files["maintainability_analysis"] = maint_path

            debt_analysis = self.legacy_advanced_metrics.calculate_technical_debt_accumulation()
            if not debt_analysis.get("debt_trend", pd.DataFrame()).empty:
                debt_path = os.path.join(output_dir, "technical_debt_analysis.csv")
                debt_analysis["debt_trend"].to_csv(debt_path, index=False)
                exported_files["technical_debt_analysis"] = debt_path

            # Export new advanced metrics
            bus_factor_analyzer = self.advanced_metrics.create_metric_analyzer("bus_factor", self.git_repo)
            bus_factor_data = bus_factor_analyzer.calculate()
            if bus_factor_data and not pd.DataFrame([bus_factor_data]).empty:
                bf_path = os.path.join(output_dir, "bus_factor_analysis.csv")
                pd.DataFrame([bus_factor_data]).to_csv(bf_path, index=False)
                exported_files["bus_factor_analysis"] = bf_path

            knowledge_dist_analyzer = self.advanced_metrics.create_metric_analyzer(
                "knowledge_distribution", self.git_repo
            )
            knowledge_dist_data = knowledge_dist_analyzer.calculate()
            if not knowledge_dist_data.get("knowledge_distribution", pd.DataFrame()).empty:
                kd_path = os.path.join(output_dir, "knowledge_distribution.csv")
                knowledge_dist_data["knowledge_distribution"].to_csv(kd_path, index=False)
                exported_files["knowledge_distribution"] = kd_path

        except Exception as e:
            logger.warning(f"Error exporting advanced metrics: {e}")

    def export_single_metric(self, metric_name: str, output_path: str) -> bool:
        """
        Export a single specific metric to a file.

        Args:
            metric_name (str): Name of the metric to export
            output_path (str): Full path where to save the file

        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Map metric names to their data sources
            metric_exporters = {
                "contributor_statistics": lambda: self.contributor_analyzer.get_contributor_statistics(),
                "commit_frequency": lambda: self.commit_analyzer.get_commit_frequency_by_date(),
                "file_extensions": lambda: self.file_analyzer.get_file_extensions_distribution(),
                "most_changed_files": lambda: self.file_analyzer.get_most_changed_files(50),
                "branch_statistics": lambda: self.branch_analyzer.get_branch_statistics(),
                "file_hotspots": lambda: self.file_analyzer.get_file_hotspots_analysis(),
                "code_churn": lambda: self.file_analyzer.get_code_churn_analysis().get(
                    "file_churn_rates", pd.DataFrame()
                ),
            }

            if metric_name not in metric_exporters:
                logger.error(f"Unknown metric name: {metric_name}")
                return False

            data = metric_exporters[metric_name]()

            if isinstance(data, pd.DataFrame) and not data.empty:
                data.to_csv(output_path, index=False)
                logger.info(f"Exported {metric_name} to {output_path}")
                return True
            else:
                logger.warning(f"No data available for metric: {metric_name}")
                return False

        except Exception as e:
            logger.error(f"Error exporting single metric {metric_name}: {e}")
            return False
