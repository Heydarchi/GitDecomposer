"""
Critical File Identification Analyzer - Identifies files that pose highest
risk due to complexity and change frequency.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from .base import BaseMetricAnalyzer


class CriticalFileAnalyzer(BaseMetricAnalyzer):
    """
    Identifies critical files based on complexity, change frequency, and impact.

    Critical files are those that pose the highest risk due to their combination
    of complexity, frequency of changes, and dependency impact.
    """

    def __init__(self, repository):
        super().__init__(repository)

    def get_metric_name(self) -> str:
        return "Critical File Identification"

    def get_description(self) -> str:
        return "Identifies files that pose highest risk due to complexity, " "change frequency, and dependency impact."

    def calculate(self, lookback_months: int = 6, critical_threshold_percentile: float = 0.8) -> Dict[str, Any]:
        """
        Identify critical files in the repository.

        Args:
            lookback_months: How many months back to analyze changes
            critical_threshold_percentile: Top percentile to consider critical (0.8 = top 20%)

        Returns:
            Dictionary containing critical file analysis results
        """
        file_metrics = self._calculate_file_metrics(lookback_months)

        if not file_metrics:
            return {"critical_files": [], "total_files_analyzed": 0, "error": "No files found for analysis"}

        critical_files = self._identify_critical_files(file_metrics, critical_threshold_percentile)

        analysis = self._analyze_critical_files(critical_files, file_metrics)

        return {
            "critical_files": critical_files,
            "total_files_analyzed": len(file_metrics),
            "critical_file_count": len(critical_files),
            "analysis": analysis,
            "recommendations": self.get_recommendations(
                {"critical_files": critical_files, "total_files": len(file_metrics)}
            ),
        }

    def _calculate_file_metrics(self, lookback_months: int) -> Dict[str, Dict[str, float]]:
        """Calculate metrics for all files in the repository."""
        file_metrics = {}
        since_date = datetime.now() - timedelta(days=30 * lookback_months)

        # Get all commits in the timeframe
        commits = self.repository.get_commits(since=since_date)

        # Track file changes
        file_changes = {}
        for commit in commits:
            for file_path in commit.stats.files:
                if file_path not in file_changes:
                    file_changes[file_path] = []
                file_changes[file_path].append(commit)

        # Calculate metrics for each file
        for file_path, commits_list in file_changes.items():
            try:
                # Calculate change frequency
                change_frequency = len(commits_list)

                # Calculate complexity
                complexity = self._calculate_complexity_score(file_path)

                # Calculate dependency impact
                dependency_impact = self._calculate_dependency_impact(file_path)

                # Combined criticality score
                criticality_score = change_frequency * complexity * dependency_impact

                file_metrics[file_path] = {
                    "change_frequency": change_frequency,
                    "complexity": complexity,
                    "dependency_impact": dependency_impact,
                    "criticality_score": criticality_score,
                    "file_size": self._get_file_size(file_path),
                    "last_modified": max(c.committed_datetime for c in commits_list),
                }
            except Exception as e:
                # Skip files that can't be analyzed
                continue

        return file_metrics

    def _calculate_complexity_score(self, file_path: str) -> float:
        """Calculate complexity score for a file."""
        try:
            # Get file content
            content = self._get_file_content(file_path)
            if not content:
                return 1.0

            # Basic complexity metrics
            lines_of_code = len([line for line in content.split("\n") if line.strip()])

            # Cyclomatic complexity estimation
            complexity_patterns = [
                r"\bif\b",
                r"\belif\b",
                r"\belse\b",
                r"\bfor\b",
                r"\bwhile\b",
                r"\bdo\b",
                r"\btry\b",
                r"\bcatch\b",
                r"\bexcept\b",
                r"\bcase\b",
                r"\bswitch\b",
                r"&&",
                r"\|\|",
                r"\?.*:",
                r"\bthrow\b",
                r"\braise\b",
            ]

            cyclomatic_complexity = 1  # Base complexity
            for pattern in complexity_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                cyclomatic_complexity += len(matches)

            # Normalize complexity
            size_factor = min(lines_of_code / 100, 5.0)  # Cap at 5x
            complexity_factor = min(cyclomatic_complexity / 10, 5.0)  # Cap at 5x

            return size_factor * complexity_factor

        except Exception:
            return 1.0  # Default complexity

    def _calculate_dependency_impact(self, file_path: str) -> float:
        """Calculate the dependency impact of a file."""
        # Simplified dependency impact calculation
        # In a real implementation, this would analyze import/dependency graphs

        impact_score = 1.0

        # File type impact
        if file_path.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
            impact_score *= 1.5

        # Special file patterns that typically have high impact
        high_impact_patterns = [
            "main",
            "index",
            "app",
            "core",
            "base",
            "config",
            "__init__",
            "setup",
            "requirements",
            "package",
        ]

        file_name = file_path.lower()
        for pattern in high_impact_patterns:
            if pattern in file_name:
                impact_score *= 2.0
                break

        # Directory structure impact
        if "/" in file_path:
            path_parts = file_path.split("/")
            if any(part in ["src", "lib", "core", "main"] for part in path_parts):
                impact_score *= 1.3

        return impact_score

    def _get_file_content(self, file_path: str) -> str:
        """Get the content of a file."""
        try:
            # This would typically use the repository's file access methods
            # For now, return empty string as placeholder
            return ""
        except Exception:
            return ""

    def _get_file_size(self, file_path: str) -> int:
        """Get the size of a file in lines."""
        try:
            content = self._get_file_content(file_path)
            return len(content.split("\n")) if content else 0
        except Exception:
            return 0

    def _identify_critical_files(
        self, file_metrics: Dict[str, Dict[str, float]], threshold_percentile: float
    ) -> List[Tuple[str, Dict[str, float]]]:
        """Identify critical files based on criticality scores."""
        # Sort files by criticality score
        sorted_files = sorted(file_metrics.items(), key=lambda x: x[1]["criticality_score"], reverse=True)

        # Calculate threshold index
        threshold_index = max(1, int(len(sorted_files) * (1 - threshold_percentile)))

        return sorted_files[:threshold_index]

    def _analyze_critical_files(
        self, critical_files: List[Tuple[str, Dict[str, float]]], all_metrics: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Analyze the critical files to provide insights."""
        if not critical_files:
            return {}

        # Extract scores for analysis
        criticality_scores = [metrics["criticality_score"] for _, metrics in critical_files]
        change_frequencies = [metrics["change_frequency"] for _, metrics in critical_files]
        complexities = [metrics["complexity"] for _, metrics in critical_files]

        analysis = {
            "avg_criticality_score": sum(criticality_scores) / len(criticality_scores),
            "max_criticality_score": max(criticality_scores),
            "avg_change_frequency": sum(change_frequencies) / len(change_frequencies),
            "avg_complexity": sum(complexities) / len(complexities),
            "file_types": self._analyze_file_types(critical_files),
            "risk_categories": self._categorize_risk_levels(critical_files),
        }

        return analysis

    def _analyze_file_types(self, critical_files: List[Tuple[str, Dict[str, float]]]) -> Dict[str, int]:
        """Analyze the types of critical files."""
        file_types = {}

        for file_path, _ in critical_files:
            # Extract file extension
            if "." in file_path:
                ext = "." + file_path.split(".")[-1]
            else:
                ext = "no_extension"

            file_types[ext] = file_types.get(ext, 0) + 1

        return file_types

    def _categorize_risk_levels(self, critical_files: List[Tuple[str, Dict[str, float]]]) -> Dict[str, int]:
        """Categorize files by risk level."""
        risk_categories = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0}

        for _, metrics in critical_files:
            complexity = metrics["complexity"]
            change_frequency = metrics["change_frequency"]

            if complexity > 10 or change_frequency > 20:
                risk_categories["CRITICAL"] += 1
            elif complexity > 5 or change_frequency > 10:
                risk_categories["HIGH"] += 1
            else:
                risk_categories["MEDIUM"] += 1

        return risk_categories

    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on critical file analysis."""
        critical_files = results.get("critical_files", [])
        total_files = results.get("total_files", 0)

        recommendations = []

        if not critical_files:
            recommendations.append("No critical files identified - good file health")
            return recommendations

        critical_count = len(critical_files)
        critical_ratio = critical_count / total_files if total_files > 0 else 0

        if critical_ratio > 0.3:
            recommendations.extend(
                [
                    "HIGH RISK: Large proportion of files are critical",
                    "Consider refactoring to reduce complexity",
                    "Implement comprehensive testing for critical files",
                    "Establish strict code review process for critical files",
                ]
            )
        elif critical_ratio > 0.2:
            recommendations.extend(
                [
                    "Monitor critical files closely",
                    "Increase test coverage for critical components",
                    "Consider breaking down complex files",
                ]
            )

        if critical_count > 0:
            recommendations.extend(
                [
                    f"Focus on the top {min(5, critical_count)} most critical files",
                    "Implement monitoring for critical file changes",
                    "Ensure critical files have comprehensive documentation",
                    "Consider pair programming for changes to critical files",
                ]
            )

        return recommendations
