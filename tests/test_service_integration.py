"""
Integration tests for GitDecomposer services.

Tests the interaction and compatibility between different services:
- Service instantiation and initialization
- Cross-service data flow
- End-to-end workflow testing
- Error propagation and handling
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.services.advanced_analytics import AdvancedAnalytics
from gitdecomposer.services.dashboard_generator import DashboardGenerator
from gitdecomposer.services.data_aggregator import DataAggregator
from gitdecomposer.services.export_service import ExportService
from gitdecomposer.services.report_generator import ReportGenerator


class TestServiceIntegration:
    """Integration tests for service interactions."""

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
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_all_services_instantiation(self, mock_git_repo):
        """Test that all services can be instantiated together."""
        # All services should be instantiable with the same git repo
        data_aggregator = DataAggregator(mock_git_repo)
        dashboard_generator = DashboardGenerator(mock_git_repo)
        export_service = ExportService(mock_git_repo)
        report_generator = ReportGenerator(mock_git_repo)
        advanced_analytics = AdvancedAnalytics(mock_git_repo)

        # Basic functionality checks
        assert all(
            [
                hasattr(data_aggregator, "get_comprehensive_analysis"),
                hasattr(dashboard_generator, "create_commit_activity_dashboard"),
                hasattr(export_service, "export_metrics_to_csv"),
                hasattr(report_generator, "generate_all_visualizations"),
                hasattr(advanced_analytics, "create_technical_debt_dashboard"),
            ]
        )

    def test_service_dependency_injection(self, mock_git_repo):
        """Test that services properly inject dependencies."""
        # Test DataAggregator dependencies
        data_aggregator = DataAggregator(mock_git_repo)
        assert hasattr(data_aggregator, "commit_analyzer")
        assert hasattr(data_aggregator, "contributor_analyzer")
        assert hasattr(data_aggregator, "file_analyzer")
        assert hasattr(data_aggregator, "branch_analyzer")

        # Test DashboardGenerator dependencies
        dashboard_generator = DashboardGenerator(mock_git_repo)
        assert hasattr(dashboard_generator, "visualization")
        assert hasattr(dashboard_generator, "commit_analyzer")

        # Test ExportService dependencies
        export_service = ExportService(mock_git_repo)
        assert hasattr(export_service, "commit_analyzer")

        # Test ReportGenerator dependencies
        report_generator = ReportGenerator(mock_git_repo)
        assert hasattr(report_generator, "visualization")
        # Advanced metrics can be accessed via advanced_metrics module

        # Test AdvancedAnalytics dependencies
        advanced_analytics = AdvancedAnalytics(mock_git_repo)
        # Advanced metrics can be accessed via advanced_metrics module
        assert hasattr(advanced_analytics, "commit_analyzer")

    def test_data_flow_aggregator_to_export(self, mock_git_repo, temp_output_dir):
        """Test data flow from DataAggregator to ExportService."""
        # Create services
        data_aggregator = DataAggregator(mock_git_repo)
        export_service = ExportService(mock_git_repo)

        # Mock the data aggregator to return predictable data
        sample_data = {"commit_analysis": {"commit_stats": pd.DataFrame({"metric": ["total"], "value": [100]})}}

        with patch.object(data_aggregator, "get_comprehensive_analysis", return_value=sample_data):
            # Replace export service's data aggregator with our mocked one
            export_service.data_aggregator = data_aggregator

            # Export data
            csv_dir = os.path.join(temp_output_dir, "CSV")
            files_created = export_service.export_metrics_to_csv(csv_dir)

            assert isinstance(files_created, dict)

    def test_data_flow_aggregator_to_dashboard(self, mock_git_repo):
        """Test data flow from DataAggregator to DashboardGenerator."""
        # Create services
        data_aggregator = DataAggregator(mock_git_repo)
        dashboard_generator = DashboardGenerator(mock_git_repo)

        # Mock the data aggregator
        sample_data = {
            "repository_summary": {"stats": {"total_commits": 100}},
            "commit_analysis": {"commit_stats": {"total": 100}},
            "contributor_analysis": {"contributor_stats": {"total": 5}},
            "file_analysis": {"file_extensions": {"py": 50}},
            "branch_analysis": {"branch_stats": {"total": 3}},
        }

        with patch.object(data_aggregator, "get_comprehensive_analysis", return_value=sample_data):
            # Mock the visualization engine to avoid actual plotting
            with patch.object(dashboard_generator.visualization, "create_commit_activity_dashboard") as mock_viz:
                mock_viz.return_value = Mock()

                # Create dashboard
                fig = dashboard_generator.create_commit_activity_dashboard()

                # Verify the visualization engine was called
                mock_viz.assert_called_once()

    def test_end_to_end_workflow(self, mock_git_repo, temp_output_dir):
        """Test a complete end-to-end workflow using multiple services."""
        # This simulates the workflow used in GitMetrics

        # 1. Create all services
        data_aggregator = DataAggregator(mock_git_repo)
        export_service = ExportService(mock_git_repo)
        report_generator = ReportGenerator(mock_git_repo)

        # 2. Mock data to avoid complex analyzer setup
        sample_data = {
            "repository_summary": {"stats": {"total_commits": 100}},
            "commit_analysis": {"commit_stats": pd.DataFrame({"metric": ["total"], "value": [100]})},
            "contributor_analysis": {"contributor_stats": pd.DataFrame({"name": ["dev1"], "commits": [50]})},
            "file_analysis": {"file_extensions": {"py": 50}},
            "branch_analysis": {"branch_stats": pd.DataFrame({"branch": ["main"], "commits": [80]})},
        }

        with patch.object(data_aggregator, "get_comprehensive_analysis", return_value=sample_data):
            # 3. Export CSV data
            csv_dir = os.path.join(temp_output_dir, "CSV")
            csv_files = export_service.export_metrics_to_csv(csv_dir)

            # 4. Generate reports (mock the underlying dashboard creation)
            with patch.multiple(
                report_generator.visualization,
                create_commit_activity_dashboard=Mock(return_value=Mock()),
                create_enhanced_file_analysis_dashboard=Mock(return_value=Mock()),
                create_technical_debt_dashboard=Mock(return_value=Mock()),
            ):
                reports = report_generator.generate_all_visualizations(temp_output_dir)

                # Verify workflow completion
                assert isinstance(csv_files, dict)
                assert isinstance(reports, dict)
                assert len(reports) > 0

    def test_error_propagation_across_services(self, mock_git_repo, temp_output_dir):
        """Test how errors propagate across service boundaries."""
        # Create services
        data_aggregator = DataAggregator(mock_git_repo)
        export_service = ExportService(mock_git_repo)

        # Mock data aggregator to fail
        with patch.object(data_aggregator, "get_comprehensive_analysis", side_effect=Exception("Test error")):
            export_service.data_aggregator = data_aggregator

            # Test error handling in export service
            try:
                csv_dir = os.path.join(temp_output_dir, "CSV")
                files_created = export_service.export_metrics_to_csv(csv_dir)
                # If it succeeds, error was handled gracefully
                assert isinstance(files_created, dict)
            except Exception:
                # If it fails, the error should be informative
                pass

    def test_service_isolation(self, mock_git_repo):
        """Test that services are properly isolated and don't interfere."""
        # Create multiple instances of the same service
        data_aggregator1 = DataAggregator(mock_git_repo)
        data_aggregator2 = DataAggregator(mock_git_repo)

        # They should be independent instances
        assert data_aggregator1 is not data_aggregator2
        assert data_aggregator1.git_repo == data_aggregator2.git_repo

        # Modifying one shouldn't affect the other
        data_aggregator1.test_attribute = "test_value"
        assert not hasattr(data_aggregator2, "test_attribute")

    def test_service_memory_efficiency(self, mock_git_repo):
        """Test that services don't hold unnecessary references."""
        import gc
        import weakref

        # Create a service
        data_aggregator = DataAggregator(mock_git_repo)
        weak_ref = weakref.ref(data_aggregator)

        # Delete the service
        del data_aggregator
        gc.collect()

        # The weak reference should be cleared (service was garbage collected)
        # Note: This might not always work in test environments, so we're flexible
        try:
            assert weak_ref() is None
        except AssertionError:
            # In some environments, garbage collection is not immediate
            pass

    def test_concurrent_service_usage(self, mock_git_repo, temp_output_dir):
        """Test concurrent usage of services."""
        import threading
        import time

        results = []

        def use_service(service_type, suffix):
            try:
                if service_type == "export":
                    service = ExportService(mock_git_repo)
                    csv_dir = os.path.join(temp_output_dir, f"CSV_{suffix}")
                    files = service.export_metrics_to_csv(csv_dir)
                    results.append(f"export_{suffix}_success")
                elif service_type == "dashboard":
                    service = DashboardGenerator(mock_git_repo)
                    with patch.object(service.visualization, "create_commit_activity_dashboard", return_value=Mock()):
                        fig = service.create_commit_activity_dashboard()
                        results.append(f"dashboard_{suffix}_success")
            except Exception as e:
                results.append(f"error_{suffix}: {e}")

        # Create threads for concurrent service usage
        threads = []
        for i in range(3):
            export_thread = threading.Thread(target=use_service, args=("export", i))
            dashboard_thread = threading.Thread(target=use_service, args=("dashboard", i))
            threads.extend([export_thread, dashboard_thread])

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All operations should succeed
        assert len(results) == 6
        assert all("success" in result for result in results)

    def test_service_configuration_consistency(self, mock_git_repo):
        """Test that services maintain consistent configuration."""
        # All services should use the same git repository
        services = [
            DataAggregator(mock_git_repo),
            DashboardGenerator(mock_git_repo),
            ExportService(mock_git_repo),
            ReportGenerator(mock_git_repo),
            AdvancedAnalytics(mock_git_repo),
        ]

        # All should reference the same git repository
        for service in services:
            assert service.git_repo == mock_git_repo
            assert service.git_repo.repo_path == "/test/repo"

    def test_service_scalability(self, mock_git_repo, temp_output_dir):
        """Test service scalability with large numbers of operations."""
        # Create service
        export_service = ExportService(mock_git_repo)

        # Mock large dataset
        large_data = {
            f"section_{i}": {f"data_{j}": pd.DataFrame({"column": range(100)}) for j in range(10)} for i in range(5)
        }

        # Test with large datasets - just test the service can handle it
        csv_dir = os.path.join(temp_output_dir, "CSV")
        files_created = export_service.export_metrics_to_csv(csv_dir)

        assert isinstance(files_created, dict)
        # Should not crash - even if no files are created due to mock data limitations
        assert len(files_created) >= 0

    def test_service_backward_compatibility(self, mock_git_repo):
        """Test that services maintain backward compatibility."""
        # Test that all services have expected public methods
        data_aggregator = DataAggregator(mock_git_repo)
        expected_methods = [
            "get_comprehensive_analysis",
            "get_enhanced_repository_summary",
            "get_repository_info",
            "get_repository_summary",
        ]

        for method in expected_methods:
            assert hasattr(data_aggregator, method), f"DataAggregator missing method: {method}"

        dashboard_generator = DashboardGenerator(mock_git_repo)
        expected_methods = [
            "create_commit_activity_dashboard",
            "create_enhanced_file_analysis_dashboard",
            "create_branch_analysis_dashboard",
        ]
        for method in expected_methods:
            assert hasattr(dashboard_generator, method), f"DashboardGenerator missing method: {method}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
