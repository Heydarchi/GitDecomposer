"""
GitDecomposer - A Python tool for analyzing Git repositories

This package provides classes and utilities for reading and analyzing
Git repository data including commits, branches, files, and contributors.
"""

__version__ = "1.0.0"
__author__ = "GitDecomposer Team"

from .core import GitRepository
from .analyzers import (
    CommitAnalyzer,
    FileAnalyzer,
    ContributorAnalyzer,
    BranchAnalyzer,
    AdvancedMetrics,
)
from .git_metrics import GitMetrics
from .viz import VisualizationEngine

__all__ = [
    "GitRepository",
    "CommitAnalyzer",
    "FileAnalyzer",
    "ContributorAnalyzer",
    "BranchAnalyzer",
    "GitMetrics",
    "AdvancedMetrics",
    "VisualizationEngine",
]
