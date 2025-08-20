"""
GitDecomposer - A Python tool for analyzing Git repositories

This package provides classes and utilities for reading and analyzing
Git repository data including commits, branches, files, and contributors.
"""

__version__ = "1.0.0"
__author__ = "GitDecomposer Team"

from .git_repository import GitRepository
from .commit_analyzer import CommitAnalyzer
from .file_analyzer import FileAnalyzer
from .contributor_analyzer import ContributorAnalyzer
from .branch_analyzer import BranchAnalyzer
from .git_metrics import GitMetrics

__all__ = [
    'GitRepository',
    'CommitAnalyzer', 
    'FileAnalyzer',
    'ContributorAnalyzer',
    'BranchAnalyzer',
    'GitMetrics'
]
