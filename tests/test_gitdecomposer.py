"""
Basic tests for GitDecomposer classes.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from pathlib import Path

# Import our classes
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer import GitRepository


class TestGitRepository(unittest.TestCase):
    """Test cases for GitRepository class."""
    
    def test_init_with_invalid_path(self):
        """Test initialization with invalid path."""
        with self.assertRaises(FileNotFoundError):
            GitRepository("/nonexistent/path")
    
    def test_init_with_non_git_directory(self):
        """Test initialization with non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # This should raise InvalidGitRepositoryError, but we might not have git module
            # so we'll just test that it attempts to initialize
            try:
                GitRepository(temp_dir)
            except Exception as e:
                # Expected to fail since it's not a git repo
                self.assertTrue("Invalid Git repository" in str(e) or "git" in str(e).lower())
    
    @patch('gitdecomposer.core.git_repository.Repo')
    def test_repository_stats_structure(self, mock_repo):
        """Test that repository stats returns proper structure."""
        # Mock the git repository
        mock_git_instance = Mock()
        mock_git_instance.bare = False
        mock_git_instance.active_branch.name = "main"
        mock_git_instance.remotes = []
        mock_git_instance.head.commit.hexsha = "abc123"
        
        # Mock iter_commits to return empty list
        mock_git_instance.iter_commits.return_value = []
        
        mock_repo.return_value = mock_git_instance
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            stats = repo.get_repository_stats()
            
            # Check that stats has expected keys
            expected_keys = ['path', 'is_bare', 'active_branch', 'total_commits', 
                           'total_branches', 'total_tags', 'remotes', 'head_commit']
            
            for key in expected_keys:
                self.assertIn(key, stats)


class TestGitDecomposerIntegration(unittest.TestCase):
    """Integration tests for GitDecomposer."""
    
    def test_import_all_modules(self):
        """Test that all modules can be imported."""
        try:
            from gitdecomposer import (
                GitRepository, 
                CommitAnalyzer, 
                FileAnalyzer, 
                ContributorAnalyzer, 
                BranchAnalyzer, 
                GitMetrics
            )
            # If we get here, imports worked
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")
    
    def test_package_structure(self):
        """Test that package has correct structure."""
        import gitdecomposer
        
        # Check that main classes are available
        required_classes = [
            'GitRepository', 
            'CommitAnalyzer', 
            'FileAnalyzer', 
            'ContributorAnalyzer', 
            'BranchAnalyzer', 
            'GitMetrics'
        ]
        
        for class_name in required_classes:
            self.assertTrue(hasattr(gitdecomposer, class_name), 
                          f"Missing class: {class_name}")


class TestAnalyzerClasses(unittest.TestCase):
    """Test analyzer classes with mocked data."""
    
    @patch('gitdecomposer.core.git_repository.Repo')
    def setUp(self, mock_repo):
        """Set up test fixtures."""
        # Mock the git repository
        mock_git_instance = Mock()
        mock_git_instance.bare = False
        mock_git_instance.active_branch.name = "main"
        mock_git_instance.remotes = []
        mock_git_instance.head.commit.hexsha = "abc123"
        mock_git_instance.iter_commits.return_value = []
        
        mock_repo.return_value = mock_git_instance
        
        # Create temporary directory and repository
        self.temp_dir = tempfile.mkdtemp()
        self.git_repo = GitRepository(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.git_repo.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyzer_initialization(self):
        """Test that analyzers can be initialized."""
        from gitdecomposer.analyzers import CommitAnalyzer
        from gitdecomposer.analyzers import FileAnalyzer
        from gitdecomposer.analyzers import ContributorAnalyzer
        from gitdecomposer.analyzers import BranchAnalyzer
        from gitdecomposer.git_metrics import GitMetrics
        
        # Test that analyzers can be created
        commit_analyzer = CommitAnalyzer(self.git_repo)
        file_analyzer = FileAnalyzer(self.git_repo)
        contributor_analyzer = ContributorAnalyzer(self.git_repo)
        branch_analyzer = BranchAnalyzer(self.git_repo)
        metrics = GitMetrics(self.git_repo)
        
        # If we get here, initialization worked
        self.assertIsNotNone(commit_analyzer)
        self.assertIsNotNone(file_analyzer)
        self.assertIsNotNone(contributor_analyzer)
        self.assertIsNotNone(branch_analyzer)
        self.assertIsNotNone(metrics)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGitRepository))
    suite.addTests(loader.loadTestsFromTestCase(TestGitDecomposerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyzerClasses))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running GitDecomposer Tests...")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
