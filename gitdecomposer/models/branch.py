"""
Branch and branching strategy data models for GitDecomposer.

This module contains data classes representing branch information
and branching strategy analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class BranchType(Enum):
    """Types of branches."""

    MAIN = "main"
    DEVELOP = "develop"
    FEATURE = "feature"
    RELEASE = "release"
    HOTFIX = "hotfix"
    BUGFIX = "bugfix"
    EXPERIMENTAL = "experimental"
    PERSONAL = "personal"
    UNKNOWN = "unknown"


class BranchStatus(Enum):
    """Status of branches."""

    ACTIVE = "active"
    STALE = "stale"
    MERGED = "merged"
    ABANDONED = "abandoned"
    PROTECTED = "protected"


class MergeStrategy(Enum):
    """Merge strategies used."""

    MERGE_COMMIT = "merge_commit"
    SQUASH = "squash"
    REBASE = "rebase"
    FAST_FORWARD = "fast_forward"


@dataclass
class BranchInfo:
    """Individual branch information."""

    name: str
    branch_type: BranchType
    status: BranchStatus
    created_date: Optional[datetime] = None
    last_commit_date: Optional[datetime] = None
    creator: Optional[str] = None
    total_commits: int = 0
    unique_contributors: int = 0
    ahead_of_main: int = 0
    behind_main: int = 0
    is_protected: bool = False
    parent_branch: Optional[str] = None

    @property
    def age_days(self) -> int:
        """Get branch age in days."""
        if not self.created_date:
            return 0
        return (datetime.now() - self.created_date).days

    @property
    def last_activity_days(self) -> int:
        """Get days since last activity."""
        if not self.last_commit_date:
            return float("inf")
        return (datetime.now() - self.last_commit_date).days

    @property
    def is_stale(self) -> bool:
        """Check if branch is stale (no activity for 30+ days)."""
        return self.last_activity_days > 30

    @property
    def is_feature_branch(self) -> bool:
        """Check if this is a feature branch."""
        return self.branch_type == BranchType.FEATURE

    @property
    def divergence_level(self) -> str:
        """Categorize divergence from main."""
        total_divergence = self.ahead_of_main + self.behind_main
        if total_divergence == 0:
            return "In Sync"
        elif total_divergence <= 10:
            return "Low"
        elif total_divergence <= 50:
            return "Medium"
        elif total_divergence <= 100:
            return "High"
        else:
            return "Very High"

    @property
    def activity_level(self) -> str:
        """Categorize activity level."""
        if self.last_activity_days <= 1:
            return "Very Active"
        elif self.last_activity_days <= 7:
            return "Active"
        elif self.last_activity_days <= 14:
            return "Moderate"
        elif self.last_activity_days <= 30:
            return "Low"
        else:
            return "Inactive"


@dataclass
class BranchStats:
    """Branch statistics and metrics."""

    total_branches: int
    active_branches: int
    stale_branches: int
    merged_branches: int
    protected_branches: int
    feature_branches: int
    avg_branch_lifetime_days: float
    avg_commits_per_branch: float
    merge_frequency: float  # merges per week
    branch_creation_rate: float  # new branches per week

    @property
    def active_ratio(self) -> float:
        """Get ratio of active branches."""
        return self.active_branches / self.total_branches if self.total_branches > 0 else 0.0

    @property
    def stale_ratio(self) -> float:
        """Get ratio of stale branches."""
        return self.stale_branches / self.total_branches if self.total_branches > 0 else 0.0

    @property
    def branch_health_score(self) -> float:
        """Calculate branch health score (0-100)."""
        score = 100.0

        # Penalty for too many stale branches
        score -= self.stale_ratio * 30

        # Penalty for very long-lived branches
        if self.avg_branch_lifetime_days > 30:
            score -= min(20, (self.avg_branch_lifetime_days - 30) * 0.5)

        # Bonus for active development
        if self.active_ratio > 0.7:
            score += 10

        # Penalty for too many branches relative to activity
        if self.total_branches > 20 and self.merge_frequency < 1:
            score -= 15

        return max(0.0, min(100.0, score))

    @property
    def branching_strategy_health(self) -> str:
        """Assess branching strategy health."""
        score = self.branch_health_score
        if score >= 80:
            return "Healthy"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Needs Attention"
        else:
            return "Poor"


@dataclass
class MergeAnalysis:
    """Merge pattern analysis."""

    total_merges: int
    merge_strategies: Dict[MergeStrategy, int] = field(default_factory=dict)
    avg_merge_time_hours: float = 0.0
    conflicts_per_merge: float = 0.0
    rollback_rate: float = 0.0
    hotfix_merges: int = 0
    emergency_merges: int = 0

    @property
    def primary_merge_strategy(self) -> Optional[MergeStrategy]:
        """Get most commonly used merge strategy."""
        if not self.merge_strategies:
            return None
        return max(self.merge_strategies.items(), key=lambda x: x[1])[0]

    @property
    def merge_efficiency_score(self) -> float:
        """Calculate merge efficiency score (0-100)."""
        score = 100.0

        # Penalty for long merge times
        if self.avg_merge_time_hours > 24:
            score -= min(30, (self.avg_merge_time_hours - 24) * 2)

        # Penalty for conflicts
        score -= min(25, self.conflicts_per_merge * 10)

        # Penalty for rollbacks
        score -= self.rollback_rate * 40

        # Penalty for emergency merges
        if self.total_merges > 0:
            emergency_ratio = self.emergency_merges / self.total_merges
            score -= emergency_ratio * 20

        return max(0.0, min(100.0, score))

    @property
    def merge_quality_grade(self) -> str:
        """Get merge quality grade."""
        score = self.merge_efficiency_score
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Fair"
        elif score >= 60:
            return "Poor"
        else:
            return "Critical"


@dataclass
class BranchingStrategy:
    """Analysis of branching strategy."""

    strategy_type: str  # git-flow, github-flow, etc.
    main_branch: str
    develop_branch: Optional[str] = None
    feature_prefix: Optional[str] = None
    release_prefix: Optional[str] = None
    hotfix_prefix: Optional[str] = None
    protection_rules: Dict[str, Any] = field(default_factory=dict)
    workflow_compliance: float = 0.0  # 0-1

    @property
    def is_git_flow(self) -> bool:
        """Check if using Git Flow strategy."""
        return self.develop_branch is not None and self.feature_prefix is not None and self.release_prefix is not None

    @property
    def is_github_flow(self) -> bool:
        """Check if using GitHub Flow strategy."""
        return self.develop_branch is None and self.main_branch in ["main", "master"]

    @property
    def compliance_grade(self) -> str:
        """Get workflow compliance grade."""
        if self.workflow_compliance >= 0.9:
            return "Excellent"
        elif self.workflow_compliance >= 0.8:
            return "Good"
        elif self.workflow_compliance >= 0.7:
            return "Fair"
        elif self.workflow_compliance >= 0.6:
            return "Poor"
        else:
            return "Non-compliant"


@dataclass
class BranchCollaboration:
    """Branch collaboration patterns."""

    shared_branches: Dict[str, Set[str]] = field(default_factory=dict)  # branch -> contributors
    collaboration_frequency: Dict[str, int] = field(default_factory=dict)  # branch -> collaborations
    conflict_patterns: Dict[str, List[str]] = field(default_factory=dict)  # branch -> conflict types
    code_review_coverage: Dict[str, float] = field(default_factory=dict)  # branch -> review coverage
    pair_programming_evidence: Dict[str, int] = field(default_factory=dict)  # branch -> pair commits

    @property
    def avg_contributors_per_branch(self) -> float:
        """Get average contributors per branch."""
        if not self.shared_branches:
            return 0.0
        return sum(len(contributors) for contributors in self.shared_branches.values()) / len(self.shared_branches)

    @property
    def high_collaboration_branches(self) -> List[str]:
        """Get branches with high collaboration."""
        return [branch for branch, contributors in self.shared_branches.items() if len(contributors) >= 3]

    @property
    def collaboration_health_score(self) -> float:
        """Calculate collaboration health score (0-100)."""
        if not self.shared_branches:
            return 0.0

        score = 0.0
        total_branches = len(self.shared_branches)

        # Code review coverage (40 points)
        if self.code_review_coverage:
            avg_coverage = sum(self.code_review_coverage.values()) / len(self.code_review_coverage)
            score += avg_coverage * 40

        # Collaboration frequency (30 points)
        if self.collaboration_frequency:
            high_collab_ratio = len(self.high_collaboration_branches) / total_branches
            score += high_collab_ratio * 30

        # Conflict management (20 points)
        if self.conflict_patterns:
            avg_conflicts = sum(len(conflicts) for conflicts in self.conflict_patterns.values()) / len(
                self.conflict_patterns
            )
            conflict_score = max(0, 20 - (avg_conflicts * 2))
            score += conflict_score

        # Pair programming (10 points)
        if self.pair_programming_evidence:
            pair_ratio = len([b for b, count in self.pair_programming_evidence.items() if count > 0]) / total_branches
            score += pair_ratio * 10

        return max(0.0, min(100.0, score))


@dataclass
class BranchLifecycle:
    """Branch lifecycle analysis."""

    creation_patterns: Dict[str, int] = field(default_factory=dict)  # day_of_week -> count
    completion_times: Dict[str, float] = field(default_factory=dict)  # branch_type -> avg_days
    abandonment_rate: float = 0.0
    merge_success_rate: float = 0.0
    rebase_frequency: float = 0.0
    cherry_pick_frequency: float = 0.0

    @property
    def peak_creation_day(self) -> Optional[str]:
        """Get day of week with most branch creations."""
        if not self.creation_patterns:
            return None
        return max(self.creation_patterns.items(), key=lambda x: x[1])[0]

    @property
    def fastest_branch_type(self) -> Optional[str]:
        """Get branch type with fastest completion."""
        if not self.completion_times:
            return None
        return min(self.completion_times.items(), key=lambda x: x[1])[0]

    @property
    def lifecycle_efficiency_score(self) -> float:
        """Calculate lifecycle efficiency score (0-100)."""
        score = 100.0

        # Penalty for high abandonment
        score -= self.abandonment_rate * 50

        # Bonus for high merge success
        score += (self.merge_success_rate - 0.5) * 20 if self.merge_success_rate > 0.5 else 0

        # Penalty for very long completion times
        if self.completion_times:
            avg_completion = sum(self.completion_times.values()) / len(self.completion_times)
            if avg_completion > 14:  # 2 weeks
                score -= min(30, (avg_completion - 14) * 2)

        return max(0.0, min(100.0, score))


@dataclass
class BranchProtection:
    """Branch protection and governance."""

    protected_branches: Set[str] = field(default_factory=set)
    protection_rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    bypass_attempts: Dict[str, int] = field(default_factory=dict)  # branch -> attempts
    rule_violations: Dict[str, List[str]] = field(default_factory=dict)  # branch -> violation types
    compliance_score: float = 0.0

    @property
    def protection_coverage(self) -> float:
        """Get protection coverage ratio."""
        # This would need total branch count from context
        return len(self.protected_branches) / max(1, len(self.protected_branches))

    @property
    def governance_health(self) -> str:
        """Assess governance health."""
        if self.compliance_score >= 0.9:
            return "Excellent"
        elif self.compliance_score >= 0.8:
            return "Good"
        elif self.compliance_score >= 0.7:
            return "Adequate"
        elif self.compliance_score >= 0.6:
            return "Poor"
        else:
            return "Critical"

    @property
    def high_risk_branches(self) -> List[str]:
        """Get branches with high violation rates."""
        return [branch for branch, violations in self.rule_violations.items() if len(violations) >= 3]
