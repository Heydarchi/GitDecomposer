"""
Analysis results and reporting data models for GitDecomposer.

This module contains data classes representing analysis results,
reports, and dashboard data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

from .repository import RepositoryInfo, RepositorySummary, AdvancedRepositorySummary
from .commit import CommitStats, CommitFrequency, CommitVelocity, CommitPattern, CommitQuality
from .contributor import ContributorStats, ContributorActivity, ContributorCollaboration, TeamDynamics
from .file import FileStats, DirectoryStats, HotspotFile, CodeQuality, FileNetwork, CodeOwnership
from .branch import BranchStats, MergeAnalysis, BranchingStrategy, BranchCollaboration
from .metrics import ProductivityMetrics, QualityMetrics, CollaborationMetrics, TechnicalMetrics, MetricsDashboard


class AnalysisType(Enum):
    """Types of analysis."""
    BASIC = "basic"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class ReportFormat(Enum):
    """Report output formats."""
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    MARKDOWN = "markdown"


class Severity(Enum):
    """Severity levels for findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnalysisConfig:
    """Configuration for analysis runs."""
    
    analysis_type: AnalysisType
    include_patterns: List[str] = field(default_factory=lambda: ["*"])
    exclude_patterns: List[str] = field(default_factory=list)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    max_commits: Optional[int] = None
    enable_advanced_metrics: bool = True
    enable_visualizations: bool = True
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_date_filter(self) -> bool:
        """Check if date filtering is enabled."""
        return self.date_range_start is not None or self.date_range_end is not None
    
    @property
    def is_comprehensive(self) -> bool:
        """Check if comprehensive analysis is enabled."""
        return self.analysis_type == AnalysisType.COMPREHENSIVE


@dataclass
class Finding:
    """A single analysis finding or insight."""
    
    title: str
    description: str
    severity: Severity
    category: str
    value: Optional[Union[str, float, int]] = None
    recommendation: Optional[str] = None
    impact: Optional[str] = None
    effort: Optional[str] = None  # Low, Medium, High
    related_files: List[str] = field(default_factory=list)
    related_contributors: List[str] = field(default_factory=list)
    
    @property
    def is_actionable(self) -> bool:
        """Check if finding has actionable recommendations."""
        return self.recommendation is not None
    
    @property
    def priority_score(self) -> int:
        """Calculate priority score for this finding."""
        severity_scores = {
            Severity.CRITICAL: 100,
            Severity.HIGH: 80,
            Severity.MEDIUM: 60,
            Severity.LOW: 40,
            Severity.INFO: 20
        }
        
        base_score = severity_scores.get(self.severity, 0)
        
        # Boost score if actionable
        if self.is_actionable:
            base_score += 10
        
        # Adjust for effort (lower effort = higher priority)
        if self.effort == "Low":
            base_score += 5
        elif self.effort == "High":
            base_score -= 5
        
        return base_score


@dataclass
class AnalysisResults:
    """Complete analysis results."""
    
    repository_info: RepositoryInfo
    repository_summary: RepositorySummary
    advanced_summary: Optional[AdvancedRepositorySummary] = None
    
    # Core analysis results
    commit_stats: Optional[CommitStats] = None
    commit_frequency: Optional[CommitFrequency] = None
    commit_velocity: Optional[CommitVelocity] = None
    commit_patterns: Optional[CommitPattern] = None
    commit_quality: Optional[CommitQuality] = None
    
    contributor_stats: Optional[ContributorStats] = None
    contributor_activity: Optional[ContributorActivity] = None
    contributor_collaboration: Optional[ContributorCollaboration] = None
    team_dynamics: Optional[TeamDynamics] = None
    
    file_stats: List[FileStats] = field(default_factory=list)
    directory_stats: List[DirectoryStats] = field(default_factory=list)
    hotspot_files: List[HotspotFile] = field(default_factory=list)
    code_quality: List[CodeQuality] = field(default_factory=list)
    file_network: Optional[FileNetwork] = None
    code_ownership: Optional[CodeOwnership] = None
    
    branch_stats: Optional[BranchStats] = None
    merge_analysis: Optional[MergeAnalysis] = None
    branching_strategy: Optional[BranchingStrategy] = None
    branch_collaboration: Optional[BranchCollaboration] = None
    
    # Metrics and findings
    metrics_dashboard: Optional[MetricsDashboard] = None
    findings: List[Finding] = field(default_factory=list)
    
    # Metadata
    analysis_config: Optional[AnalysisConfig] = None
    analysis_date: datetime = field(default_factory=datetime.now)
    analysis_duration_seconds: float = 0.0
    git_hash: Optional[str] = None
    
    @property
    def has_advanced_metrics(self) -> bool:
        """Check if advanced metrics are available."""
        return (self.advanced_summary is not None or
                self.metrics_dashboard is not None)
    
    @property
    def critical_findings(self) -> List[Finding]:
        """Get critical findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]
    
    @property
    def high_priority_findings(self) -> List[Finding]:
        """Get high priority findings."""
        return [f for f in self.findings if f.severity in [Severity.CRITICAL, Severity.HIGH]]
    
    @property
    def actionable_findings(self) -> List[Finding]:
        """Get actionable findings."""
        return [f for f in self.findings if f.is_actionable]
    
    @property
    def overall_health_score(self) -> Optional[float]:
        """Get overall repository health score."""
        if self.metrics_dashboard:
            return self.metrics_dashboard.overall_health_score
        return None
    
    @property
    def top_hotspots(self) -> List[HotspotFile]:
        """Get top 10 hotspot files."""
        return sorted(self.hotspot_files, key=lambda x: x.risk_score, reverse=True)[:10]
    
    def get_findings_by_category(self, category: str) -> List[Finding]:
        """Get findings for a specific category."""
        return [f for f in self.findings if f.category == category]
    
    def get_findings_by_severity(self, severity: Severity) -> List[Finding]:
        """Get findings for a specific severity."""
        return [f for f in self.findings if f.severity == severity]


@dataclass
class ReportSection:
    """A section of a report."""
    
    title: str
    content: str
    order: int
    include_in_summary: bool = True
    chart_data: Optional[Dict[str, Any]] = None
    table_data: Optional[List[Dict[str, Any]]] = None
    
    @property
    def has_visualizations(self) -> bool:
        """Check if section has visualization data."""
        return self.chart_data is not None or self.table_data is not None


@dataclass
class Report:
    """Generated analysis report."""
    
    title: str
    repository_name: str
    generated_date: datetime
    format: ReportFormat
    sections: List[ReportSection] = field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def section_count(self) -> int:
        """Get number of sections."""
        return len(self.sections)
    
    @property
    def has_charts(self) -> bool:
        """Check if report has any charts."""
        return any(section.chart_data for section in self.sections)
    
    @property
    def summary_sections(self) -> List[ReportSection]:
        """Get sections included in summary."""
        return [s for s in self.sections if s.include_in_summary]
    
    def get_section(self, title: str) -> Optional[ReportSection]:
        """Get section by title."""
        for section in self.sections:
            if section.title == title:
                return section
        return None
    
    def add_section(self, section: ReportSection) -> None:
        """Add a section to the report."""
        self.sections.append(section)
        # Re-sort by order
        self.sections.sort(key=lambda x: x.order)


@dataclass
class Dashboard:
    """Interactive dashboard data."""
    
    title: str
    repository_name: str
    last_updated: datetime
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    layout: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def widget_count(self) -> int:
        """Get number of widgets."""
        return len(self.widgets)
    
    def add_widget(self, widget_type: str, title: str, data: Dict[str, Any], 
                   position: Optional[Dict[str, int]] = None) -> None:
        """Add a widget to the dashboard."""
        widget = {
            "type": widget_type,
            "title": title,
            "data": data,
            "position": position or {"x": 0, "y": 0, "w": 6, "h": 4}
        }
        self.widgets.append(widget)


@dataclass
class ExportOptions:
    """Options for exporting analysis results."""
    
    formats: List[ReportFormat] = field(default_factory=lambda: [ReportFormat.HTML])
    include_raw_data: bool = False
    include_visualizations: bool = True
    compress_output: bool = False
    output_directory: Optional[str] = None
    filename_prefix: Optional[str] = None
    
    @property
    def output_formats(self) -> List[str]:
        """Get output format strings."""
        return [fmt.value for fmt in self.formats]
    
    @property
    def multiple_formats(self) -> bool:
        """Check if multiple formats are requested."""
        return len(self.formats) > 1


@dataclass
class AnalysisSession:
    """Analysis session tracking."""
    
    session_id: str
    start_time: datetime
    repository_path: str
    config: AnalysisConfig
    results: Optional[AnalysisResults] = None
    reports: List[Report] = field(default_factory=list)
    dashboard: Optional[Dashboard] = None
    end_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get session duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_completed(self) -> bool:
        """Check if session is completed."""
        return self.end_time is not None
    
    @property
    def has_errors(self) -> bool:
        """Check if session had errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if session had warnings."""
        return len(self.warnings) > 0
    
    @property
    def status(self) -> str:
        """Get session status."""
        if not self.is_completed:
            return "Running"
        elif self.has_errors:
            return "Failed"
        elif self.has_warnings:
            return "Completed with Warnings"
        else:
            return "Completed Successfully"
    
    def add_error(self, error: str) -> None:
        """Add an error to the session."""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the session."""
        self.warnings.append(warning)
    
    def complete(self) -> None:
        """Mark session as completed."""
        self.end_time = datetime.now()


@dataclass
class ComparisonAnalysis:
    """Comparison between two analysis results."""
    
    baseline_results: AnalysisResults
    current_results: AnalysisResults
    comparison_date: datetime = field(default_factory=datetime.now)
    
    # Computed differences
    commit_growth: Optional[float] = None
    contributor_growth: Optional[float] = None
    quality_change: Optional[float] = None
    complexity_change: Optional[float] = None
    
    @property
    def time_span_days(self) -> int:
        """Get time span between analyses."""
        baseline_date = self.baseline_results.analysis_date
        current_date = self.current_results.analysis_date
        return (current_date - baseline_date).days
    
    @property
    def has_improvement(self) -> bool:
        """Check if there's overall improvement."""
        baseline_score = self.baseline_results.overall_health_score or 0
        current_score = self.current_results.overall_health_score or 0
        return current_score > baseline_score
    
    @property
    def improvement_percentage(self) -> Optional[float]:
        """Get improvement percentage."""
        baseline_score = self.baseline_results.overall_health_score
        current_score = self.current_results.overall_health_score
        
        if baseline_score and current_score and baseline_score > 0:
            return ((current_score - baseline_score) / baseline_score) * 100
        return None
