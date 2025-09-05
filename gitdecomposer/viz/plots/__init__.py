"""
The plots module provides functions for creating various visualizations.
"""

from .commit import create_commit_activity_dashboard
from .contributor import create_contributor_analysis_charts
from .file import create_enhanced_file_analysis_dashboard, create_file_analysis_visualization

__all__ = [
    "create_commit_activity_dashboard",
    "create_contributor_analysis_charts",
    "create_file_analysis_visualization",
    "create_enhanced_file_analysis_dashboard",
    # Index page and technical debt are managed elsewhere now.
]
