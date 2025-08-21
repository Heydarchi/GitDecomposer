"""
Data models package for GitDecomposer.

This package contains all data classes and models used throughout
the GitDecomposer application for type-safe data structures.
"""

from .analysis import (AnalysisConfig, AnalysisResults, AnalysisSession,
                       AnalysisType, ComparisonAnalysis, Dashboard,
                       ExportOptions, Finding, Report, ReportFormat,
                       ReportSection, Severity)
from .branch import (BranchCollaboration, BranchInfo, BranchingStrategy,
                     BranchLifecycle, BranchProtection, BranchStats,
                     BranchStatus, BranchType, MergeAnalysis, MergeStrategy)
from .commit import (
    CommitFrequency, CommitInfo, CommitPattern, CommitQuality, CommitStats,
    CommitType, CommitVelocity)
from .contributor import (ActivityLevel, ContributorActivity,
                          ContributorCollaboration, ContributorExpertise,
                          ContributorInfo, ContributorRole, ContributorStats,
                          TeamDynamics)
from .file import (ChangeType, CodeOwnership, CodeQuality, DirectoryStats,
                   FileChange, FileInfo, FileNetwork, FileStats, FileType,
                   HotspotFile)
from .metrics import (CollaborationMetrics, MetricCategory, MetricsDashboard,
                      MetricTrend, MetricValue, PerformanceBenchmark,
                      ProcessMetrics, ProductivityMetrics, QualityMetrics,
                      TechnicalMetrics, TrendDirection)
# Import all data classes for easy access
from .repository import (AdvancedRepositorySummary, RepositoryInfo,
                         RepositoryMetadata, RepositorySummary)

__all__ = [
    # Repository models
    "RepositoryInfo",
    "RepositorySummary",
    "AdvancedRepositorySummary",
    "RepositoryMetadata",
    # Commit models
    "CommitType",
    "CommitInfo",
    "CommitStats",
    "CommitFrequency",
    "CommitVelocity",
    "CommitPattern",
    "CommitQuality",
    # Contributor models
    "ContributorRole",
    "ActivityLevel",
    "ContributorInfo",
    "ContributorStats",
    "ContributorActivity",
    "ContributorCollaboration",
    "ContributorExpertise",
    "TeamDynamics",
    # File models
    "FileType",
    "ChangeType",
    "FileInfo",
    "FileStats",
    "FileChange",
    "HotspotFile",
    "CodeQuality",
    "DirectoryStats",
    "FileNetwork",
    "CodeOwnership",
    # Branch models
    "BranchType",
    "BranchStatus",
    "MergeStrategy",
    "BranchInfo",
    "BranchStats",
    "MergeAnalysis",
    "BranchingStrategy",
    "BranchCollaboration",
    "BranchLifecycle",
    "BranchProtection",
    # Metrics models
    "MetricCategory",
    "TrendDirection",
    "MetricValue",
    "MetricTrend",
    "ProductivityMetrics",
    "QualityMetrics",
    "CollaborationMetrics",
    "TechnicalMetrics",
    "ProcessMetrics",
    "PerformanceBenchmark",
    "MetricsDashboard",
    # Analysis models
    "AnalysisType",
    "ReportFormat",
    "Severity",
    "AnalysisConfig",
    "Finding",
    "AnalysisResults",
    "ReportSection",
    "Report",
    "Dashboard",
    "ExportOptions",
    "AnalysisSession",
    "ComparisonAnalysis",
]
