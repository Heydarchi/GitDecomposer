"""
Single Point of Failure Files Analyzer - Finds files with dangerously
low contributor diversity.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from .base import BaseMetricAnalyzer


class SinglePointFailureAnalyzer(BaseMetricAnalyzer):
    """
    Identifies files with dangerously low contributor diversity.

    Single Point of Failure (SPOF) files are those where one contributor
    dominates the changes, creating a knowledge bottleneck and risk.
    """

    def __init__(self, repository):
        super().__init__(repository)

    def get_metric_name(self) -> str:
        return "Single Point of Failure Files"

    def get_description(self) -> str:
        return "Identifies files with dangerously low contributor diversity " "where one person dominates changes."

    def calculate(
        self, lookback_months: int = 6, dominance_threshold: float = 0.9, min_contributor_threshold: int = 3
    ) -> Dict[str, Any]:
        """
        Find single point of failure files.

        Args:
            lookback_months: How many months back to analyze
            dominance_threshold: Minimum dominance ratio to flag (0.9 = 90%)
            min_contributor_threshold: Maximum contributors for SPOF consideration

        Returns:
            Dictionary containing SPOF analysis results
        """
        spof_files = self._find_spof_files(lookback_months, dominance_threshold, min_contributor_threshold)

        analysis = self._analyze_spof_files(spof_files)

        return {
            "spof_files": spof_files,
            "spof_count": len(spof_files),
            "analysis": analysis,
            "risk_level": self._assess_overall_risk(spof_files),
            "recommendations": self.get_recommendations({"spof_files": spof_files, "spof_count": len(spof_files)}),
        }

    def _find_spof_files(
        self, lookback_months: int, dominance_threshold: float, min_contributor_threshold: int
    ) -> List[Dict[str, Any]]:
        """Find files that qualify as single points of failure."""
        spof_files = []
        since_date = datetime.now() - timedelta(days=30 * lookback_months)

        # Get all commits in the timeframe
        commits = self.repository.get_commits(since=since_date)

        # Group commits by file
        file_commits = {}
        for commit in commits:
            for file_path in commit.stats.files:
                if file_path not in file_commits:
                    file_commits[file_path] = []
                file_commits[file_path].append(commit)

        # Analyze each file for SPOF characteristics
        for file_path, commits_list in file_commits.items():
            if not commits_list:
                continue

            # Count contributions per author
            author_contributions = {}
            total_changes = 0

            for commit in commits_list:
                author = commit.author.name
                # Use commit count as weight (in real implementation, use lines changed)
                lines_changed = self._get_lines_changed_in_file(commit, file_path)

                author_contributions[author] = author_contributions.get(author, 0) + lines_changed
                total_changes += lines_changed

            # Check SPOF criteria
            if total_changes == 0:
                continue

            max_contribution = max(author_contributions.values())
            dominant_ratio = max_contribution / total_changes
            contributor_count = len(author_contributions)

            if dominant_ratio > dominance_threshold and contributor_count < min_contributor_threshold:

                dominant_author = max(author_contributions, key=author_contributions.get)

                spof_files.append(
                    {
                        "file": file_path,
                        "dominant_author": dominant_author,
                        "dominance_ratio": dominant_ratio,
                        "contributor_count": contributor_count,
                        "total_changes": total_changes,
                        "author_contributions": author_contributions,
                        "recent_commits": len(commits_list),
                        "file_criticality": self._assess_file_criticality(file_path),
                    }
                )

        # Sort by dominance ratio (highest risk first)
        spof_files.sort(key=lambda x: x["dominance_ratio"], reverse=True)

        return spof_files

    def _get_lines_changed_in_file(self, commit, file_path: str) -> int:
        """Get the number of lines changed in a specific file for a commit."""
        # Simplified implementation - in reality, would parse commit diff
        # For now, return 1 as a unit of change
        return 1

    def _assess_file_criticality(self, file_path: str) -> str:
        """Assess how critical a file is to the project."""
        critical_patterns = ["main", "index", "app", "core", "base", "config", "__init__", "setup", "requirements"]

        file_name = file_path.lower()

        # Check for critical patterns
        for pattern in critical_patterns:
            if pattern in file_name:
                return "HIGH"

        # Check file extension for importance
        important_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h"]
        for ext in important_extensions:
            if file_path.endswith(ext):
                return "MEDIUM"

        return "LOW"

    def _analyze_spof_files(self, spof_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the SPOF files to provide insights."""
        if not spof_files:
            return {"total_spof_files": 0, "risk_summary": "No single points of failure detected"}

        # Analyze by criticality
        criticality_distribution = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        dominance_ratios = []
        contributor_counts = []
        dominant_authors = {}

        for spof_file in spof_files:
            criticality = spof_file["file_criticality"]
            criticality_distribution[criticality] += 1

            dominance_ratios.append(spof_file["dominance_ratio"])
            contributor_counts.append(spof_file["contributor_count"])

            author = spof_file["dominant_author"]
            dominant_authors[author] = dominant_authors.get(author, 0) + 1

        # Find authors who dominate multiple files
        multi_file_dominators = {author: count for author, count in dominant_authors.items() if count > 1}

        analysis = {
            "total_spof_files": len(spof_files),
            "criticality_distribution": criticality_distribution,
            "avg_dominance_ratio": sum(dominance_ratios) / len(dominance_ratios),
            "avg_contributor_count": sum(contributor_counts) / len(contributor_counts),
            "multi_file_dominators": multi_file_dominators,
            "highest_risk_files": spof_files[:5],  # Top 5 highest risk
            "risk_summary": self._generate_risk_summary(spof_files, criticality_distribution),
        }

        return analysis

    def _generate_risk_summary(self, spof_files: List[Dict[str, Any]], criticality_dist: Dict[str, int]) -> str:
        """Generate a risk summary based on SPOF analysis."""
        total_files = len(spof_files)
        high_criticality = criticality_dist.get("HIGH", 0)

        if high_criticality > 5:
            return f"CRITICAL: {high_criticality} high-criticality SPOF files detected"
        elif high_criticality > 2:
            return f"HIGH RISK: {high_criticality} high-criticality SPOF files detected"
        elif total_files > 10:
            return f"MODERATE RISK: {total_files} SPOF files detected"
        elif total_files > 0:
            return f"LOW RISK: {total_files} SPOF files detected"
        else:
            return "No single points of failure detected"

    def _assess_overall_risk(self, spof_files: List[Dict[str, Any]]) -> str:
        """Assess the overall risk level based on SPOF files."""
        if not spof_files:
            return "LOW"

        high_criticality_count = sum(1 for spof in spof_files if spof["file_criticality"] == "HIGH")

        total_spof_count = len(spof_files)

        if high_criticality_count > 5 or total_spof_count > 20:
            return "CRITICAL"
        elif high_criticality_count > 2 or total_spof_count > 10:
            return "HIGH"
        elif high_criticality_count > 0 or total_spof_count > 5:
            return "MEDIUM"
        else:
            return "LOW"

    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on SPOF analysis."""
        spof_files = results.get("spof_files", [])
        spof_count = results.get("spof_count", 0)

        recommendations = []

        if spof_count == 0:
            recommendations.append("Excellent! No single points of failure detected")
            return recommendations

        # General recommendations based on SPOF count
        if spof_count > 20:
            recommendations.extend(
                [
                    "URGENT: Critical number of SPOF files detected",
                    "Implement immediate knowledge transfer sessions",
                    "Establish mandatory pair programming for all SPOF files",
                    "Create comprehensive documentation for all SPOF files",
                ]
            )
        elif spof_count > 10:
            recommendations.extend(
                [
                    "High risk: Significant number of SPOF files",
                    "Prioritize knowledge sharing for critical files",
                    "Implement code review requirements for SPOF files",
                ]
            )
        elif spof_count > 5:
            recommendations.extend(
                [
                    "Moderate risk: Address SPOF files systematically",
                    "Encourage more contributors to work on isolated files",
                ]
            )

        # Specific recommendations based on file analysis
        high_criticality_files = [spof for spof in spof_files if spof.get("file_criticality") == "HIGH"]

        if high_criticality_files:
            recommendations.extend(
                [
                    f"PRIORITY: {len(high_criticality_files)} critical files have SPOF risk",
                    "Schedule immediate knowledge transfer for critical files",
                    "Consider refactoring to reduce complexity of critical files",
                ]
            )

        # Author-specific recommendations
        multi_dominators = {}
        for spof in spof_files:
            author = spof["dominant_author"]
            if author not in multi_dominators:
                multi_dominators[author] = []
            multi_dominators[author].append(spof["file"])

        authors_with_multiple = {author: files for author, files in multi_dominators.items() if len(files) > 1}

        if authors_with_multiple:
            recommendations.append(
                f"Focus on knowledge transfer from authors who dominate multiple files: "
                f"{', '.join(authors_with_multiple.keys())}"
            )

        return recommendations
