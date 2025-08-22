#!/usr/bin/env python3
"""
Test runner for GitDecomposer test suite.

This script runs all tests with proper configuration and reporting.
"""

import sys
import unittest
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_config import setup_test_environment, cleanup_test_environment


def discover_tests(test_dir=None):
    """Discover all test files in the tests directory."""
    if test_dir is None:
        test_dir = Path(__file__).parent
    
    loader = unittest.TestLoader()
    start_dir = str(test_dir)
    suite = loader.discover(start_dir, pattern='test_*.py')
    return suite


def run_specific_test_class(test_class_name):
    """Run a specific test class."""
    loader = unittest.TestLoader()
    
    # Try to import the test class
    try:
        if test_class_name == 'analyzers':
            from tests.test_analyzers import *
            suite = loader.loadTestsFromName('tests.test_analyzers')
        elif test_class_name == 'commit_analyzer':
            from tests.test_commit_analyzer_detailed import TestCommitAnalyzerDetailed
            suite = loader.loadTestsFromTestCase(TestCommitAnalyzerDetailed)
        elif test_class_name == 'gitdecomposer':
            from tests.test_gitdecomposer import TestGitRepository
            suite = loader.loadTestsFromTestCase(TestGitRepository)
        else:
            print(f"Unknown test class: {test_class_name}")
            return False
            
    except ImportError as e:
        print(f"Failed to import test class {test_class_name}: {e}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_all_tests(verbosity=2):
    """Run all tests in the test suite."""
    suite = discover_tests()
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)
    return result


def print_test_summary(result):
    """Print a summary of test results."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("\nAll tests passed! ✓")
    else:
        print(f"\nSome tests failed! ✗")
    
    print("="*60)


def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run GitDecomposer tests')
    parser.add_argument('--test-class', '-c', 
                       help='Run specific test class (analyzers, commit_analyzer, gitdecomposer)')
    parser.add_argument('--verbose', '-v', action='count', default=1,
                       help='Increase verbosity level')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Run tests quietly')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available test classes')
    
    args = parser.parse_args()
    
    # Set verbosity
    verbosity = 0 if args.quiet else min(args.verbose, 2)
    
    # List available tests
    if args.list:
        print("Available test classes:")
        print("  - analyzers: All analyzer tests")
        print("  - commit_analyzer: Detailed CommitAnalyzer tests")
        print("  - gitdecomposer: Core GitRepository tests")
        return 0
    
    # Setup test environment
    setup_test_environment()
    
    try:
        if args.test_class:
            # Run specific test class
            print(f"Running {args.test_class} tests...")
            success = run_specific_test_class(args.test_class)
            return 0 if success else 1
        else:
            # Run all tests
            print("Running all GitDecomposer tests...")
            result = run_all_tests(verbosity=verbosity)
            
            # Print summary
            print_test_summary(result)
            
            return 0 if result.wasSuccessful() else 1
    
    finally:
        # Cleanup test environment
        cleanup_test_environment()


if __name__ == '__main__':
    exit(main())
