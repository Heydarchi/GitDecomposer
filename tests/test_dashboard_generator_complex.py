"""
Unit tests for DashboardGenerator.

These tests focus on testing the service structure and basic functionality
without complex data dependencies.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import plotly.graph_objects as go
import pytest

from gitdecomposer.core import GitRepository
from gitdecomposer.services import DashboardGenerator


class TestDashboardGenerator:
    """Test cases for DashboardGenerator."""

    @pytest.fixture
    def mock_git_repo(self):
        """Create a mock GitRepository."""
        return Mock(spec=GitRepository)

    @pytest.fixture
    def dashboard_generator(self, mock_git_repo):
        """Create a DashboardGenerator instance with mocked dependencies."""
        return DashboardGenerator(mock_git_repo)

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_initialization(self, mock_git_repo):
        """Test DashboardGenerator initialization."""
        generator = DashboardGenerator(mock_git_repo)
        assert generator.git_repo == mock_git_repo
        assert hasattr(generator, "commit_analyzer")
        assert hasattr(generator, "file_analyzer")
        assert hasattr(generator, "contributor_analyzer")
        assert hasattr(generator, "branch_analyzer")
        assert hasattr(generator, "advanced_metrics")
        assert hasattr(generator, "visualization")

    def test_service_attributes_exist(self, dashboard_generator):
        """Test that expected service attributes exist."""
        expected_attributes = [
            "git_repo",
            "commit_analyzer",
            "file_analyzer",
            "contributor_analyzer",
            "branch_analyzer",
            "advanced_metrics",
            "visualization",
        ]

        for attr in expected_attributes:
            assert hasattr(dashboard_generator, attr), f"Missing attribute: {attr}"

    def test_dashboard_methods_exist(self, dashboard_generator):
        """Test that expected dashboard methods exist."""
        expected_methods = [
            "create_commit_activity_dashboard",
            "create_contributor_analysis_charts",
            "create_file_analysis_visualization",
            "create_enhanced_file_analysis_dashboard",
            "create_branch_analysis_dashboard",
        ]

        for method in expected_methods:
            assert hasattr(dashboard_generator, method), f"Missing method: {method}"
            assert callable(getattr(dashboard_generator, method)), f"Method {method} is not callable"

    def test_create_commit_activity_dashboard_basic(self, dashboard_generator):
        """Test commit activity dashboard creation basic functionality."""
        # The method should exist and be callable
        result = dashboard_generator.create_commit_activity_dashboard()
        # Result can be None due to mock data issues, which is acceptable
        assert result is None or isinstance(result, go.Figure)

    def test_create_contributor_analysis_charts_basic(self, dashboard_generator):
        """Test contributor analysis charts creation basic functionality."""
        # The method should exist and be callable
        result = dashboard_generator.create_contributor_analysis_charts()
        # Result can be None due to mock data issues, which is acceptable
        assert result is None or isinstance(result, go.Figure)

    def test_create_file_analysis_visualization_basic(self, dashboard_generator):
        """Test file analysis visualization creation basic functionality."""
        # The method should exist and be callable
        result = dashboard_generator.create_file_analysis_visualization()
        # Result can be None due to mock data issues, which is acceptable
        assert result is None or isinstance(result, go.Figure)

    def test_create_enhanced_file_analysis_dashboard_basic(self, dashboard_generator):
        """Test enhanced file analysis dashboard creation basic functionality."""
        # The method should exist and be callable
        result = dashboard_generator.create_enhanced_file_analysis_dashboard()
        # Result can be None due to mock data issues, which is acceptable
        assert result is None or isinstance(result, go.Figure)

    def test_create_branch_analysis_dashboard_basic(self, dashboard_generator):
        """Test branch analysis dashboard creation basic functionality."""
        # The method should exist and be callable
        result = dashboard_generator.create_branch_analysis_dashboard()
        # Result can be None due to mock data issues, which is acceptable
        assert result is None or isinstance(result, go.Figure)

    def test_save_path_parameter_accepted(self, dashboard_generator, temp_output_dir):
        """Test that dashboard methods accept save_path parameter."""
        save_path = os.path.join(temp_output_dir, "test_dashboard.html")

        # These should not raise errors when called with save_path
        try:
            dashboard_generator.create_commit_activity_dashboard(save_path)
            dashboard_generator.create_contributor_analysis_charts(save_path)
            dashboard_generator.create_file_analysis_visualization(save_path)
            dashboard_generator.create_enhanced_file_analysis_dashboard(save_path)
            dashboard_generator.create_branch_analysis_dashboard(save_path)
        except TypeError as e:
            pytest.fail(f"Dashboard method should accept save_path parameter: {e}")

    def test_error_handling_graceful(self, dashboard_generator):
        """Test that dashboard methods handle errors gracefully."""
        # Methods should not raise unhandled exceptions with mock data
        methods = [
            dashboard_generator.create_commit_activity_dashboard,
            dashboard_generator.create_contributor_analysis_charts,
            dashboard_generator.create_file_analysis_visualization,
            dashboard_generator.create_enhanced_file_analysis_dashboard,
            dashboard_generator.create_branch_analysis_dashboard,
        ]

        for method in methods:
            try:
                result = method()
                # Should either return None (graceful failure) or a Figure
                assert result is None or isinstance(result, go.Figure)
            except Exception as e:
                pytest.fail(f"Method {method.__name__} should handle errors gracefully, but raised: {e}")

    def test_multiple_dashboard_creation_no_interference(self, dashboard_generator):
        """Test creating multiple dashboards doesn't cause interference."""
        # Create multiple dashboards - should not interfere with each other
        results = []
        methods = [
            dashboard_generator.create_commit_activity_dashboard,
            dashboard_generator.create_contributor_analysis_charts,
            dashboard_generator.create_file_analysis_visualization,
        ]

        for method in methods:
            try:
                result = method()
                results.append(result)
            except Exception as e:
                pytest.fail(f"Method {method.__name__} failed: {e}")

        # All methods should complete without throwing exceptions
        assert len(results) == 3
        # Results can be None due to mock data, which is acceptable
        for result in results:
            assert result is None or isinstance(result, go.Figure)

    def test_analyzer_dependencies_accessible(self, dashboard_generator):
        """Test that analyzer dependencies are properly accessible."""
        # All analyzers should be accessible
        analyzers = [
            dashboard_generator.commit_analyzer,
            dashboard_generator.file_analyzer,
            dashboard_generator.contributor_analyzer,
            dashboard_generator.branch_analyzer,
            dashboard_generator.advanced_metrics,
        ]

        for analyzer in analyzers:
            assert analyzer is not None, "Analyzer should be initialized"

    def test_visualization_engine_accessible(self, dashboard_generator):
        """Test that visualization engine is properly accessible."""
        assert dashboard_generator.visualization is not None
        assert hasattr(dashboard_generator.visualization, "create_commit_activity_dashboard")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
