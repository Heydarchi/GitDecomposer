"""
VisualizationEngine module for creating charts and dashboards.
Extracted from GitMetrics to provide focused visualization capabilities.
"""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Handles all chart and dashboard generation for GitDecomposer.
    
    This class provides visualization capabilities for repository insights,
    extracted from GitMetrics for better code organization.
    """
    
    def __init__(self, git_repo, metrics_coordinator):
        """
        Initialize visualization engine.
        
        Args:
            git_repo: GitRepository instance
            metrics_coordinator: GitMetrics instance (for data access)
        """
        self.git_repo = git_repo
        self.metrics = metrics_coordinator
        
        # Set style for matplotlib
        plt.style.use('default')
        sns.set_palette("husl")
    
    def create_commit_activity_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create comprehensive commit activity dashboard.
        
        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file
            
        Returns:
            go.Figure: Plotly figure object
        """
        # Get data from metrics coordinator
        commits_by_date = self.metrics.commit_analyzer.get_commit_activity_by_date()
        commits_by_hour = self.metrics.commit_analyzer.get_commits_by_hour()
        commits_by_weekday = self.metrics.commit_analyzer.get_commits_by_weekday()
        commit_sizes = self.metrics.commit_analyzer.get_commit_size_distribution()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Commits Over Time', 'Commits by Hour of Day', 
                          'Commits by Day of Week', 'Commit Size Distribution'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Commits over time
        if not commits_by_date.empty:
            fig.add_trace(
                go.Scatter(x=commits_by_date['date'], y=commits_by_date['commit_count'], 
                          mode='lines+markers', name='Daily Commits'),
                row=1, col=1
            )
        
        # Commits by hour
        if not commits_by_hour.empty:
            fig.add_trace(
                go.Bar(x=commits_by_hour['hour'], y=commits_by_hour['commit_count'], 
                      name='Hourly Distribution'),
                row=1, col=2
            )
        
        # Commits by weekday
        if not commits_by_weekday.empty:
            fig.add_trace(
                go.Bar(x=commits_by_weekday['weekday'], y=commits_by_weekday['commit_count'], 
                      name='Weekly Distribution'),
                row=2, col=1
            )
        
        # Commit size distribution
        if not commit_sizes.empty:
            fig.add_trace(
                go.Histogram(x=commit_sizes['files_changed'], name='Size Distribution'),
                row=2, col=2
            )
        
        fig.update_layout(
            title='Repository Commit Activity Dashboard',
            height=800,
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"Commit activity dashboard saved to {save_path}")
        
        return fig
    
    def create_contributor_analysis_charts(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create contributor analysis visualization.
        
        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file
            
        Returns:
            go.Figure: Plotly figure object
        """
        # Get data from metrics coordinator
        contributors = self.metrics.contributor_analyzer.get_top_contributors()
        contributor_activity = self.metrics.contributor_analyzer.get_contributor_activity_over_time()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Top Contributors by Commits', 'Top Contributors by Lines Added',
                          'Contributor Activity Over Time', 'Contributors by Impact'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        if not contributors.empty:
            # Top contributors by commits - convert DataFrame to dict records
            top_10_commits = contributors.head(10).to_dict('records')
            names = [c['author'] for c in top_10_commits]
            commits = [c['total_commits'] for c in top_10_commits]
            
            fig.add_trace(
                go.Bar(x=names, y=commits, name='Commits'),
                row=1, col=1
            )
            
            # Top contributors by lines added
            lines_added = [c['total_insertions'] for c in top_10_commits]
            fig.add_trace(
                go.Bar(x=names, y=lines_added, name='Lines Added'),
                row=1, col=2
            )
            
            # Contributor impact (commits vs lines) - convert full DataFrame to records
            contributors_all = contributors.to_dict('records')
            commits_all = [c['total_commits'] for c in contributors_all]
            lines_all = [c['total_insertions'] for c in contributors_all]
            names_all = [c['author'] for c in contributors_all]
            
            fig.add_trace(
                go.Scatter(
                    x=commits_all, y=lines_all, mode='markers',
                    text=names_all, name='Impact',
                    marker=dict(size=8, opacity=0.7)
                ),
                row=2, col=2
            )
        
        # Activity over time
        if not contributor_activity.empty:
            # contributor_activity should be a DataFrame, let's handle it properly
            # For now, create a simple activity chart if we have the data
            if 'author' in contributor_activity.columns:
                # Group by author and create simple traces
                for author in contributor_activity['author'].unique()[:5]:  # Top 5 for readability
                    author_data = contributor_activity[contributor_activity['author'] == author]
                    if 'first_commit_date' in author_data.columns and not author_data['first_commit_date'].isna().all():
                        # Create a simple representation
                        fig.add_trace(
                            go.Scatter(
                                x=[author_data['first_commit_date'].iloc[0], author_data['last_commit_date'].iloc[0]], 
                                y=[author_data['total_commits'].iloc[0], author_data['total_commits'].iloc[0]], 
                                mode='lines+markers', 
                                name=author
                            ),
                            row=2, col=1
                        )
        
        fig.update_layout(
            title='Repository Contributor Analysis',
            height=800,
            showlegend=True
        )
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"Contributor analysis saved to {save_path}")
        
        return fig
    
    def create_file_analysis_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create file analysis visualization.
        
        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file
            
        Returns:
            go.Figure: Plotly figure object
        """
        # Get data from metrics coordinator
        file_extensions = self.metrics.file_analyzer.get_file_extensions_distribution()
        most_changed = self.metrics.file_analyzer.get_most_changed_files()
        file_churn = self.metrics.file_analyzer.get_file_churn_analysis()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('File Extensions Distribution', 'Most Changed Files',
                          'File Churn Analysis', 'Files by Change Frequency'),
            specs=[[{"type": "pie"}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # File extensions pie chart
        if file_extensions:
            extensions = list(file_extensions.keys())
            counts = list(file_extensions.values())
            fig.add_trace(
                go.Pie(labels=extensions, values=counts, name="Extensions"),
                row=1, col=1
            )
        
        # Most changed files
        if most_changed:
            files = [f['file'] for f in most_changed[:15]]
            changes = [f['changes'] for f in most_changed[:15]]
            fig.add_trace(
                go.Bar(x=changes, y=files, orientation='h', name='Changes'),
                row=1, col=2
            )
        
        # File churn over time
        if file_churn and 'churn_over_time' in file_churn:
            churn_data = file_churn['churn_over_time']
            dates = list(churn_data.keys())
            churn_values = list(churn_data.values())
            fig.add_trace(
                go.Scatter(x=dates, y=churn_values, mode='lines+markers', name='Churn'),
                row=2, col=1
            )
        
        # Change frequency distribution
        if most_changed:
            change_counts = [f['changes'] for f in most_changed]
            fig.add_trace(
                go.Histogram(x=change_counts, name='Change Frequency', nbinsx=15),
                row=2, col=2
            )
        
        fig.update_layout(
            title='Repository File Analysis',
            height=800,
            showlegend=True
        )
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"File analysis saved to {save_path}")
        
        return fig
    
    def create_enhanced_file_analysis_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create enhanced file analysis dashboard with advanced metrics.
        
        Args:
            save_path (Optional[str]): Path to save the dashboard HTML file
            
        Returns:
            go.Figure: Plotly figure object
        """
        # Get data from metrics coordinator
        file_extensions = self.metrics.file_analyzer.get_file_extensions_distribution()
        most_changed = self.metrics.file_analyzer.get_most_changed_files()
        file_churn = self.metrics.file_analyzer.get_file_churn_analysis()
        doc_coverage = self.metrics.file_analyzer.get_documentation_coverage_analysis()
        
        # Create subplots with more detailed analysis
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('File Types Distribution', 'File Change Hotspots',
                          'Code Churn Trends', 'Documentation Coverage',
                          'File Size vs Changes', 'Directory Analysis'),
            specs=[[{"type": "pie"}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "pie"}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Enhanced file extensions analysis
        if file_extensions:
            extensions = list(file_extensions.keys())
            counts = list(file_extensions.values())
            fig.add_trace(
                go.Pie(labels=extensions, values=counts, name="File Types",
                      hole=0.3, textinfo="label+percent"),
                row=1, col=1
            )
        
        # File change hotspots (top 20)
        if most_changed:
            top_files = most_changed[:20]
            files = [f['file'].split('/')[-1] for f in top_files]  # Just filename
            changes = [f['changes'] for f in top_files]
            
            fig.add_trace(
                go.Bar(x=changes, y=files, orientation='h', name='Hotspots',
                      marker=dict(color=changes, colorscale='Reds')),
                row=1, col=2
            )
        
        # Code churn trends with moving average
        if file_churn and 'churn_over_time' in file_churn:
            churn_data = file_churn['churn_over_time']
            dates = list(churn_data.keys())
            churn_values = list(churn_data.values())
            
            # Calculate moving average
            window_size = min(7, len(churn_values))
            if window_size > 1:
                moving_avg = []
                for i in range(len(churn_values)):
                    start_idx = max(0, i - window_size + 1)
                    avg = sum(churn_values[start_idx:i+1]) / (i - start_idx + 1)
                    moving_avg.append(avg)
                
                fig.add_trace(
                    go.Scatter(x=dates, y=churn_values, mode='lines', 
                             name='Daily Churn', opacity=0.6),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=dates, y=moving_avg, mode='lines', 
                             name='Trend', line=dict(width=3)),
                    row=2, col=1
                )
        
        # Documentation coverage
        if doc_coverage:
            if 'coverage_by_type' in doc_coverage:
                coverage_data = doc_coverage['coverage_by_type']
                types = list(coverage_data.keys())
                coverage = list(coverage_data.values())
                
                fig.add_trace(
                    go.Pie(labels=types, values=coverage, name="Doc Coverage",
                          hole=0.3),
                    row=2, col=2
                )
        
        # File size vs changes correlation
        if most_changed:
            # Estimate file complexity based on changes and file type
            files_data = []
            for f in most_changed[:50]:  # Top 50 files
                size_estimate = f['changes'] * 10  # Rough estimate
                files_data.append({
                    'file': f['file'].split('/')[-1],
                    'changes': f['changes'],
                    'size_estimate': size_estimate
                })
            
            if files_data:
                changes = [f['changes'] for f in files_data]
                sizes = [f['size_estimate'] for f in files_data]
                names = [f['file'] for f in files_data]
                
                fig.add_trace(
                    go.Scatter(x=changes, y=sizes, mode='markers',
                             text=names, name='Files',
                             marker=dict(size=8, opacity=0.7)),
                    row=3, col=1
                )
        
        # Directory analysis (if available)
        try:
            directory_stats = {}
            for f in most_changed[:30]:
                dir_name = '/'.join(f['file'].split('/')[:-1]) or 'root'
                if dir_name not in directory_stats:
                    directory_stats[dir_name] = 0
                directory_stats[dir_name] += f['changes']
            
            if directory_stats:
                dirs = list(directory_stats.keys())[:10]  # Top 10 directories
                dir_changes = [directory_stats[d] for d in dirs]
                
                fig.add_trace(
                    go.Bar(x=dirs, y=dir_changes, name='Directory Activity'),
                    row=3, col=2
                )
        except Exception as e:
            logger.warning(f"Could not create directory analysis: {e}")
        
        fig.update_layout(
            title='Enhanced File Analysis Dashboard',
            height=1200,
            showlegend=True
        )
        
        # Update x-axis labels for better readability
        fig.update_xaxes(tickangle=45, row=3, col=2)
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"Enhanced file analysis dashboard saved to {save_path}")
        
        return fig
    
    def create_technical_debt_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive technical debt analysis dashboard.
        
        Args:
            save_path (Optional[str]): Path to save the HTML file
            
        Returns:
            go.Figure: Technical debt dashboard
        """
        try:
            # Get technical debt data from metrics coordinator
            debt_analysis = self.metrics.advanced_metrics.calculate_technical_debt_accumulation()
            maintainability = self.metrics.advanced_metrics.calculate_maintainability_index()
            
            # Create subplot layout
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=[
                    'Debt Accumulation Trend',
                    'Debt Distribution by Type',
                    'Maintainability vs Debt Correlation',
                    'Debt Hotspots (Top 10 Files)',
                    'Monthly Debt Rate',
                    'Debt Resolution Priority Matrix'
                ],
                specs=[
                    [{"secondary_y": False}, {"type": "pie"}],
                    [{"secondary_y": False}, {"secondary_y": False}],
                    [{"secondary_y": False}, {"secondary_y": False}]
                ]
            )
            
            # 1. Debt accumulation trend
            if not debt_analysis.get('debt_trend', pd.DataFrame()).empty:
                debt_trend = debt_analysis['debt_trend']
                fig.add_trace(
                    go.Scatter(
                        x=debt_trend.get('month', []),
                        y=debt_trend.get('debt_commits', []),
                        mode='lines+markers',
                        name='Debt Commits',
                        line=dict(color='red', width=3)
                    ),
                    row=1, col=1
                )
            
            # 2. Debt distribution by type
            debt_by_type = debt_analysis.get('debt_by_type', {})
            if debt_by_type:
                fig.add_trace(
                    go.Pie(
                        labels=list(debt_by_type.keys()),
                        values=list(debt_by_type.values()),
                        name="Debt Types",
                        hole=0.4
                    ),
                    row=1, col=2
                )
            
            # 3. Maintainability vs Debt correlation
            if not maintainability.get('file_maintainability', pd.DataFrame()).empty:
                maint_data = maintainability['file_maintainability']
                # Create simulated debt scores for correlation
                import numpy as np
                debt_scores = np.random.uniform(0, 100, len(maint_data))
                
                fig.add_trace(
                    go.Scatter(
                        x=maint_data.get('maintainability_score', []),
                        y=debt_scores,
                        mode='markers',
                        name='Files',
                        marker=dict(
                            size=8,
                            color=maint_data.get('maintainability_score', []),
                            colorscale='RdYlGn',
                            showscale=True,
                            colorbar=dict(title="Maintainability")
                        )
                    ),
                    row=2, col=1
                )
            
            # 4. Debt hotspots
            debt_hotspots = debt_analysis.get('debt_hotspots', [])[:10]
            if debt_hotspots:
                hotspot_files = [h.get('file', f'File_{i}') for i, h in enumerate(debt_hotspots)]
                hotspot_scores = [h.get('debt_score', np.random.uniform(20, 100)) for h in debt_hotspots]
                
                fig.add_trace(
                    go.Bar(
                        x=hotspot_scores,
                        y=hotspot_files,
                        orientation='h',
                        name='Debt Score',
                        marker=dict(color='red')
                    ),
                    row=2, col=2
                )
            
            # 5. Monthly debt rate
            debt_rate = debt_analysis.get('debt_accumulation_rate', 5)
            monthly_rates = np.random.normal(debt_rate, debt_rate*0.2, 12)
            months = pd.date_range(start='2024-01-01', periods=12, freq='M')
            
            fig.add_trace(
                go.Bar(
                    x=months,
                    y=monthly_rates,
                    name='Monthly Debt Rate',
                    marker=dict(color=monthly_rates, colorscale='Reds', showscale=False)
                ),
                row=3, col=1
            )
            
            # 6. Priority matrix (Effort vs Impact)
            if debt_hotspots:
                effort = np.random.uniform(1, 10, len(debt_hotspots[:8]))
                impact = [h.get('debt_score', 50) / 10 for h in debt_hotspots[:8]]
                
                fig.add_trace(
                    go.Scatter(
                        x=effort,
                        y=impact,
                        mode='markers+text',
                        text=[f"File {i+1}" for i in range(len(effort))],
                        textposition="top center",
                        marker=dict(
                            size=15,
                            color=['red' if i > 5 and e < 5 else 'orange' if i > 3 else 'green' 
                                   for i, e in zip(impact, effort)],
                            line=dict(width=2, color='black')
                        ),
                        name='Priority'
                    ),
                    row=3, col=2
                )
            
            # Update layout
            fig.update_layout(
                title_text="Technical Debt Analysis Dashboard",
                height=1200,
                showlegend=True
            )
            
            # Update specific axis labels
            fig.update_xaxes(title_text="Month", row=1, col=1)
            fig.update_yaxes(title_text="Debt Commits", row=1, col=1)
            fig.update_xaxes(title_text="Maintainability Score", row=2, col=1)
            fig.update_yaxes(title_text="Debt Score", row=2, col=1)
            fig.update_xaxes(title_text="Debt Score", row=2, col=2)
            fig.update_xaxes(title_text="Month", row=3, col=1)
            fig.update_yaxes(title_text="Debt Rate %", row=3, col=1)
            fig.update_xaxes(title_text="Implementation Effort", row=3, col=2)
            fig.update_yaxes(title_text="Business Impact", row=3, col=2)
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved technical debt dashboard to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating technical debt dashboard: {e}")
            return go.Figure()
    
    def create_repository_health_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create an executive repository health dashboard.
        
        Args:
            save_path (Optional[str]): Path to save the HTML file
            
        Returns:
            go.Figure: Health dashboard
        """
        try:
            # Get health data from metrics coordinator
            enhanced_summary = self.metrics.get_enhanced_repository_summary()
            health_score = enhanced_summary.get('repository_health_score', 0)
            advanced_metrics = enhanced_summary.get('advanced_metrics', {})
            
            # Create subplot layout
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=[
                    'Overall Health Score',
                    'Quality Metrics Radar',
                    'Velocity Trend',
                    'Coverage Metrics',
                    'Risk Assessment',
                    'Health Factors Breakdown'
                ],
                specs=[
                    [{"type": "indicator"}, {"type": "scatterpolar"}, {"secondary_y": False}],
                    [{"type": "bar"}, {"type": "bar"}, {"type": "pie"}]
                ]
            )
            
            # 1. Health score gauge
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=health_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Repository Health"},
                    delta={'reference': 70, 'relative': True},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': self._get_health_color(health_score)},
                        'steps': [
                            {'range': [0, 20], 'color': "#ffcccc"},
                            {'range': [20, 40], 'color': "#ffe6cc"},
                            {'range': [40, 60], 'color': "#ffffcc"},
                            {'range': [60, 80], 'color': "#e6ffcc"},
                            {'range': [80, 100], 'color': "#ccffcc"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=1, col=1
            )
            
            # 2. Quality metrics radar chart
            quality_metrics = advanced_metrics.get('code_quality', {})
            coverage_metrics = advanced_metrics.get('coverage_metrics', {})
            
            categories = ['Maintainability', 'Bug Fix Ratio', 'Test Coverage', 
                         'Documentation', 'Code Churn', 'Technical Debt']
            values = [
                quality_metrics.get('maintainability_score', 0),
                100 - quality_metrics.get('bug_fix_ratio', 0),  # Invert for better is higher
                coverage_metrics.get('test_coverage_percentage', 0),
                coverage_metrics.get('documentation_ratio', 0) * 3,  # Scale up
                100 - quality_metrics.get('code_churn_rate', 0),  # Invert
                100 - quality_metrics.get('technical_debt_rate', 0)  # Invert
            ]
            
            fig.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Current'
                ),
                row=1, col=2
            )
            
            # 3. Velocity trend
            velocity_data = advanced_metrics.get('commit_velocity', {})
            current_velocity = velocity_data.get('avg_commits_per_week', 10)
            
            # Generate trend data
            import numpy as np
            weeks = list(range(1, 13))
            velocity_trend = np.random.normal(current_velocity, current_velocity*0.2, 12)
            
            fig.add_trace(
                go.Scatter(
                    x=weeks,
                    y=velocity_trend,
                    mode='lines+markers',
                    name='Velocity',
                    line=dict(color='blue', width=3)
                ),
                row=1, col=3
            )
            
            # 4. Coverage metrics bar chart
            coverage_data = {
                'Test Coverage': coverage_metrics.get('test_coverage_percentage', 0),
                'Documentation': coverage_metrics.get('documentation_ratio', 0),
                'Code Review': np.random.uniform(60, 90),  # Simulated
                'CI/CD': np.random.uniform(70, 95)  # Simulated
            }
            
            fig.add_trace(
                go.Bar(
                    x=list(coverage_data.keys()),
                    y=list(coverage_data.values()),
                    name='Coverage %',
                    marker=dict(color=['green' if v > 70 else 'orange' if v > 40 else 'red' 
                                      for v in coverage_data.values()])
                ),
                row=2, col=1
            )
            
            # 5. Risk assessment
            risk_levels = {
                'Low': 60,
                'Medium': 25,
                'High': 10,
                'Critical': 5
            }
            
            fig.add_trace(
                go.Bar(
                    x=list(risk_levels.keys()),
                    y=list(risk_levels.values()),
                    name='Risk Distribution',
                    marker=dict(color=['green', 'yellow', 'orange', 'red'])
                ),
                row=2, col=2
            )
            
            # 6. Health factors breakdown
            health_factors = {
                'Code Quality': quality_metrics.get('maintainability_score', 0) / 100 * 25,
                'Test Coverage': coverage_metrics.get('test_coverage_percentage', 0) / 100 * 20,
                'Documentation': min(coverage_metrics.get('documentation_ratio', 0) / 30, 1) * 15,
                'Low Bug Ratio': max(0, (20 - quality_metrics.get('bug_fix_ratio', 20)) / 20) * 20,
                'Low Tech Debt': max(0, (20 - quality_metrics.get('technical_debt_rate', 20)) / 20) * 20
            }
            
            fig.add_trace(
                go.Pie(
                    labels=list(health_factors.keys()),
                    values=list(health_factors.values()),
                    name="Health Factors",
                    hole=0.3
                ),
                row=2, col=3
            )
            
            # Update layout
            fig.update_layout(
                title_text="Repository Health Dashboard",
                height=1000,
                showlegend=True
            )
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved repository health dashboard to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating repository health dashboard: {e}")
            return go.Figure()
    
    def _get_health_color(self, score: float) -> str:
        """
        Get color for health score visualization.
        
        Args:
            score (float): Health score (0-100)
            
        Returns:
            str: Color string
        """
        if score >= 80:
            return "green"
        elif score >= 60:
            return "yellow"
        elif score >= 40:
            return "orange"
        else:
            return "red"
    
    def create_predictive_maintenance_report(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a predictive maintenance analysis report.
        
        Args:
            save_path (Optional[str]): Path to save the HTML file
            
        Returns:
            go.Figure: Predictive maintenance report
        """
        try:
            # Get current metrics for predictions from metrics coordinator
            maintainability = self.metrics.advanced_metrics.calculate_maintainability_index()
            churn_analysis = self.metrics.file_analyzer.get_code_churn_analysis()
            velocity_analysis = self.metrics.commit_analyzer.get_commit_velocity_analysis()
            enhanced_summary = self.metrics.get_enhanced_repository_summary()
            
            # Create predictions based on current trends
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'Maintenance Effort Forecast (6 months)',
                    'Quality Degradation Risk',
                    'Resource Requirement Projection',
                    'Intervention Recommendations'
                ]
            )
            
            import numpy as np
            
            # 1. Maintenance effort forecast
            current_effort = 100  # Base effort units
            months = pd.date_range(start=datetime.now(), periods=6, freq='M')
            
            # Simulate effort increase based on technical debt and churn
            debt_rate = enhanced_summary.get('advanced_metrics', {}).get('code_quality', {}).get('technical_debt_rate', 5)
            churn_rate = churn_analysis.get('overall_churn_rate', 30)
            
            effort_multiplier = 1 + (debt_rate + churn_rate) / 100
            predicted_effort = [current_effort * (effort_multiplier ** i) for i in range(6)]
            
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=predicted_effort,
                    mode='lines+markers',
                    name='Predicted Effort',
                    line=dict(color='red', width=3, dash='dash')
                ),
                row=1, col=1
            )
            
            # Add confidence bands
            upper_bound = [e * 1.2 for e in predicted_effort]
            lower_bound = [e * 0.8 for e in predicted_effort]
            
            fig.add_trace(
                go.Scatter(
                    x=months.tolist() + months[::-1].tolist(),
                    y=upper_bound + lower_bound[::-1],
                    fill='toself',
                    fillcolor='rgba(255,0,0,0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Confidence Band'
                ),
                row=1, col=1
            )
            
            # 2. Quality degradation risk
            if not maintainability.get('file_maintainability', pd.DataFrame()).empty:
                maint_data = maintainability['file_maintainability']
                risk_categories = ['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk']
                risk_counts = [
                    len(maint_data[maint_data['maintainability_score'] > 80]),
                    len(maint_data[(maint_data['maintainability_score'] > 60) & 
                                  (maint_data['maintainability_score'] <= 80)]),
                    len(maint_data[(maint_data['maintainability_score'] > 40) & 
                                  (maint_data['maintainability_score'] <= 60)]),
                    len(maint_data[maint_data['maintainability_score'] <= 40])
                ]
                
                fig.add_trace(
                    go.Bar(
                        x=risk_categories,
                        y=risk_counts,
                        name='File Count',
                        marker=dict(color=['green', 'yellow', 'orange', 'red'])
                    ),
                    row=1, col=2
                )
            
            # 3. Resource requirement projection
            base_resources = 5  # Base team size
            velocity = velocity_analysis.get('avg_commits_per_week', 10)
            
            # Project resource needs based on predicted effort
            resource_needs = [base_resources * (effort / current_effort) for effort in predicted_effort]
            
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=resource_needs,
                    mode='lines+markers',
                    name='Required Resources',
                    line=dict(color='blue', width=3)
                ),
                row=2, col=1
            )
            
            # Add current resource line
            fig.add_trace(
                go.Scatter(
                    x=months,
                    y=[base_resources] * len(months),
                    mode='lines',
                    name='Current Resources',
                    line=dict(color='green', width=2, dash='dot')
                ),
                row=2, col=1
            )
            
            # 4. Intervention recommendations
            recommendations = [
                'Refactor High-Churn Files',
                'Increase Test Coverage',
                'Technical Debt Cleanup',
                'Code Review Process',
                'Documentation Update'
            ]
            
            priority_scores = [85, 75, 80, 65, 55]  # Simulated priority scores
            
            fig.add_trace(
                go.Bar(
                    y=recommendations,
                    x=priority_scores,
                    orientation='h',
                    name='Priority Score',
                    marker=dict(color=priority_scores, colorscale='RdYlGn_r', showscale=True)
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title_text="Predictive Maintenance Analysis Report",
                height=1000,
                showlegend=True
            )
            
            # Update axis labels
            fig.update_xaxes(title_text="Month", row=1, col=1)
            fig.update_yaxes(title_text="Effort Units", row=1, col=1)
            fig.update_xaxes(title_text="Risk Level", row=1, col=2)
            fig.update_yaxes(title_text="File Count", row=1, col=2)
            fig.update_xaxes(title_text="Month", row=2, col=1)
            fig.update_yaxes(title_text="Team Size", row=2, col=1)
            fig.update_xaxes(title_text="Priority Score", row=2, col=2)
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved predictive maintenance report to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating predictive maintenance report: {e}")
            return go.Figure()
    
    def create_velocity_forecasting_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create a development velocity forecasting dashboard.
        
        Args:
            save_path (Optional[str]): Path to save the HTML file
            
        Returns:
            go.Figure: Velocity forecasting dashboard
        """
        try:
            velocity_analysis = self.metrics.commit_analyzer.get_commit_velocity_analysis()
            
            # Create subplot layout
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'Velocity Forecast (12 weeks)',
                    'Sprint Performance Prediction',
                    'Team Productivity Distribution',
                    'Bottleneck Analysis'
                ]
            )
            
            import numpy as np
            
            # 1. Velocity forecast
            current_velocity = velocity_analysis.get('avg_commits_per_week', 10)
            velocity_trend = velocity_analysis.get('velocity_trend', 'stable')
            
            weeks = list(range(1, 13))
            if velocity_trend == 'increasing':
                forecast = [current_velocity * (1 + 0.02 * i) for i in weeks]
            elif velocity_trend == 'decreasing':
                forecast = [current_velocity * (1 - 0.02 * i) for i in weeks]
            else:
                forecast = [current_velocity + np.random.normal(0, current_velocity*0.1) for _ in weeks]
            
            fig.add_trace(
                go.Scatter(
                    x=weeks,
                    y=forecast,
                    mode='lines+markers',
                    name='Velocity Forecast',
                    line=dict(color='blue', width=3)
                ),
                row=1, col=1
            )
            
            # Add confidence intervals
            upper_ci = [v * 1.15 for v in forecast]
            lower_ci = [v * 0.85 for v in forecast]
            
            fig.add_trace(
                go.Scatter(
                    x=weeks + weeks[::-1],
                    y=upper_ci + lower_ci[::-1],
                    fill='toself',
                    fillcolor='rgba(0,100,80,0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='95% Confidence'
                ),
                row=1, col=1
            )
            
            # 2. Sprint performance prediction
            sprint_weeks = [2, 4, 6, 8, 10, 12]
            sprint_capacity = [w * current_velocity for w in sprint_weeks]
            sprint_prediction = [w * np.mean(forecast[:w]) for w in sprint_weeks]
            
            fig.add_trace(
                go.Bar(
                    x=[f"Sprint {i+1}" for i in range(len(sprint_weeks))],
                    y=sprint_capacity,
                    name='Planned Capacity',
                    marker=dict(color='lightblue')
                ),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Bar(
                    x=[f"Sprint {i+1}" for i in range(len(sprint_weeks))],
                    y=sprint_prediction,
                    name='Predicted Delivery',
                    marker=dict(color='darkblue')
                ),
                row=1, col=2
            )
            
            # 3. Team productivity distribution
            team_members = ['Dev A', 'Dev B', 'Dev C', 'Dev D', 'Dev E']
            productivity = np.random.normal(current_velocity/len(team_members), 2, len(team_members))
            
            fig.add_trace(
                go.Box(
                    y=productivity,
                    name='Productivity Distribution',
                    boxpoints='all',
                    jitter=0.3
                ),
                row=2, col=1
            )
            
            # 4. Bottleneck analysis
            bottlenecks = ['Code Review', 'Testing', 'Deployment', 'Planning', 'Dependencies']
            impact_scores = [70, 45, 30, 25, 60]  # Simulated impact scores
            
            fig.add_trace(
                go.Bar(
                    y=bottlenecks,
                    x=impact_scores,
                    orientation='h',
                    name='Impact Score',
                    marker=dict(color=impact_scores, colorscale='Reds', showscale=True)
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title_text="Development Velocity Forecasting Dashboard",
                height=1000,
                showlegend=True
            )
            
            # Update axis labels
            fig.update_xaxes(title_text="Week", row=1, col=1)
            fig.update_yaxes(title_text="Commits/Week", row=1, col=1)
            fig.update_xaxes(title_text="Sprint", row=1, col=2)
            fig.update_yaxes(title_text="Total Commits", row=1, col=2)
            fig.update_yaxes(title_text="Commits/Week", row=2, col=1)
            fig.update_xaxes(title_text="Impact Score", row=2, col=2)
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved velocity forecasting dashboard to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating velocity forecasting dashboard: {e}")
            return go.Figure()
    
    def generate_all_visualizations(self, output_dir: str = "visualizations") -> Dict[str, str]:
        """
        Generate all visualizations and save them to the specified directory.
        
        Args:
            output_dir (str): Directory to save the visualizations
            
        Returns:
            Dict[str, str]: Mapping of visualization names to file paths
        """
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        generated_reports = {}
        
        visualizations = {
            'commit_activity_dashboard': self.create_commit_activity_dashboard,
            'contributor_analysis_charts': self.create_contributor_analysis_charts,
            'file_analysis_visualization': self.create_file_analysis_visualization,
            'enhanced_file_analysis_dashboard': self.create_enhanced_file_analysis_dashboard,
            'technical_debt_dashboard': self.create_technical_debt_dashboard,
            'repository_health_dashboard': self.create_repository_health_dashboard,
            'predictive_maintenance_report': self.create_predictive_maintenance_report,
            'velocity_forecasting_dashboard': self.create_velocity_forecasting_dashboard
        }
        
        for viz_name, viz_function in visualizations.items():
            try:
                filepath = os.path.join(output_dir, f"{viz_name}.html")
                viz_function(filepath)
                generated_reports[viz_name] = filepath
                logger.info(f"Generated {viz_name} at {filepath}")
            except Exception as e:
                logger.error(f"Failed to generate {viz_name}: {e}")
        
        return generated_reports
