"""
The plots module provides functions for creating various visualizations.
"""

from .commit import create_commit_activity_dashboard
from .contributor import create_contributor_analysis_charts
from .file import create_enhanced_file_analysis_dashboard, create_file_analysis_visualization
from .index_page import create_index_page
from .technical_debt import create_technical_debt_dashboard

__all__ = [
    "create_commit_activity_dashboard",
    "create_contributor_analysis_charts",
    "create_file_analysis_visualization",
    "create_enhanced_file_analysis_dashboard",
    "create_technical_debt_dashboard",
    "create_index_page",
]
