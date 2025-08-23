#!/usr/bin/env python3
"""
Debug script to check the actual data structures from advanced metrics.
"""

import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gitdecomposer.core import GitRepository
from gitdecomposer.analyzers.advanced_metrics import create_metric_analyzer

def debug_analyzers():
    """Debug the analyzers to see actual data structures."""
    try:
        print("Initializing repository...")
        repo = GitRepository('.')
        
        print("\n=== Velocity Trend Analyzer ===")
        try:
            analyzer = create_metric_analyzer('velocity_trend', repo)
            data = analyzer.calculate()
            print(f"Data keys: {list(data.keys())}")
            if 'weekly_data' in data and data['weekly_data']:
                print(f"Weekly data sample: {data['weekly_data'][0]}")
                print(f"Week start type: {type(data['weekly_data'][0]['week_start'])}")
                print(f"Week start value: {data['weekly_data'][0]['week_start']}")
        except Exception as e:
            print(f"Velocity trend error: {e}")
            import traceback
            traceback.print_exc()
            
        print("\n=== Cycle Time Analyzer ===")
        try:
            analyzer = create_metric_analyzer('cycle_time', repo)
            data = analyzer.calculate()
            print(f"Data keys: {list(data.keys())}")
            if 'statistics' in data:
                print(f"Statistics type: {type(data['statistics'])}")
                print(f"Statistics content: {data['statistics']}")
        except Exception as e:
            print(f"Cycle time error: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_analyzers()
