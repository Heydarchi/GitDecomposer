"""
AdvancedMetrics module for sophisticated repository analysis.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd
import math
import re
import logging
from datetime import datetime, timedelta

from ..core.git_repository import GitRepository

logger = logging.getLogger(__name__)


class AdvancedMetrics:
    """
    Advanced metrics analyzer for sophisticated repository insights.

    This class provides advanced analytical capabilities including
    maintainability index, technical debt analysis, and test coverage.
    """

    def __init__(self, git_repo: GitRepository):
        """
        Initialize the AdvancedMetrics analyzer.

        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        logger.info("Initialized AdvancedMetrics")

    def calculate_maintainability_index(self) -> Dict[str, Any]:
        """
        Calculate code maintainability index based on various metrics.

        Returns:
            Dict[str, Any]: Maintainability metrics and analysis
        """
        try:
            commits = self.git_repo.get_all_commits()
            if not commits:
                return {
                    "overall_maintainability_score": 0,
                    "file_maintainability": pd.DataFrame(),
                    "maintainability_factors": {},
                    "recommendations": [],
                }

            # Collect file metrics
            file_metrics = defaultdict(
                lambda: {
                    "commit_count": 0,
                    "author_count": 0,
                    "total_changes": 0,
                    "avg_commit_size": 0,
                    "last_change_days": 0,
                    "first_change_days": 0,
                    # complexity_score will be computed after aggregation
                }
            )

            all_authors = set()

            for commit in commits:
                try:
                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    days_since_commit = (datetime.now() - commit_date).days

                    changed_files = self.git_repo.get_changed_files(commit.hexsha)
                    commit_stats = commit.stats
                    all_authors.add(commit.author.name)

                    for file_path in changed_files.keys():
                        metrics = file_metrics[file_path]

                        # Update basic metrics
                        metrics["commit_count"] += 1

                        # Get changes from commit stats
                        changes = 0
                        if file_path in commit_stats.files:
                            file_stat = commit_stats.files[file_path]
                            if (
                                isinstance(file_stat, dict)
                                and "insertions" in file_stat
                                and "deletions" in file_stat
                            ):
                                changes = file_stat["insertions"] + file_stat["deletions"]

                        metrics["total_changes"] += changes

                        # Track unique authors for this file
                        if "authors" not in metrics:
                            metrics["authors"] = set()
                        metrics["authors"].add(commit.author.name)

                        # Update last/first change (in days since now)
                        if (
                            metrics["last_change_days"] == 0
                            or days_since_commit < metrics["last_change_days"]
                        ):
                            metrics["last_change_days"] = days_since_commit
                        if (
                            metrics["first_change_days"] == 0
                            or days_since_commit > metrics["first_change_days"]
                        ):
                            metrics["first_change_days"] = days_since_commit

                        # Defer complexity calculation until after aggregation

                except Exception as e:
                    logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                    continue

            # Calculate maintainability scores for each file
            maintainability_data = []

            for file_path, metrics in file_metrics.items():
                if metrics["commit_count"] == 0:
                    continue

                # Calculate average commit size
                metrics["avg_commit_size"] = metrics["total_changes"] / metrics["commit_count"]
                metrics["author_count"] = len(metrics.get("authors", set()))
                # Compute complexity based on file type and total historical changes
                metrics["complexity_score"] = self._calculate_file_complexity_score(
                    file_path, metrics["total_changes"]
                )

                # Calculate maintainability score (0-100 scale)
                # Lower scores for high complexity, frequent changes, many authors, large commits.
                complexity_penalty = min(
                    metrics["complexity_score"], 30
                )  # log-scaled complexity, capped
                # Use commit density over active period (commits per month) instead of raw count
                active_days = max(1, metrics["first_change_days"] - metrics["last_change_days"] + 1)
                commits_per_month = metrics["commit_count"] / max(1.0, active_days / 30.0)
                change_frequency_penalty = min(
                    commits_per_month * 3.0, 20
                )  # ~3 pts per commit/month
                author_penalty = min(max(0, metrics["author_count"] - 1) * 5, 15)
                size_penalty = min((metrics["avg_commit_size"] / 100) * 10, 10)
                # Older, stable files get a small bonus
                staleness_bonus = min((metrics["last_change_days"] / 365) * 5, 5)

                maintainability_score = max(
                    0,
                    min(
                        100,
                        100
                        - (
                            complexity_penalty
                            + change_frequency_penalty
                            + author_penalty
                            + size_penalty
                        )
                        + staleness_bonus,
                    ),
                )

                # Categorize maintainability
                if maintainability_score >= 80:
                    category = "Excellent"
                elif maintainability_score >= 60:
                    category = "Good"
                elif maintainability_score >= 40:
                    category = "Fair"
                elif maintainability_score >= 20:
                    category = "Poor"
                else:
                    category = "Critical"

                maintainability_data.append(
                    {
                        "file_path": file_path,
                        "maintainability_score": maintainability_score,
                        "category": category,
                        "commit_count": metrics["commit_count"],
                        "author_count": metrics["author_count"],
                        "total_changes": metrics["total_changes"],
                        "avg_commit_size": metrics["avg_commit_size"],
                        "complexity_score": metrics["complexity_score"],
                        "last_change_days": metrics["last_change_days"],
                        "extension": Path(file_path).suffix.lower() or "no_extension",
                    }
                )

            file_maintainability = pd.DataFrame(maintainability_data)

            # Calculate overall metrics
            if not file_maintainability.empty:
                overall_score = file_maintainability["maintainability_score"].mean()

                # Maintainability factors
                factors = {
                    "avg_commits_per_file": file_maintainability["commit_count"].mean(),
                    "avg_authors_per_file": file_maintainability["author_count"].mean(),
                    "avg_complexity": file_maintainability["complexity_score"].mean(),
                    "files_needing_attention": len(
                        file_maintainability[file_maintainability["maintainability_score"] < 40]
                    ),
                    "excellent_files": len(
                        file_maintainability[file_maintainability["maintainability_score"] >= 80]
                    ),
                    "total_files_analyzed": len(file_maintainability),
                }

                # Generate recommendations
                recommendations = self._generate_maintainability_recommendations(
                    file_maintainability, factors
                )
            else:
                overall_score = 0
                factors = {}
                recommendations = ["No file data available for analysis"]

            logger.info(f"Calculated maintainability index: {overall_score:.1f}")
            return {
                "overall_maintainability_score": overall_score,
                "file_maintainability": file_maintainability,
                "maintainability_factors": factors,
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.error(f"Error calculating maintainability index: {e}")
            return {
                "overall_maintainability_score": 0,
                "file_maintainability": pd.DataFrame(),
                "maintainability_factors": {},
                "recommendations": [],
            }

    def _calculate_file_complexity_score(self, file_path: str, total_changes: int) -> float:
        """Calculate a heuristic complexity score by file type and cumulative change volume.

        Uses a log scale on total historical changes so very old files aren't unfairly penalized.
        Returns an unbounded value typically in the 0-30 range and then capped by caller.
        """
        extension = Path(file_path).suffix.lower()

        # Base complexity by file type
        complexity_map = {
            ".py": 3,
            ".java": 3,
            ".cpp": 4,
            ".c": 4,
            ".js": 2,
            ".ts": 2,
            ".jsx": 2,
            ".tsx": 2,
            ".php": 2,
            ".rb": 2,
            ".go": 2,
            ".rs": 3,
            ".html": 1,
            ".css": 1,
            ".scss": 1,
            ".less": 1,
            ".json": 0.5,
            ".xml": 0.5,
            ".yaml": 0.5,
            ".yml": 0.5,
            ".md": 0.2,
            ".txt": 0.1,
            ".rst": 0.2,
        }

        base_complexity = complexity_map.get(extension, 1.5)
        # Log scale keeps growth reasonable for very high churn
        return base_complexity * math.log1p(max(0, total_changes))

    def calculate_technical_debt_accumulation(self) -> Dict[str, Any]:
        """
        Calculate technical debt accumulation rate over time.

        Returns:
            Dict[str, Any]: Technical debt metrics and trends
        """
        try:
            commits = self.git_repo.get_all_commits()
            if not commits:
                return {
                    "debt_accumulation_rate": 0,
                    "debt_trend": pd.DataFrame(),
                    "debt_hotspots": [],
                    "debt_by_type": {},
                }

            # Technical debt indicators in commit messages
            # Split into introducing vs reducing indicators to avoid counting refactors as debt accumulation
            introducing_patterns = {
                "quick_fix": r"\b(quick\s*fix|hotfix|patch|band\s*aid)\b",
                "todo": r"\b(todo|fixme|hack|temporary|temp)\b",
                "workaround": r"\b(workaround|work\s*around|bypass)\b",
                "code_smell": r"\b(smell|ugly|messy|dirty)\b",
                "debt_terms": r"\b(incur|introduc\w*\s+debt)\b",
            }
            reducing_patterns = {
                "refactor": r"\b(refactor(ing)?|cleanup|clean\s*up|restructure|pay(ing)?\s+debt|address\s+debt|remove\s+todo\w*)\b"
            }

            monthly_debt = defaultdict(
                lambda: {
                    "total_commits": 0,
                    "debt_commits_introducing": 0,
                    "debt_commits_reducing": 0,
                    "debt_types": Counter(),
                }
            )

            file_debt_scores = defaultdict(float)

            for commit in commits:
                try:
                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    month_key = commit_date.strftime("%Y-%m")

                    monthly_debt[month_key]["total_commits"] += 1

                    # Check commit message for debt indicators
                    message_lower = commit.message.lower()
                    introducing = False
                    reducing = False

                    for debt_type, pattern in introducing_patterns.items():
                        if re.search(pattern, message_lower):
                            monthly_debt[month_key]["debt_types"][f"introducing:{debt_type}"] += 1
                            introducing = True

                    for debt_type, pattern in reducing_patterns.items():
                        if re.search(pattern, message_lower):
                            monthly_debt[month_key]["debt_types"][f"reducing:{debt_type}"] += 1
                            reducing = True

                    if introducing or reducing:
                        # Track net effect in files (+1 for introducing, -1 for reducing)
                        changed_files = self.git_repo.get_changed_files(commit.hexsha)
                        for file_path in changed_files.keys():
                            file_debt_scores[file_path] += (1 if introducing else 0) + (
                                -1 if reducing else 0
                            )

                    if introducing:
                        monthly_debt[month_key]["debt_commits_introducing"] += 1
                    if reducing:
                        monthly_debt[month_key]["debt_commits_reducing"] += 1

                except Exception as e:
                    logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                    continue

            # Calculate debt accumulation trend
            trend_data = []
            for month in sorted(monthly_debt.keys()):
                data = monthly_debt[month]
                introducing_rate = (
                    (data["debt_commits_introducing"] / data["total_commits"] * 100)
                    if data["total_commits"] > 0
                    else 0
                )
                reducing_rate = (
                    (data["debt_commits_reducing"] / data["total_commits"] * 100)
                    if data["total_commits"] > 0
                    else 0
                )

                trend_data.append(
                    {
                        "month": month,
                        "total_commits": data["total_commits"],
                        "debt_commits_introducing": data["debt_commits_introducing"],
                        "debt_commits_reducing": data["debt_commits_reducing"],
                        "introducing_rate": introducing_rate,
                        "reducing_rate": reducing_rate,
                        "net_debt_delta_percentage": introducing_rate - reducing_rate,
                        # Backward-compat fields
                        "debt_commits": data["debt_commits_introducing"],
                        "debt_rate": introducing_rate,
                    }
                )

            debt_trend = pd.DataFrame(trend_data)
            if not debt_trend.empty:
                debt_trend["month"] = pd.to_datetime(debt_trend["month"])

            # Calculate overall debt accumulation rate
            total_commits = sum(data["total_commits"] for data in monthly_debt.values())
            total_introducing = sum(
                data["debt_commits_introducing"] for data in monthly_debt.values()
            )
            total_reducing = sum(data["debt_commits_reducing"] for data in monthly_debt.values())
            debt_accumulation_rate = (
                (total_introducing / total_commits * 100) if total_commits > 0 else 0
            )
            net_debt_delta_percentage = (
                ((total_introducing - total_reducing) / total_commits * 100)
                if total_commits > 0
                else 0
            )

            # Identify debt hotspots (files with highest debt scores)
            debt_hotspots = [
                {"file_path": file_path, "debt_score": score}
                for file_path, score in sorted(
                    file_debt_scores.items(), key=lambda x: x[1], reverse=True
                )[:20]
            ]

            # Aggregate debt by type
            debt_by_type = {}
            for data in monthly_debt.values():
                for debt_type, count in data["debt_types"].items():
                    debt_by_type[debt_type] = debt_by_type.get(debt_type, 0) + count

            logger.info(f"Technical debt accumulation rate: {debt_accumulation_rate:.1f}%")
            return {
                "debt_accumulation_rate": debt_accumulation_rate,  # % of commits introducing debt
                "net_debt_delta_percentage": net_debt_delta_percentage,  # introducing minus reducing
                "debt_trend": debt_trend,
                "debt_hotspots": debt_hotspots,
                "debt_by_type": debt_by_type,
                # Backward-compat aggregate
                "total_debt_commits": total_introducing,
                "total_debt_commits_introducing": total_introducing,
                "total_debt_commits_reducing": total_reducing,
                "total_commits": total_commits,
            }

        except Exception as e:
            logger.error(f"Error calculating technical debt: {e}")
            return {
                "debt_accumulation_rate": 0,
                "debt_trend": pd.DataFrame(),
                "debt_hotspots": [],
                "debt_by_type": {},
            }

    def calculate_test_to_code_ratio(self) -> Dict[str, Any]:
        """
        Calculate the ratio of test files to production code files.

        Returns:
            Dict[str, Any]: Test coverage and ratio metrics
        """
        try:
            # Prefer analyzing current repository state (HEAD) rather than all historical changes
            current_files = []
            try:
                # Requires GitRepository.get_all_files_at_head
                current_files = getattr(self.git_repo, "get_all_files_at_head")()
            except Exception:
                # Fallback: derive from commit history if helper not available
                commits = self.git_repo.get_all_commits()
                seen = set()
                for commit in commits:
                    changed_files = self.git_repo.get_changed_files(commit.hexsha)
                    for fp in changed_files.keys():
                        seen.add(fp)
                current_files = list(seen)

            # Test file patterns
            test_patterns = {
                "test_files": r"(^test_|_test\.|^spec_|_spec\.)",
                # Match directory segments to avoid matching words like "contest"
                "test_dirs": r"(^|/)(tests?|spec|__tests__|test)(/|$)",
                "test_extensions": {
                    ".test.js",
                    ".spec.js",
                    ".test.ts",
                    ".spec.ts",
                    ".test.py",
                    ".spec.py",
                },
            }

            test_files = set()
            code_files = set()
            directories = defaultdict(lambda: {"total": 0, "tests": 0})

            # Classify files in current HEAD
            for file_path in current_files:
                path_obj = Path(file_path)
                extension = path_obj.suffix.lower()
                file_name = path_obj.name.lower()
                dir_path = str(path_obj.parent).lower()

                # Track directory
                if len(path_obj.parts) > 1:
                    main_dir = path_obj.parts[0]
                    directories[main_dir]["total"] += 1

                # Check if it's a test file
                is_test = (
                    re.search(test_patterns["test_files"], file_name) is not None
                    or re.search(test_patterns["test_dirs"], str(path_obj).replace("\\", "/"))
                    is not None
                    or any(file_name.endswith(ext) for ext in test_patterns["test_extensions"])
                )

                if is_test:
                    test_files.add(file_path)
                    if len(path_obj.parts) > 1:
                        directories[path_obj.parts[0]]["tests"] += 1
                else:
                    # Consider it a code file if it has a programming language extension
                    code_extensions = {
                        ".py",
                        ".js",
                        ".ts",
                        ".java",
                        ".cpp",
                        ".c",
                        ".go",
                        ".rs",
                        ".php",
                        ".rb",
                    }
                    if extension in code_extensions:
                        code_files.add(file_path)

            # Calculate metrics
            test_files_count = len(test_files)
            code_files_count = len(code_files)
            test_to_code_ratio = (
                (test_files_count / code_files_count) if code_files_count > 0 else 0
            )

            # Find directories without tests
            untested_directories = []
            for dir_name, counts in directories.items():
                if counts["total"] > 1 and counts["tests"] == 0:  # Has files but no tests
                    untested_directories.append(
                        {"directory": dir_name, "file_count": counts["total"]}
                    )

            # Sort by file count descending
            untested_directories.sort(key=lambda x: x["file_count"], reverse=True)

            # Calculate test pattern usage
            pattern_usage = {}
            for test_file in test_files:
                file_name = Path(test_file).name.lower()
                if "test_" in file_name:
                    pattern_usage["prefix_test"] = pattern_usage.get("prefix_test", 0) + 1
                elif "_test." in file_name:
                    pattern_usage["suffix_test"] = pattern_usage.get("suffix_test", 0) + 1
                elif "spec_" in file_name:
                    pattern_usage["prefix_spec"] = pattern_usage.get("prefix_spec", 0) + 1
                elif "_spec." in file_name:
                    pattern_usage["suffix_spec"] = pattern_usage.get("suffix_spec", 0) + 1
                elif "/test" in test_file.lower():
                    pattern_usage["test_directory"] = pattern_usage.get("test_directory", 0) + 1

            logger.info(f"Test to code ratio: {test_to_code_ratio:.2f}")
            return {
                "test_to_code_ratio": test_to_code_ratio,
                "test_files_count": test_files_count,
                "code_files_count": code_files_count,
                "total_files_analyzed": len(current_files),
                "test_patterns": pattern_usage,
                "untested_directories": untested_directories[:10],  # Top 10
                "test_coverage_percentage": (test_to_code_ratio * 100),
                "recommendations": self._generate_test_recommendations(
                    test_to_code_ratio, untested_directories
                ),
            }

        except Exception as e:
            logger.error(f"Error calculating test to code ratio: {e}")
            return {
                "test_to_code_ratio": 0,
                "test_files_count": 0,
                "code_files_count": 0,
                "test_patterns": {},
                "untested_directories": [],
            }

    def _generate_maintainability_recommendations(
        self, df: pd.DataFrame, factors: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for improving maintainability."""
        recommendations = []

        if df.empty:
            return ["No data available for recommendations"]

        avg_score = df["maintainability_score"].mean()

        if avg_score < 40:
            recommendations.append(
                "Critical: Overall maintainability is very low - prioritize refactoring"
            )
        elif avg_score < 60:
            recommendations.append(
                "Low maintainability - focus on reducing complexity and commit sizes"
            )
        elif avg_score < 80:
            recommendations.append("Moderate maintainability - continue improving code quality")
        else:
            recommendations.append("Good maintainability - maintain current standards")

        # Specific recommendations based on factors
        if factors.get("avg_commits_per_file", 0) > 20:
            recommendations.append(
                "High commit frequency detected - consider breaking down large files"
            )

        if factors.get("avg_authors_per_file", 0) > 3:
            recommendations.append(
                "Many contributors per file - ensure good documentation and code standards"
            )

        if factors.get("files_needing_attention", 0) > 0:
            recommendations.append(
                f"{factors['files_needing_attention']} files need immediate attention"
            )

        return recommendations

    def _generate_test_recommendations(self, ratio: float, untested_dirs: List[Dict]) -> List[str]:
        """Generate recommendations for improving test coverage."""
        recommendations = []

        if ratio < 0.1:
            recommendations.append(
                "Very low test coverage - start adding tests for critical components"
            )
        elif ratio < 0.3:
            recommendations.append("Low test coverage - increase test writing efforts")
        elif ratio < 0.7:
            recommendations.append("Moderate test coverage - continue expanding test suite")
        elif ratio < 1.0:
            recommendations.append("Good test coverage - focus on quality and edge cases")
        else:
            recommendations.append("Excellent test coverage - maintain high standards")

        if untested_dirs:
            top_dirs = [d["directory"] for d in untested_dirs[:3]]
            recommendations.append(f"Add tests to directories: {', '.join(top_dirs)}")

        return recommendations
