"""
Metrics and measurement data models for GitDecomposer.

This module contains data classes representing various metrics
and measurement results for repository analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class MetricCategory(Enum):
    """Categories of metrics."""
    PRODUCTIVITY = "productivity"
    QUALITY = "quality"
    COLLABORATION = "collaboration"
    TECHNICAL = "technical"
    PROCESS = "process"
    BUSINESS = "business"


class TrendDirection(Enum):
    """Trend directions."""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class MetricValue:
    """A single metric value with metadata."""
    
    name: str
    value: float
    unit: str
    category: MetricCategory
    timestamp: datetime
    description: Optional[str] = None
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    
    @property
    def status(self) -> str:
        """Get metric status based on thresholds."""
        if self.threshold_critical is not None and self.value <= self.threshold_critical:
            return "Critical"
        elif self.threshold_warning is not None and self.value <= self.threshold_warning:
            return "Warning"
        elif self.target_value is not None:
            if abs(self.value - self.target_value) / self.target_value < 0.1:
                return "On Target"
            elif self.value > self.target_value:
                return "Above Target"
            else:
                return "Below Target"
        else:
            return "Normal"
    
    @property
    def performance_ratio(self) -> Optional[float]:
        """Get performance ratio compared to target."""
        if self.target_value is not None and self.target_value != 0:
            return self.value / self.target_value
        return None
    
    @property
    def is_healthy(self) -> bool:
        """Check if metric is in healthy range."""
        return self.status not in ["Critical", "Warning"]


@dataclass
class MetricTrend:
    """Trend analysis for a metric over time."""
    
    metric_name: str
    values: List[Tuple[datetime, float]] = field(default_factory=list)
    direction: TrendDirection = TrendDirection.STABLE
    slope: float = 0.0
    variance: float = 0.0
    correlation_coefficient: float = 0.0
    
    @property
    def latest_value(self) -> Optional[float]:
        """Get the most recent value."""
        if not self.values:
            return None
        return self.values[-1][1]
    
    @property
    def earliest_value(self) -> Optional[float]:
        """Get the earliest value."""
        if not self.values:
            return None
        return self.values[0][1]
    
    @property
    def percent_change(self) -> Optional[float]:
        """Get percentage change from earliest to latest."""
        earliest = self.earliest_value
        latest = self.latest_value
        
        if earliest is None or latest is None or earliest == 0:
            return None
        
        return ((latest - earliest) / earliest) * 100
    
    @property
    def is_improving(self) -> bool:
        """Check if trend is improving."""
        return self.direction == TrendDirection.IMPROVING
    
    @property
    def volatility_level(self) -> str:
        """Categorize volatility level."""
        if self.variance < 0.1:
            return "Low"
        elif self.variance < 0.3:
            return "Medium"
        elif self.variance < 0.5:
            return "High"
        else:
            return "Very High"


@dataclass
class ProductivityMetrics:
    """Productivity-related metrics."""
    
    commits_per_day: float
    commits_per_developer: float
    lines_changed_per_day: float
    features_delivered: int
    bugs_fixed: int
    velocity_points: float
    cycle_time_hours: float
    lead_time_hours: float
    deployment_frequency: float
    
    @property
    def productivity_score(self) -> float:
        """Calculate overall productivity score (0-100)."""
        score = 0.0
        
        # Commit frequency (20 points)
        if self.commits_per_day >= 5:
            score += 20
        elif self.commits_per_day >= 3:
            score += 15
        elif self.commits_per_day >= 1:
            score += 10
        
        # Developer efficiency (20 points)
        if self.commits_per_developer >= 2:
            score += 20
        elif self.commits_per_developer >= 1:
            score += 15
        elif self.commits_per_developer >= 0.5:
            score += 10
        
        # Feature delivery (20 points)
        if self.features_delivered >= 10:
            score += 20
        elif self.features_delivered >= 5:
            score += 15
        elif self.features_delivered >= 2:
            score += 10
        
        # Cycle time (20 points)
        if self.cycle_time_hours <= 24:
            score += 20
        elif self.cycle_time_hours <= 72:
            score += 15
        elif self.cycle_time_hours <= 168:  # 1 week
            score += 10
        
        # Deployment frequency (20 points)
        if self.deployment_frequency >= 1:  # Daily
            score += 20
        elif self.deployment_frequency >= 0.2:  # Weekly
            score += 15
        elif self.deployment_frequency >= 0.033:  # Monthly
            score += 10
        
        return max(0.0, min(100.0, score))
    
    @property
    def productivity_grade(self) -> str:
        """Get productivity grade."""
        score = self.productivity_score
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
class QualityMetrics:
    """Quality-related metrics."""
    
    defect_density: float  # defects per KLOC
    bug_fix_time_hours: float
    test_coverage: float
    code_duplication: float
    technical_debt_hours: float
    code_review_coverage: float
    static_analysis_violations: int
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0
        
        # Defect density penalty
        score -= min(30, self.defect_density * 10)
        
        # Bug fix time penalty
        if self.bug_fix_time_hours > 24:
            score -= min(20, (self.bug_fix_time_hours - 24) * 0.1)
        
        # Test coverage bonus/penalty
        if self.test_coverage >= 80:
            score += 10
        elif self.test_coverage < 50:
            score -= 20
        
        # Code duplication penalty
        score -= self.code_duplication * 0.5
        
        # Technical debt penalty
        score -= min(20, self.technical_debt_hours * 0.01)
        
        # Code review bonus
        score += self.code_review_coverage * 10
        
        # Static analysis penalty
        score -= min(15, self.static_analysis_violations * 0.1)
        
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


@dataclass
class CollaborationMetrics:
    """Collaboration-related metrics."""
    
    active_contributors: int
    contributor_diversity: float
    code_review_participation: float
    knowledge_sharing_index: float
    communication_frequency: float
    pair_programming_ratio: float
    mentorship_relationships: int
    
    @property
    def collaboration_score(self) -> float:
        """Calculate collaboration score (0-100)."""
        score = 0.0
        
        # Active contributors (25 points)
        if self.active_contributors >= 10:
            score += 25
        elif self.active_contributors >= 5:
            score += 20
        elif self.active_contributors >= 3:
            score += 15
        elif self.active_contributors >= 1:
            score += 10
        
        # Diversity (20 points)
        score += self.contributor_diversity * 20
        
        # Code review participation (20 points)
        score += self.code_review_participation * 20
        
        # Knowledge sharing (15 points)
        score += self.knowledge_sharing_index * 15
        
        # Communication (10 points)
        score += min(10, self.communication_frequency * 5)
        
        # Pair programming (10 points)
        score += self.pair_programming_ratio * 10
        
        return max(0.0, min(100.0, score))
    
    @property
    def team_health(self) -> str:
        """Get team health assessment."""
        score = self.collaboration_score
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 35:
            return "Poor"
        else:
            return "Critical"


@dataclass
class TechnicalMetrics:
    """Technical metrics."""
    
    complexity_score: float
    maintainability_index: float
    architecture_violations: int
    dependency_health: float
    performance_score: float
    security_score: float
    scalability_index: float
    
    @property
    def technical_health_score(self) -> float:
        """Calculate technical health score (0-100)."""
        score = 0.0
        
        # Maintainability (25 points)
        score += (self.maintainability_index / 100) * 25
        
        # Complexity (20 points)
        complexity_score = max(0, 100 - (self.complexity_score * 10))
        score += (complexity_score / 100) * 20
        
        # Architecture (15 points)
        arch_score = max(0, 100 - (self.architecture_violations * 5))
        score += (arch_score / 100) * 15
        
        # Dependency health (15 points)
        score += self.dependency_health * 15
        
        # Performance (10 points)
        score += (self.performance_score / 100) * 10
        
        # Security (10 points)
        score += (self.security_score / 100) * 10
        
        # Scalability (5 points)
        score += self.scalability_index * 5
        
        return max(0.0, min(100.0, score))
    
    @property
    def technical_grade(self) -> str:
        """Get technical grade."""
        score = self.technical_health_score
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Acceptable"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Critical"


@dataclass
class ProcessMetrics:
    """Process and workflow metrics."""
    
    build_success_rate: float
    deployment_success_rate: float
    rollback_rate: float
    automation_coverage: float
    compliance_score: float
    incident_response_time_hours: float
    change_failure_rate: float
    
    @property
    def process_maturity_score(self) -> float:
        """Calculate process maturity score (0-100)."""
        score = 0.0
        
        # Build success (20 points)
        score += self.build_success_rate * 20
        
        # Deployment success (20 points)
        score += self.deployment_success_rate * 20
        
        # Low rollback rate (15 points)
        score += (1 - self.rollback_rate) * 15
        
        # Automation coverage (15 points)
        score += self.automation_coverage * 15
        
        # Compliance (15 points)
        score += self.compliance_score * 15
        
        # Incident response (10 points)
        if self.incident_response_time_hours <= 1:
            score += 10
        elif self.incident_response_time_hours <= 4:
            score += 7
        elif self.incident_response_time_hours <= 24:
            score += 5
        
        # Change failure rate (5 points)
        score += (1 - self.change_failure_rate) * 5
        
        return max(0.0, min(100.0, score))
    
    @property
    def maturity_level(self) -> str:
        """Get process maturity level."""
        score = self.process_maturity_score
        if score >= 90:
            return "Optimizing"
        elif score >= 80:
            return "Managed"
        elif score >= 70:
            return "Defined"
        elif score >= 60:
            return "Repeatable"
        else:
            return "Initial"


@dataclass
class PerformanceBenchmark:
    """Performance benchmarks and comparisons."""
    
    metric_name: str
    current_value: float
    industry_average: Optional[float] = None
    industry_best: Optional[float] = None
    team_average: Optional[float] = None
    historical_best: Optional[float] = None
    percentile_rank: Optional[float] = None
    
    @property
    def vs_industry_average(self) -> Optional[str]:
        """Compare against industry average."""
        if self.industry_average is None:
            return None
        
        ratio = self.current_value / self.industry_average
        if ratio >= 1.2:
            return "Significantly Above"
        elif ratio >= 1.1:
            return "Above Average"
        elif ratio >= 0.9:
            return "Average"
        elif ratio >= 0.8:
            return "Below Average"
        else:
            return "Significantly Below"
    
    @property
    def vs_industry_best(self) -> Optional[str]:
        """Compare against industry best practice."""
        if self.industry_best is None:
            return None
        
        ratio = self.current_value / self.industry_best
        if ratio >= 0.95:
            return "World Class"
        elif ratio >= 0.8:
            return "Very Good"
        elif ratio >= 0.6:
            return "Good"
        elif ratio >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    @property
    def improvement_potential(self) -> Optional[float]:
        """Calculate improvement potential to industry best."""
        if self.industry_best is None or self.current_value >= self.industry_best:
            return 0.0
        
        return ((self.industry_best - self.current_value) / self.current_value) * 100


@dataclass
class MetricsDashboard:
    """Comprehensive metrics dashboard."""
    
    productivity: ProductivityMetrics
    quality: QualityMetrics
    collaboration: CollaborationMetrics
    technical: TechnicalMetrics
    process: ProcessMetrics
    trends: Dict[str, MetricTrend] = field(default_factory=dict)
    benchmarks: Dict[str, PerformanceBenchmark] = field(default_factory=dict)
    
    @property
    def overall_health_score(self) -> float:
        """Calculate overall repository health score."""
        scores = [
            self.productivity.productivity_score * 0.25,
            self.quality.quality_score * 0.25,
            self.collaboration.collaboration_score * 0.20,
            self.technical.technical_health_score * 0.20,
            self.process.process_maturity_score * 0.10
        ]
        return sum(scores)
    
    @property
    def health_grade(self) -> str:
        """Get overall health grade."""
        score = self.overall_health_score
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    @property
    def critical_metrics(self) -> List[str]:
        """Get list of metrics in critical state."""
        critical = []
        
        if self.productivity.productivity_score < 60:
            critical.append("Productivity")
        if self.quality.quality_score < 60:
            critical.append("Quality")
        if self.collaboration.collaboration_score < 35:
            critical.append("Collaboration")
        if self.technical.technical_health_score < 60:
            critical.append("Technical Health")
        if self.process.process_maturity_score < 60:
            critical.append("Process Maturity")
        
        return critical
    
    @property
    def improvement_priorities(self) -> List[str]:
        """Get prioritized list of improvement areas."""
        scores = [
            ("Productivity", self.productivity.productivity_score),
            ("Quality", self.quality.quality_score),
            ("Collaboration", self.collaboration.collaboration_score),
            ("Technical", self.technical.technical_health_score),
            ("Process", self.process.process_maturity_score)
        ]
        
        # Sort by score (lowest first) and return area names
        return [area for area, score in sorted(scores, key=lambda x: x[1])]
