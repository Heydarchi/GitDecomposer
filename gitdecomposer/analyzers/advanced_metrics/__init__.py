"""
Advanced repository metrics analyzers for GitDecomposer.

This module provides sophisticated metrics for analyzing repository health,
development patterns, and team productivity.
"""

from datetime import datetime
from typing import Any, Dict, Optional

# Import base class
from .base import BaseMetricAnalyzer
from .branch_lifecycle_analyzer import BranchLifecycleAnalyzer

# Import all metric analyzers
from .bus_factor_analyzer import BusFactorAnalyzer
from .critical_file_analyzer import CriticalFileAnalyzer
from .flow_efficiency_analyzer import FlowEfficiencyAnalyzer
from .single_point_failure_analyzer import SinglePointFailureAnalyzer

# Registry of all available metric analyzers
METRIC_ANALYZERS = {
    "bus_factor": BusFactorAnalyzer,
    "critical_files": CriticalFileAnalyzer,
    "single_point_failure": SinglePointFailureAnalyzer,
    "flow_efficiency": FlowEfficiencyAnalyzer,
    "branch_lifecycle": BranchLifecycleAnalyzer,
}


def get_available_metrics():
    """Get a list of all available metric names."""
    return list(METRIC_ANALYZERS.keys())


def create_metric_analyzer(metric_name: str, repository):
    """
    Create a metric analyzer instance.

    Args:
        metric_name: Name of the metric analyzer to create
        repository: GitRepository instance

    Returns:
        Metric analyzer instance

    Raises:
        ValueError: If metric_name is not recognized
    """
    if metric_name not in METRIC_ANALYZERS:
        available = ", ".join(get_available_metrics())
        raise ValueError(f"Unknown metric '{metric_name}'. Available metrics: {available}")

    analyzer_class = METRIC_ANALYZERS[metric_name]
    return analyzer_class(repository)


__all__ = [
    "BaseMetricAnalyzer",
    "BusFactorAnalyzer",
    "CriticalFileAnalyzer",
    "SinglePointFailureAnalyzer",
    "FlowEfficiencyAnalyzer",
    "BranchLifecycleAnalyzer",
    "METRIC_ANALYZERS",
    "get_available_metrics",
    "create_metric_analyzer",
]
