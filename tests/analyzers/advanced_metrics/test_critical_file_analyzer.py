"""
Test suite for Critical File Analyzer.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from gitdecomposer.analyzers.advanced_metrics.critical_file_analyzer import CriticalFileAnalyzer
from . import MockCommit, MockRepository


class TestCriticalFileAnalyzer(unittest.TestCase):
    """Test the Critical File Analyzer."""
    
    def setUp(self):
        self.mock_repo = MockRepository()
        self.analyzer = CriticalFileAnalyzer(self.mock_repo)
        
        # Create test data with different file change patterns
        now = datetime.now()
        self.test_commits = [
            # file1.py - high frequency changes
            MockCommit("Alice", now - timedelta(days=5), {"file1.py": {}}, 50, 10),
            MockCommit("Bob", now - timedelta(days=10), {"file1.py": {}}, 30, 5),
            MockCommit("Charlie", now - timedelta(days=15), {"file1.py": {}}, 20, 8),
            MockCommit("Alice", now - timedelta(days=20), {"file1.py": {}}, 40, 12),
            
            # file2.py - moderate frequency
            MockCommit("Bob", now - timedelta(days=12), {"file2.py": {}}, 100, 20),
            MockCommit("Charlie", now - timedelta(days=25), {"file2.py": {}}, 80, 15),
            
            # file3.py - low frequency
            MockCommit("Alice", now - timedelta(days=30), {"file3.py": {}}, 200, 50),
        ]
        self.mock_repo.commits = self.test_commits
    
    def test_get_metric_name(self):
        """Test metric name."""
        self.assertEqual(self.analyzer.get_metric_name(), "Critical File Identification")
    
    def test_get_description(self):
        """Test metric description."""
        description = self.analyzer.get_description()
        self.assertIn("highest risk", description.lower())
        self.assertIn("complexity", description.lower())
        self.assertIn("change frequency", description.lower())
    
    def test_calculate_with_files(self):
        """Test calculation with files."""
        result = self.analyzer.calculate(lookback_months=2)
        
        # Check structure
        self.assertIn('critical_files', result)
        self.assertIn('total_files_analyzed', result)
        self.assertIn('critical_file_count', result)
        self.assertIn('analysis', result)
        self.assertIn('recommendations', result)
        
        # Check values
        self.assertIsInstance(result['critical_files'], list)
        self.assertGreaterEqual(result['total_files_analyzed'], 0)
        self.assertGreaterEqual(result['critical_file_count'], 0)
    
    def test_calculate_no_files(self):
        """Test calculation with no files."""
        self.mock_repo.commits = []
        result = self.analyzer.calculate()
        
        self.assertIn('error', result)
        self.assertEqual(result['critical_files'], [])
        self.assertEqual(result['total_files_analyzed'], 0)
    
    def test_file_metrics_calculation(self):
        """Test file metrics calculation."""
        file_metrics = self.analyzer._calculate_file_metrics(6)
        
        # Should have metrics for files
        self.assertGreater(len(file_metrics), 0)
        
        # Check structure for each file
        for file_path, metrics in file_metrics.items():
            self.assertIn('change_frequency', metrics)
            self.assertIn('complexity', metrics)
            self.assertIn('dependency_impact', metrics)
            self.assertIn('criticality_score', metrics)
            self.assertIn('file_size', metrics)
            self.assertIn('last_modified', metrics)
            
            # Check types
            self.assertIsInstance(metrics['change_frequency'], int)
            self.assertIsInstance(metrics['complexity'], (int, float))
            self.assertIsInstance(metrics['dependency_impact'], (int, float))
            self.assertIsInstance(metrics['criticality_score'], (int, float))
            self.assertIsInstance(metrics['last_modified'], datetime)
    
    def test_complexity_score_calculation(self):
        """Test complexity score calculation."""
        # Mock file content for testing
        with patch.object(self.analyzer, '_get_file_content') as mock_get_content:
            # Test simple file
            mock_get_content.return_value = "print('hello world')"
            simple_complexity = self.analyzer._calculate_complexity_score('simple.py')
            
            # Test complex file with decision points
            complex_code = """
            def complex_function(x):
                if x > 0:
                    for i in range(x):
                        if i % 2 == 0:
                            try:
                                result = process(i)
                            except Exception:
                                raise ValueError("Error")
                        else:
                            while i > 0:
                                i -= 1
                elif x < 0:
                    switch_case(x)
                return result
            """
            mock_get_content.return_value = complex_code
            complex_complexity = self.analyzer._calculate_complexity_score('complex.py')
            
            # Complex file should have higher complexity
            self.assertGreater(complex_complexity, simple_complexity)
    
    def test_dependency_impact_calculation(self):
        """Test dependency impact calculation."""
        # Test high-impact files
        main_impact = self.analyzer._calculate_dependency_impact('main.py')
        index_impact = self.analyzer._calculate_dependency_impact('src/index.js')
        core_impact = self.analyzer._calculate_dependency_impact('lib/core.py')
        
        # Test regular files
        util_impact = self.analyzer._calculate_dependency_impact('utils/helper.py')
        
        # High-impact files should have higher scores
        self.assertGreater(main_impact, util_impact)
        self.assertGreater(index_impact, util_impact)
        self.assertGreater(core_impact, util_impact)
    
    def test_critical_files_identification(self):
        """Test critical files identification."""
        file_metrics = {
            'file1.py': {'criticality_score': 100.0},
            'file2.py': {'criticality_score': 80.0},
            'file3.py': {'criticality_score': 60.0},
            'file4.py': {'criticality_score': 40.0},
            'file5.py': {'criticality_score': 20.0},
        }
        
        # Test with 80th percentile (top 20%)
        critical_files = self.analyzer._identify_critical_files(file_metrics, 0.8)
        
        # Should return top 20% (1 file out of 5)
        self.assertEqual(len(critical_files), 1)
        self.assertEqual(critical_files[0][0], 'file1.py')
        self.assertEqual(critical_files[0][1]['criticality_score'], 100.0)
    
    def test_critical_files_analysis(self):
        """Test critical files analysis."""
        critical_files = [
            ('file1.py', {
                'criticality_score': 100.0,
                'change_frequency': 10,
                'complexity': 15.0
            }),
            ('file2.js', {
                'criticality_score': 80.0,
                'change_frequency': 8,
                'complexity': 12.0
            }),
        ]
        
        all_metrics = {
            'file1.py': critical_files[0][1],
            'file2.js': critical_files[1][1],
            'file3.py': {'criticality_score': 20.0, 'change_frequency': 2, 'complexity': 3.0}
        }
        
        analysis = self.analyzer._analyze_critical_files(critical_files, all_metrics)
        
        # Check structure
        self.assertIn('avg_criticality_score', analysis)
        self.assertIn('max_criticality_score', analysis)
        self.assertIn('avg_change_frequency', analysis)
        self.assertIn('avg_complexity', analysis)
        self.assertIn('file_types', analysis)
        self.assertIn('risk_categories', analysis)
        
        # Check values
        self.assertEqual(analysis['avg_criticality_score'], 90.0)
        self.assertEqual(analysis['max_criticality_score'], 100.0)
        self.assertIn('.py', analysis['file_types'])
        self.assertIn('.js', analysis['file_types'])
    
    def test_file_types_analysis(self):
        """Test file types analysis."""
        critical_files = [
            ('file1.py', {}),
            ('file2.py', {}),
            ('script.js', {}),
            ('style.css', {}),
            ('README', {}),  # No extension
        ]
        
        file_types = self.analyzer._analyze_file_types(critical_files)
        
        self.assertEqual(file_types['.py'], 2)
        self.assertEqual(file_types['.js'], 1)
        self.assertEqual(file_types['.css'], 1)
        self.assertEqual(file_types['no_extension'], 1)
    
    def test_risk_categorization(self):
        """Test risk level categorization."""
        critical_files = [
            ('file1.py', {'complexity': 25.0, 'change_frequency': 30}),  # CRITICAL
            ('file2.py', {'complexity': 8.0, 'change_frequency': 15}),   # HIGH
            ('file3.py', {'complexity': 3.0, 'change_frequency': 5}),    # MEDIUM
        ]
        
        risk_categories = self.analyzer._categorize_risk_levels(critical_files)
        
        self.assertEqual(risk_categories['CRITICAL'], 1)
        self.assertEqual(risk_categories['HIGH'], 1)
        self.assertEqual(risk_categories['MEDIUM'], 1)
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        # Test high-risk scenario
        high_risk_result = {
            'critical_files': [('file1.py', {})] * 10,  # 10 critical files
            'total_files': 20
        }
        high_risk_recs = self.analyzer.get_recommendations(high_risk_result)
        
        self.assertGreater(len(high_risk_recs), 0)
        self.assertTrue(any('HIGH RISK' in rec for rec in high_risk_recs))
        
        # Test no critical files
        no_risk_result = {
            'critical_files': [],
            'total_files': 20
        }
        no_risk_recs = self.analyzer.get_recommendations(no_risk_result)
        
        self.assertGreater(len(no_risk_recs), 0)
        self.assertTrue(any('good file health' in rec.lower() for rec in no_risk_recs))
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with commits but no file changes
        empty_commits = [MockCommit("Alice", datetime.now(), {}, 0, 0)]
        self.mock_repo.commits = empty_commits
        
        result = self.analyzer.calculate()
        # Should handle gracefully - might have empty results but no errors
        self.assertIn('critical_files', result)


if __name__ == '__main__':
    unittest.main()
