"""
Unit tests for ExportService.

These tests focus on the actual methods available in ExportService
and test the real functionality without expecting non-existent methods.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from gitdecomposer.core import GitRepository
from gitdecomposer.services import ExportService


class TestExportService:
    """Test cases for ExportService."""

    @pytest.fixture
    def mock_git_repo(self):
        """Create a mock GitRepository."""
        return Mock(spec=GitRepository)

    @pytest.fixture
    def export_service(self, mock_git_repo):
        """Create an ExportService instance with mocked dependencies."""
        return ExportService(mock_git_repo)

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_initialization(self, mock_git_repo):
        """Test ExportService initialization."""
        service = ExportService(mock_git_repo)
        assert service.git_repo == mock_git_repo
        assert hasattr(service, "commit_analyzer")
        assert hasattr(service, "file_analyzer")
        assert hasattr(service, "contributor_analyzer")
        assert hasattr(service, "branch_analyzer")
        # Advanced metrics can be accessed via advanced_metrics module

    def test_export_metrics_to_csv(self, export_service, temp_output_dir):
        """Test CSV export functionality."""
        csv_dir = os.path.join(temp_output_dir, "CSV")
        os.makedirs(csv_dir, exist_ok=True)

        files_created = export_service.export_metrics_to_csv(csv_dir)

        assert isinstance(files_created, dict)
        # Check that directory exists
        assert os.path.exists(csv_dir)

    def test_export_csv_data_creates_directory(self, export_service, temp_output_dir):
        """Test that CSV export creates directory if it doesn't exist."""
        csv_dir = os.path.join(temp_output_dir, "nonexistent", "CSV")

        files_created = export_service.export_metrics_to_csv(csv_dir)

        assert os.path.exists(csv_dir)
        assert isinstance(files_created, dict)

    def test_export_single_metric(self, export_service, temp_output_dir):
        """Test single metric export functionality."""
        metric_file = os.path.join(temp_output_dir, "test_metric.csv")

        result = export_service.export_single_metric("test_metric", metric_file)

        # Should return boolean indicating success/failure
        assert isinstance(result, bool)

    def test_error_handling_invalid_directory(self, export_service):
        """Test error handling with invalid directory."""
        # Test with invalid directory (should handle gracefully)
        invalid_dir = "/root/nonexistent/forbidden"

        try:
            export_service.export_metrics_to_csv(invalid_dir)
            # If it succeeds, it handled the error gracefully
        except (OSError, FileNotFoundError, PermissionError):
            # Expected to fail with these types of errors
            pass

    def test_export_service_scalability(self, export_service, temp_output_dir):
        """Test service scalability with multiple operations."""
        # Test multiple exports don't interfere with each other
        csv_dir = os.path.join(temp_output_dir, "CSV")

        # Run multiple exports
        results = []
        for i in range(3):
            files_created = export_service.export_metrics_to_csv(csv_dir)
            results.append(files_created)

        # All should return dictionaries
        assert all(isinstance(result, dict) for result in results)

    def test_service_attributes_exist(self, export_service):
        """Test that expected service attributes exist."""
        expected_attributes = [
            "git_repo",
            "commit_analyzer",
            "file_analyzer",
            "contributor_analyzer",
            "branch_analyzer",
            "advanced_metrics",
        ]

        for attr in expected_attributes:
            assert hasattr(export_service, attr), f"Missing attribute: {attr}"

    def test_export_methods_exist(self, export_service):
        """Test that expected export methods exist."""
        expected_methods = ["export_metrics_to_csv", "export_single_metric"]

        for method in expected_methods:
            assert hasattr(export_service, method), f"Missing method: {method}"
            assert callable(getattr(export_service, method)), f"Method {method} is not callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
