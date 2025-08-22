"""
Test suite for Knowledge Distribution Analyzer.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from gitdecomposer.analyzers.advanced_metrics.knowledge_distribution_analyzer import KnowledgeDistributionAnalyzer

from . import MockCommit, MockRepository


class TestKnowledgeDistributionAnalyzer(unittest.TestCase):
    """Test the Knowledge Distribution Analyzer."""

    def setUp(self):
        self.mock_repo = MockRepository()
        self.analyzer = KnowledgeDistributionAnalyzer(self.mock_repo)

        # Create test data
        now = datetime.now()
        self.test_commits = [
            MockCommit("Alice", now - timedelta(days=10), {"file1.py": {}}),
            MockCommit("Alice", now - timedelta(days=20), {"file1.py": {}, "file2.py": {}}),
            MockCommit("Bob", now - timedelta(days=15), {"file2.py": {}}),
            MockCommit("Charlie", now - timedelta(days=5), {"file3.py": {}}),
        ]
        self.mock_repo.commits = self.test_commits

    def test_get_metric_name(self):
        """Test metric name."""
        expected_name = "Knowledge Distribution Index (Gini Coefficient)"
        self.assertEqual(self.analyzer.get_metric_name(), expected_name)

    def test_get_description(self):
        """Test metric description."""
        description = self.analyzer.get_description()
        self.assertIn("inequality", description.lower())
        self.assertIn("gini", description.lower())
        self.assertIn("0.6", description)

    def test_calculate_with_knowledge_weights(self):
        """Test calculation with provided knowledge weights."""
        knowledge_weights = {
            "Alice": {"file1.py": 10.0, "file2.py": 5.0},
            "Bob": {"file2.py": 3.0, "file3.py": 2.0},
            "Charlie": {"file3.py": 1.0},
        }

        result = self.analyzer.calculate(knowledge_weights=knowledge_weights)

        # Check structure
        self.assertIn("gini_coefficient", result)
        self.assertIn("distribution_quality", result)
        self.assertIn("contributor_count", result)
        self.assertIn("distribution_analysis", result)
        self.assertIn("recommendations", result)

        # Check values
        self.assertIsInstance(result["gini_coefficient"], float)
        self.assertGreaterEqual(result["gini_coefficient"], 0.0)
        self.assertLessEqual(result["gini_coefficient"], 1.0)
        self.assertEqual(result["contributor_count"], 3)

    def test_calculate_without_knowledge_weights(self):
        """Test calculation without provided knowledge weights."""
        result = self.analyzer.calculate()

        self.assertIn("gini_coefficient", result)
        self.assertIn("distribution_quality", result)

    def test_calculate_no_data(self):
        """Test calculation with no data."""
        self.mock_repo.commits = []
        result = self.analyzer.calculate()

        self.assertIn("error", result)
        self.assertEqual(result["gini_coefficient"], 0.0)

    def test_gini_coefficient_calculation(self):
        """Test Gini coefficient calculation."""
        # Test perfect equality
        equal_weights = {"Alice": {"file1.py": 5.0}, "Bob": {"file2.py": 5.0}, "Charlie": {"file3.py": 5.0}}
        gini_equal = self.analyzer._calculate_gini_coefficient(equal_weights)
        self.assertLess(gini_equal, 0.1)  # Should be close to 0

        # Test perfect inequality
        unequal_weights = {
            "Alice": {"file1.py": 100.0, "file2.py": 100.0, "file3.py": 100.0},
            "Bob": {"file4.py": 0.1},
            "Charlie": {"file5.py": 0.1},
        }
        gini_unequal = self.analyzer._calculate_gini_coefficient(unequal_weights)
        self.assertGreater(gini_unequal, 0.5)  # Should be high

        # Test with empty weights
        gini_empty = self.analyzer._calculate_gini_coefficient({})
        self.assertEqual(gini_empty, 0.0)

    def test_knowledge_weights_calculation(self):
        """Test knowledge weights calculation from commits."""
        knowledge_weights = self.analyzer._calculate_knowledge_weights()

        # Should have contributors
        self.assertGreater(len(knowledge_weights), 0)

        # Check structure
        for author, files in knowledge_weights.items():
            self.assertIsInstance(files, dict)
            for file_path, weight in files.items():
                self.assertIsInstance(weight, (int, float))
                self.assertGreater(weight, 0)

    def test_distribution_analysis(self):
        """Test distribution analysis."""
        knowledge_weights = {
            "Alice": {"file1.py": 50.0, "file2.py": 30.0},  # 80 total
            "Bob": {"file2.py": 15.0, "file3.py": 5.0},  # 20 total
            "Charlie": {"file3.py": 10.0},  # 10 total
        }

        analysis = self.analyzer._analyze_distribution(knowledge_weights)

        # Check structure
        self.assertIn("total_knowledge", analysis)
        self.assertIn("contributor_count", analysis)
        self.assertIn("top_contributor_share", analysis)
        self.assertIn("top_3_contributors_share", analysis)

        # Check values
        self.assertEqual(analysis["total_knowledge"], 110.0)
        self.assertEqual(analysis["contributor_count"], 3)
        self.assertAlmostEqual(analysis["top_contributor_share"], 80 / 110, places=2)

    def test_distribution_quality_assessment(self):
        """Test distribution quality assessment."""
        # Test excellent distribution
        excellent = self.analyzer._assess_distribution_quality(0.2)
        self.assertEqual(excellent, "EXCELLENT")

        # Test good distribution
        good = self.analyzer._assess_distribution_quality(0.4)
        self.assertEqual(good, "GOOD")

        # Test acceptable distribution
        acceptable = self.analyzer._assess_distribution_quality(0.55)
        self.assertEqual(acceptable, "ACCEPTABLE")

        # Test poor distribution
        poor = self.analyzer._assess_distribution_quality(0.7)
        self.assertEqual(poor, "POOR")

        # Test critical distribution
        critical = self.analyzer._assess_distribution_quality(0.9)
        self.assertEqual(critical, "CRITICAL")

    def test_recommendations_generation(self):
        """Test recommendations generation."""
        # Test critical scenario
        critical_recs = self.analyzer.get_recommendations({"gini_coefficient": 0.9})
        self.assertGreater(len(critical_recs), 0)
        self.assertTrue(any("CRITICAL" in rec for rec in critical_recs))

        # Test poor scenario
        poor_recs = self.analyzer.get_recommendations({"gini_coefficient": 0.7})
        self.assertGreater(len(poor_recs), 0)
        self.assertTrue(any("concerning" in rec.lower() for rec in poor_recs))

        # Test excellent scenario
        excellent_recs = self.analyzer.get_recommendations({"gini_coefficient": 0.2})
        self.assertGreater(len(excellent_recs), 0)
        self.assertTrue(any("excellent" in rec.lower() for rec in excellent_recs))

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with single contributor
        single_weights = {"Alice": {"file1.py": 10.0}}
        gini_single = self.analyzer._calculate_gini_coefficient(single_weights)
        self.assertEqual(gini_single, 0.0)  # Single contributor means no inequality

        # Test with zero knowledge
        zero_weights = {"Alice": {"file1.py": 0.0}, "Bob": {"file2.py": 0.0}}
        gini_zero = self.analyzer._calculate_gini_coefficient(zero_weights)
        self.assertEqual(gini_zero, 0.0)


if __name__ == "__main__":
    unittest.main()
