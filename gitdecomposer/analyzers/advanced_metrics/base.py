"""
Base classes for advanced repository metrics analyzers.

This module contains the abstract base class that all metric analyzers inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class BaseMetricAnalyzer(ABC):
    """Base class for all advanced repository metrics."""
    
    def __init__(self, repository):
        """
        Initialize the metric analyzer.
        
        Args:
            repository: GitRepository instance to analyze
        """
        self.repository = repository
        self.cache = {}
        
    @abstractmethod
    def calculate(self, **kwargs) -> Dict[str, Any]:
        """
        Calculate the metric.
        
        Returns:
            Dictionary containing the calculated metric results
        """
        pass
    
    @abstractmethod
    def get_metric_name(self) -> str:
        """Return the name of this metric."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of what this metric measures."""
        pass
    
    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """
        Get recommendations based on metric results.
        
        Args:
            results: The calculated metric results
            
        Returns:
            List of actionable recommendations
        """
        return []
    
    def clear_cache(self):
        """Clear the analyzer's cache."""
        self.cache.clear()
    
    def get_cache_key(self, **kwargs) -> str:
        """
        Generate a cache key for the given parameters.
        
        Args:
            **kwargs: Parameters used in calculation
            
        Returns:
            String cache key
        """
        key_parts = [self.get_metric_name()]
        for k, v in sorted(kwargs.items()):
            if isinstance(v, datetime):
                key_parts.append(f"{k}:{v.isoformat()}")
            else:
                key_parts.append(f"{k}:{v}")
        return "|".join(key_parts)
