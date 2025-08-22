"""
Knowledge Distribution Index Analyzer - Measures inequality in knowledge
distribution across team members using Gini Coefficient.
"""

from typing import Any, Dict, List

from .base import BaseMetricAnalyzer


class KnowledgeDistributionAnalyzer(BaseMetricAnalyzer):
    """
    Calculates the Knowledge Distribution Index (Gini Coefficient) for a repository.

    The Gini coefficient measures inequality in knowledge distribution across
    team members, where 0 represents perfect equality and 1 represents maximum
    inequality.
    """

    def __init__(self, repository):
        super().__init__(repository)

    def get_metric_name(self) -> str:
        return "Knowledge Distribution Index (Gini Coefficient)"

    def get_description(self) -> str:
        return (
            "Measures inequality in knowledge distribution across team members using Gini coefficient. "
            "0 = perfect equality, 1 = maximum inequality. Target: < 0.6"
        )

    def calculate(self, knowledge_weights: Dict[str, Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate the knowledge distribution index.

        Args:
            knowledge_weights: Pre-calculated knowledge weights from bus factor analysis

        Returns:
            Dictionary containing knowledge distribution analysis results
        """
        if knowledge_weights is None:
            knowledge_weights = self._calculate_knowledge_weights()

        if not knowledge_weights:
            return {"gini_coefficient": 0.0, "distribution_quality": "UNKNOWN", "error": "No knowledge data available"}

        gini_coefficient = self._calculate_gini_coefficient(knowledge_weights)
        distribution_analysis = self._analyze_distribution(knowledge_weights)

        return {
            "gini_coefficient": gini_coefficient,
            "distribution_quality": self._assess_distribution_quality(gini_coefficient),
            "contributor_count": len(knowledge_weights),
            "distribution_analysis": distribution_analysis,
            "recommendations": self.get_recommendations({"gini_coefficient": gini_coefficient}),
        }

    def _calculate_knowledge_weights(self) -> Dict[str, Dict[str, float]]:
        """Calculate knowledge weights for each contributor (simplified version)."""
        # This would typically be provided by the bus factor analyzer
        # For now, implement a simplified version
        knowledge_weights = {}

        commits = self.repository.get_commits(limit=1000)  # Last 1000 commits

        for commit in commits:
            author = commit.author.name

            if author not in knowledge_weights:
                knowledge_weights[author] = {}

            for file_path in commit.stats.files:
                if file_path not in knowledge_weights[author]:
                    knowledge_weights[author][file_path] = 0
                knowledge_weights[author][file_path] += 1

        return knowledge_weights

    def _calculate_gini_coefficient(self, knowledge_weights: Dict[str, Dict[str, float]]) -> float:
        """Calculate the Gini coefficient for knowledge distribution."""
        # Extract total knowledge per contributor
        contributor_knowledge = [sum(files.values()) for files in knowledge_weights.values()]
        contributor_knowledge.sort()

        n = len(contributor_knowledge)
        if n == 0:
            return 0.0

        # Calculate cumulative sum weighted by position
        cumulative_sum = sum((i + 1) * knowledge for i, knowledge in enumerate(contributor_knowledge))
        total_knowledge = sum(contributor_knowledge)

        if total_knowledge == 0:
            return 0.0

        # Gini coefficient formula
        gini = (2 * cumulative_sum) / (n * total_knowledge) - (n + 1) / n

        return max(0.0, min(1.0, gini))  # Clamp between 0 and 1

    def _analyze_distribution(self, knowledge_weights: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyze the knowledge distribution in detail."""
        contributor_totals = [sum(files.values()) for files in knowledge_weights.values()]
        contributor_totals.sort(reverse=True)

        total_knowledge = sum(contributor_totals)
        contributor_count = len(contributor_totals)

        analysis = {
            "total_knowledge": total_knowledge,
            "contributor_count": contributor_count,
            "top_contributor_share": 0.0,
            "top_3_contributors_share": 0.0,
            "bottom_50_percent_share": 0.0,
        }

        if contributor_count > 0 and total_knowledge > 0:
            # Top contributor share
            analysis["top_contributor_share"] = contributor_totals[0] / total_knowledge

            # Top 3 contributors share
            top_3_total = sum(contributor_totals[: min(3, contributor_count)])
            analysis["top_3_contributors_share"] = top_3_total / total_knowledge

            # Bottom 50% share
            bottom_50_count = contributor_count // 2
            if bottom_50_count > 0:
                bottom_50_total = sum(contributor_totals[-bottom_50_count:])
                analysis["bottom_50_percent_share"] = bottom_50_total / total_knowledge

        return analysis

    def _assess_distribution_quality(self, gini_coefficient: float) -> str:
        """Assess the quality of knowledge distribution."""
        if gini_coefficient < 0.3:
            return "EXCELLENT"
        elif gini_coefficient < 0.5:
            return "GOOD"
        elif gini_coefficient < 0.6:
            return "ACCEPTABLE"
        elif gini_coefficient < 0.8:
            return "POOR"
        else:
            return "CRITICAL"

    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on knowledge distribution results."""
        gini = results.get("gini_coefficient", 0.0)
        recommendations = []

        if gini > 0.8:
            recommendations.extend(
                [
                    "CRITICAL: Knowledge is extremely concentrated - implement immediate knowledge sharing",
                    "Establish mandatory pair programming for all critical components",
                    "Create comprehensive documentation for all systems",
                    "Implement cross-training program immediately",
                ]
            )
        elif gini > 0.6:
            recommendations.extend(
                [
                    "Knowledge distribution is concerning - increase collaboration",
                    "Implement regular knowledge sharing sessions",
                    "Encourage code reviews across different team members",
                    "Document critical business logic and architectural decisions",
                ]
            )
        elif gini > 0.5:
            recommendations.extend(
                [
                    "Consider improving knowledge sharing practices",
                    "Rotate development responsibilities more frequently",
                    "Ensure all team members participate in code reviews",
                ]
            )
        elif gini > 0.3:
            recommendations.extend(
                [
                    "Good knowledge distribution - maintain current practices",
                    "Continue encouraging collaborative development",
                ]
            )
        else:
            recommendations.append("Excellent knowledge distribution across the team")

        return recommendations
