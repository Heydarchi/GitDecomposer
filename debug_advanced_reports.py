#!/usr/bin/env python3
"""
Test script to debug advanced report generation.
"""

import sys
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from gitdecomposer.core import GitRepository
from gitdecomposer.services.advanced_report_generator import AdvancedReportGenerator

def test_advanced_reports():
    """Test the advanced report generation directly."""
    try:
        print("Initializing repository...")
        repo = GitRepository('.')
        
        print("Creating advanced report generator...")
        advanced_gen = AdvancedReportGenerator(repo)
        
        print("Testing knowledge distribution report...")
        try:
            fig = advanced_gen.create_knowledge_distribution_report("test_knowledge.html")
            print("✓ Knowledge distribution report generated successfully")
        except Exception as e:
            print(f"✗ Knowledge distribution report failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("Testing bus factor report...")
        try:
            fig = advanced_gen.create_bus_factor_report("test_bus_factor.html")
            print("✓ Bus factor report generated successfully")
        except Exception as e:
            print(f"✗ Bus factor report failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_advanced_reports()
