"""
Plotting functions for commit-related visualizations.
"""
from typing import Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_commit_activity_dashboard(metrics_coordinator, save_path: Optional[str] = None) -> go.Figure:
    """
    Create comprehensive commit activity dashboard.
    
    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the dashboard HTML file
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Get data from metrics coordinator
    commits_by_date = metrics_coordinator.commit_analyzer.get_commit_activity_by_date()
    commits_by_hour = metrics_coordinator.commit_analyzer.get_commits_by_hour()
    commits_by_weekday = metrics_coordinator.commit_analyzer.get_commits_by_weekday()
    commit_sizes = metrics_coordinator.commit_analyzer.get_commit_size_distribution()
    
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
    
    return fig
