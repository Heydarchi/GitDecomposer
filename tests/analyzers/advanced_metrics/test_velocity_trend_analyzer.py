"""
Test suite for Velocity Trend Analyzer.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from gitdecomposer.analyzers.advanced_metrics.velocity_trend_analyzer import VelocityTrendAnalyzer
from . import MockCommit, MockRepository


class TestVelocityTrendAnalyzer(unittest.TestCase):
    """Test the Velocity Trend Analyzer."""
    
    def setUp(self):
        self.mock_repo = MockRepository()
        self.analyzer = VelocityTrendAnalyzer(self.mock_repo)
        
        # Create test data with trend patterns
        now = datetime.now()
        self.test_commits = []
        
        # Create 12 weeks of commit data with increasing trend
        for week in range(12):
            week_start = now - timedelta(weeks=week)
            
            # Increasing trend: more commits in recent weeks
            commit_count = 12 - week  # 1 commit in oldest week, 12 in newest
            
            for i in range(commit_count):
                commit_date = week_start - timedelta(days=i)
                self.test_commits.append(
                    MockCommit(
                        f"Author{i % 3}",  # 3 different authors
                        commit_date,
                        {f"file{i % 5}.py": {}},  # 5 different files
                        10 + i,  # insertions
                        2 + i    # deletions
                    )
                )
        
        self.mock_repo.commits = self.test_commits
    
    def test_get_metric_name(self):
        """Test metric name."""
        self.assertEqual(self.analyzer.get_metric_name(), "Development Velocity Trend")
    
    def test_get_description(self):
        """Test metric description."""
        description = self.analyzer.get_description()
        self.assertIn("velocity trends", description.lower())
        self.assertIn("speeding up", description.lower())
        self.assertIn("slowing down", description.lower())
    
    def test_calculate_with_sufficient_data(self):
        """Test calculation with sufficient data."""
        result = self.analyzer.calculate(weeks_lookback=8)
        
        # Check structure
        self.assertIn('weekly_data', result)
        self.assertIn('trends', result)
        self.assertIn('overall_health', result)
        self.assertIn('recommendations', result)
        
        # Check types
        self.assertIsInstance(result['weekly_data'], list)
        self.assertIsInstance(result['trends'], dict)
        self.assertIsInstance(result['overall_health'], dict)
        self.assertIsInstance(result['recommendations'], list)
        
        # Should have enough data
        self.assertGreaterEqual(len(result['weekly_data']), 3)
    
    def test_calculate_insufficient_data(self):
        """Test calculation with insufficient data."""
        # Only 2 commits
        self.mock_repo.commits = self.test_commits[:2]
        result = self.analyzer.calculate(weeks_lookback=8)
        
        # Should handle gracefully with valid results, not error
        self.assertIn('weekly_data', result)
        self.assertIn('trends', result)
        self.assertIn('overall_health', result)
        # Should indicate low confidence due to insufficient data
        if 'overall_health' in result and 'confidence' in result['overall_health']:
            self.assertLessEqual(result['overall_health']['confidence'], 0.5)
    
    def test_weekly_data_collection(self):
        """Test weekly data collection."""
        weekly_data = self.analyzer._collect_weekly_data(4)
        
        # Should have 4 weeks of data
        self.assertEqual(len(weekly_data), 4)
        
        # Check structure of each week
        for week_data in weekly_data:
            self.assertIn('week', week_data)
            self.assertIn('week_start', week_data)
            self.assertIn('week_end', week_data)
            self.assertIn('commit_count', week_data)
            self.assertIn('unique_authors', week_data)
            self.assertIn('files_changed', week_data)
            self.assertIn('total_lines_changed', week_data)
            self.assertIn('avg_commit_size', week_data)
            self.assertIn('files_per_commit', week_data)
            self.assertIn('commits_per_author', week_data)
            
            # Check types
            self.assertIsInstance(week_data['commit_count'], int)
            self.assertIsInstance(week_data['unique_authors'], int)
            self.assertIsInstance(week_data['files_changed'], int)
            self.assertIsInstance(week_data['total_lines_changed'], int)
    
    def test_weekly_metrics_calculation(self):
        """Test weekly metrics calculation."""
        # Create test commits for a specific week
        now = datetime.now()
        week_commits = [
            MockCommit("Alice", now, {"file1.py": {}}, 50, 10),
            MockCommit("Bob", now, {"file1.py": {}, "file2.py": {}}, 30, 5),
            MockCommit("Alice", now, {"file3.py": {}}, 20, 3),
        ]
        
        week_start = now - timedelta(days=7)
        week_end = now
        
        metrics = self.analyzer._calculate_weekly_metrics(
            week_commits, 0, week_start, week_end
        )
        
        # Check calculated values
        self.assertEqual(metrics['commit_count'], 3)
        self.assertEqual(metrics['unique_authors'], 2)  # Alice and Bob
        self.assertEqual(metrics['files_changed'], 3)   # file1, file2, file3
        self.assertEqual(metrics['total_lines_changed'], 118)  # Sum of all changes
        self.assertGreater(metrics['avg_commit_size'], 0)
        self.assertGreater(metrics['commits_per_author'], 0)
    
    def test_trend_analysis(self):
        """Test trend analysis."""
        # Create weekly data with clear increasing trend
        weekly_data = [
            {'commit_count': 2, 'unique_authors': 1, 'files_changed': 2, 'total_lines_changed': 20, 'avg_commit_size': 10},
            {'commit_count': 4, 'unique_authors': 2, 'files_changed': 4, 'total_lines_changed': 40, 'avg_commit_size': 10},
            {'commit_count': 6, 'unique_authors': 2, 'files_changed': 6, 'total_lines_changed': 60, 'avg_commit_size': 10},
            {'commit_count': 8, 'unique_authors': 3, 'files_changed': 8, 'total_lines_changed': 80, 'avg_commit_size': 10},
        ]
        
        trends = self.analyzer._analyze_trends(weekly_data)
        
        # Check structure
        expected_metrics = ['commit_count', 'unique_authors', 'files_changed', 'total_lines_changed', 'avg_commit_size']
        for metric in expected_metrics:
            self.assertIn(metric, trends)
            
            trend_data = trends[metric]
            self.assertIn('trend', trend_data)
            self.assertIn('slope', trend_data)
            self.assertIn('confidence', trend_data)
            self.assertIn('current_value', trend_data)
            self.assertIn('predicted_next_week', trend_data)
        
        # With clear increasing data, commit_count should show increasing trend
        commit_trend = trends['commit_count']
        self.assertEqual(commit_trend['trend'], 'increasing')
        self.assertGreater(commit_trend['slope'], 0)
    
    def test_linear_regression(self):
        """Test linear regression calculation."""
        # Test with perfect linear relationship
        x = [0, 1, 2, 3, 4]
        y = [2, 4, 6, 8, 10]  # y = 2x + 2
        
        slope, intercept, r_squared = self.analyzer._linear_regression(x, y)
        
        self.assertAlmostEqual(slope, 2.0, places=1)
        self.assertAlmostEqual(intercept, 2.0, places=1)
        self.assertAlmostEqual(r_squared, 1.0, places=1)  # Perfect correlation
        
        # Test with no relationship
        x_flat = [0, 1, 2, 3]
        y_flat = [5, 5, 5, 5]  # Flat line
        
        slope_flat, intercept_flat, r_squared_flat = self.analyzer._linear_regression(x_flat, y_flat)
        
        self.assertAlmostEqual(slope_flat, 0.0, places=1)
        self.assertAlmostEqual(intercept_flat, 5.0, places=1)
    
    def test_trend_statistics_calculation(self):
        """Test trend statistics calculation."""
        # Test increasing trend
        increasing_values = [1, 3, 5, 7, 9]
        increasing_stats = self.analyzer._calculate_trend_statistics(increasing_values, 'test_metric')
        
        self.assertEqual(increasing_stats['trend'], 'increasing')
        self.assertGreater(increasing_stats['slope'], 0)
        self.assertEqual(increasing_stats['current_value'], 9)
        
        # Test decreasing trend
        decreasing_values = [9, 7, 5, 3, 1]
        decreasing_stats = self.analyzer._calculate_trend_statistics(decreasing_values, 'test_metric')
        
        self.assertEqual(decreasing_stats['trend'], 'decreasing')
        self.assertLess(decreasing_stats['slope'], 0)
        
        # Test stable trend
        stable_values = [5, 5.1, 4.9, 5.2, 4.8]
        stable_stats = self.analyzer._calculate_trend_statistics(stable_values, 'test_metric')
        
        self.assertEqual(stable_stats['trend'], 'stable')
    
    def test_velocity_health_assessment(self):
        """Test velocity health assessment."""
        # Test improving scenario
        improving_trends = {
            'commit_count': {'trend': 'increasing', 'confidence': 0.8},
            'unique_authors': {'trend': 'increasing', 'confidence': 0.7},
            'files_changed': {'trend': 'stable', 'confidence': 0.6},
            'total_lines_changed': {'trend': 'increasing', 'confidence': 0.9},
        }
        
        improving_health = self.analyzer._assess_velocity_health(improving_trends)
        
        self.assertEqual(improving_health['overall_status'], 'improving')
        self.assertIn(improving_health['health_level'], ['excellent', 'good'])
        self.assertGreater(improving_health['positive_trends'], improving_health['negative_trends'])
        
        # Test declining scenario
        declining_trends = {
            'commit_count': {'trend': 'decreasing', 'confidence': 0.8},
            'unique_authors': {'trend': 'decreasing', 'confidence': 0.7},
            'files_changed': {'trend': 'decreasing', 'confidence': 0.6},
            'total_lines_changed': {'trend': 'stable', 'confidence': 0.5},
        }
        
        declining_health = self.analyzer._assess_velocity_health(declining_trends)
        
        self.assertEqual(declining_health['overall_status'], 'declining')
        self.assertIn(declining_health['health_level'], ['poor', 'concerning'])
        self.assertGreater(declining_health['negative_trends'], declining_health['positive_trends'])
    
    def test_concerns_and_strengths_identification(self):
        """Test identification of key concerns and strengths."""
        trends_with_issues = {
            'commit_count': {'trend': 'decreasing', 'confidence': 0.8},
            'unique_authors': {'trend': 'decreasing', 'confidence': 0.7},
            'files_changed': {'trend': 'increasing', 'confidence': 0.9},
            'total_lines_changed': {'trend': 'stable', 'confidence': 0.5},
        }
        
        concerns = self.analyzer._identify_key_concerns(trends_with_issues)
        strengths = self.analyzer._identify_key_strengths(trends_with_issues)
        
        # Should identify decreasing trends as concerns
        self.assertGreater(len(concerns), 0)
        self.assertTrue(any('commit frequency' in concern.lower() for concern in concerns))
        
        # Should identify increasing trends as strengths
        self.assertGreater(len(strengths), 0)
        self.assertTrue(any('codebase coverage' in strength.lower() for strength in strengths))
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        # Test poor health scenario
        poor_result = {
            'trends': {
                'commit_count': {'trend': 'decreasing', 'confidence': 0.8}
            },
            'overall_health': {
                'health_level': 'poor',
                'overall_status': 'declining',
                'key_concerns': ['Decreasing commit frequency'],
                'confidence': 0.7
            },
            'weeks_analyzed': 8
        }
        
        poor_recs = self.analyzer.get_recommendations(poor_result)
        
        self.assertGreater(len(poor_recs), 0)
        self.assertTrue(any('URGENT' in rec for rec in poor_recs))
        
        # Test excellent health scenario
        excellent_result = {
            'trends': {
                'commit_count': {'trend': 'increasing', 'confidence': 0.9}
            },
            'overall_health': {
                'health_level': 'excellent',
                'overall_status': 'improving',
                'key_concerns': [],
                'key_strengths': ['Increasing development activity'],
                'confidence': 0.9
            },
            'weeks_analyzed': 12
        }
        
        excellent_recs = self.analyzer.get_recommendations(excellent_result)
        
        self.assertGreater(len(excellent_recs), 0)
        self.assertTrue(any('excellent' in rec.lower() for rec in excellent_recs))
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with insufficient data
        result = self.analyzer.calculate(weeks_lookback=1)
        # Should handle gracefully
        
        # Test with no commits
        self.mock_repo.commits = []
        result = self.analyzer.calculate(weeks_lookback=4)
        # Should handle gracefully with zero values, not error
        self.assertIn('weekly_data', result)
        self.assertIn('trends', result)
        # All values should be zero
        for week_data in result['weekly_data']:
            self.assertEqual(week_data['commit_count'], 0)
        
        # Test linear regression with insufficient data
        slope, intercept, r_squared = self.analyzer._linear_regression([1], [1])
        self.assertEqual(slope, 0)
        self.assertEqual(intercept, 0)
        self.assertEqual(r_squared, 0)


if __name__ == '__main__':
    unittest.main()
