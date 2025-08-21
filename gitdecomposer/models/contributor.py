"""
Contributor data models for GitDecomposer.

This module contains data classes representing contributor information
and contribution analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ContributorRole(Enum):
    """Types of contributor roles."""

    CORE_MAINTAINER = "core_maintainer"
    REGULAR_CONTRIBUTOR = "regular_contributor"
    OCCASIONAL_CONTRIBUTOR = "occasional_contributor"
    ONE_TIME_CONTRIBUTOR = "one_time_contributor"
    REVIEWER = "reviewer"
    COMMITTER = "committer"


class ActivityLevel(Enum):
    """Activity levels for contributors."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INACTIVE = "inactive"


@dataclass
class ContributorInfo:
    """Individual contributor information."""

    name: str
    email: str
    aliases: Set[str] = field(default_factory=set)  # other names/emails
    first_commit_date: Optional[datetime] = None
    last_commit_date: Optional[datetime] = None
    total_commits: int = 0
    total_insertions: int = 0
    total_deletions: int = 0
    files_touched: Set[str] = field(default_factory=set)
    commit_shas: List[str] = field(default_factory=list)
    role: ContributorRole = ContributorRole.ONE_TIME_CONTRIBUTOR

    @property
    def total_changes(self) -> int:
        """Get total line changes."""
        return self.total_insertions + self.total_deletions

    @property
    def net_changes(self) -> int:
        """Get net line changes."""
        return self.total_insertions - self.total_deletions

    @property
    def files_count(self) -> int:
        """Get number of unique files touched."""
        return len(self.files_touched)

    @property
    def avg_commit_size(self) -> float:
        """Get average commit size."""
        return self.total_changes / self.total_commits if self.total_commits > 0 else 0.0

    @property
    def activity_span_days(self) -> int:
        """Get activity span in days."""
        if self.first_commit_date and self.last_commit_date:
            return (self.last_commit_date - self.first_commit_date).days
        return 0

    @property
    def activity_level(self) -> ActivityLevel:
        """Determine activity level based on commits."""
        if self.total_commits >= 100:
            return ActivityLevel.VERY_HIGH
        elif self.total_commits >= 50:
            return ActivityLevel.HIGH
        elif self.total_commits >= 10:
            return ActivityLevel.MEDIUM
        elif self.total_commits >= 2:
            return ActivityLevel.LOW
        else:
            return ActivityLevel.INACTIVE

    @property
    def identifier(self) -> str:
        """Get primary identifier (name or email)."""
        return self.name if self.name else self.email

    def is_active_in_period(self, start_date: datetime, end_date: datetime) -> bool:
        """Check if contributor was active in given period."""
        return (
            self.first_commit_date
            and self.last_commit_date
            and self.first_commit_date <= end_date
            and self.last_commit_date >= start_date
        )


@dataclass
class ContributorStats:
    """Aggregated contributor statistics."""

    total_contributors: int
    active_contributors: int  # contributors with activity in last 90 days
    core_contributors: int  # top contributors (80% of commits)
    new_contributors: int  # first commit in last 90 days
    retention_rate: float  # percentage of contributors still active
    avg_commits_per_contributor: float
    avg_contribution_span_days: float
    top_contributor_commits: int
    contributor_diversity_index: float  # 0-1, higher is more diverse

    @property
    def active_ratio(self) -> float:
        """Get ratio of active to total contributors."""
        return (
            self.active_contributors / self.total_contributors
            if self.total_contributors > 0
            else 0.0
        )

    @property
    def core_ratio(self) -> float:
        """Get ratio of core to total contributors."""
        return (
            self.core_contributors / self.total_contributors if self.total_contributors > 0 else 0.0
        )

    @property
    def health_score(self) -> float:
        """Calculate contributor health score (0-100)."""
        score = 0.0

        # Active contributors (30 points)
        score += min(30, self.active_ratio * 100 * 0.3)

        # Retention rate (25 points)
        score += self.retention_rate * 25

        # New contributors (20 points)
        new_ratio = (
            self.new_contributors / self.total_contributors if self.total_contributors > 0 else 0
        )
        score += min(20, new_ratio * 100)

        # Diversity (15 points)
        score += self.contributor_diversity_index * 15

        # Core contributors balance (10 points)
        ideal_core_ratio = 0.2  # 20% core contributors is ideal
        core_balance = 1 - abs(self.core_ratio - ideal_core_ratio) / ideal_core_ratio
        score += core_balance * 10

        return max(0.0, min(100.0, score))

    @property
    def health_grade(self) -> str:
        """Get health grade."""
        score = self.health_score
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
class ContributorActivity:
    """Contributor activity patterns."""

    commits_by_month: Dict[str, int] = field(default_factory=dict)
    commits_by_weekday: Dict[str, int] = field(default_factory=dict)
    commits_by_hour: Dict[int, int] = field(default_factory=dict)
    streak_analysis: Dict[str, Any] = field(default_factory=dict)
    productivity_cycles: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def peak_activity_month(self) -> Optional[str]:
        """Get month with highest activity."""
        if not self.commits_by_month:
            return None
        return max(self.commits_by_month.items(), key=lambda x: x[1])[0]

    @property
    def preferred_weekday(self) -> Optional[str]:
        """Get preferred day of week for commits."""
        if not self.commits_by_weekday:
            return None
        return max(self.commits_by_weekday.items(), key=lambda x: x[1])[0]

    @property
    def preferred_hour(self) -> Optional[int]:
        """Get preferred hour for commits."""
        if not self.commits_by_hour:
            return None
        return max(self.commits_by_hour.items(), key=lambda x: x[1])[0]

    @property
    def is_consistent(self) -> bool:
        """Check if contributor has consistent activity."""
        if not self.commits_by_month:
            return False

        # Calculate coefficient of variation
        values = list(self.commits_by_month.values())
        if not values:
            return False

        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return False

        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance**0.5
        cv = std_dev / mean_val

        return cv < 0.5  # Less than 50% variation is considered consistent


@dataclass
class ContributorCollaboration:
    """Contributor collaboration metrics."""

    coauthored_commits: Dict[str, int] = field(default_factory=dict)  # collaborator -> count
    review_interactions: Dict[str, int] = field(default_factory=dict)  # reviewer -> count
    mentorship_relations: List[Dict[str, Any]] = field(default_factory=list)
    file_overlap_network: Dict[str, Set[str]] = field(default_factory=dict)  # contributor -> files
    communication_patterns: Dict[str, Any] = field(default_factory=dict)

    @property
    def collaboration_score(self) -> float:
        """Calculate collaboration score (0-100)."""
        score = 0.0

        # Coauthored commits (40 points)
        if self.coauthored_commits:
            unique_collaborators = len(self.coauthored_commits)
            total_coauthored = sum(self.coauthored_commits.values())
            score += min(40, (unique_collaborators * 5) + (total_coauthored * 2))

        # Review interactions (30 points)
        if self.review_interactions:
            unique_reviewers = len(self.review_interactions)
            total_reviews = sum(self.review_interactions.values())
            score += min(30, (unique_reviewers * 3) + (total_reviews * 1.5))

        # File overlap network (20 points)
        if self.file_overlap_network:
            network_size = len(self.file_overlap_network)
            score += min(20, network_size * 2)

        # Mentorship (10 points)
        if self.mentorship_relations:
            score += min(10, len(self.mentorship_relations) * 5)

        return min(100.0, score)

    @property
    def top_collaborators(self) -> List[str]:
        """Get top 5 collaborators by interaction count."""
        if not self.coauthored_commits:
            return []

        sorted_collaborators = sorted(
            self.coauthored_commits.items(), key=lambda x: x[1], reverse=True
        )
        return [name for name, _ in sorted_collaborators[:5]]


@dataclass
class ContributorExpertise:
    """Contributor expertise and specialization."""

    primary_languages: Dict[str, int] = field(default_factory=dict)  # language -> lines changed
    file_types_touched: Dict[str, int] = field(default_factory=dict)  # extension -> count
    domain_expertise: Dict[str, float] = field(default_factory=dict)  # domain -> expertise score
    specialization_areas: List[str] = field(default_factory=list)
    knowledge_breadth: float = 0.0  # 0-1, higher is broader knowledge
    knowledge_depth: float = 0.0  # 0-1, higher is deeper knowledge

    @property
    def primary_language(self) -> Optional[str]:
        """Get primary programming language."""
        if not self.primary_languages:
            return None
        return max(self.primary_languages.items(), key=lambda x: x[1])[0]

    @property
    def language_diversity(self) -> int:
        """Get number of different languages worked with."""
        return len(self.primary_languages)

    @property
    def is_specialist(self) -> bool:
        """Check if contributor is a specialist (deep knowledge)."""
        return self.knowledge_depth > 0.7

    @property
    def is_generalist(self) -> bool:
        """Check if contributor is a generalist (broad knowledge)."""
        return self.knowledge_breadth > 0.7

    @property
    def expertise_type(self) -> str:
        """Determine expertise type."""
        if self.is_specialist and self.is_generalist:
            return "Expert"
        elif self.is_specialist:
            return "Specialist"
        elif self.is_generalist:
            return "Generalist"
        else:
            return "Developing"


@dataclass
class TeamDynamics:
    """Team-level contributor dynamics."""

    contributor_network: Dict[str, Set[str]] = field(default_factory=dict)
    influence_scores: Dict[str, float] = field(default_factory=dict)
    bottleneck_contributors: List[str] = field(default_factory=list)
    knowledge_silos: List[Dict[str, Any]] = field(default_factory=list)
    onboarding_success_rate: float = 0.0
    team_cohesion_score: float = 0.0
    leadership_distribution: Dict[str, float] = field(default_factory=dict)

    @property
    def network_density(self) -> float:
        """Calculate network density (0-1)."""
        if not self.contributor_network:
            return 0.0

        total_contributors = len(self.contributor_network)
        if total_contributors <= 1:
            return 0.0

        total_connections = sum(
            len(connections) for connections in self.contributor_network.values()
        )
        max_connections = total_contributors * (total_contributors - 1)

        return total_connections / max_connections if max_connections > 0 else 0.0

    @property
    def has_bottlenecks(self) -> bool:
        """Check if team has knowledge bottlenecks."""
        return len(self.bottleneck_contributors) > 0

    @property
    def team_health_score(self) -> float:
        """Calculate overall team health score (0-100)."""
        score = 0.0

        # Team cohesion (30 points)
        score += self.team_cohesion_score * 30

        # Network density (25 points)
        score += self.network_density * 25

        # Onboarding success (20 points)
        score += self.onboarding_success_rate * 20

        # Knowledge distribution (15 points)
        if not self.knowledge_silos:
            score += 15
        else:
            score += max(0, 15 - len(self.knowledge_silos) * 3)

        # Leadership distribution (10 points)
        if self.leadership_distribution:
            # More distributed leadership is better
            values = list(self.leadership_distribution.values())
            if values:
                max_leadership = max(values)
                distribution_score = 1 - (max_leadership / sum(values)) if sum(values) > 0 else 0
                score += distribution_score * 10

        return max(0.0, min(100.0, score))
