"""
Unit tests for DataAggregator service.

Tests the data aggregation service including:
- Comprehensive analysis aggregation
- Performance metrics aggregation
- Error handling
- Data validation
"""

import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import pytest
import pandas as pd

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer.services.data_aggregator import DataAggregator
from gitdecomposer.core.git_repository import GitRepository


class TestDataAggregator:
    """Test cases for DataAggregator service."""

    @pytest.fixture
    def mock_git_repo(self):
        """Create a mock GitRepository for testing."""
        mock_repo = Mock(spec=GitRepository)
        mock_repo.repo_path = "/test/repo"
        mock_repo.get_repository_stats.return_value = {
            "total_commits": 100,
            "total_files": 50,
            "active_branches": 3,
            "contributors": 5
        }
        return mock_repo

    @pytest.fixture
    def mock_analyzers(self):
        """Create mock analyzer objects with return values."""
        analyzers = {}
        
        # Mock commit analyzer
        analyzers["commit_analyzer"] = Mock()
        analyzers["commit_analyzer"].get_commit_stats.return_value = {
            "total_commits": 100,
            "average_commits_per_day": 2.5,
            "first_commit_date": "2023-01-01",
            "last_commit_date": "2023-12-31"
        }
        analyzers["commit_analyzer"].get_commit_frequency_by_date.return_value = pd.DataFrame({
            "date": ["2023-01-01", "2023-01-02"],
            "commits": [5, 3]
        })
        analyzers["commit_analyzer"].get_commit_size_distribution.return_value = {
            "small": 20, "medium": 50, "large": 30
        }
        
        # Mock contributor analyzer
        analyzers["contributor_analyzer"] = Mock()
        analyzers["contributor_analyzer"].get_contributor_statistics.return_value = {
            "total_contributors": 5,
            "active_contributors": 3,
            "top_contributors": ["dev1", "dev2", "dev3"]
        }
        analyzers["contributor_analyzer"].get_contributor_impact_analysis.return_value = pd.DataFrame({
            "contributor": ["dev1", "dev2"],
            "commits": [50, 30],
            "files_changed": [100, 60]
        })
        
        # Mock file analyzer
        analyzers["file_analyzer"] = Mock()
        analyzers["file_analyzer"].get_file_extensions_distribution.return_value = {
            "py": 50, "js": 30, "md": 20
        }
        analyzers["file_analyzer"].get_most_changed_files.return_value = pd.DataFrame({
            "file_path": ["file1.py", "file2.py"],
            "change_count": [15, 10]
        })
        
        # Mock branch analyzer
        analyzers["branch_analyzer"] = Mock()
        analyzers["branch_analyzer"].get_branch_statistics.return_value = {
            "total_branches": 5,
            "active_branches": 3,
            "default_branch": "main"
        }
        
        # Mock advanced metrics
        analyzers["advanced_metrics"] = Mock()
        analyzers["advanced_metrics"].calculate_commit_velocity.return_value = {
            "average_velocity": 3.0,
            "velocity_trend": [1, 2, 3, 4, 5]
        }
        analyzers["advanced_metrics"].calculate_code_churn.return_value = {
            "total_churn": 1000,
            "churn_rate": 0.25
        }
        analyzers["advanced_metrics"].calculate_test_to_code_ratio.return_value = {
            "test_coverage_percentage": 80
        }
        
        return analyzers

    @pytest.fixture
    def data_aggregator(self, mock_git_repo, mock_analyzers):
        """Create DataAggregator instance with mocked dependencies."""
        aggregator = DataAggregator(mock_git_repo)
        for name, analyzer in mock_analyzers.items():
            setattr(aggregator, name, analyzer)
        return aggregator

    def test_initialization(self, mock_git_repo):
        """Test DataAggregator initialization."""
        aggregator = DataAggregator(mock_git_repo)
        assert aggregator.git_repo == mock_git_repo
        assert hasattr(aggregator, "commit_analyzer")
        assert hasattr(aggregator, "contributor_analyzer")
        assert hasattr(aggregator, "file_analyzer")
        assert hasattr(aggregator, "branch_analyzer")
        assert hasattr(aggregator, "advanced_metrics")

    def test_get_comprehensive_analysis(self, data_aggregator):
        """Test comprehensive analysis aggregation."""
        analysis = data_aggregator.get_comprehensive_analysis()
        
        assert isinstance(analysis, dict)
        assert "repository_summary" in analysis
        assert "commit_analysis" in analysis
        assert "contributor_analysis" in analysis
        assert "file_analysis" in analysis
        assert "branch_analysis" in analysis
        
        # Verify nested structure
        repo_summary = analysis["repository_summary"]
        assert "stats" in repo_summary
        assert isinstance(repo_summary["stats"], dict)

    def test_get_commit_analysis_data(self, data_aggregator):
        """Test commit analysis data aggregation."""
        commit_data = data_aggregator.get_commit_analysis_data()
        
        assert isinstance(commit_data, dict)
        assert "commit_stats" in commit_data
        assert "commit_frequency" in commit_data
        assert "commit_size_distribution" in commit_data

    def test_get_contributor_analysis_data(self, data_aggregator):
        """Test contributor analysis data aggregation."""
        contributor_data = data_aggregator.get_contributor_analysis_data()
        
        assert isinstance(contributor_data, dict)
        assert "contributor_stats" in contributor_data
        assert "contributor_impact" in contributor_data

    def test_get_file_analysis_data(self, data_aggregator):
        """Test file analysis data aggregation."""
        file_data = data_aggregator.get_file_analysis_data()
        
        assert isinstance(file_data, dict)
        assert "file_extensions" in file_data
        assert "most_changed_files" in file_data

    def test_get_branch_analysis_data(self, data_aggregator):
        """Test branch analysis data aggregation."""
        branch_data = data_aggregator.get_branch_analysis_data()
        
        assert isinstance(branch_data, dict)
        assert "branch_stats" in branch_data

    def test_get_performance_metrics(self, data_aggregator):
        """Test performance metrics aggregation."""
        metrics = data_aggregator.get_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert "commit_velocity" in metrics
        assert "code_churn" in metrics
        assert "test_coverage" in metrics
        
        # Verify metrics structure
        velocity = metrics["commit_velocity"]
        assert "average_velocity" in velocity
        
        churn = metrics["code_churn"]
        assert "total_churn" in churn

    def test_get_repository_summary(self, data_aggregator):
        """Test repository summary generation."""
        summary = data_aggregator.get_repository_summary()
        
        assert isinstance(summary, dict)
        assert "stats" in summary
        assert "basic_info" in summary
        
        # Verify stats are properly aggregated
        stats = summary["stats"]
        assert "total_commits" in stats
        assert "total_files" in stats

    def test_error_handling_commit_analyzer(self, mock_git_repo):
        """Test error handling when commit analyzer fails."""
        aggregator = DataAggregator(mock_git_repo)
        
        # Mock failing analyzer
        aggregator.commit_analyzer = Mock()
        aggregator.commit_analyzer.get_commit_stats.side_effect = Exception("Test error")
        
        # Should handle errors gracefully
        analysis = aggregator.get_comprehensive_analysis()
        assert isinstance(analysis, dict)
        # Should still have other sections even if one fails
        assert "repository_summary" in analysis

    def test_error_handling_contributor_analyzer(self, mock_git_repo):
        """Test error handling when contributor analyzer fails."""
        aggregator = DataAggregator(mock_git_repo)
        
        # Mock failing analyzer
        aggregator.contributor_analyzer = Mock()
        aggregator.contributor_analyzer.get_contributor_statistics.side_effect = Exception("Test error")
        
        # Should handle errors gracefully
        contributor_data = aggregator.get_contributor_analysis_data()
        assert isinstance(contributor_data, dict)

    def test_error_handling_file_analyzer(self, mock_git_repo):
        """Test error handling when file analyzer fails."""
        aggregator = DataAggregator(mock_git_repo)
        
        # Mock failing analyzer
        aggregator.file_analyzer = Mock()
        aggregator.file_analyzer.get_file_extensions_distribution.side_effect = Exception("Test error")
        
        # Should handle errors gracefully
        file_data = aggregator.get_file_analysis_data()
        assert isinstance(file_data, dict)

    def test_data_validation(self, data_aggregator):
        """Test that aggregated data meets expected formats."""
        analysis = data_aggregator.get_comprehensive_analysis()
        
        # Test repository summary structure
        repo_summary = analysis["repository_summary"]
        assert isinstance(repo_summary["stats"], dict)
        
        # Test commit analysis structure
        commit_analysis = analysis["commit_analysis"]
        assert isinstance(commit_analysis["commit_stats"], dict)
        
        # Test contributor analysis structure
        contributor_analysis = analysis["contributor_analysis"]
        assert isinstance(contributor_analysis["contributor_stats"], dict)

    def test_performance_metrics_validation(self, data_aggregator):
        """Test that performance metrics have expected structure."""
        metrics = data_aggregator.get_performance_metrics()
        
        # Validate velocity metrics
        velocity = metrics["commit_velocity"]
        assert isinstance(velocity["average_velocity"], (int, float))
        
        # Validate churn metrics
        churn = metrics["code_churn"]
        assert isinstance(churn["total_churn"], (int, float))
        
        # Validate test coverage
        coverage = metrics["test_coverage"]
        assert isinstance(coverage["test_coverage_percentage"], (int, float))

    def test_empty_data_handling(self, mock_git_repo):
        """Test handling of empty or None data from analyzers."""
        aggregator = DataAggregator(mock_git_repo)
        
        # Mock analyzers returning empty data
        aggregator.commit_analyzer = Mock()
        aggregator.commit_analyzer.get_commit_stats.return_value = {}
        aggregator.commit_analyzer.get_commit_frequency_by_date.return_value = pd.DataFrame()
        
        aggregator.contributor_analyzer = Mock()
        aggregator.contributor_analyzer.get_contributor_statistics.return_value = {}
        
        # Should handle empty data gracefully
        analysis = aggregator.get_comprehensive_analysis()
        assert isinstance(analysis, dict)
        assert "commit_analysis" in analysis

    def test_large_dataset_handling(self, data_aggregator):
        """Test handling of large datasets."""
        # Mock large dataset
        large_df = pd.DataFrame({
            "date": pd.date_range("2020-01-01", periods=1000),
            "commits": range(1000)
        })
        
        data_aggregator.commit_analyzer.get_commit_frequency_by_date.return_value = large_df
        
        # Should handle large datasets without issues
        analysis = data_aggregator.get_comprehensive_analysis()
        assert isinstance(analysis, dict)
        assert "commit_analysis" in analysis


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
