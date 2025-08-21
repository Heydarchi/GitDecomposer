"""
Data models package for GitDecomposer.

This package contains all data classes and models used throughout
the GitDecomposer application for type-safe data structures.
"""

# Import all data classes for easy access
from .repository import (
    RepositoryInfo,
    RepositorySummary,
    AdvancedRepositorySummary,
    RepositoryMetadata
)

from .commit import (
    CommitType,
    CommitInfo,
    CommitStats,
    CommitFrequency,
    CommitVelocity,
    CommitPattern,
    CommitQuality
)

from .contributor import (
    ContributorRole,
    ActivityLevel,
    ContributorInfo,
    ContributorStats,
    ContributorActivity,
    ContributorCollaboration,
    ContributorExpertise,
    TeamDynamics
)

from .file import (
    FileType,
    ChangeType,
    FileInfo,
    FileStats,
    FileChange,
    HotspotFile,
    CodeQuality,
    DirectoryStats,
    FileNetwork,
    CodeOwnership
)

from .branch import (
    BranchType,
    BranchStatus,
    MergeStrategy,
    BranchInfo,
    BranchStats,
    MergeAnalysis,
    BranchingStrategy,
    BranchCollaboration,
    BranchLifecycle,
    BranchProtection
)

from .metrics import (
    MetricCategory,
    TrendDirection,
    MetricValue,
    MetricTrend,
    ProductivityMetrics,
    QualityMetrics,
    CollaborationMetrics,
    TechnicalMetrics,
    ProcessMetrics,
    PerformanceBenchmark,
    MetricsDashboard
)

from .analysis import (
    AnalysisType,
    ReportFormat,
    Severity,
    AnalysisConfig,
    Finding,
    AnalysisResults,
    ReportSection,
    Report,
    Dashboard,
    ExportOptions,
    AnalysisSession,
    ComparisonAnalysis
)

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
    "ComparisonAnalysis"
]
