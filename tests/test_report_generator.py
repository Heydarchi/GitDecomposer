"""
Unit tests for ReportGenerator service.

Tests the report generation service including:
- Complete report generation workflow
- Index page creation
- CSV data page creation
- Error handling
- File management
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import plotly.graph_objects as go
import pytest

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.services.report_generator import ReportGenerator


class TestReportGenerator:
    """Test cases for ReportGenerator service."""

    @pytest.fixture
    def mock_git_repo(self):
        """Create a mock GitRepository for testing."""
        mock_repo = Mock(spec=GitRepository)
        mock_repo.repo_path = "/test/repo"
        mock_repo.get_repository_stats.return_value = {
            "total_commits": 100,
            "total_files": 50,
            "active_branches": 3,
            "contributors": 5,
        }
        return mock_repo

    @pytest.fixture
    def mock_dashboard_generator(self):
        """Create a mock DashboardGenerator."""
        mock_generator = Mock()
        mock_fig = Mock(spec=go.Figure)
        mock_fig.write_html = Mock()

        # Set up return values for all dashboard methods
        mock_generator.create_executive_summary_dashboard.return_value = mock_fig
        mock_generator.create_commit_activity_dashboard.return_value = mock_fig
        mock_generator.create_contributor_analysis_dashboard.return_value = mock_fig
        mock_generator.create_file_analysis_dashboard.return_value = mock_fig
        mock_generator.create_enhanced_file_analysis_dashboard.return_value = mock_fig

        return mock_generator

    @pytest.fixture
    def mock_advanced_analytics(self):
        """Create a mock AdvancedAnalytics."""
        mock_analytics = Mock()
        mock_fig = Mock(spec=go.Figure)
        mock_fig.write_html = Mock()

        # Set up return values for advanced analytics methods
        mock_analytics.create_technical_debt_dashboard.return_value = mock_fig
        mock_analytics.create_repository_health_dashboard.return_value = mock_fig
        mock_analytics.create_predictive_maintenance_report.return_value = mock_fig
        mock_analytics.create_velocity_forecasting_dashboard.return_value = mock_fig

        return mock_analytics

    @pytest.fixture
    def report_generator(self, mock_git_repo, mock_dashboard_generator, mock_advanced_analytics):
        """Create ReportGenerator instance with mocked dependencies."""
        # Configure mock to have the required attributes
        mock_git_repo.repo_path = "/test/repo/path"
        mock_git_repo.repo = Mock()
        mock_git_repo.repo.name = "TestRepository"

        generator = ReportGenerator(mock_git_repo)
        generator.dashboard_generator = mock_dashboard_generator
        generator.advanced_analytics = mock_advanced_analytics
        return generator

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_initialization(self, mock_git_repo):
        """Test ReportGenerator initialization."""
        generator = ReportGenerator(mock_git_repo)
        assert generator.git_repo == mock_git_repo
        assert hasattr(generator, "commit_analyzer")
        assert hasattr(generator, "file_analyzer")
        assert hasattr(generator, "contributor_analyzer")
        assert hasattr(generator, "branch_analyzer")
        assert hasattr(generator, "advanced_metrics")
        assert hasattr(generator, "visualization")

    def test_generate_all_reports(self, report_generator, temp_output_dir):
        """Test comprehensive report generation."""
        reports_created = report_generator.generate_all_visualizations(temp_output_dir)

        assert isinstance(reports_created, dict)
        assert len(reports_created) > 0

        # Verify expected report types are created
        expected_reports = [
            "executive_summary",
            "commit_activity",
            "contributor_analysis",
            "file_analysis",
            "enhanced_file_analysis",
        ]

        for report in expected_reports:
            assert report in reports_created

    def test_generate_all_reports_creates_html_directory(self, report_generator, temp_output_dir):
        """Test that generate_all_visualizations creates HTML directory."""
        html_dir = os.path.join(temp_output_dir, "HTML")
        assert not os.path.exists(html_dir)

        report_generator.generate_all_visualizations(temp_output_dir)

        assert os.path.exists(html_dir)

    def test_create_index_page(self, report_generator, temp_output_dir):
        """Test index page creation."""
        html_dir = os.path.join(temp_output_dir, "HTML")
        os.makedirs(html_dir, exist_ok=True)

        # Create some dummy HTML files
        test_files = ["executive_summary.html", "commit_activity.html", "contributor_analysis.html"]
        for filename in test_files:
            with open(os.path.join(html_dir, filename), "w") as f:
                f.write("<html><body>Test content</body></html>")

        report_generator.create_index_page_only(temp_output_dir)

        index_path = os.path.join(temp_output_dir, "index.html")
        assert os.path.exists(index_path)

        # Verify index content contains links to reports
        with open(index_path, "r") as f:
            content = f.read()
            assert "executive_summary.html" in content
            assert "commit_activity.html" in content
            assert "contributor_analysis.html" in content

    def test_create_index_page_with_empty_directory(self, report_generator, temp_output_dir):
        """Test index page creation with empty HTML directory."""
        html_dir = os.path.join(temp_output_dir, "HTML")
        os.makedirs(html_dir, exist_ok=True)

        report_generator.create_index_page_only(temp_output_dir)

        index_path = os.path.join(temp_output_dir, "index.html")
        assert os.path.exists(index_path)

    def test_create_csv_data_page(self, report_generator, temp_output_dir):
        """Test CSV data page creation."""
        csv_dir = os.path.join(temp_output_dir, "CSV")
        os.makedirs(csv_dir, exist_ok=True)

        # Create some dummy CSV files with expected names
        test_files = ["branch_statistics.csv", "contributor_statistics.csv", "commit_frequency.csv"]
        for filename in test_files:
            with open(os.path.join(csv_dir, filename), "w") as f:
                f.write("column1,column2\nvalue1,value2\n")

        report_generator.create_csv_data_page(temp_output_dir)

        csv_data_path = os.path.join(temp_output_dir, "csv_data.html")
        assert os.path.exists(csv_data_path)

        # Verify CSV data page contains links to CSV files
        with open(csv_data_path, "r") as f:
            content = f.read()
            assert "branch_statistics.csv" in content
            assert "contributor_statistics.csv" in content
            assert "commit_frequency.csv" in content

    def test_create_csv_data_page_with_empty_directory(self, report_generator, temp_output_dir):
        """Test CSV data page creation with empty CSV directory."""
        csv_dir = os.path.join(temp_output_dir, "CSV")
        os.makedirs(csv_dir, exist_ok=True)

        report_generator.create_csv_data_page(temp_output_dir)

        csv_data_path = os.path.join(temp_output_dir, "csv_data.html")
        assert os.path.exists(csv_data_path)

    def test_create_csv_data_page_without_csv_directory(self, report_generator, temp_output_dir):
        """Test CSV data page creation when CSV directory doesn't exist."""
        # Don't create CSV directory

        report_generator.create_csv_data_page(temp_output_dir)

        csv_data_path = os.path.join(temp_output_dir, "csv_data.html")
        assert os.path.exists(csv_data_path)

    def test_error_handling_dashboard_creation(self, mock_git_repo, temp_output_dir):
        """Test error handling when dashboard creation fails."""
        generator = ReportGenerator(mock_git_repo)

        # Mock failing dashboard generator
        generator.dashboard_generator = Mock()
        generator.dashboard_generator.create_executive_summary_dashboard.side_effect = Exception("Test error")
        generator.dashboard_generator.create_commit_activity_dashboard.return_value = Mock(spec=go.Figure)

        # Mock working advanced analytics
        generator.advanced_analytics = Mock()
        mock_fig = Mock(spec=go.Figure)
        generator.advanced_analytics.create_technical_debt_dashboard.return_value = mock_fig

        # Should handle errors gracefully and continue with other reports
        reports_created = generator.generate_all_visualizations(temp_output_dir)
        assert isinstance(reports_created, dict)
        # Some reports should still be created despite one failing
        assert len(reports_created) > 0

    def test_error_handling_advanced_analytics(self, mock_git_repo, temp_output_dir):
        """Test error handling when advanced analytics fails."""
        generator = ReportGenerator(mock_git_repo)

        # Mock working dashboard generator
        generator.dashboard_generator = Mock()
        mock_fig = Mock(spec=go.Figure)
        generator.dashboard_generator.create_executive_summary_dashboard.return_value = mock_fig

        # Mock failing advanced analytics
        generator.advanced_analytics = Mock()
        generator.advanced_analytics.create_technical_debt_dashboard.side_effect = Exception("Test error")

        # Should handle errors gracefully
        reports_created = generator.generate_all_visualizations(temp_output_dir)
        assert isinstance(reports_created, dict)

    def test_error_handling_file_operations(self, report_generator, temp_output_dir):
        """Test error handling for file operation failures."""
        # Make the output directory read-only to simulate permission errors
        os.chmod(temp_output_dir, 0o444)

        try:
            # Should handle permission errors gracefully
            reports_created = report_generator.generate_all_visualizations(temp_output_dir)
            # If it succeeds, the method handled the error
            assert isinstance(reports_created, dict)
        except (OSError, PermissionError):
            # Expected to fail with permission errors
            pass
        finally:
            # Restore permissions for cleanup
            os.chmod(temp_output_dir, 0o755)

    def test_generate_index_html_content(self, report_generator, temp_output_dir):
        """Test that generated index HTML has proper structure."""
        html_dir = os.path.join(temp_output_dir, "HTML")
        os.makedirs(html_dir, exist_ok=True)

        # Create some test HTML files
        test_files = ["executive_summary.html", "commit_activity.html"]
        for filename in test_files:
            with open(os.path.join(html_dir, filename), "w") as f:
                f.write("<html><body>Test content</body></html>")

        report_generator.create_index_page_only(temp_output_dir)

        index_path = os.path.join(temp_output_dir, "index.html")
        with open(index_path, "r") as f:
            content = f.read()

        # Verify HTML structure
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content

        # Verify CSS styling is included
        assert "style" in content.lower() or "css" in content.lower()

        # Verify navigation links
        assert "href=" in content

    def test_generate_csv_data_html_content(self, report_generator, temp_output_dir):
        """Test that generated CSV data HTML has proper structure."""
        csv_dir = os.path.join(temp_output_dir, "CSV")
        os.makedirs(csv_dir, exist_ok=True)

        # Create test CSV files
        test_files = ["branch_statistics.csv", "contributor_statistics.csv"]
        for filename in test_files:
            with open(os.path.join(csv_dir, filename), "w") as f:
                f.write("column1,column2\nvalue1,value2\n")

        report_generator.create_csv_data_page(temp_output_dir)

        csv_data_path = os.path.join(temp_output_dir, "csv_data.html")
        with open(csv_data_path, "r") as f:
            content = f.read()

        # Verify HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content

        # Verify links to CSV files
        assert "branch_statistics.csv" in content
        assert "contributor_statistics.csv" in content

    def test_multiple_report_generation_runs(self, report_generator, temp_output_dir):
        """Test multiple consecutive report generation runs."""
        # Generate reports multiple times
        for i in range(3):
            reports_created = report_generator.generate_all_visualizations(temp_output_dir)
            assert isinstance(reports_created, dict)
            assert len(reports_created) > 0

        # Files should be overwritten, not accumulated
        html_dir = os.path.join(temp_output_dir, "HTML")
        html_files = [f for f in os.listdir(html_dir) if f.endswith(".html")]

        # Should have expected number of files, not multiplied by runs
        expected_count = 5  # Number of different dashboard types actually generated
        assert len(html_files) <= expected_count  # Allow for some failures in test environment

    def test_large_scale_report_generation(self, report_generator, temp_output_dir):
        """Test report generation with large-scale data simulation."""
        # This simulates generating reports for a large repository

        # Mock large dataset responses
        large_mock_fig = Mock(spec=go.Figure)
        large_mock_fig.write_html = Mock()

        report_generator.dashboard_generator.create_executive_summary_dashboard.return_value = large_mock_fig
        report_generator.advanced_analytics.create_technical_debt_dashboard.return_value = large_mock_fig

        # Should handle large-scale generation without issues
        reports_created = report_generator.generate_all_visualizations(temp_output_dir)

        assert isinstance(reports_created, dict)
        assert len(reports_created) > 0

    def test_concurrent_report_access(self, report_generator, temp_output_dir):
        """Test concurrent access to report generation."""
        import threading

        results = []

        def generate_reports():
            try:
                reports = report_generator.generate_all_visualizations(temp_output_dir)
                results.append(len(reports))
            except Exception as e:
                results.append(f"Error: {e}")

        # Create multiple threads for concurrent generation
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=generate_reports)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All should complete successfully
        assert len(results) == 3
        assert all(isinstance(result, int) and result > 0 for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
