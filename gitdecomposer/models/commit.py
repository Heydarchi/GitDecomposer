"""
Commit data models for GitDecomposer.

This module contains data classes representing commit-level information
and analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CommitType(Enum):
    """Types of commits based on conventional commit patterns."""

    FEATURE = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    MERGE = "merge"
    INITIAL = "initial"
    OTHER = "other"


@dataclass
class CommitInfo:
    """Individual commit information."""

    sha: str
    message: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    authored_date: datetime
    committed_date: datetime
    parent_shas: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    is_merge: bool = False
    commit_type: CommitType = CommitType.OTHER

    @property
    def total_changes(self) -> int:
        """Get total number of line changes."""
        return self.insertions + self.deletions

    @property
    def net_changes(self) -> int:
        """Get net line changes (insertions - deletions)."""
        return self.insertions - self.deletions

    @property
    def files_touched(self) -> int:
        """Get number of files changed in this commit."""
        return len(self.files_changed)

    @property
    def short_sha(self) -> str:
        """Get short SHA (first 7 characters)."""
        return self.sha[:7] if len(self.sha) >= 7 else self.sha

    @property
    def short_message(self) -> str:
        """Get short commit message (first line only)."""
        return self.message.split("\n")[0] if self.message else ""

    def is_same_author_committer(self) -> bool:
        """Check if author and committer are the same person."""
        return self.author_name == self.committer_name and self.author_email == self.committer_email


@dataclass
class CommitStats:
    """Statistics for a collection of commits."""

    total_commits: int
    total_insertions: int
    total_deletions: int
    total_files_changed: int
    merge_commits: int
    unique_authors: int
    unique_committers: int
    first_commit_date: Optional[datetime] = None
    last_commit_date: Optional[datetime] = None
    avg_commit_size: float = 0.0
    avg_files_per_commit: float = 0.0
    commit_types: Dict[CommitType, int] = field(default_factory=dict)

    @property
    def total_changes(self) -> int:
        """Get total line changes."""
        return self.total_insertions + self.total_deletions

    @property
    def net_changes(self) -> int:
        """Get net line changes."""
        return self.total_insertions - self.total_deletions

    @property
    def merge_ratio(self) -> float:
        """Get ratio of merge commits to total commits."""
        return self.merge_commits / self.total_commits if self.total_commits > 0 else 0.0

    @property
    def activity_span_days(self) -> int:
        """Get span of activity in days."""
        if self.first_commit_date and self.last_commit_date:
            return (self.last_commit_date - self.first_commit_date).days
        return 0

    @property
    def commits_per_day(self) -> float:
        """Get average commits per day."""
        span = self.activity_span_days
        return self.total_commits / span if span > 0 else 0.0


@dataclass
class CommitFrequency:
    """Commit frequency analysis data."""

    daily_frequencies: Dict[str, int] = field(default_factory=dict)  # date -> count
    hourly_frequencies: Dict[int, int] = field(default_factory=dict)  # hour -> count
    weekday_frequencies: Dict[str, int] = field(default_factory=dict)  # weekday -> count
    monthly_frequencies: Dict[str, int] = field(default_factory=dict)  # month -> count

    @property
    def peak_hour(self) -> int:
        """Get the hour with most commits."""
        if not self.hourly_frequencies:
            return 0
        return max(self.hourly_frequencies.items(), key=lambda x: x[1])[0]

    @property
    def peak_weekday(self) -> str:
        """Get the weekday with most commits."""
        if not self.weekday_frequencies:
            return "Unknown"
        return max(self.weekday_frequencies.items(), key=lambda x: x[1])[0]

    @property
    def busiest_day(self) -> Optional[str]:
        """Get the date with most commits."""
        if not self.daily_frequencies:
            return None
        return max(self.daily_frequencies.items(), key=lambda x: x[1])[0]

    @property
    def total_active_days(self) -> int:
        """Get total number of days with commits."""
        return len(self.daily_frequencies)


@dataclass
class CommitVelocity:
    """Commit velocity and trend analysis."""

    avg_commits_per_week: float
    avg_commits_per_month: float
    current_velocity: float
    trend: str  # "increasing", "decreasing", "stable"
    velocity_stability: float  # 0-1, higher is more stable
    seasonal_patterns: Dict[str, Any] = field(default_factory=dict)
    sprint_analysis: Dict[str, Any] = field(default_factory=dict)

    @property
    def velocity_category(self) -> str:
        """Categorize velocity level."""
        if self.avg_commits_per_week >= 50:
            return "Very High"
        elif self.avg_commits_per_week >= 25:
            return "High"
        elif self.avg_commits_per_week >= 10:
            return "Medium"
        elif self.avg_commits_per_week >= 3:
            return "Low"
        else:
            return "Very Low"

    @property
    def trend_indicator(self) -> str:
        """Get trend indicator symbol."""
        return {"increasing": "up", "decreasing": "down", "stable": "stable"}.get(self.trend, "unknown")

    @property
    def is_consistent(self) -> bool:
        """Check if velocity is consistent (stable)."""
        return self.velocity_stability >= 0.7


@dataclass
class CommitPattern:
    """Commit pattern analysis."""

    message_patterns: Dict[str, int] = field(default_factory=dict)
    size_patterns: Dict[str, int] = field(default_factory=dict)  # small, medium, large
    time_patterns: Dict[str, Any] = field(default_factory=dict)
    author_patterns: Dict[str, Any] = field(default_factory=dict)
    file_patterns: Dict[str, int] = field(default_factory=dict)

    @property
    def most_common_message_pattern(self) -> Optional[str]:
        """Get most common commit message pattern."""
        if not self.message_patterns:
            return None
        return max(self.message_patterns.items(), key=lambda x: x[1])[0]

    @property
    def most_common_size(self) -> Optional[str]:
        """Get most common commit size."""
        if not self.size_patterns:
            return None
        return max(self.size_patterns.items(), key=lambda x: x[1])[0]


@dataclass
class CommitQuality:
    """Commit quality metrics."""

    avg_message_length: float
    messages_with_body: int
    total_messages: int
    conventional_commits: int
    descriptive_messages: int
    typos_detected: int
    empty_messages: int

    @property
    def message_quality_score(self) -> float:
        """Calculate message quality score (0-100)."""
        if self.total_messages == 0:
            return 0.0

        score = 0.0

        # Points for having body text
        score += (self.messages_with_body / self.total_messages) * 30

        # Points for conventional commits
        score += (self.conventional_commits / self.total_messages) * 25

        # Points for descriptive messages
        score += (self.descriptive_messages / self.total_messages) * 25

        # Penalty for empty messages
        score -= (self.empty_messages / self.total_messages) * 20

        # Penalty for typos
        score -= (self.typos_detected / self.total_messages) * 10

        # Bonus for good average length (around 50-72 characters)
        if 50 <= self.avg_message_length <= 72:
            score += 10

        return max(0.0, min(100.0, score))

    @property
    def quality_grade(self) -> str:
        """Get quality grade."""
        score = self.message_quality_score
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
