"""
Test suite for Bus Factor Analyzer.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from gitdecomposer.analyzers.advanced_metrics.bus_factor_analyzer import BusFactorAnalyzer

from . import MockCommit, MockRepository


class TestBusFactorAnalyzer(unittest.TestCase):
    """Test the Bus Factor Analyzer."""

    def setUp(self):
        self.mock_repo = MockRepository()
        self.analyzer = BusFactorAnalyzer(self.mock_repo)

        # Create test data
        now = datetime.now()
        self.test_commits = [
            MockCommit("Alice", now - timedelta(days=10), {"file1.py": {}}, 100, 20),
            MockCommit("Alice", now - timedelta(days=20), {"file1.py": {}, "file2.py": {}}, 50, 10),
            MockCommit("Bob", now - timedelta(days=15), {"file2.py": {}}, 80, 15),
            MockCommit("Charlie", now - timedelta(days=5), {"file3.py": {}}, 30, 5),
            MockCommit("Alice", now - timedelta(days=30), {"file1.py": {}}, 200, 50),
        ]
        self.mock_repo.commits = self.test_commits

    def test_get_metric_name(self):
        """Test metric name."""
        self.assertEqual(self.analyzer.get_metric_name(), "Bus Factor")

    def test_get_description(self):
        """Test metric description."""
        description = self.analyzer.get_description()
        self.assertIn("minimum number of people", description.lower())
        self.assertIn("project continuity", description.lower())

    def test_calculate_with_commits(self):
        """Test calculation with valid commits."""
        result = self.analyzer.calculate(lookback_months=2)

        # Check structure
        self.assertIn("bus_factor", result)
        self.assertIn("knowledge_weights", result)
        self.assertIn("coverage_analysis", result)
        self.assertIn("risk_level", result)
        self.assertIn("recommendations", result)

        # Check values
        self.assertIsInstance(result["bus_factor"], int)
        self.assertGreater(result["bus_factor"], 0)
        self.assertIn(result["risk_level"], ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.assertIsInstance(result["recommendations"], list)

    def test_calculate_no_commits(self):
        """Test calculation with no commits."""
        self.mock_repo.commits = []
        result = self.analyzer.calculate()

        self.assertEqual(result["bus_factor"], 0)
        self.assertIn("error", result)

    def test_knowledge_weights_calculation(self):
        """Test knowledge weights calculation."""
        knowledge_weights = self.analyzer._calculate_knowledge_weights(6, 90)

        # Should have contributors
        self.assertGreater(len(knowledge_weights), 0)

        # Alice should be present (most active)
        self.assertIn("Alice", knowledge_weights)

        # Check structure
        for author, files in knowledge_weights.items():
            self.assertIsInstance(files, dict)
            for file_path, weight in files.items():
                self.assertIsInstance(weight, (int, float))
                self.assertGreater(weight, 0)

    def test_bus_factor_calculation(self):
        """Test bus factor calculation logic."""
        # Create simple knowledge weights
        knowledge_weights = {
            "Alice": {"file1.py": 10.0, "file2.py": 5.0},
            "Bob": {"file2.py": 3.0, "file3.py": 2.0},
            "Charlie": {"file3.py": 1.0},
        }

        bus_factor, coverage_analysis = self.analyzer._calculate_bus_factor(knowledge_weights, 0.8)

        # Should be reasonable
        self.assertGreater(bus_factor, 0)
        self.assertLessEqual(bus_factor, len(knowledge_weights))

        # Check coverage analysis
        self.assertIn("target_coverage", coverage_analysis)
        self.assertIn("actual_coverage", coverage_analysis)
        self.assertIn("coverage_path", coverage_analysis)

        self.assertEqual(coverage_analysis["target_coverage"], 0.8)
        self.assertGreaterEqual(coverage_analysis["actual_coverage"], 0.8)

    def test_file_complexity_estimation(self):
        """Test file complexity estimation."""
        # Test different file types
        py_complexity = self.analyzer._get_file_complexity("test.py")
        js_complexity = self.analyzer._get_file_complexity("test.js")
        md_complexity = self.analyzer._get_file_complexity("test.md")

        self.assertGreater(py_complexity, md_complexity)
        self.assertEqual(py_complexity, js_complexity)  # Same weight

    def test_file_criticality_estimation(self):
        """Test file criticality estimation."""
        # Test critical files
        main_criticality = self.analyzer._get_file_criticality("main.py")
        index_criticality = self.analyzer._get_file_criticality("index.js")
        regular_criticality = self.analyzer._get_file_criticality("utils.py")

        self.assertGreater(main_criticality, regular_criticality)
        self.assertGreater(index_criticality, regular_criticality)

    def test_risk_assessment(self):
        """Test risk level assessment."""
        # Test different scenarios
        critical_risk = self.analyzer._assess_risk_level(1, 5)
        high_risk = self.analyzer._assess_risk_level(2, 5)
        medium_risk = self.analyzer._assess_risk_level(3, 5)
        low_risk = self.analyzer._assess_risk_level(4, 5)

        self.assertEqual(critical_risk, "CRITICAL")
        self.assertEqual(high_risk, "HIGH")
        self.assertEqual(medium_risk, "MEDIUM")
        self.assertEqual(low_risk, "LOW")

    def test_recommendations_generation(self):
        """Test recommendations generation."""
        # Test critical scenario
        critical_recs = self.analyzer.get_recommendations({"bus_factor": 1, "total_contributors": 5})

        self.assertGreater(len(critical_recs), 0)
        self.assertTrue(any("URGENT" in rec for rec in critical_recs))

        # Test good scenario
        good_recs = self.analyzer.get_recommendations({"bus_factor": 5, "total_contributors": 8})

        self.assertGreater(len(good_recs), 0)

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with single commit
        single_commit = [MockCommit("Alice", datetime.now(), {"file1.py": {}}, 10, 2)]
        self.mock_repo.commits = single_commit

        result = self.analyzer.calculate()
        self.assertIn("bus_factor", result)

        # Test with empty knowledge weights
        bus_factor, _ = self.analyzer._calculate_bus_factor({}, 0.8)
        self.assertEqual(bus_factor, 0)


if __name__ == "__main__":
    unittest.main()
