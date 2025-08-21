"""
File and code analysis data models for GitDecomposer.

This module contains data classes representing file-level information
and code analysis results.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
from pathlib import Path


class FileType(Enum):
    """Types of files in the repository."""

    SOURCE_CODE = "source_code"
    TEST = "test"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    BUILD = "build"
    ASSET = "asset"
    DATA = "data"
    UNKNOWN = "unknown"


class ChangeType(Enum):
    """Types of changes to files."""

    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    TYPE_CHANGED = "T"
    UNMERGED = "U"
    UNKNOWN = "X"


@dataclass
class FileInfo:
    """Basic file information."""

    path: str
    name: str
    extension: str
    size_bytes: int
    file_type: FileType
    language: Optional[str] = None
    is_binary: bool = False
    encoding: Optional[str] = None

    @property
    def directory(self) -> str:
        """Get directory path."""
        return str(Path(self.path).parent)

    @property
    def depth(self) -> int:
        """Get directory depth."""
        return len(Path(self.path).parts) - 1

    @property
    def size_kb(self) -> float:
        """Get size in kilobytes."""
        return self.size_bytes / 1024

    @property
    def size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    @property
    def is_test_file(self) -> bool:
        """Check if this is a test file."""
        return (
            self.file_type == FileType.TEST
            or "test" in self.path.lower()
            or "spec" in self.path.lower()
        )

    @property
    def is_config_file(self) -> bool:
        """Check if this is a configuration file."""
        return self.file_type == FileType.CONFIGURATION


@dataclass
class FileStats:
    """File statistics and metrics."""

    path: str
    total_commits: int
    total_contributors: int
    total_insertions: int
    total_deletions: int
    first_commit_date: Optional[datetime] = None
    last_commit_date: Optional[datetime] = None
    current_lines: int = 0
    complexity_score: float = 0.0
    maintainability_index: float = 0.0

    @property
    def total_changes(self) -> int:
        """Get total line changes."""
        return self.total_insertions + self.total_deletions

    @property
    def net_changes(self) -> int:
        """Get net line changes."""
        return self.total_insertions - self.total_deletions

    @property
    def churn_rate(self) -> float:
        """Calculate churn rate (changes per commit)."""
        return self.total_changes / self.total_commits if self.total_commits > 0 else 0.0

    @property
    def stability_score(self) -> float:
        """Calculate stability score (0-100)."""
        if self.total_commits == 0:
            return 100.0

        # Lower churn rate indicates higher stability
        base_score = max(0, 100 - (self.churn_rate * 2))

        # Adjust for contributor count (more contributors = less stable)
        if self.total_contributors > 1:
            contributor_penalty = min(20, (self.total_contributors - 1) * 2)
            base_score -= contributor_penalty

        return max(0.0, min(100.0, base_score))

    @property
    def activity_level(self) -> str:
        """Categorize activity level."""
        if self.total_commits >= 50:
            return "Very High"
        elif self.total_commits >= 20:
            return "High"
        elif self.total_commits >= 10:
            return "Medium"
        elif self.total_commits >= 3:
            return "Low"
        else:
            return "Very Low"


@dataclass
class FileChange:
    """Individual file change information."""

    path: str
    change_type: ChangeType
    insertions: int
    deletions: int
    commit_sha: str
    author: str
    timestamp: datetime
    old_path: Optional[str] = None  # For renames/moves

    @property
    def total_changes(self) -> int:
        """Get total line changes."""
        return self.insertions + self.deletions

    @property
    def net_changes(self) -> int:
        """Get net line changes."""
        return self.insertions - self.deletions

    @property
    def is_major_change(self) -> bool:
        """Check if this is a major change (>50 lines)."""
        return self.total_changes > 50

    @property
    def change_ratio(self) -> float:
        """Get insertion to deletion ratio."""
        if self.deletions == 0:
            return float("inf") if self.insertions > 0 else 0.0
        return self.insertions / self.deletions


@dataclass
class HotspotFile:
    """File identified as a hotspot (frequent changes)."""

    path: str
    change_frequency: int
    unique_contributors: int
    complexity_score: float
    risk_score: float
    recent_activity: int  # changes in last 30 days

    @property
    def hotspot_category(self) -> str:
        """Categorize hotspot severity."""
        if self.risk_score >= 80:
            return "Critical"
        elif self.risk_score >= 60:
            return "High"
        elif self.risk_score >= 40:
            return "Medium"
        else:
            return "Low"

    @property
    def requires_attention(self) -> bool:
        """Check if file requires immediate attention."""
        return self.risk_score >= 70 or (
            self.change_frequency >= 20 and self.complexity_score >= 7.0
        )


@dataclass
class CodeQuality:
    """Code quality metrics for a file."""

    path: str
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    code_duplication: float  # percentage
    test_coverage: float  # percentage
    technical_debt_ratio: float
    maintainability_index: float
    code_smells: List[str] = field(default_factory=list)

    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0

        # Complexity penalties
        if self.cyclomatic_complexity > 10:
            score -= min(30, (self.cyclomatic_complexity - 10) * 3)

        if self.cognitive_complexity > 15:
            score -= min(20, (self.cognitive_complexity - 15) * 2)

        # Duplication penalty
        score -= self.code_duplication * 0.5

        # Test coverage bonus/penalty
        if self.test_coverage >= 80:
            score += 10
        elif self.test_coverage < 50:
            score -= 15

        # Technical debt penalty
        score -= self.technical_debt_ratio * 20

        # Code smells penalty
        score -= len(self.code_smells) * 2

        return max(0.0, min(100.0, score))

    @property
    def quality_grade(self) -> str:
        """Get quality grade."""
        score = self.quality_score
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    @property
    def needs_refactoring(self) -> bool:
        """Check if file needs refactoring."""
        return (
            self.cyclomatic_complexity > 15
            or self.cognitive_complexity > 20
            or self.code_duplication > 10
            or self.technical_debt_ratio > 0.3
        )


@dataclass
class DirectoryStats:
    """Statistics for a directory."""

    path: str
    total_files: int
    total_lines: int
    total_commits: int
    unique_contributors: int
    file_types: Dict[FileType, int] = field(default_factory=dict)
    languages: Dict[str, int] = field(default_factory=dict)
    avg_file_size: float = 0.0
    avg_complexity: float = 0.0

    @property
    def primary_language(self) -> Optional[str]:
        """Get primary language in directory."""
        if not self.languages:
            return None
        return max(self.languages.items(), key=lambda x: x[1])[0]

    @property
    def diversity_index(self) -> float:
        """Calculate language diversity index (0-1)."""
        if not self.languages or len(self.languages) <= 1:
            return 0.0

        total_lines = sum(self.languages.values())
        if total_lines == 0:
            return 0.0

        # Shannon diversity index
        diversity = 0.0
        for lines in self.languages.values():
            if lines > 0:
                p = lines / total_lines
                diversity -= p * (p**0.5).bit_length()  # Approximation of log2

        # Normalize to 0-1
        max_diversity = (len(self.languages) ** 0.5).bit_length()
        return diversity / max_diversity if max_diversity > 0 else 0.0


@dataclass
class FileNetwork:
    """File relationship and dependency network."""

    dependencies: Dict[str, Set[str]] = field(default_factory=dict)  # file -> dependencies
    dependents: Dict[str, Set[str]] = field(default_factory=dict)  # file -> dependents
    coupling_scores: Dict[Tuple[str, str], float] = field(default_factory=dict)
    cohesion_scores: Dict[str, float] = field(default_factory=dict)
    change_impact_map: Dict[str, Set[str]] = field(default_factory=dict)

    @property
    def highly_coupled_files(self) -> List[str]:
        """Get files with high coupling."""
        return [file for file, score in self.cohesion_scores.items() if score > 0.7]

    @property
    def central_files(self) -> List[str]:
        """Get files that are central to the network."""
        centrality_scores = {}

        for file in self.dependencies.keys():
            # Simple centrality: number of dependencies + dependents
            deps = len(self.dependencies.get(file, set()))
            dependents = len(self.dependents.get(file, set()))
            centrality_scores[file] = deps + dependents

        # Return top 10% most central files
        if not centrality_scores:
            return []

        sorted_files = sorted(centrality_scores.items(), key=lambda x: x[1], reverse=True)

        top_count = max(1, len(sorted_files) // 10)
        return [file for file, _ in sorted_files[:top_count]]

    def get_impact_radius(self, file_path: str) -> Set[str]:
        """Get all files that could be impacted by changes to given file."""
        impacted = set()
        to_check = {file_path}
        checked = set()

        while to_check:
            current = to_check.pop()
            if current in checked:
                continue

            checked.add(current)
            dependents = self.dependents.get(current, set())
            impacted.update(dependents)
            to_check.update(dependents - checked)

        return impacted


@dataclass
class CodeOwnership:
    """Code ownership analysis for files."""

    primary_owners: Dict[str, str] = field(default_factory=dict)  # file -> owner
    ownership_distribution: Dict[str, Dict[str, float]] = field(
        default_factory=dict
    )  # file -> {contributor: percentage}
    bus_factor: Dict[str, int] = field(default_factory=dict)  # file -> number of people needed
    orphaned_files: Set[str] = field(default_factory=set)
    contested_files: Set[str] = field(default_factory=set)  # files with unclear ownership

    @property
    def ownership_health_score(self) -> float:
        """Calculate ownership health score (0-100)."""
        if not self.primary_owners:
            return 0.0

        total_files = len(self.primary_owners)
        score = 100.0

        # Penalty for orphaned files
        orphan_penalty = (len(self.orphaned_files) / total_files) * 30
        score -= orphan_penalty

        # Penalty for contested files
        contest_penalty = (len(self.contested_files) / total_files) * 20
        score -= contest_penalty

        # Bonus for good bus factor distribution
        if self.bus_factor:
            avg_bus_factor = sum(self.bus_factor.values()) / len(self.bus_factor)
            if avg_bus_factor >= 2:
                score += 10

        return max(0.0, min(100.0, score))

    def get_files_by_owner(self, owner: str) -> List[str]:
        """Get all files owned by a specific contributor."""
        return [file for file, file_owner in self.primary_owners.items() if file_owner == owner]
