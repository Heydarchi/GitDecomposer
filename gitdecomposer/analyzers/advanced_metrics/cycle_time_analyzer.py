"""
Cycle Time Distribution Analyzer - Analyzes feature delivery time patterns
for better planning.
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .base import BaseMetricAnalyzer


class CycleTimeAnalyzer(BaseMetricAnalyzer):
    """
    Analyzes cycle time distribution for feature delivery.

    Cycle time is measured from the first commit of a feature to its
    completion (merge), providing insights for delivery planning.
    """

    def __init__(self, repository):
        super().__init__(repository)

    def get_metric_name(self) -> str:
        return "Cycle Time Distribution"

    def get_description(self) -> str:
        return (
            "Analyzes feature delivery time patterns from first commit "
            "to completion for better planning and estimation."
        )

    def calculate(self, branch_patterns: List[str] = None, lookback_months: int = 6) -> Dict[str, Any]:
        """
        Analyze cycle time distribution.

        Args:
            branch_patterns: List of branch patterns to analyze
            lookback_months: How many months back to analyze

        Returns:
            Dictionary containing cycle time analysis results
        """
        if branch_patterns is None:
            branch_patterns = ["feature/*", "bugfix/*", "hotfix/*"]

        cycle_times = self._collect_cycle_times(branch_patterns, lookback_months)

        if not cycle_times:
            return {"cycle_times": [], "statistics": {}, "error": "No completed features found for cycle time analysis"}

        statistics_analysis = self._calculate_distribution_statistics(cycle_times)
        planning_recommendations = self._generate_planning_recommendations(statistics_analysis)

        return {
            "cycle_times": cycle_times,
            "statistics": statistics_analysis,
            "planning_recommendations": planning_recommendations,
            "recommendations": self.get_recommendations(statistics_analysis),
        }

    def _collect_cycle_times(self, branch_patterns: List[str], lookback_months: int) -> List[Dict[str, Any]]:
        """Collect cycle times from completed features."""
        cycle_times = []
        since_date = datetime.now() - timedelta(days=30 * lookback_months)

        # Get merged branches (simplified implementation)
        branches = self.repository.get_branches()

        for branch in branches:
            # Handle branch as string or object
            if isinstance(branch, str):
                branch_name = branch
            elif hasattr(branch, 'name'):
                branch_name = branch.name
            else:
                # Skip if we can't determine branch name
                continue
                
            # Skip main branches
            if branch_name in ["main", "master", "develop"]:
                continue

            # Check if branch matches any pattern
            matches_pattern = False
            for pattern in branch_patterns:
                if pattern.endswith("*") and branch_name.startswith(pattern[:-1]):
                    matches_pattern = True
                    break
                elif branch_name == pattern:
                    matches_pattern = True
                    break

            if not matches_pattern:
                continue

            try:
                cycle_time_data = self._calculate_branch_cycle_time(branch, branch_name, since_date)
                if cycle_time_data:
                    cycle_times.append(cycle_time_data)
            except Exception as e:
                # Skip branches that can't be analyzed
                continue

        return cycle_times

    def _calculate_branch_cycle_time(self, branch, branch_name: str, since_date: datetime) -> Dict[str, Any]:
        """Calculate cycle time for a single branch."""
        commits = list(self.repository.get_all_commits(branch=branch_name))

        if len(commits) < 1:
            return None

        # Sort commits by date
        commits.sort(key=lambda c: c.committed_datetime)

        # Filter commits after since_date
        recent_commits = [c for c in commits if c.committed_datetime >= since_date]
        if not recent_commits:
            return None

        first_commit = recent_commits[0]

        # Find merge commit (simplified - in reality would track actual merges)
        merge_commit = self._find_merge_commit(branch)

        if merge_commit and merge_commit.committed_datetime >= since_date:
            cycle_time_hours = (
                merge_commit.committed_datetime - first_commit.committed_datetime
            ).total_seconds() / 3600
        else:
            # Use last commit if no merge commit found
            last_commit = recent_commits[-1]
            cycle_time_hours = (last_commit.committed_datetime - first_commit.committed_datetime).total_seconds() / 3600

        # Skip very short cycles (likely not real features)
        if cycle_time_hours < 1:
            return None

        # Calculate complexity indicators
        files_changed = set()
        total_lines_changed = 0

        for commit in recent_commits:
            files_changed.update(commit.stats.files.keys())
            total_lines_changed += commit.stats.total["insertions"] + commit.stats.total["deletions"]

        complexity_indicator = len(recent_commits) * len(files_changed)

        return {
            "branch": branch_name,
            "cycle_time_hours": cycle_time_hours,
            "cycle_time_days": cycle_time_hours / 24,
            "commits": len(recent_commits),
            "files_changed": len(files_changed),
            "total_lines_changed": total_lines_changed,
            "complexity_indicator": complexity_indicator,
            "first_commit_date": first_commit.committed_datetime,
            "completion_date": (
                merge_commit.committed_datetime if merge_commit else recent_commits[-1].committed_datetime
            ),
            "avg_lines_per_commit": total_lines_changed / len(recent_commits) if recent_commits else 0,
        }

    def _find_merge_commit(self, branch):
        """Find the merge commit for a branch (simplified implementation)."""
        # In a real implementation, this would search for actual merge commits
        return None

    def _calculate_distribution_statistics(self, cycle_times: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistical distribution of cycle times."""
        if not cycle_times:
            return {}

        # Extract time values for analysis
        times_hours = [ct["cycle_time_hours"] for ct in cycle_times]
        times_days = [ct["cycle_time_days"] for ct in cycle_times]

        # Basic statistics
        statistics_data = {
            "count": len(times_hours),
            "mean_hours": statistics.mean(times_hours),
            "median_hours": statistics.median(times_hours),
            "std_deviation_hours": statistics.stdev(times_hours) if len(times_hours) > 1 else 0,
            "min_hours": min(times_hours),
            "max_hours": max(times_hours),
            "mean_days": statistics.mean(times_days),
            "median_days": statistics.median(times_days),
        }

        # Percentiles for planning
        sorted_times = sorted(times_hours)
        percentiles = {}
        for p in [50, 75, 85, 90, 95, 99]:
            index = min(int(len(sorted_times) * p / 100), len(sorted_times) - 1)
            percentiles[f"p{p}"] = sorted_times[index]
            percentiles[f"p{p}_days"] = sorted_times[index] / 24

        statistics_data["percentiles"] = percentiles

        # Identify outliers (beyond 95th percentile)
        p95_threshold = percentiles.get("p95", float("inf"))
        outliers = [ct for ct in cycle_times if ct["cycle_time_hours"] > p95_threshold]

        # Identify fast deliveries (below 25th percentile)
        p25_threshold = percentiles.get("p50", 0) / 2  # Approximate 25th percentile
        fast_deliveries = [ct for ct in cycle_times if ct["cycle_time_hours"] < p25_threshold]

        statistics_data.update(
            {
                "outliers": outliers,
                "fast_deliveries": fast_deliveries,
                "outlier_count": len(outliers),
                "fast_delivery_count": len(fast_deliveries),
            }
        )

        # Distribution categories
        distribution_categories = self._categorize_cycle_times(cycle_times)
        statistics_data["distribution_categories"] = distribution_categories

        return statistics_data

    def _categorize_cycle_times(self, cycle_times: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorize cycle times into delivery speed buckets."""
        categories = {
            "very_fast": 0,  # < 1 day
            "fast": 0,  # 1-3 days
            "normal": 0,  # 3-7 days
            "slow": 0,  # 7-14 days
            "very_slow": 0,  # > 14 days
        }

        for ct in cycle_times:
            days = ct["cycle_time_days"]

            if days < 1:
                categories["very_fast"] += 1
            elif days <= 3:
                categories["fast"] += 1
            elif days <= 7:
                categories["normal"] += 1
            elif days <= 14:
                categories["slow"] += 1
            else:
                categories["very_slow"] += 1

        # Calculate percentages
        total = len(cycle_times)
        category_percentages = {
            category: (count / total * 100) if total > 0 else 0 for category, count in categories.items()
        }

        return {"counts": categories, "percentages": category_percentages, "total": total}

    def _generate_planning_recommendations(self, statistics: Dict[str, Any]) -> List[str]:
        """Generate planning recommendations based on cycle time analysis."""
        if not statistics:
            return []

        recommendations = []

        percentiles = statistics.get("percentiles", {})
        mean_days = statistics.get("mean_days", 0)
        median_days = statistics.get("median_days", 0)

        # Planning estimates based on percentiles
        p50_days = percentiles.get("p50_days", 0)
        p75_days = percentiles.get("p75_days", 0)
        p90_days = percentiles.get("p90_days", 0)

        recommendations.extend(
            [
                f"For 50% confidence in delivery: plan {p50_days:.1f} days",
                f"For 75% confidence in delivery: plan {p75_days:.1f} days",
                f"For 90% confidence in delivery: plan {p90_days:.1f} days",
            ]
        )

        # Risk-based recommendations
        if mean_days > 14:
            recommendations.extend(
                [
                    "High average cycle time - consider breaking down features",
                    "Implement feature flags for incremental delivery",
                ]
            )

        if median_days > mean_days * 1.5:
            recommendations.append("Cycle times are skewed by outliers - investigate long-running features")

        # Distribution-based recommendations
        distribution = statistics.get("distribution_categories", {})
        percentages = distribution.get("percentages", {})

        very_slow_pct = percentages.get("very_slow", 0)
        if very_slow_pct > 20:
            recommendations.append("Too many features take >14 days - review feature sizing")

        very_fast_pct = percentages.get("very_fast", 0)
        if very_fast_pct > 50:
            recommendations.append("Many very fast deliveries - ensure adequate testing")

        return recommendations

    def get_recommendations(self, statistics: Dict[str, Any]) -> List[str]:
        """Generate general recommendations based on cycle time analysis."""
        if not statistics:
            return ["Unable to generate recommendations - insufficient data"]

        recommendations = []

        mean_days = statistics.get("mean_days", 0)
        median_days = statistics.get("median_days", 0)
        std_deviation = statistics.get("std_deviation_hours", 0) / 24  # Convert to days

        # Recommendations based on central tendency
        if mean_days > 21:
            recommendations.extend(
                [
                    "URGENT: Very long average cycle time (>21 days)",
                    "Implement feature decomposition practices",
                    "Consider continuous delivery approaches",
                    "Review and streamline approval processes",
                ]
            )
        elif mean_days > 14:
            recommendations.extend(
                [
                    "Long average cycle time (>14 days)",
                    "Break down large features into smaller deliverables",
                    "Implement work-in-progress limits",
                ]
            )
        elif mean_days > 7:
            recommendations.extend(
                ["Moderate cycle time - room for improvement", "Consider optimizing development workflow"]
            )
        else:
            recommendations.append("Good average cycle time - maintain current practices")

        # Recommendations based on variability
        if std_deviation > mean_days:
            recommendations.extend(
                [
                    "High variability in cycle times",
                    "Investigate causes of long-running features",
                    "Improve estimation practices",
                ]
            )

        # Recommendations based on outliers
        outlier_count = statistics.get("outlier_count", 0)
        total_count = statistics.get("count", 0)

        if total_count > 0:
            outlier_percentage = (outlier_count / total_count) * 100
            if outlier_percentage > 10:
                recommendations.append("High percentage of outlier features - investigate root causes")

        # Distribution-based recommendations
        distribution = statistics.get("distribution_categories", {})
        percentages = distribution.get("percentages", {})

        normal_and_fast = percentages.get("normal", 0) + percentages.get("fast", 0) + percentages.get("very_fast", 0)
        if normal_and_fast > 80:
            recommendations.append("Good cycle time distribution - most features delivered efficiently")

        slow_features = percentages.get("slow", 0) + percentages.get("very_slow", 0)
        if slow_features > 40:
            recommendations.append("Too many slow features - focus on reducing cycle time")

        return recommendations
