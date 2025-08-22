"""
Services package for GitDecomposer.

This package contains service classes that handle specific responsibilities
previously managed by the monolithic GitMetrics class.
"""

from .advanced_analytics import AdvancedAnalytics
from .dashboard_generator import DashboardGenerator
from .data_aggregator import DataAggregator
from .export_service import ExportService
from .report_generator import ReportGenerator

__all__ = [
    "DataAggregator",
    "DashboardGenerator",
    "ExportService",
    "ReportGenerator",
    "AdvancedAnalytics",
]
