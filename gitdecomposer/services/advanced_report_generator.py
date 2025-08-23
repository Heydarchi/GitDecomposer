"""
Advanced Report Generator Service for GitDecomposer.
This service handles generating HTML reports for advanced metrics.
"""

import logging
import os
from typing import Dict, Optional
import plotly.graph_objects as go
import pandas as pd
from ..core import GitRepository
from ..analyzers.advanced_metrics import create_metric_analyzer

logger = logging.getLogger(__name__)


class AdvancedReportGenerator:
    """
    Service for generating advanced HTML reports.
    """

    def __init__(self, git_repo: GitRepository, advanced_analytics=None):
        self.git_repo = git_repo
        self.advanced_analytics = advanced_analytics

    def create_knowledge_distribution_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create knowledge distribution report."""
        logger.info("Creating knowledge distribution report")
        try:
            analyzer = create_metric_analyzer('knowledge_distribution', self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or 'knowledge_distribution' not in data or data['knowledge_distribution'].empty:
                fig.add_annotation(
                    text="Insufficient data for Knowledge Distribution report.",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Knowledge Distribution Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            gini_coefficient = data.get('gini_coefficient', 0)
            distribution_df = data.get('knowledge_distribution')

            # Main Gauge for Gini Coefficient
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=gini_coefficient,
                title={'text': "Knowledge Gini Coefficient"},
                domain={'x': [0.1, 0.9], 'y': [0.6, 0.95]},
                gauge={
                    'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 0.3], 'color': 'rgba(44, 160, 44, 0.5)'}, # green
                        {'range': [0.3, 0.6], 'color': 'rgba(255, 127, 14, 0.5)'}, # orange
                        {'range': [0.6, 1], 'color': 'rgba(214, 39, 40, 0.5)'} # red
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.6
                    }
                }
            ))

            # Bar chart for distribution
            if distribution_df is not None and not distribution_df.empty:
                distribution_df = distribution_df.sort_values(by='knowledge_percentage', ascending=False).head(15)
                fig.add_trace(go.Bar(
                    x=distribution_df['author'],
                    y=distribution_df['knowledge_percentage'],
                    name='Knowledge Distribution',
                    marker_color='rgba(31, 119, 180, 0.8)'
                ))

            fig.update_layout(
                title_text="Knowledge Distribution Analysis",
                template="plotly_white",
                height=700,
                showlegend=False,
                xaxis_title="Contributor",
                yaxis_title="Knowledge Percentage (%)",
                bargap=0.2,
            )

            if save_path:
                fig.write_html(save_path)
            return fig
        except Exception as e:
            logger.error(f"Error creating knowledge distribution report: {e}")
            return self._create_error_figure("Error creating knowledge distribution report")

    def create_bus_factor_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create bus factor analysis report."""
        logger.info("Creating bus factor report")
        try:
            analyzer = create_metric_analyzer('bus_factor', self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or 'bus_factor' not in data:
                fig.add_annotation(
                    text="Insufficient data for Bus Factor report.",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Bus Factor Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            bus_factor = data.get('bus_factor', 0)
            risk_level = data.get('risk_level', 'Unknown')
            key_contributors = data.get('key_contributors', [])

            fig.add_trace(go.Indicator(
                mode="number+gauge",
                value=bus_factor,
                title={'text': f"Bus Factor (Risk: {risk_level})"},
                domain={'x': [0.1, 0.9], 'y': [0.6, 0.95]},
                gauge={
                    'shape': "angular",
                    'axis': {'range': [0, 10]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 1], 'color': 'rgba(214, 39, 40, 0.5)'}, # red
                        {'range': [1, 3], 'color': 'rgba(255, 127, 14, 0.5)'}, # orange
                        {'range': [3, 5], 'color': 'rgba(255, 255, 0, 0.5)'}, # yellow
                        {'range': [5, 10], 'color': 'rgba(44, 160, 44, 0.5)'}, # green
                    ],
                }
            ))

            if key_contributors:
                contributors_df = pd.DataFrame(key_contributors)
                contributors_df = contributors_df.sort_values(by='knowledge_percentage', ascending=False)
                
                fig.add_trace(go.Bar(
                    x=contributors_df['author'],
                    y=contributors_df['knowledge_percentage'],
                    name='Key Contributors',
                    marker_color='rgba(31, 119, 180, 0.8)'
                ))

            fig.update_layout(
                title_text="Bus Factor Analysis",
                template="plotly_white",
                height=700,
                showlegend=False,
                xaxis_title="Key Contributors",
                yaxis_title="Knowledge Percentage (%)",
                bargap=0.2,
            )

            if save_path:
                fig.write_html(save_path)
            return fig
        except Exception as e:
            logger.error(f"Error creating bus factor report: {e}")
            return self._create_error_figure("Error creating bus factor report")

    def _create_error_figure(self, error_message: str) -> go.Figure:
        """Create a simple error figure when visualization fails."""
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="red"),
        )
        fig.update_layout(
            title="Report Generation Error",
            template="plotly_white",
        )
        return fig

    def create_critical_files_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create critical files analysis report."""
        logger.info("Creating critical files report")
        try:
            analyzer = create_metric_analyzer('critical_files', self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or 'critical_files' not in data or not data['critical_files']:
                fig.add_annotation(
                    text="No critical files identified or insufficient data.",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Critical Files Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            critical_files = data['critical_files'][:10]  # Top 10 most critical

            # Create bar chart for critical files
            file_names = [file_path.split('/')[-1] for file_path, metrics in critical_files]
            risk_scores = [metrics['criticality_score'] for file_path, metrics in critical_files]
            
            fig.add_trace(go.Bar(
                x=file_names,
                y=risk_scores,
                name='Risk Score',
                marker_color='red',
                text=[f"Risk: {score:.1f}<br>Changes: {metrics['change_frequency']}<br>Complexity: {metrics['complexity']:.1f}" 
                      for (file_path, metrics), score in zip(critical_files, risk_scores)],
                textposition='auto',
            ))

            fig.update_layout(
                title="Critical Files Analysis - Top Risk Files",
                xaxis_title="Files",
                yaxis_title="Risk Score",
                template="plotly_white",
                height=600,
                xaxis_tickangle=-45
            )

            if save_path:
                fig.write_html(save_path)
            return fig

        except Exception as e:
            logger.error(f"Error creating critical files report: {e}")
            return self._create_error_figure(f"Error generating Critical Files report: {str(e)}")

    def create_velocity_trend_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create velocity trend analysis report."""
        logger.info("Creating velocity trend report")
        try:
            analyzer = create_metric_analyzer('velocity_trend', self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or 'weekly_data' not in data or not data['weekly_data']:
                fig.add_annotation(
                    text="Insufficient data for velocity trend analysis.",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Velocity Trend Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            weekly_data = data['weekly_data']
            weeks = []
            for w in weekly_data:
                if isinstance(w['week_start'], str):
                    weeks.append(w['week_start'])
                elif hasattr(w['week_start'], 'strftime'):
                    weeks.append(w['week_start'].strftime('%Y-%m-%d'))
                else:
                    weeks.append(str(w['week_start']))
            
            commits = [w['commit_count'] for w in weekly_data]
            lines_changed = [w['total_lines_changed'] for w in weekly_data]

            # Create velocity trend chart
            fig.add_trace(go.Scatter(
                x=weeks,
                y=commits,
                mode='lines+markers',
                name='Commits per Week',
                line=dict(color='blue', width=2),
                yaxis='y1'
            ))

            fig.add_trace(go.Scatter(
                x=weeks,
                y=lines_changed,
                mode='lines+markers',
                name='Lines Changed per Week',
                line=dict(color='red', width=2),
                yaxis='y2'
            ))

            fig.update_layout(
                title="Development Velocity Trends",
                xaxis_title="Week",
                yaxis=dict(title="Commits", side="left"),
                yaxis2=dict(title="Lines Changed", side="right", overlaying="y"),
                template="plotly_white",
                height=600,
                legend=dict(x=0.02, y=0.98)
            )

            if save_path:
                fig.write_html(save_path)
            return fig

        except Exception as e:
            logger.error(f"Error creating velocity trend report: {e}")
            return self._create_error_figure(f"Error generating Velocity Trend report: {str(e)}")

    def create_cycle_time_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create cycle time analysis report."""
        logger.info("Creating cycle time report")
        try:
            analyzer = create_metric_analyzer('cycle_time', self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or 'statistics' not in data or not data['statistics']:
                fig.add_annotation(
                    text="Insufficient data for cycle time analysis.",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="orange"),
                )
                fig.update_layout(title="Cycle Time Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            metrics = data['statistics']
            
            # Create gauge for average cycle time
            avg_cycle_time = metrics.get('average_cycle_time_hours', 0) if isinstance(metrics, dict) else 0
            
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=avg_cycle_time,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Average Cycle Time (Hours)"},
                gauge={'axis': {'range': [None, 168]},  # 1 week in hours
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 24], 'color': "lightgreen"},
                           {'range': [24, 72], 'color': "yellow"},
                           {'range': [72, 168], 'color': "orange"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 120}}))

            fig.update_layout(
                title="Development Cycle Time Analysis",
                template="plotly_white",
                height=600
            )

            if save_path:
                fig.write_html(save_path)
            return fig

        except Exception as e:
            logger.error(f"Error creating cycle time report: {e}")
            return self._create_error_figure(f"Error generating Cycle Time report: {str(e)}")

    def create_single_point_failure_report(self, save_path: Optional[str] = None) -> go.Figure:
        """Create single point of failure analysis report."""
        logger.info("Creating single point failure report")
        try:
            analyzer = create_metric_analyzer('single_point_failure', self.git_repo)
            data = analyzer.calculate()

            fig = go.Figure()

            if not data or 'spof_files' not in data or not data['spof_files']:
                fig.add_annotation(
                    text="No single point of failure files identified.",
                    xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                    font=dict(size=16, color="green"),
                )
                fig.update_layout(title="Single Point of Failure Analysis")
                if save_path:
                    fig.write_html(save_path)
                return fig

            spof_files = data['spof_files'][:10]  # Top 10 SPOF files
            
            # Create bar chart for SPOF files
            file_names = [f['file'].split('/')[-1] for f in spof_files]
            dominance_scores = [f['dominance_ratio'] * 100 for f in spof_files]  # Convert to percentage
            
            fig.add_trace(go.Bar(
                x=file_names,
                y=dominance_scores,
                name='Dominance %',
                marker_color='darkred',
                text=[f"Dominance: {score:.1f}%<br>Main Author: {f['dominant_author']}" 
                      for score, f in zip(dominance_scores, spof_files)],
                textposition='auto',
            ))

            fig.update_layout(
                title="Single Point of Failure Files - High Risk Areas",
                xaxis_title="Files",
                yaxis_title="Dominance Percentage",
                template="plotly_white",
                height=600,
                xaxis_tickangle=-45
            )

            if save_path:
                fig.write_html(save_path)
            return fig

        except Exception as e:
            logger.error(f"Error creating single point failure report: {e}")
            return self._create_error_figure(f"Error generating Single Point Failure report: {str(e)}")
