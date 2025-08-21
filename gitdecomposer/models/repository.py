"""
Repository data models for GitDecomposer.

This module contains data classes representing repository-level information
and summary data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class RepositoryInfo:
    """Basic repository information."""

    name: str
    path: str
    remote_url: Optional[str] = None
    current_branch: Optional[str] = None
    total_commits: int = 0
    total_branches: int = 0
    total_contributors: int = 0
    repository_size_mb: float = 0.0
    created_date: Optional[datetime] = None
    last_commit_date: Optional[datetime] = None
    default_branch: str = "main"
    is_bare: bool = False

    def __post_init__(self):
        """Validate repository info after initialization."""
        if self.total_commits < 0:
            raise ValueError("Total commits cannot be negative")
        if self.total_branches < 0:
            raise ValueError("Total branches cannot be negative")
        if self.total_contributors < 0:
            raise ValueError("Total contributors cannot be negative")


@dataclass
class RepositorySummary:
    """Basic repository analysis summary."""

    repository_info: RepositoryInfo
    commit_summary: Dict[str, Any] = field(default_factory=dict)
    contributor_summary: Dict[str, Any] = field(default_factory=dict)
    file_summary: Dict[str, Any] = field(default_factory=dict)
    branch_summary: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def total_files_analyzed(self) -> int:
        """Get total number of files analyzed."""
        return self.file_summary.get("total_files", 0)

    @property
    def most_active_contributor(self) -> Optional[str]:
        """Get the most active contributor name."""
        contributors = self.contributor_summary.get("top_contributors", [])
        return contributors[0].get("name") if contributors else None

    @property
    def analysis_period_days(self) -> int:
        """Get the analysis period in days."""
        if self.repository_info.last_commit_date and self.repository_info.created_date:
            return (self.repository_info.last_commit_date - self.repository_info.created_date).days
        return 0


@dataclass
class AdvancedRepositorySummary(RepositorySummary):
    """Advanced repository analysis summary with additional metrics."""

    advanced_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    health_metrics: Dict[str, Any] = field(default_factory=dict)
    technical_debt_metrics: Dict[str, Any] = field(default_factory=dict)
    maintainability_metrics: Dict[str, Any] = field(default_factory=dict)
    test_coverage_metrics: Dict[str, Any] = field(default_factory=dict)
    repository_health_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)

    @property
    def overall_quality_grade(self) -> str:
        """Get overall quality grade based on health score."""
        if self.repository_health_score >= 90:
            return "A+"
        elif self.repository_health_score >= 80:
            return "A"
        elif self.repository_health_score >= 70:
            return "B"
        elif self.repository_health_score >= 60:
            return "C"
        elif self.repository_health_score >= 50:
            return "D"
        else:
            return "F"

    @property
    def critical_issues_count(self) -> int:
        """Get count of critical issues."""
        return len(
            [r for r in self.recommendations if "critical" in r.lower() or "urgent" in r.lower()]
        )

    @property
    def maintainability_category(self) -> str:
        """Get maintainability category."""
        score = self.maintainability_metrics.get("overall_maintainability_score", 0)
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


@dataclass
class RepositoryConfiguration:
    """Repository configuration and settings."""

    analysis_depth: str = "full"  # full, basic, quick
    include_deleted_files: bool = True
    max_commits_to_analyze: Optional[int] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    excluded_file_patterns: List[str] = field(default_factory=list)
    excluded_directories: List[str] = field(default_factory=list)
    minimum_commit_threshold: int = 1
    cache_results: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        valid_depths = ["full", "basic", "quick"]
        if self.analysis_depth not in valid_depths:
            raise ValueError(f"Analysis depth must be one of {valid_depths}")

        if self.max_commits_to_analyze and self.max_commits_to_analyze <= 0:
            raise ValueError("Max commits to analyze must be positive")

        if self.minimum_commit_threshold < 0:
            raise ValueError("Minimum commit threshold cannot be negative")


@dataclass
class RepositoryMetadata:
    """Extended repository metadata."""

    languages_detected: Dict[str, float] = field(default_factory=dict)
    framework_hints: List[str] = field(default_factory=list)
    project_type: Optional[str] = None  # web, mobile, library, tool, etc.
    license_detected: Optional[str] = None
    documentation_files: List[str] = field(default_factory=list)
    configuration_files: List[str] = field(default_factory=list)
    test_directories: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    ci_cd_detected: List[str] = field(default_factory=list)
    package_managers: List[str] = field(default_factory=list)

    @property
    def primary_language(self) -> Optional[str]:
        """Get the primary programming language."""
        if not self.languages_detected:
            return None
        return max(self.languages_detected.items(), key=lambda x: x[1])[0]

    @property
    def has_tests(self) -> bool:
        """Check if the repository has test directories."""
        return len(self.test_directories) > 0

    @property
    def has_ci_cd(self) -> bool:
        """Check if the repository has CI/CD configuration."""
        return len(self.ci_cd_detected) > 0

    @property
    def complexity_indicator(self) -> str:
        """Get a complexity indicator based on detected tools and languages."""
        complexity_score = (
            len(self.languages_detected) * 2
            + len(self.framework_hints)
            + len(self.build_tools)
            + len(self.package_managers)
        )

        if complexity_score >= 15:
            return "High"
        elif complexity_score >= 8:
            return "Medium"
        elif complexity_score >= 3:
            return "Low"
        else:
            return "Minimal"
