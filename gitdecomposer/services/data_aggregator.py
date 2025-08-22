"""
Data Aggregator Service for GitDecomposer.

This service handles data collection and aggregation from various analyzers,
providing comprehensive repository summaries and metrics.
"""

import logging
from typing import Any, Dict, Optional

from ..analyzers import (
    AdvancedMetrics,
    BranchAnalyzer,
    CommitAnalyzer,
    ContributorAnalyzer,
    FileAnalyzer,
)
from ..core import GitRepository
from ..models.analysis import AnalysisConfig, AnalysisResults, AnalysisType
from ..models.repository import AdvancedRepositorySummary, RepositoryInfo, RepositorySummary

logger = logging.getLogger(__name__)


class DataAggregator:
    """
    Service for aggregating data from various analyzers and generating repository summaries.

    This class consolidates data collection responsibilities previously handled
    by GitMetrics, providing clean separation of concerns.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize DataAggregator with analyzer instances.

        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self.commit_analyzer = CommitAnalyzer(git_repo)
        self.file_analyzer = FileAnalyzer(git_repo)
        self.contributor_analyzer = ContributorAnalyzer(git_repo)
        self.branch_analyzer = BranchAnalyzer(git_repo)
        self.advanced_metrics = AdvancedMetrics(git_repo)

        logger.info("DataAggregator initialized with all analyzers")

    def get_enhanced_repository_summary(self) -> Dict[str, Any]:
        """
        Generate an enhanced repository summary with new analytical capabilities.

        Returns:
            Dict[str, Any]: Enhanced repository analysis summary
        """
        try:
            # Get basic summary
            basic_summary = self.generate_repository_summary()

            # Add new analytical capabilities
            velocity_analysis = self.commit_analyzer.get_commit_velocity_analysis()
            bug_fix_analysis = self.commit_analyzer.get_bug_fix_ratio_analysis()
            churn_analysis = self.file_analyzer.get_code_churn_analysis()
            doc_coverage = self.file_analyzer.get_documentation_coverage_analysis()
            maintainability = self.advanced_metrics.calculate_maintainability_index()
            technical_debt = self.advanced_metrics.calculate_technical_debt_accumulation()
            test_ratio = self.advanced_metrics.calculate_test_to_code_ratio()

            # Enhance the summary with new metrics
            enhanced_summary = basic_summary.copy()

            # Add advanced metrics section
            enhanced_summary["advanced_metrics"] = {
                "commit_velocity": {
                    "avg_commits_per_week": velocity_analysis.get("avg_commits_per_week", 0),
                    "velocity_trend": velocity_analysis.get("velocity_trend", "unknown"),
                    "velocity_change_percentage": velocity_analysis.get("velocity_change_percentage", 0),
                },
                "code_quality": {
                    "bug_fix_ratio": bug_fix_analysis.get("bug_fix_ratio", 0),
                    "code_churn_rate": churn_analysis.get("overall_churn_rate", 0),
                    "maintainability_score": maintainability.get("overall_maintainability_score", 0),
                    "technical_debt_rate": technical_debt.get("debt_accumulation_rate", 0),
                },
                "coverage_metrics": {
                    "documentation_ratio": doc_coverage.get("documentation_ratio", 0),
                    "test_to_code_ratio": test_ratio.get("test_to_code_ratio", 0),
                    "test_coverage_percentage": test_ratio.get("test_coverage_percentage", 0),
                },
            }

            # Add recommendations
            all_recommendations = []
            all_recommendations.extend(maintainability.get("recommendations", []))
            all_recommendations.extend(doc_coverage.get("recommendations", []))
            all_recommendations.extend(test_ratio.get("recommendations", []))

            enhanced_summary["enhanced_recommendations"] = all_recommendations

            # Calculate overall health score (0-100)
            health_factors = self._calculate_health_factors(
                maintainability, test_ratio, doc_coverage, bug_fix_analysis, technical_debt, churn_analysis
            )

            overall_health_score = sum(health_factors.values()) / len(health_factors) * 100
            enhanced_summary["repository_health_score"] = overall_health_score

            # Health category
            enhanced_summary["repository_health_category"] = self._get_health_category(overall_health_score)

            logger.info(f"Generated enhanced repository summary with health score: {overall_health_score:.1f}")
            return enhanced_summary

        except Exception as e:
            logger.error(f"Error generating enhanced repository summary: {e}")
            # Fallback to basic summary with error handling
            try:
                return self.generate_repository_summary()
            except Exception as fallback_error:
                logger.error(f"Error in fallback basic summary: {fallback_error}")
                return {"error": f"Enhanced summary failed: {e}, Basic summary failed: {fallback_error}"}

    def generate_repository_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive repository summary.

        Returns:
            Dict[str, Any]: Complete repository analysis summary
        """
        try:
            # Get basic repository stats
            logger.info("Starting repository summary generation...")
            try:
                repo_stats = self.git_repo.get_repository_stats()
                logger.info(f"Repository stats retrieved: {type(repo_stats)}")
            except Exception as e:
                logger.warning(f"Error getting repository stats: {e}")
                repo_stats = {}

            if not repo_stats:
                logger.warning("Repository stats is empty, using defaults")
                repo_stats = {
                    "total_commits": 0,
                    "total_contributors": 0,
                    "first_commit_date": "Unknown",
                    "last_commit_date": "Unknown",
                    "repository_age_days": 0,
                }

            # Get analysis data from each analyzer
            try:
                commit_data = self.commit_analyzer.get_commit_frequency_by_date()
                commit_stats = self.commit_analyzer.get_commit_stats()
            except Exception as e:
                logger.warning(f"Error getting commit data: {e}")
                commit_data = {}
                commit_stats = {}

            try:
                contributor_data = self.contributor_analyzer.get_contributor_statistics()
                top_contributors = self.contributor_analyzer.get_top_contributors(top_n=10)
            except Exception as e:
                logger.warning(f"Error getting contributor data: {e}")
                contributor_data = {}
                top_contributors = []

            try:
                file_data = self.file_analyzer.get_most_changed_files()
                hotspots = self.file_analyzer.get_file_hotspots_analysis()
            except Exception as e:
                logger.warning(f"Error getting file data: {e}")
                file_data = {}
                hotspots = []

            try:
                branch_data = self.branch_analyzer.get_branch_statistics()
                active_branches = self.branch_analyzer.get_branch_statistics()
            except Exception as e:
                logger.warning(f"Error getting branch data: {e}")
                branch_data = {}
                active_branches = []

            # Compile summary
            summary = {
                "repository": {
                    "name": getattr(self.git_repo.repo, "name", "Unknown"),
                    "path": str(self.git_repo.repo_path),
                    "total_commits": repo_stats.get("total_commits", 0),
                    "total_contributors": repo_stats.get("total_contributors", 0),
                    "first_commit_date": repo_stats.get("first_commit_date", "Unknown"),
                    "last_commit_date": repo_stats.get("last_commit_date", "Unknown"),
                    "repository_age_days": repo_stats.get("repository_age_days", 0),
                },
                "commits": {
                    "total_commits": repo_stats.get("total_commits", 0),
                    "avg_commits_per_day": (
                        getattr(commit_stats, "avg_commit_size", 0) / 7
                        if hasattr(commit_stats, "avg_commit_size")
                        else 0
                    ),
                    "avg_commits_per_week": (
                        getattr(commit_stats, "total_commits", 0) / 52 if hasattr(commit_stats, "total_commits") else 0
                    ),
                    "avg_commits_per_month": (
                        getattr(commit_stats, "total_commits", 0) / 12 if hasattr(commit_stats, "total_commits") else 0
                    ),
                    "commit_frequency_data": commit_data,
                },
                "contributors": {
                    "total_contributors": len(top_contributors),
                    "active_contributors": contributor_data.get("active_contributors", 0),
                    "top_contributors": top_contributors[:5],  # Top 5 for summary
                    "contributor_distribution": contributor_data.get("contribution_distribution", {}),
                },
                "files": {
                    "total_files": file_data.get("total_files", 0),
                    "total_lines": file_data.get("total_lines", 0),
                    "file_types": file_data.get("file_extensions", {}),
                    "hotspots": hotspots[:5],  # Top 5 hotspots
                },
                "branches": {
                    "total_branches": branch_data.get("total_branches", 0),
                    "active_branches": len(active_branches),
                    "default_branch": branch_data.get("default_branch", "main"),
                    "branch_activity": active_branches[:5],  # Top 5 active branches
                },
            }

            logger.info("Repository summary generation completed successfully")
            return summary

        except Exception as e:
            logger.error(f"Error generating repository summary: {e}")
            return {
                "error": f"Summary generation failed: {e}",
                "repository": {"name": "Unknown", "path": str(self.git_repo.repo_path)},
            }

    def get_repository_info(self) -> RepositoryInfo:
        """
        Get basic repository information as a structured model.

        Returns:
            RepositoryInfo: Basic repository information
        """
        try:
            repo_stats = self.git_repo.get_repository_stats()

            return RepositoryInfo(
                name=getattr(self.git_repo.repo, "name", "Unknown"),
                path=str(self.git_repo.repo_path),
                total_commits=repo_stats.get("total_commits", 0),
                total_contributors=repo_stats.get("total_contributors", 0),
                created_date=repo_stats.get("first_commit_date"),
                last_commit_date=repo_stats.get("last_commit_date"),
            )
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return RepositoryInfo(
                name="Unknown",
                path=str(self.git_repo.repo_path),
                total_commits=0,
                total_contributors=0,
            )

    def get_repository_summary(self) -> RepositorySummary:
        """
        Get comprehensive repository summary as a structured model.

        Returns:
            RepositorySummary: Comprehensive repository summary
        """
        try:
            summary_data = self.generate_repository_summary()
            # Only use summary_data if it doesn't contain error
            if "error" not in summary_data:
                return RepositorySummary(
                    repository_info=self.get_repository_info(),
                    commit_summary=summary_data.get("commits", {}),
                    contributor_summary=summary_data.get("contributors", {}),
                    file_summary=summary_data.get("files", {}),
                    branch_summary=summary_data.get("branches", {}),
                )
            else:
                raise Exception(summary_data["error"])
        except Exception as e:
            logger.error(f"Error creating repository summary model: {e}")
            # Return minimal summary on error
            return RepositorySummary(
                repository_info=self.get_repository_info(),
                commit_summary={},
                contributor_summary={},
                file_summary={},
                branch_summary={},
            )

    def get_comprehensive_analysis(self, config: Optional[AnalysisConfig] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis based on configuration.

        Args:
            config: Analysis configuration (optional)

        Returns:
            Dict[str, Any]: Complete analysis results
        """
        if config is None:
            config = AnalysisConfig(analysis_type=AnalysisType.COMPREHENSIVE)

        try:
            results = {}

            # Run analyses based on configuration
            if config.analysis_type in [AnalysisType.COMPREHENSIVE, AnalysisType.ADVANCED]:
                results["commit_analysis"] = self.commit_analyzer.get_commit_stats()
                results["contributor_analysis"] = self.contributor_analyzer.get_contributor_statistics()
                results["file_analysis"] = self.file_analyzer.get_most_changed_files()
                results["branch_analysis"] = self.branch_analyzer.get_branch_statistics()
            elif config.analysis_type == AnalysisType.BASIC:
                results["commit_analysis"] = self.commit_analyzer.get_commit_stats()
                results["contributor_analysis"] = self.contributor_analyzer.get_contributor_statistics()
            # For CUSTOM, handle via custom_metrics if needed

            return {
                "config": config,
                "results": results,
                "summary": self.get_repository_summary(),
            }
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {
                "config": config,
                "results": {"error": str(e)},
                "summary": self.get_repository_summary(),
            }

    def _calculate_health_factors(
        self, maintainability, test_ratio, doc_coverage, bug_fix_analysis, technical_debt, churn_analysis
    ) -> Dict[str, float]:
        """Calculate health factors for repository health score."""
        return {
            "maintainability": maintainability.get("overall_maintainability_score", 0) / 100,
            "test_coverage": min(test_ratio.get("test_coverage_percentage", 0) / 100, 1.0),
            "documentation": min(doc_coverage.get("documentation_ratio", 0) / 30, 1.0),  # 30% doc ratio = perfect
            "low_bug_ratio": max(0, (20 - bug_fix_analysis.get("bug_fix_ratio", 20)) / 20),  # Lower bug ratio is better
            "low_debt": max(0, (20 - technical_debt.get("debt_accumulation_rate", 20)) / 20),  # Lower debt is better
            "low_churn": max(0, (50 - churn_analysis.get("overall_churn_rate", 50)) / 50),  # Lower churn is better
        }

    def _get_health_category(self, score: float) -> str:
        """Get health category based on score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"
