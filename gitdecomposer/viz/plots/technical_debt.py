"""
Plotting functions for technical debt visualizations.
"""
from typing import Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_technical_debt_dashboard(metrics_coordinator, save_path: Optional[str] = None) -> go.Figure:
    """
    Create a comprehensive technical debt analysis dashboard.
    
    Args:
        metrics_coordinator: GitMetrics instance for data access.
        save_path (Optional[str]): Path to save the HTML file
        
    Returns:
        go.Figure: Technical debt dashboard
    """
    try:
        debt_analysis = metrics_coordinator.advanced_metrics.calculate_technical_debt_accumulation()
        maintainability = metrics_coordinator.advanced_metrics.calculate_maintainability_index()
        
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
        
        if debt_analysis and 'debt_over_time' in debt_analysis:
            debt_df = pd.DataFrame(debt_analysis['debt_over_time'])
            fig.add_trace(
                go.Scatter(x=debt_df['date'], y=debt_df['cumulative_debt'], mode='lines', name='Debt Trend'),
                row=1, col=1
            )
            
        if debt_analysis and 'debt_by_type' in debt_analysis:
            debt_types = debt_analysis['debt_by_type']
            fig.add_trace(
                go.Pie(labels=list(debt_types.keys()), values=list(debt_types.values()), name="Debt Types"),
                row=1, col=2
            )
            
        if maintainability and 'maintainability_scores' in maintainability:
            mi_df = pd.DataFrame(maintainability['maintainability_scores'])
            if not mi_df.empty and debt_analysis and 'debt_hotspots' in debt_analysis:
                debt_hotspots_df = pd.DataFrame(debt_analysis['debt_hotspots'])
                if not debt_hotspots_df.empty:
                    merged_df = pd.merge(mi_df, debt_hotspots_df, on='file')
                    fig.add_trace(
                        go.Scatter(x=merged_df['maintainability_index'], y=merged_df['debt_score'],
                                   mode='markers', text=merged_df['file'], name='MI vs Debt'),
                        row=2, col=1
                    )
                    
                    fig.add_trace(
                        go.Bar(x=debt_hotspots_df['file'][:10], y=debt_hotspots_df['debt_score'][:10], name='Debt Hotspots'),
                        row=2, col=2
                    )

        if debt_analysis and 'debt_over_time' in debt_analysis:
            debt_df['month'] = debt_df['date'].dt.to_period('M')
            monthly_debt = debt_df.groupby('month')['debt_score'].sum().reset_index()
            monthly_debt['month'] = monthly_debt['month'].astype(str)
            fig.add_trace(
                go.Bar(x=monthly_debt['month'], y=monthly_debt['debt_score'], name='Monthly Debt'),
                row=3, col=1
            )

        fig.update_layout(
            title_text='Technical Debt Analysis Dashboard',
            height=1200,
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
            
        return fig
    except Exception:
        return go.Figure()
