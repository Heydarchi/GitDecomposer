"""
Flow Efficiency Analyzer - Measures how much time is spent on active 
development vs. waiting.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseMetricAnalyzer


class FlowEfficiencyAnalyzer(BaseMetricAnalyzer):
    """
    Calculates flow efficiency for development processes.
    
    Flow efficiency measures the ratio of active development time to total
    flow time, helping identify bottlenecks in the development process.
    """
    
    def __init__(self, repository):
        super().__init__(repository)
        
    def get_metric_name(self) -> str:
        return "Flow Efficiency"
        
    def get_description(self) -> str:
        return ("Measures the ratio of active development time to total flow time, "
                "identifying bottlenecks in the development process.")
    
    def calculate(self, branch_patterns: List[str] = None) -> Dict[str, Any]:
        """
        Calculate flow efficiency for feature branches.
        
        Args:
            branch_patterns: List of branch patterns to analyze (e.g., ['feature/*', 'bugfix/*'])
            
        Returns:
            Dictionary containing flow efficiency analysis results
        """
        if branch_patterns is None:
            branch_patterns = ['feature/*', 'bugfix/*', 'hotfix/*']
        
        flow_metrics = self._analyze_branch_flow(branch_patterns)
        
        if not flow_metrics:
            return {
                'flow_metrics': [],
                'overall_efficiency': 0.0,
                'error': 'No suitable branches found for analysis'
            }
        
        analysis = self._analyze_flow_efficiency(flow_metrics)
        
        return {
            'flow_metrics': flow_metrics,
            'analysis': analysis,
            'recommendations': self.get_recommendations(analysis)
        }
    
    def _analyze_branch_flow(self, branch_patterns: List[str]) -> List[Dict[str, Any]]:
        """Analyze flow efficiency for branches matching the given patterns."""
        flow_metrics = []
        
        # Get all branches
        all_branches = self.repository.get_branches()
        
        # Filter branches by patterns
        target_branches = []
        for branch in all_branches:
            for pattern in branch_patterns:
                # Simple pattern matching (in real implementation, use glob)
                if pattern.endswith('*') and branch.name.startswith(pattern[:-1]):
                    target_branches.append(branch)
                    break
                elif branch.name == pattern:
                    target_branches.append(branch)
                    break
        
        # Analyze each branch
        for branch in target_branches:
            try:
                branch_metrics = self._calculate_branch_flow_efficiency(branch)
                if branch_metrics:
                    flow_metrics.append(branch_metrics)
            except Exception as e:
                # Skip branches that can't be analyzed
                continue
        
        return flow_metrics
    
    def _calculate_branch_flow_efficiency(self, branch) -> Dict[str, Any]:
        """Calculate flow efficiency for a single branch."""
        # Get commits for the branch
        commits = list(self.repository.get_commits(branch=branch.name))
        
        if len(commits) < 2:
            return None
        
        # Sort commits by date
        commits.sort(key=lambda c: c.committed_datetime)
        
        # Timeline analysis
        first_commit = commits[0]
        last_commit = commits[-1]
        total_time = last_commit.committed_datetime - first_commit.committed_datetime
        
        if total_time.total_seconds() == 0:
            return None
        
        # Calculate active development days
        commit_dates = set(commit.committed_datetime.date() for commit in commits)
        active_days = len(commit_dates)
        
        # Find merge information (simplified - in reality, would check for merge commits)
        merge_commit = self._find_merge_commit(branch)
        
        if merge_commit:
            flow_time = merge_commit.committed_datetime - first_commit.committed_datetime
            flow_time_days = flow_time.days if flow_time.days > 0 else 1
        else:
            flow_time_days = total_time.days if total_time.days > 0 else 1
        
        # Calculate flow efficiency
        flow_efficiency = (active_days / flow_time_days) if flow_time_days > 0 else 0
        
        return {
            'branch': branch.name,
            'flow_time_days': flow_time_days,
            'active_days': active_days,
            'flow_efficiency': min(flow_efficiency, 1.0),  # Cap at 100%
            'commits': len(commits),
            'avg_commits_per_active_day': len(commits) / active_days if active_days > 0 else 0,
            'first_commit_date': first_commit.committed_datetime,
            'last_commit_date': last_commit.committed_datetime,
            'total_duration_hours': total_time.total_seconds() / 3600
        }
    
    def _find_merge_commit(self, branch):
        """Find the merge commit for a branch (simplified implementation)."""
        # In a real implementation, this would search for merge commits
        # For now, return None to use last commit date
        return None
    
    def _analyze_flow_efficiency(self, flow_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the flow efficiency data to provide insights."""
        if not flow_metrics:
            return {}
        
        # Calculate aggregate metrics
        efficiencies = [fm['flow_efficiency'] for fm in flow_metrics]
        flow_times = [fm['flow_time_days'] for fm in flow_metrics]
        active_days_list = [fm['active_days'] for fm in flow_metrics]
        
        analysis = {
            'total_branches_analyzed': len(flow_metrics),
            'overall_efficiency': sum(efficiencies) / len(efficiencies),
            'median_efficiency': self._calculate_median(efficiencies),
            'avg_flow_time_days': sum(flow_times) / len(flow_times),
            'avg_active_days': sum(active_days_list) / len(active_days_list),
            'efficiency_distribution': self._analyze_efficiency_distribution(efficiencies),
            'bottleneck_indicators': self._identify_bottlenecks(flow_metrics),
            'best_practices': self._identify_best_practices(flow_metrics),
            'performance_category': self._categorize_performance(sum(efficiencies) / len(efficiencies))
        }
        
        return analysis
    
    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median of a list of values."""
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _analyze_efficiency_distribution(self, efficiencies: List[float]) -> Dict[str, int]:
        """Analyze the distribution of efficiency scores."""
        distribution = {
            'excellent': 0,  # > 0.8
            'good': 0,       # 0.6 - 0.8
            'average': 0,    # 0.4 - 0.6
            'poor': 0,       # 0.2 - 0.4
            'very_poor': 0   # < 0.2
        }
        
        for efficiency in efficiencies:
            if efficiency > 0.8:
                distribution['excellent'] += 1
            elif efficiency > 0.6:
                distribution['good'] += 1
            elif efficiency > 0.4:
                distribution['average'] += 1
            elif efficiency > 0.2:
                distribution['poor'] += 1
            else:
                distribution['very_poor'] += 1
        
        return distribution
    
    def _identify_bottlenecks(self, flow_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential bottlenecks in the development flow."""
        bottlenecks = []
        
        # Find branches with low efficiency but high flow time
        for metrics in flow_metrics:
            if (metrics['flow_efficiency'] < 0.3 and 
                metrics['flow_time_days'] > 7):
                
                bottlenecks.append({
                    'branch': metrics['branch'],
                    'efficiency': metrics['flow_efficiency'],
                    'flow_time_days': metrics['flow_time_days'],
                    'active_days': metrics['active_days'],
                    'issue': 'Low efficiency with long flow time'
                })
        
        # Sort by severity (lowest efficiency first)
        bottlenecks.sort(key=lambda x: x['efficiency'])
        
        return bottlenecks[:10]  # Return top 10 bottlenecks
    
    def _identify_best_practices(self, flow_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify branches that demonstrate best practices."""
        best_practices = []
        
        # Find branches with high efficiency and reasonable flow time
        for metrics in flow_metrics:
            if (metrics['flow_efficiency'] > 0.7 and 
                metrics['flow_time_days'] <= 14):
                
                best_practices.append({
                    'branch': metrics['branch'],
                    'efficiency': metrics['flow_efficiency'],
                    'flow_time_days': metrics['flow_time_days'],
                    'active_days': metrics['active_days'],
                    'practice': 'High efficiency with reasonable flow time'
                })
        
        # Sort by efficiency (highest first)
        best_practices.sort(key=lambda x: x['efficiency'], reverse=True)
        
        return best_practices[:5]  # Return top 5 examples
    
    def _categorize_performance(self, overall_efficiency: float) -> str:
        """Categorize the overall flow efficiency performance."""
        if overall_efficiency > 0.8:
            return "EXCELLENT"
        elif overall_efficiency > 0.6:
            return "GOOD"
        elif overall_efficiency > 0.4:
            return "AVERAGE"
        elif overall_efficiency > 0.2:
            return "POOR"
        else:
            return "VERY_POOR"
    
    def get_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on flow efficiency analysis."""
        recommendations = []
        
        if not analysis:
            return ["Unable to generate recommendations - insufficient data"]
        
        overall_efficiency = analysis.get('overall_efficiency', 0)
        performance_category = analysis.get('performance_category', 'UNKNOWN')
        bottlenecks = analysis.get('bottleneck_indicators', [])
        
        # Performance-based recommendations
        if performance_category == "VERY_POOR":
            recommendations.extend([
                "URGENT: Flow efficiency is critically low",
                "Investigate major process bottlenecks immediately",
                "Consider implementing continuous integration/deployment",
                "Review code review and approval processes"
            ])
        elif performance_category == "POOR":
            recommendations.extend([
                "Flow efficiency needs significant improvement",
                "Identify and address process bottlenecks",
                "Consider reducing work-in-progress limits",
                "Implement automated testing to reduce review time"
            ])
        elif performance_category == "AVERAGE":
            recommendations.extend([
                "Flow efficiency has room for improvement",
                "Optimize development workflows",
                "Consider improving tooling and automation"
            ])
        elif performance_category in ["GOOD", "EXCELLENT"]:
            recommendations.extend([
                "Good flow efficiency - maintain current practices",
                "Continue monitoring for process degradation",
                "Share best practices with other teams"
            ])
        
        # Bottleneck-specific recommendations
        if bottlenecks:
            recommendations.extend([
                f"Address {len(bottlenecks)} identified bottlenecks",
                "Focus on branches with long wait times",
                "Consider parallel development strategies"
            ])
        
        # General process recommendations
        avg_flow_time = analysis.get('avg_flow_time_days', 0)
        if avg_flow_time > 14:
            recommendations.append("Consider breaking down large features into smaller chunks")
        
        if avg_flow_time > 30:
            recommendations.append("PRIORITY: Feature delivery time is too long - review process")
        
        return recommendations
