"""
Plotting functions for file-related visualizations.
"""
from typing import Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_file_analysis_visualization(metrics_coordinator, save_path: Optional[str] = None) -> go.Figure:
    """
    Create file analysis visualization.
    
    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the dashboard HTML file
        
    Returns:
        go.Figure: Plotly figure object
    """
    file_extensions = metrics_coordinator.file_analyzer.get_file_extensions_distribution()
    most_changed = metrics_coordinator.file_analyzer.get_most_changed_files()
    file_churn = metrics_coordinator.file_analyzer.get_file_churn_analysis()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('File Extensions Distribution', 'Most Changed Files',
                      'File Churn Analysis', 'Files by Change Frequency'),
        specs=[[{"type": "pie"}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    if file_extensions:
        fig.add_trace(
            go.Pie(labels=list(file_extensions.keys()), values=list(file_extensions.values()), name="Extensions"),
            row=1, col=1
        )
    
    if most_changed:
        top_files = most_changed[:15]
        files = [f['file'] for f in top_files]
        changes = [f['changes'] for f in top_files]
        fig.add_trace(
            go.Bar(x=changes, y=files, orientation='h', name='Changes',
                  marker=dict(color='lightcoral')),
            row=1, col=2
        )
        
        change_counts = [f['changes'] for f in most_changed]
        fig.add_trace(
            go.Histogram(x=change_counts, name='Change Frequency', nbinsx=15),
            row=2, col=2
        )
    
    if file_churn and 'churn_over_time' in file_churn:
        churn_data = file_churn['churn_over_time']
        fig.add_trace(
            go.Scatter(x=list(churn_data.keys()), y=list(churn_data.values()), mode='lines+markers', name='Churn',
                       line=dict(color='green', width=2)),
            row=2, col=1
        )
    
    fig.update_layout(
        title='Repository File Analysis',
        height=800,
        showlegend=True
    )
    
    if save_path:
        fig.write_html(save_path)
        
    return fig


def create_enhanced_file_analysis_dashboard(metrics_coordinator, save_path: Optional[str] = None) -> go.Figure:
    """
    Create enhanced file analysis dashboard with advanced metrics.
    
    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the dashboard HTML file
        
    Returns:
        go.Figure: Plotly figure object
    """
    file_extensions = metrics_coordinator.file_analyzer.get_file_extensions_distribution()
    most_changed = metrics_coordinator.file_analyzer.get_most_changed_files()
    file_churn = metrics_coordinator.file_analyzer.get_file_churn_analysis()
    doc_coverage = metrics_coordinator.file_analyzer.get_documentation_coverage_analysis()
    
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('File Types Distribution', 'File Change Hotspots',
                      'Code Churn Trends', 'Documentation Coverage',
                      'File Size vs Changes', 'Directory Analysis'),
        specs=[[{"type": "pie"}, {"secondary_y": False}],
               [{"secondary_y": False}, {"type": "pie"}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    if file_extensions:
        fig.add_trace(
            go.Pie(labels=list(file_extensions.keys()), values=list(file_extensions.values()), name="File Types",
                  hole=0.3, textinfo="label+percent"),
            row=1, col=1
        )
    
    if most_changed:
        top_files = most_changed[:20]
        files = [f['file'].split('/')[-1] for f in top_files]
        changes = [f['changes'] for f in top_files]
        
        fig.add_trace(
            go.Bar(x=changes, y=files, orientation='h', name='Hotspots',
                  marker=dict(color=changes, colorscale='Reds')),
            row=1, col=2
        )
        
        files_data = []
        for f in most_changed[:50]:
            size_estimate = f['changes'] * 10
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
            
        try:
            directory_stats = {}
            for f in most_changed[:30]:
                dir_name = '/'.join(f['file'].split('/')[:-1]) or 'root'
                if dir_name not in directory_stats:
                    directory_stats[dir_name] = 0
                directory_stats[dir_name] += f['changes']
            
            if directory_stats:
                dirs = list(directory_stats.keys())[:10]
                dir_changes = [directory_stats[d] for d in dirs]
                
                fig.add_trace(
                    go.Bar(x=dirs, y=dir_changes, name='Directory Activity'),
                    row=3, col=2
                )
        except Exception:
            pass

    if file_churn and 'churn_over_time' in file_churn:
        churn_data = file_churn['churn_over_time']
        dates = list(churn_data.keys())
        churn_values = list(churn_data.values())
        
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
            
    if doc_coverage and 'coverage_by_type' in doc_coverage:
        coverage_data = doc_coverage['coverage_by_type']
        fig.add_trace(
            go.Pie(labels=list(coverage_data.keys()), values=list(coverage_data.values()), name="Doc Coverage",
                  hole=0.3),
            row=2, col=2
        )
        
    fig.update_layout(
        title='Enhanced File Analysis Dashboard',
        height=1200,
        showlegend=True
    )
    fig.update_xaxes(tickangle=45, row=3, col=2)
    
    if save_path:
        fig.write_html(save_path)
        
    return fig
