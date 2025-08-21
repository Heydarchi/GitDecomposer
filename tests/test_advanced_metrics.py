#!/usr/bin/env python3
"""
Comprehensive tests for the improved AdvancedMetrics module.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pandas as pd
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitdecomposer.git_repository import GitRepository
from gitdecomposer.advanced_metrics import AdvancedMetrics


class TestAdvancedMetrics(unittest.TestCase):
    """Test cases for AdvancedMetrics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock repository
        self.mock_repo = Mock()
        self.mock_git_repo = Mock(spec=GitRepository)
        self.mock_git_repo.repo = self.mock_repo
        
        # Initialize AdvancedMetrics with mock
        self.metrics = AdvancedMetrics(self.mock_git_repo)
    
    def test_empty_repository_maintainability(self):
        """Test maintainability calculation with empty repository."""
        self.mock_git_repo.get_all_commits.return_value = []
        
        result = self.metrics.calculate_maintainability_index()
        
        self.assertEqual(result['overall_maintainability_score'], 0)
        self.assertTrue(result['file_maintainability'].empty)
        self.assertIn('No commit data available', result['recommendations'][0])
    
    def test_empty_repository_technical_debt(self):
        """Test technical debt calculation with empty repository."""
        self.mock_git_repo.get_all_commits.return_value = []
        
        result = self.metrics.calculate_technical_debt_accumulation()
        
        self.assertEqual(result['debt_accumulation_rate'], 0)
        self.assertTrue(result['debt_trend'].empty)
        self.assertEqual(result['total_commits'], 0)
    
    def test_empty_repository_test_coverage(self):
        """Test test coverage calculation with empty repository."""
        # Mock head commit approach failing
        self.mock_repo.head.commit.side_effect = Exception("No HEAD")
        self.mock_git_repo.get_all_commits.return_value = []
        
        result = self.metrics.calculate_test_to_code_ratio()
        
        self.assertEqual(result['test_to_code_ratio'], 0)
        self.assertEqual(result['test_files_count'], 0)
        self.assertEqual(result['code_files_count'], 0)
    
    def test_safe_changed_files_with_parents(self):
        """Test safe changed files extraction with normal commits."""
        # Create mock commit with parents
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.parents = [Mock()]
        
        # Mock parent and diff
        mock_parent = mock_commit.parents[0]
        mock_parent.tree = Mock()  # Make parent accessible
        
        mock_diff_item = Mock()
        mock_diff_item.new_file = True
        mock_diff_item.b_path = "new_file.py"
        
        mock_parent.diff.return_value = [mock_diff_item]
        
        result = self.metrics._get_safe_changed_files(mock_commit)
        
        self.assertEqual(result["new_file.py"], "A")
    
    def test_safe_changed_files_without_parents(self):
        """Test safe changed files extraction with initial commit."""
        # Create mock commit without parents
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.parents = []
        
        # Mock tree traversal
        mock_blob = Mock()
        mock_blob.path = "initial_file.py"
        mock_blob.type = 'blob'
        
        mock_commit.tree.traverse.return_value = [mock_blob]
        
        result = self.metrics._get_safe_changed_files(mock_commit)
        
        self.assertEqual(result["initial_file.py"], "A")
    
    def test_safe_changed_files_inaccessible_parent(self):
        """Test safe changed files extraction with inaccessible parent (grafted repo)."""
        # Create mock commit with inaccessible parent
        mock_commit = Mock()
        mock_commit.hexsha = "abc123"
        mock_commit.parents = [Mock()]
        
        # Make parent access fail (simulating grafted repo issue)
        mock_parent = mock_commit.parents[0]
        mock_parent.tree.side_effect = Exception("Bad object")
        
        # Mock current commit tree traversal
        mock_blob = Mock()
        mock_blob.path = "current_file.py"
        mock_blob.type = 'blob'
        
        mock_commit.tree.traverse.return_value = [mock_blob]
        
        result = self.metrics._get_safe_changed_files(mock_commit)
        
        self.assertEqual(result["current_file.py"], "M")
    
    def test_is_analyzable_file(self):
        """Test file analyzability check."""
        # Test analyzable files
        self.assertTrue(self.metrics._is_analyzable_file("src/main.py"))
        self.assertTrue(self.metrics._is_analyzable_file("test/test_main.py"))
        self.assertTrue(self.metrics._is_analyzable_file("script.js"))
        self.assertTrue(self.metrics._is_analyzable_file("Dockerfile"))
        self.assertTrue(self.metrics._is_analyzable_file("Makefile"))
        
        # Test non-analyzable files
        self.assertFalse(self.metrics._is_analyzable_file("image.jpg"))
        self.assertFalse(self.metrics._is_analyzable_file("binary.exe"))
        self.assertFalse(self.metrics._is_analyzable_file("node_modules/package.js"))
        self.assertFalse(self.metrics._is_analyzable_file(".git/config"))
        self.assertFalse(self.metrics._is_analyzable_file("__pycache__/module.pyc"))
    
    def test_complexity_score_calculation(self):
        """Test file complexity score calculation."""
        # Test high complexity languages
        cpp_score = self.metrics._calculate_file_complexity_score("src/main.cpp", 50)
        py_score = self.metrics._calculate_file_complexity_score("src/main.py", 50)
        js_score = self.metrics._calculate_file_complexity_score("src/main.js", 50)
        
        # C++ should have higher complexity than Python, which should be higher than JS
        self.assertGreater(cpp_score, py_score)
        self.assertGreater(py_score, js_score)
        
        # Test that more changes increase complexity
        small_changes = self.metrics._calculate_file_complexity_score("src/main.py", 10)
        large_changes = self.metrics._calculate_file_complexity_score("src/main.py", 100)
        self.assertGreater(large_changes, small_changes)
        
        # Test special file adjustments
        test_score = self.metrics._calculate_file_complexity_score("tests/test_main.py", 50)
        main_score = self.metrics._calculate_file_complexity_score("src/main.py", 50)
        self.assertLess(test_score, main_score)  # Tests should have lower complexity
    
    def test_technical_debt_pattern_detection(self):
        """Test technical debt pattern detection in commit messages."""
        mock_commits = []
        
        # Create commits with different debt patterns
        debt_messages = [
            "Quick fix for urgent bug",
            "TODO: refactor this later",
            "Temporary workaround for the issue",
            "Code cleanup and refactoring",
            "This is ugly but works",
            "Fix critical bug in production",
            "Add magic number configuration"
        ]
        
        for i, message in enumerate(debt_messages):
            mock_commit = Mock()
            mock_commit.hexsha = f"commit{i}"
            mock_commit.message = message
            mock_commit.committed_date = datetime.now().timestamp()
            mock_commits.append(mock_commit)
        
        self.mock_git_repo.get_all_commits.return_value = mock_commits
        
        # Mock safe changed files to return some files
        def mock_changed_files(commit):
            return {"src/main.py": "M"}
        
        self.metrics._get_safe_changed_files = Mock(side_effect=mock_changed_files)
        
        result = self.metrics.calculate_technical_debt_accumulation()
        
        # Should detect debt in most commits
        self.assertGreater(result['debt_accumulation_rate'], 50)
        self.assertGreater(result['total_debt_commits'], 5)
        
        # Should detect different types of debt
        debt_types = result['debt_by_type']
        self.assertIn('quick_fix', debt_types)
        self.assertIn('todo', debt_types)
        self.assertIn('workaround', debt_types)
        self.assertIn('bug_fix', debt_types)
    
    def test_test_file_detection_patterns(self):
        """Test test file detection with various patterns."""
        # Mock HEAD commit approach
        mock_blob1 = Mock()
        mock_blob1.path = "test_main.py"
        mock_blob1.type = 'blob'
        
        mock_blob2 = Mock()
        mock_blob2.path = "main_test.py"
        mock_blob2.type = 'blob'
        
        mock_blob3 = Mock()
        mock_blob3.path = "tests/integration_test.py"
        mock_blob3.type = 'blob'
        
        mock_blob4 = Mock()
        mock_blob4.path = "spec/main_spec.js"
        mock_blob4.type = 'blob'
        
        mock_blob5 = Mock()
        mock_blob5.path = "src/main.py"
        mock_blob5.type = 'blob'
        
        mock_blob6 = Mock()
        mock_blob6.path = "app.test.js"
        mock_blob6.type = 'blob'
        
        mock_commit = Mock()
        mock_commit.tree.traverse.return_value = [
            mock_blob1, mock_blob2, mock_blob3, mock_blob4, mock_blob5, mock_blob6
        ]
        
        self.mock_repo.head.commit = mock_commit
        
        result = self.metrics.calculate_test_to_code_ratio()
        
        # Should detect test files
        self.assertGreater(result['test_files_count'], 0)
        self.assertGreater(result['code_files_count'], 0)
        self.assertGreater(result['test_to_code_ratio'], 0)
        
        # Should have pattern usage data
        self.assertIsInstance(result['test_patterns'], dict)
    
    def test_maintainability_score_calculation(self):
        """Test maintainability score calculation logic."""
        # Create mock commits with varying complexity
        mock_commits = []
        
        for i in range(3):
            mock_commit = Mock()
            mock_commit.hexsha = f"commit{i}"
            mock_commit.committed_date = datetime.now().timestamp()
            mock_commit.author.name = f"author{i}"
            mock_commits.append(mock_commit)
        
        self.mock_git_repo.get_all_commits.return_value = mock_commits
        
        # Mock changed files - simulate some files with varying change patterns
        def mock_changed_files(commit):
            if commit.hexsha == "commit0":
                return {"simple.py": "M", "complex.cpp": "M"}
            elif commit.hexsha == "commit1":
                return {"simple.py": "M"}
            else:
                return {"complex.cpp": "M"}
        
        def mock_commit_stats(commit):
            if commit.hexsha == "commit0":
                return {"simple.py": 5, "complex.cpp": 50}
            elif commit.hexsha == "commit1":
                return {"simple.py": 3}
            else:
                return {"complex.cpp": 30}
        
        self.metrics._get_safe_changed_files = Mock(side_effect=mock_changed_files)
        self.metrics._get_safe_commit_stats = Mock(side_effect=mock_commit_stats)
        
        result = self.metrics.calculate_maintainability_index()
        
        # Should calculate scores for files
        self.assertGreater(len(result['file_maintainability']), 0)
        self.assertGreater(result['overall_maintainability_score'], 0)
        
        # Should have maintainability factors
        factors = result['maintainability_factors']
        self.assertIn('avg_commits_per_file', factors)
        self.assertIn('avg_authors_per_file', factors)
        
        # Should provide recommendations
        self.assertIsInstance(result['recommendations'], list)
        self.assertGreater(len(result['recommendations']), 0)


def run_advanced_metrics_tests():
    """Run all advanced metrics tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAdvancedMetrics)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Advanced Metrics Tests...")
    print("=" * 50)
    
    success = run_advanced_metrics_tests()
    
    if success:
        print("\n✅ All advanced metrics tests passed!")
    else:
        print("\n❌ Some advanced metrics tests failed!")
        sys.exit(1)