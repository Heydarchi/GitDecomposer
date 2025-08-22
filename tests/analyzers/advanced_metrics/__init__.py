"""
Test suite for advanced metrics analyzers.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from gitdecomposer.analyzers.advanced_metrics import (
    METRIC_ANALYZERS,
    BaseMetricAnalyzer,
    create_metric_analyzer,
    get_available_metrics,
)


class MockCommit:
    """Mock commit object for testing."""

    def __init__(self, author_name, date, files=None, insertions=0, deletions=0):
        self.author = Mock()
        self.author.name = author_name
        self.committed_datetime = date
        self.stats = Mock()
        self.stats.files = files or {}
        self.stats.total = {"insertions": insertions, "deletions": deletions}


class MockBranch:
    """Mock branch object for testing."""

    def __init__(self, name):
        self.name = name


class MockRepository:
    """Mock repository for testing."""

    def __init__(self):
        self.commits = []
        self.branches = []

    def get_commits(self, since=None, until=None, branch=None, limit=None):
        """Return filtered commits based on parameters."""
        filtered_commits = self.commits.copy()

        if since:
            filtered_commits = [c for c in filtered_commits if c.committed_datetime >= since]
        if until:
            filtered_commits = [c for c in filtered_commits if c.committed_datetime <= until]
        if limit:
            filtered_commits = filtered_commits[:limit]

        return filtered_commits

    def get_branches(self):
        """Return all branches."""
        return self.branches


class TestBaseMetricAnalyzer(unittest.TestCase):
    """Test the base metric analyzer interface."""

    def setUp(self):
        self.mock_repo = MockRepository()

        # Create a concrete implementation for testing
        class TestAnalyzer(BaseMetricAnalyzer):
            def get_metric_name(self):
                return "Test Metric"

            def get_description(self):
                return "Test description"

            def calculate(self, **kwargs):
                return {"test": "result"}

        self.analyzer = TestAnalyzer(self.mock_repo)

    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer.repository, self.mock_repo)
        self.assertEqual(self.analyzer.cache, {})

    def test_metric_interface(self):
        """Test that the metric interface works correctly."""
        self.assertEqual(self.analyzer.get_metric_name(), "Test Metric")
        self.assertEqual(self.analyzer.get_description(), "Test description")
        self.assertEqual(self.analyzer.calculate(), {"test": "result"})

    def test_cache_operations(self):
        """Test cache operations."""
        self.analyzer.cache["test"] = "value"
        self.assertEqual(self.analyzer.cache["test"], "value")

        self.analyzer.clear_cache()
        self.assertEqual(self.analyzer.cache, {})

    def test_recommendations_default(self):
        """Test default recommendations implementation."""
        recommendations = self.analyzer.get_recommendations({})
        self.assertEqual(recommendations, [])


class TestMetricRegistry(unittest.TestCase):
    """Test the metric registry functionality."""

    def test_get_available_metrics(self):
        """Test getting available metrics."""
        metrics = get_available_metrics()
        expected_metrics = [
            "bus_factor",
            "knowledge_distribution",
            "critical_files",
            "single_point_failure",
            "flow_efficiency",
            "branch_lifecycle",
            "velocity_trend",
            "cycle_time",
        ]

        for metric in expected_metrics:
            self.assertIn(metric, metrics)

    def test_create_metric_analyzer_valid(self):
        """Test creating valid metric analyzers."""
        mock_repo = MockRepository()

        for metric_name in get_available_metrics():
            analyzer = create_metric_analyzer(metric_name, mock_repo)
            self.assertIsInstance(analyzer, BaseMetricAnalyzer)
            self.assertEqual(analyzer.repository, mock_repo)

    def test_create_metric_analyzer_invalid(self):
        """Test creating invalid metric analyzer."""
        mock_repo = MockRepository()

        with self.assertRaises(ValueError) as context:
            create_metric_analyzer("invalid_metric", mock_repo)

        self.assertIn("Unknown metric", str(context.exception))
        self.assertIn("invalid_metric", str(context.exception))


if __name__ == "__main__":
    unittest.main()
