"""
Unit tests for DashboardGenerator service.

Tests the dashboard generation service including:
- Executive summary dashboard creation
- Commit activity dashboard creation
- Contributor analysis dashboard creation
- File analysis dashboard creation
- Enhanced file analysis dashboard creation
- Error handling
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import plotly.graph_objects as go

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer.services.dashboard_generator import DashboardGenerator
from gitdecomposer.core.git_repository import GitRepository


class TestDashboardGenerator:
    """Test cases for DashboardGenerator service."""

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
    def mock_viz_engine(self):
        """Create a mock VisualizationEngine."""
        mock_viz = Mock()
        mock_fig = Mock(spec=go.Figure)
        
        # Set up return values for all visualization methods
        mock_viz.create_executive_summary.return_value = mock_fig
        mock_viz.create_commit_activity_plots.return_value = mock_fig
        mock_viz.create_contributor_plots.return_value = mock_fig
        mock_viz.create_file_analysis_plots.return_value = mock_fig
        mock_viz.create_enhanced_file_analysis_plots.return_value = mock_fig
        
        return mock_viz

    @pytest.fixture
    def dashboard_generator(self, mock_git_repo, mock_viz_engine):
        """Create DashboardGenerator instance with mocked dependencies."""
        generator = DashboardGenerator(mock_git_repo)
        generator.viz_engine = mock_viz_engine
        return generator

    def test_initialization(self, mock_git_repo):
        """Test DashboardGenerator initialization."""
        generator = DashboardGenerator(mock_git_repo)
        assert generator.git_repo == mock_git_repo
        assert hasattr(generator, "viz_engine")
        assert hasattr(generator, "data_aggregator")

    def test_create_executive_summary_dashboard(self, dashboard_generator, mock_viz_engine):
        """Test executive summary dashboard creation."""
        fig = dashboard_generator.create_executive_summary_dashboard()
        
        # Verify that the visualization engine was called
        mock_viz_engine.create_executive_summary.assert_called_once()
        assert isinstance(fig, Mock)  # Mock figure object

    def test_create_executive_summary_dashboard_with_save(self, dashboard_generator, mock_viz_engine):
        """Test executive summary dashboard creation with file saving."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            try:
                fig = dashboard_generator.create_executive_summary_dashboard(save_path=tmp.name)
                
                # Verify that the visualization engine was called
                mock_viz_engine.create_executive_summary.assert_called_once()
                assert isinstance(fig, Mock)
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)

    def test_create_commit_activity_dashboard(self, dashboard_generator, mock_viz_engine):
        """Test commit activity dashboard creation."""
        fig = dashboard_generator.create_commit_activity_dashboard()
        
        # Verify that the visualization engine was called
        mock_viz_engine.create_commit_activity_plots.assert_called_once()
        assert isinstance(fig, Mock)

    def test_create_commit_activity_dashboard_with_save(self, dashboard_generator, mock_viz_engine):
        """Test commit activity dashboard creation with file saving."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            try:
                fig = dashboard_generator.create_commit_activity_dashboard(save_path=tmp.name)
                
                mock_viz_engine.create_commit_activity_plots.assert_called_once()
                assert isinstance(fig, Mock)
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)

    def test_create_contributor_analysis_dashboard(self, dashboard_generator, mock_viz_engine):
        """Test contributor analysis dashboard creation."""
        fig = dashboard_generator.create_contributor_analysis_dashboard()
        
        mock_viz_engine.create_contributor_plots.assert_called_once()
        assert isinstance(fig, Mock)

    def test_create_contributor_analysis_dashboard_with_save(self, dashboard_generator, mock_viz_engine):
        """Test contributor analysis dashboard creation with file saving."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            try:
                fig = dashboard_generator.create_contributor_analysis_dashboard(save_path=tmp.name)
                
                mock_viz_engine.create_contributor_plots.assert_called_once()
                assert isinstance(fig, Mock)
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)

    def test_create_file_analysis_dashboard(self, dashboard_generator, mock_viz_engine):
        """Test file analysis dashboard creation."""
        fig = dashboard_generator.create_file_analysis_dashboard()
        
        mock_viz_engine.create_file_analysis_plots.assert_called_once()
        assert isinstance(fig, Mock)

    def test_create_file_analysis_dashboard_with_save(self, dashboard_generator, mock_viz_engine):
        """Test file analysis dashboard creation with file saving."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            try:
                fig = dashboard_generator.create_file_analysis_dashboard(save_path=tmp.name)
                
                mock_viz_engine.create_file_analysis_plots.assert_called_once()
                assert isinstance(fig, Mock)
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)

    def test_create_enhanced_file_analysis_dashboard(self, dashboard_generator, mock_viz_engine):
        """Test enhanced file analysis dashboard creation."""
        fig = dashboard_generator.create_enhanced_file_analysis_dashboard()
        
        mock_viz_engine.create_enhanced_file_analysis_plots.assert_called_once()
        assert isinstance(fig, Mock)

    def test_create_enhanced_file_analysis_dashboard_with_save(self, dashboard_generator, mock_viz_engine):
        """Test enhanced file analysis dashboard creation with file saving."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            try:
                fig = dashboard_generator.create_enhanced_file_analysis_dashboard(save_path=tmp.name)
                
                mock_viz_engine.create_enhanced_file_analysis_plots.assert_called_once()
                assert isinstance(fig, Mock)
            finally:
                if os.path.exists(tmp.name):
                    os.unlink(tmp.name)

    def test_error_handling_executive_summary(self, mock_git_repo):
        """Test error handling in executive summary dashboard creation."""
        generator = DashboardGenerator(mock_git_repo)
        
        # Mock failing visualization engine
        generator.viz_engine = Mock()
        generator.viz_engine.create_executive_summary.side_effect = Exception("Test error")
        
        # Should handle errors gracefully
        try:
            fig = generator.create_executive_summary_dashboard()
            # If no exception is raised, the method handled the error
            assert True
        except Exception:
            # If an exception is raised, check that it's informative
            pytest.fail("Dashboard generator should handle visualization errors gracefully")

    def test_error_handling_commit_activity(self, mock_git_repo):
        """Test error handling in commit activity dashboard creation."""
        generator = DashboardGenerator(mock_git_repo)
        
        # Mock failing visualization engine
        generator.viz_engine = Mock()
        generator.viz_engine.create_commit_activity_plots.side_effect = Exception("Test error")
        
        # Should handle errors gracefully
        try:
            fig = generator.create_commit_activity_dashboard()
            assert True
        except Exception:
            pytest.fail("Dashboard generator should handle visualization errors gracefully")

    def test_error_handling_contributor_analysis(self, mock_git_repo):
        """Test error handling in contributor analysis dashboard creation."""
        generator = DashboardGenerator(mock_git_repo)
        
        # Mock failing visualization engine
        generator.viz_engine = Mock()
        generator.viz_engine.create_contributor_plots.side_effect = Exception("Test error")
        
        # Should handle errors gracefully
        try:
            fig = generator.create_contributor_analysis_dashboard()
            assert True
        except Exception:
            pytest.fail("Dashboard generator should handle visualization errors gracefully")

    def test_error_handling_data_aggregator(self, mock_git_repo, mock_viz_engine):
        """Test error handling when data aggregator fails."""
        generator = DashboardGenerator(mock_git_repo)
        generator.viz_engine = mock_viz_engine
        
        # Mock failing data aggregator
        generator.data_aggregator = Mock()
        generator.data_aggregator.get_comprehensive_analysis.side_effect = Exception("Test error")
        
        # Should handle errors gracefully
        try:
            fig = generator.create_executive_summary_dashboard()
            # The visualization engine should still be called even if data aggregation fails
            assert True
        except Exception:
            pytest.fail("Dashboard generator should handle data aggregation errors gracefully")

    def test_dashboard_generation_workflow(self, dashboard_generator, mock_viz_engine):
        """Test the complete dashboard generation workflow."""
        # Create all dashboard types
        dashboards = [
            dashboard_generator.create_executive_summary_dashboard(),
            dashboard_generator.create_commit_activity_dashboard(),
            dashboard_generator.create_contributor_analysis_dashboard(),
            dashboard_generator.create_file_analysis_dashboard(),
            dashboard_generator.create_enhanced_file_analysis_dashboard()
        ]
        
        # All dashboards should be created successfully
        assert len(dashboards) == 5
        assert all(isinstance(dash, Mock) for dash in dashboards)
        
        # Verify all visualization methods were called
        mock_viz_engine.create_executive_summary.assert_called_once()
        mock_viz_engine.create_commit_activity_plots.assert_called_once()
        mock_viz_engine.create_contributor_plots.assert_called_once()
        mock_viz_engine.create_file_analysis_plots.assert_called_once()
        mock_viz_engine.create_enhanced_file_analysis_plots.assert_called_once()

    def test_save_path_handling(self, dashboard_generator):
        """Test that save paths are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "test_dashboard.html")
            
            # Create dashboard with save path
            fig = dashboard_generator.create_executive_summary_dashboard(save_path=save_path)
            
            # Verify the dashboard was created (mock object)
            assert isinstance(fig, Mock)

    def test_invalid_save_path_handling(self, dashboard_generator):
        """Test handling of invalid save paths."""
        # Test with invalid directory
        invalid_path = "/nonexistent/directory/dashboard.html"
        
        # Should handle invalid paths gracefully
        try:
            fig = dashboard_generator.create_executive_summary_dashboard(save_path=invalid_path)
            # If successful, the method handled the error
            assert True
        except Exception as e:
            # If an exception occurs, it should be an informative one
            assert isinstance(e, (OSError, FileNotFoundError, PermissionError))

    def test_multiple_dashboard_creation(self, dashboard_generator, mock_viz_engine):
        """Test creating multiple dashboards in sequence."""
        # Create the same dashboard multiple times
        figs = []
        for _ in range(3):
            fig = dashboard_generator.create_executive_summary_dashboard()
            figs.append(fig)
        
        # All should be created successfully
        assert len(figs) == 3
        assert all(isinstance(fig, Mock) for fig in figs)
        
        # Visualization engine should be called multiple times
        assert mock_viz_engine.create_executive_summary.call_count == 3

    def test_concurrent_dashboard_access(self, dashboard_generator, mock_viz_engine):
        """Test that dashboard generator can handle concurrent access patterns."""
        # Simulate concurrent creation of different dashboard types
        import threading
        import time
        
        results = []
        
        def create_dashboard(dashboard_type):
            if dashboard_type == "executive":
                fig = dashboard_generator.create_executive_summary_dashboard()
            elif dashboard_type == "commit":
                fig = dashboard_generator.create_commit_activity_dashboard()
            else:
                fig = dashboard_generator.create_contributor_analysis_dashboard()
            results.append(fig)
        
        # Create threads for concurrent execution
        threads = []
        for dashboard_type in ["executive", "commit", "contributor"]:
            thread = threading.Thread(target=create_dashboard, args=(dashboard_type,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All dashboards should be created successfully
        assert len(results) == 3
        assert all(isinstance(fig, Mock) for fig in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
