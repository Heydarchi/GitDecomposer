"""
Services package for GitDecomposer.

This package contains service classes that handle specific responsibilities
previously managed by the monolithic GitMetrics class.
"""

from .data_aggregator import DataAggregator
from .dashboard_generator import DashboardGenerator
from .export_service import ExportService
from .report_generator import ReportGenerator
from .advanced_analytics import AdvancedAnalytics

__all__ = [
    "DataAggregator",
    "DashboardGenerator", 
    "ExportService",
    "ReportGenerator",
    "AdvancedAnalytics",
]
