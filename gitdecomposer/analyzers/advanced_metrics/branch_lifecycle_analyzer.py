"""
Branch Lifecycle Analyzer - Analyzes how long features take from
conception to completion.
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .base import BaseMetricAnalyzer


class BranchLifecycleAnalyzer(BaseMetricAnalyzer):
    """
    Analyzes the complete lifecycle of feature branches.

    Tracks the time from branch creation through development phases
    to completion, identifying patterns in feature delivery.
    """

    def __init__(self, repository):
        super().__init__(repository)

    def get_metric_name(self) -> str:
        return "Branch Lifecycle Analysis"

    def get_description(self) -> str:
        return (
            "Analyzes the complete lifecycle of feature branches from "
            "conception to completion, identifying delivery patterns."
        )

    def calculate(self, include_active_branches: bool = False) -> Dict[str, Any]:
        """
        Analyze branch lifecycles.

        Args:
            include_active_branches: Whether to include branches that haven't been merged

        Returns:
            Dictionary containing branch lifecycle analysis results
        """
        lifecycle_data = self._analyze_merged_branches()

        if include_active_branches:
            active_data = self._analyze_active_branches()
            lifecycle_data.extend(active_data)

        if not lifecycle_data:
            return {"lifecycle_data": [], "analysis": {}, "error": "No branches found for lifecycle analysis"}

        analysis = self._perform_lifecycle_analysis(lifecycle_data)

        return {
            "lifecycle_data": lifecycle_data,
            "analysis": analysis,
            "recommendations": self.get_recommendations(analysis),
        }

    def _analyze_merged_branches(self) -> List[Dict[str, Any]]:
        """Analyze lifecycle data for merged branches."""
        lifecycle_data = []

        # Get merged branches (simplified - in reality would track merge commits)
        branches = self.repository.get_branches()

        for branch in branches:
            if branch.name in ["main", "master", "develop"]:
                continue  # Skip main branches

            try:
                branch_data = self._analyze_single_branch(branch, is_merged=True)
                if branch_data:
                    lifecycle_data.append(branch_data)
            except Exception as e:
                # Skip branches that can't be analyzed
                continue

        return lifecycle_data

    def _analyze_active_branches(self) -> List[Dict[str, Any]]:
        """Analyze lifecycle data for active (unmerged) branches."""
        active_data = []

        # This would analyze currently active branches
        # For now, return empty list
        return active_data

    def _analyze_single_branch(self, branch, is_merged: bool = True) -> Dict[str, Any]:
        """Analyze the lifecycle of a single branch."""
        commits = list(self.repository.get_all_commits(branch=branch.name))

        if len(commits) < 1:
            return None

        # Sort commits by date
        commits.sort(key=lambda c: c.committed_datetime)

        # Phase 1: Branch creation to first commit
        branch_created = self._get_branch_creation_date(branch)
        first_commit = commits[0]

        if branch_created:
            setup_time = first_commit.committed_datetime - branch_created
        else:
            setup_time = timedelta(0)  # Unknown setup time

        # Phase 2: Development phase metrics
        commit_intervals = []
        for i in range(1, len(commits)):
            interval = commits[i].committed_datetime - commits[i - 1].committed_datetime
            commit_intervals.append(interval.total_seconds() / 3600)  # hours

        # Phase 3: Completion phase
        last_commit = commits[-1]

        if is_merged:
            merge_commit = self._find_merge_commit(branch)
            if merge_commit:
                completion_time = merge_commit.committed_datetime - last_commit.committed_datetime
                total_lifecycle_time = (
                    merge_commit.committed_datetime - branch_created if branch_created else timedelta(0)
                )
            else:
                completion_time = timedelta(0)
                total_lifecycle_time = (
                    last_commit.committed_datetime - branch_created if branch_created else timedelta(0)
                )
        else:
            completion_time = timedelta(0)
            total_lifecycle_time = datetime.now() - branch_created if branch_created else timedelta(0)

        # Calculate metrics
        development_time_hours = sum(commit_intervals) if commit_intervals else 0
        avg_commit_interval = statistics.mean(commit_intervals) if commit_intervals else 0
        commit_frequency = len(commits) / (development_time_hours / 24) if development_time_hours > 0 else 0

        return {
            "branch": branch.name,
            "is_merged": is_merged,
            "setup_time_hours": setup_time.total_seconds() / 3600,
            "development_time_hours": development_time_hours,
            "completion_time_hours": completion_time.total_seconds() / 3600,
            "total_lifecycle_hours": total_lifecycle_time.total_seconds() / 3600,
            "commit_count": len(commits),
            "commit_frequency_per_day": commit_frequency,
            "avg_commit_interval_hours": avg_commit_interval,
            "first_commit_date": first_commit.committed_datetime,
            "last_commit_date": last_commit.committed_datetime,
            "files_changed": self._count_unique_files_changed(commits),
            "total_lines_changed": self._count_total_lines_changed(commits),
        }

    def _get_branch_creation_date(self, branch) -> datetime:
        """Get the creation date of a branch (simplified implementation)."""
        # In a real implementation, this would find the actual branch creation point
        # For now, use the first commit date as approximation
        commits = list(self.repository.get_all_commits(branch=branch.name))
        if commits:
            return min(c.committed_datetime for c in commits)
        return None

    def _find_merge_commit(self, branch):
        """Find the merge commit for a branch (simplified implementation)."""
        # In a real implementation, this would search for merge commits
        return None

    def _count_unique_files_changed(self, commits) -> int:
        """Count unique files changed across all commits."""
        unique_files = set()
        for commit in commits:
            unique_files.update(commit.stats.files.keys())
        return len(unique_files)

    def _count_total_lines_changed(self, commits) -> int:
        """Count total lines changed across all commits."""
        total_lines = 0
        for commit in commits:
            total_lines += commit.stats.total["insertions"] + commit.stats.total["deletions"]
        return total_lines

    def _perform_lifecycle_analysis(self, lifecycle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive analysis of lifecycle data."""
        if not lifecycle_data:
            return {}

        # Extract metrics for analysis
        setup_times = [ld["setup_time_hours"] for ld in lifecycle_data if ld["setup_time_hours"] > 0]
        development_times = [ld["development_time_hours"] for ld in lifecycle_data if ld["development_time_hours"] > 0]
        total_lifecycle_times = [
            ld["total_lifecycle_hours"] for ld in lifecycle_data if ld["total_lifecycle_hours"] > 0
        ]
        commit_counts = [ld["commit_count"] for ld in lifecycle_data]
        commit_frequencies = [
            ld["commit_frequency_per_day"] for ld in lifecycle_data if ld["commit_frequency_per_day"] > 0
        ]

        analysis = {
            "total_branches_analyzed": len(lifecycle_data),
            "phase_analysis": {
                "setup_phase": self._analyze_phase_metrics(setup_times, "Setup"),
                "development_phase": self._analyze_phase_metrics(development_times, "Development"),
                "total_lifecycle": self._analyze_phase_metrics(total_lifecycle_times, "Total Lifecycle"),
            },
            "commit_patterns": {
                "avg_commits_per_branch": statistics.mean(commit_counts) if commit_counts else 0,
                "median_commits_per_branch": statistics.median(commit_counts) if commit_counts else 0,
                "avg_commit_frequency_per_day": statistics.mean(commit_frequencies) if commit_frequencies else 0,
            },
            "delivery_patterns": self._analyze_delivery_patterns(lifecycle_data),
            "efficiency_metrics": self._calculate_efficiency_metrics(lifecycle_data),
            "outliers": self._identify_outliers(lifecycle_data),
        }

        return analysis

    def _analyze_phase_metrics(self, phase_times: List[float], phase_name: str) -> Dict[str, Any]:
        """Analyze metrics for a specific phase."""
        if not phase_times:
            return {
                "phase": phase_name,
                "sample_size": 0,
                "avg_hours": 0,
                "median_hours": 0,
                "std_deviation": 0,
                "min_hours": 0,
                "max_hours": 0,
            }

        return {
            "phase": phase_name,
            "sample_size": len(phase_times),
            "avg_hours": statistics.mean(phase_times),
            "median_hours": statistics.median(phase_times),
            "std_deviation": statistics.stdev(phase_times) if len(phase_times) > 1 else 0,
            "min_hours": min(phase_times),
            "max_hours": max(phase_times),
            "avg_days": statistics.mean(phase_times) / 24,
            "median_days": statistics.median(phase_times) / 24,
        }

    def _analyze_delivery_patterns(self, lifecycle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in feature delivery."""
        # Categorize branches by delivery speed
        fast_delivery = []  # < 3 days
        normal_delivery = []  # 3-14 days
        slow_delivery = []  # > 14 days

        for branch_data in lifecycle_data:
            total_days = branch_data["total_lifecycle_hours"] / 24

            if total_days < 3:
                fast_delivery.append(branch_data)
            elif total_days <= 14:
                normal_delivery.append(branch_data)
            else:
                slow_delivery.append(branch_data)

        return {
            "fast_delivery_count": len(fast_delivery),
            "normal_delivery_count": len(normal_delivery),
            "slow_delivery_count": len(slow_delivery),
            "fast_delivery_percentage": len(fast_delivery) / len(lifecycle_data) * 100,
            "normal_delivery_percentage": len(normal_delivery) / len(lifecycle_data) * 100,
            "slow_delivery_percentage": len(slow_delivery) / len(lifecycle_data) * 100,
            "delivery_distribution": {
                "fast": len(fast_delivery),
                "normal": len(normal_delivery),
                "slow": len(slow_delivery),
            },
        }

    def _calculate_efficiency_metrics(self, lifecycle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate efficiency metrics for the development process."""
        efficiency_metrics = []

        for branch_data in lifecycle_data:
            # Calculate efficiency as ratio of development time to total time
            dev_time = branch_data["development_time_hours"]
            total_time = branch_data["total_lifecycle_hours"]

            if total_time > 0:
                efficiency = dev_time / total_time
                efficiency_metrics.append(efficiency)

        if not efficiency_metrics:
            return {"avg_efficiency": 0, "efficiency_distribution": {}}

        # Categorize efficiency
        high_efficiency = sum(1 for e in efficiency_metrics if e > 0.7)
        medium_efficiency = sum(1 for e in efficiency_metrics if 0.4 <= e <= 0.7)
        low_efficiency = sum(1 for e in efficiency_metrics if e < 0.4)

        return {
            "avg_efficiency": statistics.mean(efficiency_metrics),
            "median_efficiency": statistics.median(efficiency_metrics),
            "efficiency_distribution": {"high": high_efficiency, "medium": medium_efficiency, "low": low_efficiency},
        }

    def _identify_outliers(self, lifecycle_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Identify outlier branches in terms of lifecycle metrics."""
        if len(lifecycle_data) < 3:
            return {"longest_lifecycle": [], "shortest_lifecycle": []}

        # Sort by total lifecycle time
        sorted_by_time = sorted(lifecycle_data, key=lambda x: x["total_lifecycle_hours"])

        return {
            "longest_lifecycle": sorted_by_time[-3:],  # Top 3 longest
            "shortest_lifecycle": sorted_by_time[:3],  # Top 3 shortest
            "highest_commit_count": sorted(lifecycle_data, key=lambda x: x["commit_count"], reverse=True)[:3],
            "lowest_commit_count": sorted(lifecycle_data, key=lambda x: x["commit_count"])[:3],
        }

    def get_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on branch lifecycle analysis."""
        recommendations = []

        if not analysis:
            return ["Unable to generate recommendations - insufficient data"]

        phase_analysis = analysis.get("phase_analysis", {})
        delivery_patterns = analysis.get("delivery_patterns", {})
        efficiency_metrics = analysis.get("efficiency_metrics", {})

        # Recommendations based on total lifecycle time
        total_lifecycle = phase_analysis.get("total_lifecycle", {})
        avg_days = total_lifecycle.get("avg_days", 0)

        if avg_days > 30:
            recommendations.extend(
                [
                    "URGENT: Average feature delivery time is too long (>30 days)",
                    "Break down large features into smaller, manageable pieces",
                    "Implement feature flags for incremental delivery",
                    "Review and streamline approval processes",
                ]
            )
        elif avg_days > 14:
            recommendations.extend(
                [
                    "Feature delivery time is longer than optimal (>14 days)",
                    "Consider reducing feature scope or improving process efficiency",
                    "Implement continuous integration practices",
                ]
            )
        elif avg_days < 3:
            recommendations.extend(
                [
                    "Very fast feature delivery - ensure quality is maintained",
                    "Consider if features are appropriately sized",
                    "Maintain current efficient processes",
                ]
            )

        # Recommendations based on delivery patterns
        slow_percentage = delivery_patterns.get("slow_delivery_percentage", 0)
        if slow_percentage > 50:
            recommendations.extend(
                [
                    f"Over half of features take >14 days to deliver",
                    "Investigate common causes of delays",
                    "Implement work-in-progress limits",
                ]
            )

        # Recommendations based on efficiency
        avg_efficiency = efficiency_metrics.get("avg_efficiency", 0)
        if avg_efficiency < 0.3:
            recommendations.extend(
                [
                    "Low development efficiency detected",
                    "Reduce waiting time between development phases",
                    "Improve tooling and automation",
                ]
            )
        elif avg_efficiency > 0.8:
            recommendations.append("Excellent development efficiency - maintain practices")

        # Setup phase recommendations
        setup_phase = phase_analysis.get("setup_phase", {})
        setup_hours = setup_phase.get("avg_hours", 0)
        if setup_hours > 24:
            recommendations.append("Branch setup time is high - improve onboarding automation")

        return recommendations
