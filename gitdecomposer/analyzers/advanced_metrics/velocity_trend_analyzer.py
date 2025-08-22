"""
Development Velocity Trend Analyzer - Detects if team is speeding up,
slowing down, or maintaining steady pace.
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from .base import BaseMetricAnalyzer


class VelocityTrendAnalyzer(BaseMetricAnalyzer):
    """
    Analyzes development velocity trends over time.

    Tracks multiple velocity indicators to determine if the team is
    accelerating, decelerating, or maintaining steady development pace.
    """

    def __init__(self, repository):
        super().__init__(repository)

    def get_metric_name(self) -> str:
        return "Development Velocity Trend"

    def get_description(self) -> str:
        return (
            "Analyzes development velocity trends to detect if the team "
            "is speeding up, slowing down, or maintaining steady pace."
        )

    def calculate(self, weeks_lookback: int = 12) -> Dict[str, Any]:
        """
        Calculate velocity trends over the specified time period.

        Args:
            weeks_lookback: Number of weeks to analyze

        Returns:
            Dictionary containing velocity trend analysis results
        """
        weekly_data = self._collect_weekly_data(weeks_lookback)

        if len(weekly_data) < 3:
            return {
                "weekly_data": weekly_data,
                "trends": {},
                "error": "Insufficient data for trend analysis (need at least 3 weeks)",
            }

        trends = self._analyze_trends(weekly_data)
        overall_health = self._assess_velocity_health(trends)

        return {
            "weekly_data": weekly_data,
            "trends": trends,
            "overall_health": overall_health,
            "recommendations": self.get_recommendations(
                {"trends": trends, "overall_health": overall_health, "weeks_analyzed": len(weekly_data)}
            ),
        }

    def _collect_weekly_data(self, weeks_lookback: int) -> List[Dict[str, Any]]:
        """Collect weekly development metrics."""
        end_date = datetime.now()
        weekly_data = []

        for week in range(weeks_lookback):
            week_start = end_date - timedelta(weeks=week + 1)
            week_end = end_date - timedelta(weeks=week)

            # Get commits for this week
            commits = list(self.repository.get_commits(since=week_start, until=week_end))

            # Calculate weekly metrics
            weekly_metrics = self._calculate_weekly_metrics(commits, week, week_start, week_end)
            weekly_data.append(weekly_metrics)

        # Reverse to get chronological order (oldest first)
        weekly_data.reverse()

        return weekly_data

    def _calculate_weekly_metrics(
        self, commits: List, week_number: int, week_start: datetime, week_end: datetime
    ) -> Dict[str, Any]:
        """Calculate metrics for a single week."""
        # Basic commit metrics
        commit_count = len(commits)
        unique_authors = len(set(c.author.name for c in commits))

        # File and line change metrics
        files_changed = set()
        total_insertions = 0
        total_deletions = 0

        for commit in commits:
            files_changed.update(commit.stats.files.keys())
            total_insertions += commit.stats.total["insertions"]
            total_deletions += commit.stats.total["deletions"]

        total_lines_changed = total_insertions + total_deletions

        # Advanced metrics
        avg_commit_size = total_lines_changed / commit_count if commit_count > 0 else 0
        files_per_commit = len(files_changed) / commit_count if commit_count > 0 else 0
        commits_per_author = commit_count / unique_authors if unique_authors > 0 else 0

        return {
            "week": week_number,
            "week_start": week_start,
            "week_end": week_end,
            "commit_count": commit_count,
            "unique_authors": unique_authors,
            "files_changed": len(files_changed),
            "total_lines_changed": total_lines_changed,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "avg_commit_size": avg_commit_size,
            "files_per_commit": files_per_commit,
            "commits_per_author": commits_per_author,
        }

    def _analyze_trends(self, weekly_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze trends for each velocity metric."""
        metrics_to_analyze = [
            "commit_count",
            "unique_authors",
            "files_changed",
            "total_lines_changed",
            "avg_commit_size",
        ]

        trends = {}

        for metric in metrics_to_analyze:
            values = [week[metric] for week in weekly_data]
            trend_analysis = self._calculate_trend_statistics(values, metric)
            trends[metric] = trend_analysis

        return trends

    def _calculate_trend_statistics(self, values: List[float], metric_name: str) -> Dict[str, Any]:
        """Calculate trend statistics for a single metric using linear regression."""
        if len(values) < 2:
            return {
                "trend": "insufficient_data",
                "slope": 0,
                "confidence": 0,
                "current_value": values[-1] if values else 0,
            }

        time_points = list(range(len(values)))

        # Simple linear regression
        slope, intercept, r_squared = self._linear_regression(time_points, values)

        # Determine trend direction
        if abs(slope) < 0.1:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"

        # Statistical significance (simplified)
        confidence = abs(r_squared)
        statistical_significance = confidence > 0.5  # Simplified threshold

        # Predictions
        next_week_prediction = slope * len(values) + intercept

        return {
            "metric": metric_name,
            "slope": slope,
            "trend": trend_direction,
            "confidence": confidence,
            "statistical_significance": statistical_significance,
            "weekly_change_rate": slope,
            "current_value": values[-1] if values else 0,
            "predicted_next_week": max(0, next_week_prediction),  # Don't predict negative values
            "r_squared": r_squared,
            "values": values,
        }

    def _linear_regression(self, x: List[float], y: List[float]) -> Tuple[float, float, float]:
        """Perform simple linear regression."""
        n = len(x)
        if n < 2:
            return 0, 0, 0

        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        # Calculate slope and intercept
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0, y_mean, 0

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Calculate R-squared
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return slope, intercept, r_squared

    def _assess_velocity_health(self, trends: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall velocity health based on trends."""
        if not trends:
            return {"overall_status": "unknown", "confidence": 0}

        # Count positive, negative, and stable trends
        positive_trends = 0
        negative_trends = 0
        stable_trends = 0
        total_confidence = 0

        for metric, trend_data in trends.items():
            trend = trend_data.get("trend", "stable")
            confidence = trend_data.get("confidence", 0)

            if trend == "increasing":
                positive_trends += 1
            elif trend == "decreasing":
                negative_trends += 1
            else:
                stable_trends += 1

            total_confidence += confidence

        avg_confidence = total_confidence / len(trends) if trends else 0

        # Determine overall status
        if positive_trends > negative_trends:
            overall_status = "improving"
        elif negative_trends > positive_trends:
            overall_status = "declining"
        else:
            overall_status = "stable"

        # Assess health level
        if positive_trends >= 3 and negative_trends <= 1:
            health_level = "excellent"
        elif positive_trends >= 2 and negative_trends <= 2:
            health_level = "good"
        elif negative_trends >= 3 and positive_trends <= 1:
            health_level = "poor"
        elif negative_trends >= 2 and positive_trends <= 2:
            health_level = "concerning"
        else:
            health_level = "average"

        return {
            "overall_status": overall_status,
            "health_level": health_level,
            "confidence": avg_confidence,
            "positive_trends": positive_trends,
            "negative_trends": negative_trends,
            "stable_trends": stable_trends,
            "key_concerns": self._identify_key_concerns(trends),
            "key_strengths": self._identify_key_strengths(trends),
        }

    def _identify_key_concerns(self, trends: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify key concerns from trend analysis."""
        concerns = []

        for metric, trend_data in trends.items():
            trend = trend_data.get("trend", "stable")
            confidence = trend_data.get("confidence", 0)

            if trend == "decreasing" and confidence > 0.6:
                if metric == "commit_count":
                    concerns.append("Decreasing commit frequency")
                elif metric == "unique_authors":
                    concerns.append("Decreasing contributor diversity")
                elif metric == "total_lines_changed":
                    concerns.append("Decreasing code change volume")
                elif metric == "files_changed":
                    concerns.append("Decreasing file modification breadth")

        return concerns

    def _identify_key_strengths(self, trends: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify key strengths from trend analysis."""
        strengths = []

        for metric, trend_data in trends.items():
            trend = trend_data.get("trend", "stable")
            confidence = trend_data.get("confidence", 0)

            if trend == "increasing" and confidence > 0.6:
                if metric == "commit_count":
                    strengths.append("Increasing commit frequency")
                elif metric == "unique_authors":
                    strengths.append("Increasing contributor diversity")
                elif metric == "total_lines_changed":
                    strengths.append("Increasing development activity")
                elif metric == "files_changed":
                    strengths.append("Increasing codebase coverage")

        return strengths

    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on velocity trend analysis."""
        recommendations = []

        trends = results.get("trends", {})
        overall_health = results.get("overall_health", {})
        weeks_analyzed = results.get("weeks_analyzed", 0)

        if weeks_analyzed < 4:
            recommendations.append("Extend analysis period for more reliable trend detection")

        health_level = overall_health.get("health_level", "unknown")
        overall_status = overall_health.get("overall_status", "unknown")

        # Health-based recommendations
        if health_level == "poor":
            recommendations.extend(
                [
                    "URGENT: Multiple velocity metrics are declining",
                    "Investigate team capacity and process bottlenecks",
                    "Consider team morale and technical debt issues",
                    "Review and optimize development workflow",
                ]
            )
        elif health_level == "concerning":
            recommendations.extend(
                [
                    "Monitor velocity trends closely",
                    "Address identified declining metrics",
                    "Consider process improvements",
                ]
            )
        elif health_level == "excellent":
            recommendations.extend(
                [
                    "Excellent velocity trends - maintain current practices",
                    "Document and share successful practices",
                    "Monitor for sustainability",
                ]
            )

        # Specific trend-based recommendations
        key_concerns = overall_health.get("key_concerns", [])
        key_strengths = overall_health.get("key_strengths", [])

        if "Decreasing commit frequency" in key_concerns:
            recommendations.append("Investigate causes of reduced commit frequency")

        if "Decreasing contributor diversity" in key_concerns:
            recommendations.extend(
                ["Focus on team engagement and knowledge sharing", "Ensure equitable work distribution"]
            )

        if "Increasing development activity" in key_strengths:
            recommendations.append("Monitor increased activity for sustainability")

        # Confidence-based recommendations
        avg_confidence = overall_health.get("confidence", 0)
        if avg_confidence < 0.4:
            recommendations.append("Trends show low confidence - extend analysis period")

        return recommendations
