"""
Bus Factor Analyzer - Identifies minimum number of people whose absence
would severely impact project continuity.
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

from .base import BaseMetricAnalyzer


class BusFactorAnalyzer(BaseMetricAnalyzer):
    """
    Calculates the bus factor for a repository.

    The bus factor represents the minimum number of team members that could be
    "hit by a bus" (become unavailable) before the project would be severely
    impacted by knowledge loss.
    """

    def __init__(self, repository):
        super().__init__(repository)

    def get_metric_name(self) -> str:
        return "Bus Factor"

    def get_description(self) -> str:
        return (
            "Minimum number of people whose absence would severely impact "
            "project continuity based on knowledge distribution."
        )

    def calculate(
        self, lookback_months: int = 6, knowledge_threshold: float = 0.8, decay_half_life: int = 90
    ) -> Dict[str, Any]:
        """
        Calculate the bus factor for the repository.

        Args:
            lookback_months: How many months back to analyze
            knowledge_threshold: Coverage threshold (0.8 = 80%)
            decay_half_life: Half-life for recency weight in days

        Returns:
            Dictionary containing bus factor analysis results
        """
        # Step 1: Weight each contributor's knowledge by recency
        knowledge_weights = self._calculate_knowledge_weights(lookback_months, decay_half_life)

        if not knowledge_weights:
            return {"bus_factor": 0, "knowledge_weights": {}, "error": "No commits found in the specified timeframe"}

        # Step 2: Find minimum contributor set covering target knowledge
        bus_factor, coverage_analysis = self._calculate_bus_factor(knowledge_weights, knowledge_threshold)

        return {
            "bus_factor": bus_factor,
            "knowledge_threshold": knowledge_threshold,
            "total_contributors": len(knowledge_weights),
            "knowledge_weights": knowledge_weights,
            "coverage_analysis": coverage_analysis,
            "risk_level": self._assess_risk_level(bus_factor, len(knowledge_weights)),
            "recommendations": self.get_recommendations(
                {"bus_factor": bus_factor, "total_contributors": len(knowledge_weights)}
            ),
        }

    def _calculate_knowledge_weights(self, lookback_months: int, decay_half_life: int) -> Dict[str, Dict[str, float]]:
        """Calculate knowledge weights for each contributor per file."""
        knowledge_weights = {}

        # Get commits from the specified timeframe
        since_date = datetime.now() - timedelta(days=30 * lookback_months)
        commits = self.repository.get_all_commits()

        for commit in commits:
            author = commit.author.name
            # Handle timezone-aware datetime comparison
            commit_date = commit.committed_datetime.replace(tzinfo=None) if commit.committed_datetime.tzinfo else commit.committed_datetime
            days_ago = (datetime.now() - commit_date).days
            recency_weight = math.exp(-days_ago / decay_half_life)

            for file_path in commit.stats.files:
                # Weight by file complexity and criticality
                complexity = self._get_file_complexity(file_path)
                criticality = self._get_file_criticality(file_path)

                file_weight = recency_weight * complexity * criticality

                if author not in knowledge_weights:
                    knowledge_weights[author] = {}

                current_weight = knowledge_weights[author].get(file_path, 0)
                knowledge_weights[author][file_path] = current_weight + file_weight

        return knowledge_weights

    def _calculate_bus_factor(
        self, knowledge_weights: Dict[str, Dict[str, float]], threshold: float
    ) -> Tuple[int, Dict[str, Any]]:
        """Calculate the actual bus factor from knowledge weights."""
        total_knowledge = sum(sum(files.values()) for files in knowledge_weights.values())
        target_coverage = total_knowledge * threshold

        # Sort contributors by total knowledge
        sorted_contributors = sorted(knowledge_weights.items(), key=lambda x: sum(x[1].values()), reverse=True)

        cumulative_knowledge = 0
        bus_factor = 0
        coverage_path = []

        for contributor, files_knowledge in sorted_contributors:
            contributor_total = sum(files_knowledge.values())
            cumulative_knowledge += contributor_total
            bus_factor += 1

            coverage_path.append(
                {
                    "contributor": contributor,
                    "knowledge_amount": contributor_total,
                    "cumulative_coverage": cumulative_knowledge / total_knowledge,
                    "files_count": len(files_knowledge),
                }
            )

            if cumulative_knowledge >= target_coverage:
                break

        coverage_analysis = {
            "target_coverage": threshold,
            "actual_coverage": cumulative_knowledge / total_knowledge if total_knowledge > 0 else 0,
            "total_knowledge": total_knowledge,
            "coverage_path": coverage_path,
        }

        return bus_factor, coverage_analysis

    def _get_file_complexity(self, file_path: str) -> float:
        """Estimate file complexity (placeholder implementation)."""
        # TODO: Implement actual complexity calculation
        # For now, use file extension as a simple heuristic
        complexity_weights = {
            ".py": 1.0,
            ".js": 1.0,
            ".ts": 1.0,
            ".java": 1.2,
            ".cpp": 1.3,
            ".c": 1.3,
            ".h": 1.1,
            ".css": 0.5,
            ".html": 0.3,
            ".md": 0.2,
            ".txt": 0.1,
        }

        for ext, weight in complexity_weights.items():
            if file_path.endswith(ext):
                return weight

        return 0.8  # Default complexity

    def _get_file_criticality(self, file_path: str) -> float:
        """Estimate file criticality (placeholder implementation)."""
        # TODO: Implement actual criticality calculation based on dependencies
        critical_patterns = ["main", "index", "app", "core", "base", "config", "__init__", "setup", "requirements"]

        file_name = file_path.lower()
        for pattern in critical_patterns:
            if pattern in file_name:
                return 1.5

        return 1.0  # Default criticality

    def _assess_risk_level(self, bus_factor: int, total_contributors: int) -> str:
        """Assess the risk level based on bus factor."""
        if bus_factor <= 1:
            return "CRITICAL"
        elif bus_factor <= 2:
            return "HIGH"
        elif bus_factor <= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def get_recommendations(self, results: Dict[str, Any]) -> list:
        """Generate recommendations based on bus factor results."""
        bus_factor = results.get("bus_factor", 0)
        total_contributors = results.get("total_contributors", 0)

        recommendations = []

        if bus_factor <= 1:
            recommendations.extend(
                [
                    "URGENT: Implement immediate knowledge sharing sessions",
                    "Create comprehensive documentation for critical components",
                    "Establish pair programming practices",
                    "Cross-train team members on critical systems",
                ]
            )
        elif bus_factor <= 2:
            recommendations.extend(
                [
                    "Increase code review participation",
                    "Implement knowledge sharing workshops",
                    "Document critical business logic",
                    "Encourage rotation of development responsibilities",
                ]
            )
        elif bus_factor <= 3:
            recommendations.extend(
                [
                    "Continue current knowledge sharing practices",
                    "Monitor for knowledge concentration trends",
                    "Ensure new team members are onboarded on critical systems",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Excellent knowledge distribution",
                    "Maintain current practices",
                    "Consider mentoring junior developers",
                ]
            )

        if total_contributors > 0:
            concentration_ratio = bus_factor / total_contributors
            if concentration_ratio < 0.3:
                recommendations.append("Consider spreading knowledge more evenly across team members")

        return recommendations
