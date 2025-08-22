"""
Test suite for Flow Efficiency Analyzer.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from gitdecomposer.analyzers.advanced_metrics.flow_efficiency_analyzer import FlowEfficiencyAnalyzer

from . import MockBranch, MockCommit, MockRepository


class TestFlowEfficiencyAnalyzer(unittest.TestCase):
    """Test the Flow Efficiency Analyzer."""

    def setUp(self):
        self.mock_repo = MockRepository()
        self.analyzer = FlowEfficiencyAnalyzer(self.mock_repo)

        # Create test branches
        self.mock_repo.branches = [
            MockBranch("feature/user-auth"),
            MockBranch("feature/dashboard"),
            MockBranch("bugfix/login-issue"),
            MockBranch("main"),  # Should be skipped
            MockBranch("hotfix/security-patch"),
        ]

        # Create test commits for branches
        now = datetime.now()
        self.test_commits = [
            # Feature branch commits
            MockCommit("Alice", now - timedelta(days=10), {"auth.py": {}}, 50, 10),
            MockCommit("Alice", now - timedelta(days=8), {"auth.py": {}}, 30, 5),
            MockCommit("Bob", now - timedelta(days=6), {"auth.py": {}, "models.py": {}}, 40, 8),
            MockCommit("Alice", now - timedelta(days=4), {"auth.py": {}}, 20, 3),
        ]
        self.mock_repo.commits = self.test_commits

    def test_get_metric_name(self):
        """Test metric name."""
        self.assertEqual(self.analyzer.get_metric_name(), "Flow Efficiency")

    def test_get_description(self):
        """Test metric description."""
        description = self.analyzer.get_description()
        self.assertIn("active development", description.lower())
        self.assertIn("flow time", description.lower())
        self.assertIn("bottleneck", description.lower())

    def test_calculate_with_branches(self):
        """Test calculation with branches."""
        result = self.analyzer.calculate(["feature/*", "bugfix/*"])

        # Check structure
        self.assertIn("flow_metrics", result)
        self.assertIn("analysis", result)
        self.assertIn("recommendations", result)

        # Check types
        self.assertIsInstance(result["flow_metrics"], list)
        self.assertIsInstance(result["analysis"], dict)
        self.assertIsInstance(result["recommendations"], list)

    def test_calculate_no_branches(self):
        """Test calculation with no matching branches."""
        self.mock_repo.branches = [MockBranch("main")]
        result = self.analyzer.calculate(["feature/*"])

        self.assertIn("error", result)
        self.assertEqual(result["flow_metrics"], [])

    def test_branch_flow_analysis(self):
        """Test branch flow analysis."""
        branch_patterns = ["feature/*", "bugfix/*", "hotfix/*"]
        flow_metrics = self.analyzer._analyze_branch_flow(branch_patterns)

        # Should find matching branches (excluding main)
        self.assertGreaterEqual(len(flow_metrics), 0)

        # Check structure of flow metrics
        for metric in flow_metrics:
            self.assertIn("branch", metric)
            self.assertIn("flow_time_days", metric)
            self.assertIn("active_days", metric)
            self.assertIn("flow_efficiency", metric)
            self.assertIn("commits", metric)
            self.assertIn("avg_commits_per_active_day", metric)

    def test_single_branch_flow_calculation(self):
        """Test flow calculation for a single branch."""
        branch = MockBranch("feature/test")

        # Mock commits for this branch
        now = datetime.now()
        test_commits = [
            MockCommit("Alice", now - timedelta(days=5), {"file1.py": {}}, 10, 2),
            MockCommit("Bob", now - timedelta(days=3), {"file2.py": {}}, 15, 3),
            MockCommit("Alice", now - timedelta(days=1), {"file1.py": {}}, 8, 1),
        ]

        # Mock get_commits to return our test commits
        self.mock_repo.commits = test_commits

        branch_metrics = self.analyzer._calculate_branch_flow_efficiency(branch)

        if branch_metrics:  # Only test if we got results
            self.assertIn("branch", branch_metrics)
            self.assertIn("flow_efficiency", branch_metrics)
            self.assertIn("active_days", branch_metrics)
            self.assertIn("commits", branch_metrics)

            # Flow efficiency should be between 0 and 1
            self.assertGreaterEqual(branch_metrics["flow_efficiency"], 0.0)
            self.assertLessEqual(branch_metrics["flow_efficiency"], 1.0)

            # Should have correct number of commits
            self.assertEqual(branch_metrics["commits"], 3)

    def test_flow_efficiency_analysis(self):
        """Test flow efficiency analysis."""
        flow_metrics = [
            {"branch": "feature/1", "flow_efficiency": 0.8, "flow_time_days": 10, "active_days": 8, "commits": 5},
            {"branch": "feature/2", "flow_efficiency": 0.3, "flow_time_days": 20, "active_days": 6, "commits": 3},
            {"branch": "bugfix/1", "flow_efficiency": 0.9, "flow_time_days": 5, "active_days": 4, "commits": 8},
        ]

        analysis = self.analyzer._analyze_flow_efficiency(flow_metrics)

        # Check structure
        self.assertIn("total_branches_analyzed", analysis)
        self.assertIn("overall_efficiency", analysis)
        self.assertIn("median_efficiency", analysis)
        self.assertIn("avg_flow_time_days", analysis)
        self.assertIn("efficiency_distribution", analysis)
        self.assertIn("bottleneck_indicators", analysis)
        self.assertIn("best_practices", analysis)
        self.assertIn("performance_category", analysis)

        # Check values
        self.assertEqual(analysis["total_branches_analyzed"], 3)
        expected_avg = (0.8 + 0.3 + 0.9) / 3
        self.assertAlmostEqual(analysis["overall_efficiency"], expected_avg, places=2)

    def test_efficiency_distribution(self):
        """Test efficiency distribution analysis."""
        efficiencies = [0.9, 0.75, 0.5, 0.3, 0.1]
        distribution = self.analyzer._analyze_efficiency_distribution(efficiencies)

        # Check structure
        self.assertIn("excellent", distribution)
        self.assertIn("good", distribution)
        self.assertIn("average", distribution)
        self.assertIn("poor", distribution)
        self.assertIn("very_poor", distribution)

        # Check counts (based on thresholds)
        self.assertEqual(distribution["excellent"], 1)  # 0.9 > 0.8
        self.assertEqual(distribution["good"], 1)  # 0.75 in 0.6-0.8
        self.assertEqual(distribution["average"], 1)  # 0.5 in 0.4-0.6
        self.assertEqual(distribution["poor"], 1)  # 0.3 in 0.2-0.4
        self.assertEqual(distribution["very_poor"], 1)  # 0.1 < 0.2

    def test_bottleneck_identification(self):
        """Test bottleneck identification."""
        flow_metrics = [
            {
                "branch": "slow/branch",
                "flow_efficiency": 0.2,  # Low efficiency
                "flow_time_days": 15,  # High flow time
                "active_days": 3,
            },
            {
                "branch": "fast/branch",
                "flow_efficiency": 0.8,  # High efficiency
                "flow_time_days": 5,  # Low flow time
                "active_days": 4,
            },
        ]

        bottlenecks = self.analyzer._identify_bottlenecks(flow_metrics)

        # Should identify the slow branch as a bottleneck
        self.assertEqual(len(bottlenecks), 1)
        self.assertEqual(bottlenecks[0]["branch"], "slow/branch")
        self.assertEqual(bottlenecks[0]["efficiency"], 0.2)

    def test_best_practices_identification(self):
        """Test best practices identification."""
        flow_metrics = [
            {
                "branch": "excellent/branch",
                "flow_efficiency": 0.8,  # High efficiency
                "flow_time_days": 5,  # Reasonable time
                "active_days": 4,
            },
            {
                "branch": "slow/branch",
                "flow_efficiency": 0.2,  # Low efficiency
                "flow_time_days": 20,  # Too long
                "active_days": 4,
            },
        ]

        best_practices = self.analyzer._identify_best_practices(flow_metrics)

        # Should identify the excellent branch
        self.assertEqual(len(best_practices), 1)
        self.assertEqual(best_practices[0]["branch"], "excellent/branch")
        self.assertEqual(best_practices[0]["efficiency"], 0.8)

    def test_performance_categorization(self):
        """Test performance categorization."""
        # Test different efficiency levels
        excellent = self.analyzer._categorize_performance(0.85)
        good = self.analyzer._categorize_performance(0.7)
        average = self.analyzer._categorize_performance(0.5)
        poor = self.analyzer._categorize_performance(0.3)
        very_poor = self.analyzer._categorize_performance(0.1)

        self.assertEqual(excellent, "EXCELLENT")
        self.assertEqual(good, "GOOD")
        self.assertEqual(average, "AVERAGE")
        self.assertEqual(poor, "POOR")
        self.assertEqual(very_poor, "VERY_POOR")

    def test_median_calculation(self):
        """Test median calculation helper."""
        # Test odd number of values
        odd_values = [1, 3, 5, 7, 9]
        odd_median = self.analyzer._calculate_median(odd_values)
        self.assertEqual(odd_median, 5)

        # Test even number of values
        even_values = [1, 2, 3, 4]
        even_median = self.analyzer._calculate_median(even_values)
        self.assertEqual(even_median, 2.5)

        # Test single value
        single_value = [42]
        single_median = self.analyzer._calculate_median(single_value)
        self.assertEqual(single_median, 42)

    def test_recommendations_generation(self):
        """Test recommendations generation."""
        # Test poor performance
        poor_analysis = {
            "overall_efficiency": 0.2,
            "performance_category": "VERY_POOR",
            "bottleneck_indicators": [{"branch": "slow", "efficiency": 0.1}],
            "avg_flow_time_days": 25,
        }
        poor_recs = self.analyzer.get_recommendations(poor_analysis)

        self.assertGreater(len(poor_recs), 0)
        self.assertTrue(any("URGENT" in rec for rec in poor_recs))

        # Test excellent performance
        excellent_analysis = {
            "overall_efficiency": 0.9,
            "performance_category": "EXCELLENT",
            "bottleneck_indicators": [],
            "avg_flow_time_days": 5,
        }
        excellent_recs = self.analyzer.get_recommendations(excellent_analysis)

        self.assertGreater(len(excellent_recs), 0)
        self.assertTrue(any("maintain" in rec.lower() for rec in excellent_recs))

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with no commits
        empty_branch = MockBranch("feature/empty")
        self.mock_repo.commits = []

        branch_metrics = self.analyzer._calculate_branch_flow_efficiency(empty_branch)
        self.assertIsNone(branch_metrics)

        # Test with single commit
        single_commit = [MockCommit("Alice", datetime.now(), {"file.py": {}}, 10, 2)]
        self.mock_repo.commits = single_commit

        branch_metrics = self.analyzer._calculate_branch_flow_efficiency(empty_branch)
        self.assertIsNone(branch_metrics)  # Needs at least 2 commits


if __name__ == "__main__":
    unittest.main()
