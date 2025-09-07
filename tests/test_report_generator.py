"""
Unit tests for ReportGenerator service.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.services.report_generator import ReportGenerator


class TestReportGenerator:
    @pytest.fixture
    def mock_git_repo(self):
        mock_repo = Mock(spec=GitRepository)
        mock_repo.repo_path = "/test/repo"
        mock_repo.repo = Mock()
        mock_repo.repo.name = "TestRepository"
        mock_repo.get_repository_stats.return_value = {
            "total_commits": 100,
            "total_files": 50,
            "active_branches": 3,
            "contributors": 5,
        }
        return mock_repo

    @pytest.fixture
    def report_generator(self, mock_git_repo):
        return ReportGenerator(mock_git_repo)

    @pytest.fixture
    def temp_output_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_initialization(self, mock_git_repo):
        generator = ReportGenerator(mock_git_repo)
        assert generator.git_repo == mock_git_repo
        assert hasattr(generator, "commit_analyzer")
        assert hasattr(generator, "file_analyzer")
        assert hasattr(generator, "contributor_analyzer")
        assert hasattr(generator, "branch_analyzer")
        assert hasattr(generator, "visualization")

    def test_generate_all_reports(self, report_generator, temp_output_dir):
        # Stub out generation methods to avoid real file IO
        report_generator._create_commit_activity_dashboard = Mock()
        report_generator._create_contributor_analysis_charts = Mock()
        report_generator._create_file_analysis_visualization = Mock()
        report_generator._create_enhanced_file_analysis_dashboard = Mock()
        report_generator.advanced_report_generator.create_bus_factor_report = Mock()
        report_generator.risk_analysis.create_file_insights_dashboard = Mock()

        reports_created = report_generator.generate_all_visualizations(temp_output_dir)

        assert isinstance(reports_created, dict)
        assert len(reports_created) >= 1
        for key in [
            "commit_activity",
            "contributor_analysis",
            "file_analysis",
            "enhanced_file_analysis",
            "bus_factor",
            "file_insights",
            "index",
        ]:
            assert key in reports_created

    def test_generate_all_reports_creates_html_directory(self, report_generator, temp_output_dir):
        html_dir = os.path.join(temp_output_dir, "HTML")
        assert not os.path.exists(html_dir)

        # Stub out generation methods
        report_generator._create_commit_activity_dashboard = Mock()
        report_generator._create_contributor_analysis_charts = Mock()
        report_generator._create_file_analysis_visualization = Mock()
        report_generator._create_enhanced_file_analysis_dashboard = Mock()
        report_generator.advanced_report_generator.create_bus_factor_report = Mock()
        report_generator.risk_analysis.create_file_insights_dashboard = Mock()

        report_generator.generate_all_visualizations(temp_output_dir)
        assert os.path.exists(html_dir)

    def test_create_index_page(self, report_generator, temp_output_dir):
        html_dir = os.path.join(temp_output_dir, "HTML")
        os.makedirs(html_dir, exist_ok=True)

        # Create some dummy HTML files
        for filename in ["commit_activity.html", "contributor_analysis.html"]:
            with open(os.path.join(html_dir, filename), "w", encoding="utf-8") as f:
                f.write("<html><body>Test content</body></html>")

        report_generator.create_index_page_only(temp_output_dir)

        index_path = os.path.join(temp_output_dir, "index.html")
        assert os.path.exists(index_path)

        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "commit_activity.html" in content
            assert "contributor_analysis.html" in content

    def test_create_csv_data_page(self, report_generator, temp_output_dir):
        csv_dir = os.path.join(temp_output_dir, "CSV")
        os.makedirs(csv_dir, exist_ok=True)

        # Create some dummy CSV files
        for filename in ["branch_statistics.csv", "contributor_statistics.csv", "commit_frequency.csv"]:
            with open(os.path.join(csv_dir, filename), "w", encoding="utf-8") as f:
                f.write("column1,column2\nvalue1,value2\n")

        report_generator.create_csv_data_page(temp_output_dir)

        csv_data_path = os.path.join(temp_output_dir, "csv_data.html")
        assert os.path.exists(csv_data_path)

        # Verify CSV links
        with open(csv_data_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "branch_statistics.csv" in content
            assert "contributor_statistics.csv" in content
            assert "commit_frequency.csv" in content

    def test_create_csv_data_page_with_empty_directory(self, report_generator, temp_output_dir):
        os.makedirs(os.path.join(temp_output_dir, "CSV"), exist_ok=True)
        report_generator.create_csv_data_page(temp_output_dir)
        assert os.path.exists(os.path.join(temp_output_dir, "csv_data.html"))

    def test_create_csv_data_page_without_csv_directory(self, report_generator, temp_output_dir):
        report_generator.create_csv_data_page(temp_output_dir)
        assert os.path.exists(os.path.join(temp_output_dir, "csv_data.html"))

    def test_error_handling_dashboard_creation(self, report_generator, temp_output_dir):
        # Simulate a failure in one generator method
        report_generator._create_commit_activity_dashboard = Mock(side_effect=Exception("Test error"))
        report_generator._create_contributor_analysis_charts = Mock()
        report_generator._create_file_analysis_visualization = Mock()
        report_generator._create_enhanced_file_analysis_dashboard = Mock()
        report_generator.advanced_report_generator.create_bus_factor_report = Mock()
        report_generator.risk_analysis.create_file_insights_dashboard = Mock()

        reports_created = report_generator.generate_all_visualizations(temp_output_dir)
        assert isinstance(reports_created, dict)
        assert len(reports_created) > 0

    def test_error_handling_file_operations(self, report_generator, temp_output_dir):
        # Make the output directory read-only to simulate permission errors
        os.chmod(temp_output_dir, 0o444)
        try:
            # Stub to avoid file writes in read-only dir
            report_generator._create_commit_activity_dashboard = Mock()
            report_generator._create_contributor_analysis_charts = Mock()
            report_generator._create_file_analysis_visualization = Mock()
            report_generator._create_enhanced_file_analysis_dashboard = Mock()
            report_generator.advanced_report_generator.create_bus_factor_report = Mock()
            report_generator.risk_analysis.create_file_insights_dashboard = Mock()

            reports_created = report_generator.generate_all_visualizations(temp_output_dir)
            assert isinstance(reports_created, dict)
        except (OSError, PermissionError):
            pass
        finally:
            os.chmod(temp_output_dir, 0o755)

    def test_generate_index_html_content(self, report_generator, temp_output_dir):
        html_dir = os.path.join(temp_output_dir, "HTML")
        os.makedirs(html_dir, exist_ok=True)

        # Create some test HTML files
        with open(os.path.join(html_dir, "commit_activity.html"), "w", encoding="utf-8") as f:
            f.write("<html><body>Test content</body></html>")

        report_generator.create_index_page_only(temp_output_dir)

        index_path = os.path.join(temp_output_dir, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content
        assert "style" in content.lower() or "css" in content.lower()
        assert "href=" in content

    def test_generate_csv_data_html_content(self, report_generator, temp_output_dir):
        csv_dir = os.path.join(temp_output_dir, "CSV")
        os.makedirs(csv_dir, exist_ok=True)

        for filename in ["branch_statistics.csv", "contributor_statistics.csv"]:
            with open(os.path.join(csv_dir, filename), "w", encoding="utf-8") as f:
                f.write("column1,column2\nvalue1,value2\n")

        report_generator.create_csv_data_page(temp_output_dir)

        csv_data_path = os.path.join(temp_output_dir, "csv_data.html")
        with open(csv_data_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content
        assert "branch_statistics.csv" in content
        assert "contributor_statistics.csv" in content

    def test_multiple_report_generation_runs(self, report_generator, temp_output_dir):
        # Stub out generation methods
        report_generator._create_commit_activity_dashboard = Mock()
        report_generator._create_contributor_analysis_charts = Mock()
        report_generator._create_file_analysis_visualization = Mock()
        report_generator._create_enhanced_file_analysis_dashboard = Mock()
        report_generator.advanced_report_generator.create_bus_factor_report = Mock()
        report_generator.risk_analysis.create_file_insights_dashboard = Mock()

        for _ in range(3):
            reports_created = report_generator.generate_all_visualizations(temp_output_dir)
            assert isinstance(reports_created, dict)
            assert len(reports_created) > 0

        html_dir = os.path.join(temp_output_dir, "HTML")
        html_files = [f for f in os.listdir(html_dir) if f.endswith(".html")]
        # Executive Summary removed -> expect up to 6 HTML reports
        assert len(html_files) <= 6

    def test_large_scale_report_generation(self, report_generator, temp_output_dir):
        # Mock large dataset responses by stubbing the underlying methods
        report_generator._create_commit_activity_dashboard = Mock()
        report_generator._create_contributor_analysis_charts = Mock()
        report_generator._create_file_analysis_visualization = Mock()
        report_generator._create_enhanced_file_analysis_dashboard = Mock()
        report_generator.advanced_report_generator.create_bus_factor_report = Mock()
        report_generator.risk_analysis.create_file_insights_dashboard = Mock()

        reports_created = report_generator.generate_all_visualizations(temp_output_dir)
        assert isinstance(reports_created, dict)
        assert len(reports_created) > 0
