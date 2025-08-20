"""
GitMetrics module for calculating and visualizing Git repository metrics.
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

from .git_repository import GitRepository
from .commit_analyzer import CommitAnalyzer
from .file_analyzer import FileAnalyzer
from .contributor_analyzer import ContributorAnalyzer
from .branch_analyzer import BranchAnalyzer

logger = logging.getLogger(__name__)


class GitMetrics:
    """
    Comprehensive metrics and visualization class for Git repository analysis.
    
    This class combines data from all analyzers and provides visualization
    capabilities for repository insights.
    """
    
    def __init__(self, git_repo: GitRepository):
        """
        Initialize GitMetrics with all analyzers.
        
        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self.commit_analyzer = CommitAnalyzer(git_repo)
        self.file_analyzer = FileAnalyzer(git_repo)
        self.contributor_analyzer = ContributorAnalyzer(git_repo)
        self.branch_analyzer = BranchAnalyzer(git_repo)
        
        # Set style for matplotlib
        plt.style.use('default')
        sns.set_palette("husl")
        
        logger.info("Initialized GitMetrics with all analyzers")
    
    def generate_repository_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive repository summary.
        
        Returns:
            Dict[str, Any]: Complete repository analysis summary
        """
        try:
            # Get basic repository stats
            repo_stats = self.git_repo.get_repository_stats()
            
            # Get contributor statistics
            contributor_stats = self.contributor_analyzer.get_contributor_statistics()
            
            # Get file statistics
            file_extensions = self.file_analyzer.get_file_extensions_distribution()
            most_changed_files = self.file_analyzer.get_most_changed_files(10)
            
            # Get commit analysis
            commit_messages = self.commit_analyzer.get_commit_messages_analysis()
            merge_analysis = self.commit_analyzer.get_merge_commit_analysis()
            
            # Get branch analysis
            branch_stats = self.branch_analyzer.get_branch_statistics()
            branching_insights = self.branch_analyzer.get_branching_strategy_insights()
            
            summary = {
                'repository_info': repo_stats,
                'contributors': {
                    'total_contributors': len(contributor_stats),
                    'top_contributors': contributor_stats.head(5)[['author', 'total_commits', 'total_insertions', 'total_deletions']].to_dict('records') if not contributor_stats.empty else [],
                    'avg_commits_per_contributor': contributor_stats['total_commits'].mean() if not contributor_stats.empty else 0
                },
                'files': {
                    'total_unique_extensions': len(file_extensions),
                    'top_extensions': file_extensions.head(5).to_dict('records') if not file_extensions.empty else [],
                    'most_changed_files': most_changed_files.head(5).to_dict('records') if not most_changed_files.empty else []
                },
                'commits': {
                    'total_commits': commit_messages.get('total_commits', 0),
                    'avg_message_length': commit_messages.get('avg_message_length', 0),
                    'merge_percentage': merge_analysis.get('merge_percentage', 0),
                    'common_commit_words': commit_messages.get('common_words', [])[:5]
                },
                'branches': {
                    'total_branches': len(branch_stats) if not branch_stats.empty else 0,
                    'branching_model': branching_insights.get('branching_model', 'Unknown'),
                    'avg_branch_lifetime': branching_insights.get('avg_branch_lifetime_days', 0),
                    'recommendations': branching_insights.get('recommendations', [])
                }
            }
            
            logger.info("Generated comprehensive repository summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating repository summary: {e}")
            return {'error': str(e)}
    
    def create_commit_activity_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create an interactive dashboard showing commit activity patterns.
        
        Args:
            save_path (str, optional): Path to save the HTML file
            
        Returns:
            plotly.graph_objects.Figure: Interactive dashboard
        """
        try:
            # Get data
            daily_commits = self.commit_analyzer.get_commit_frequency_by_date()
            hourly_commits = self.commit_analyzer.get_commit_frequency_by_hour()
            weekday_commits = self.commit_analyzer.get_commit_frequency_by_weekday()
            commit_timeline = self.commit_analyzer.get_commit_timeline('month')
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Commits Over Time', 'Commits by Hour of Day', 
                              'Commits by Day of Week', 'Monthly Commit Trend'],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Daily commits over time
            if not daily_commits.empty:
                fig.add_trace(
                    go.Scatter(x=daily_commits['date'], y=daily_commits['commit_count'],
                             mode='lines', name='Daily Commits', line=dict(color='blue')),
                    row=1, col=1
                )
            
            # Hourly distribution
            if not hourly_commits.empty:
                fig.add_trace(
                    go.Bar(x=hourly_commits['hour'], y=hourly_commits['commit_count'],
                          name='Hourly Distribution', marker_color='green'),
                    row=1, col=2
                )
            
            # Weekday distribution
            if not weekday_commits.empty:
                fig.add_trace(
                    go.Bar(x=weekday_commits['weekday'], y=weekday_commits['commit_count'],
                          name='Weekday Distribution', marker_color='orange'),
                    row=2, col=1
                )
            
            # Monthly trend
            if not commit_timeline.empty:
                fig.add_trace(
                    go.Scatter(x=commit_timeline['period'], y=commit_timeline['commit_count'],
                             mode='lines+markers', name='Monthly Trend', line=dict(color='red')),
                    row=2, col=2
                )
            
            # Update layout
            fig.update_layout(
                title_text="Git Repository Commit Activity Dashboard",
                showlegend=False,
                height=800
            )
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved commit activity dashboard to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating commit activity dashboard: {e}")
            return go.Figure()
    
    def create_contributor_analysis_charts(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create charts analyzing contributor patterns.
        
        Args:
            save_path (str, optional): Path to save the HTML file
            
        Returns:
            plotly.graph_objects.Figure: Contributor analysis charts
        """
        try:
            # Get data
            contributor_stats = self.contributor_analyzer.get_contributor_statistics()
            contributor_timeline = self.contributor_analyzer.get_contributor_activity_timeline()
            impact_analysis = self.contributor_analyzer.get_contributor_impact_analysis()
            
            if contributor_stats.empty:
                logger.warning("No contributor data available")
                return go.Figure()
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Top Contributors by Commits', 'Contributor Activity Timeline',
                              'Lines Added vs Deleted', 'Contributor Impact Score'],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Top contributors bar chart
            top_contributors = contributor_stats.head(10)
            fig.add_trace(
                go.Bar(x=top_contributors['author'], y=top_contributors['total_commits'],
                      name='Commits', marker_color='lightblue'),
                row=1, col=1
            )
            
            # Activity timeline
            if not contributor_timeline.empty:
                for author in contributor_timeline['author'].unique()[:5]:  # Top 5 for readability
                    author_data = contributor_timeline[contributor_timeline['author'] == author]
                    fig.add_trace(
                        go.Scatter(x=author_data['date'], y=author_data['commits'],
                                 mode='lines+markers', name=author),
                        row=1, col=2
                    )
            
            # Lines added vs deleted scatter
            fig.add_trace(
                go.Scatter(x=contributor_stats['total_insertions'], 
                          y=contributor_stats['total_deletions'],
                          mode='markers',
                          text=contributor_stats['author'],
                          name='Contributors',
                          marker=dict(size=contributor_stats['total_commits']/10, 
                                    color=contributor_stats['total_commits'],
                                    colorscale='Viridis', showscale=True)),
                row=2, col=1
            )
            
            # Impact score
            if not impact_analysis.empty:
                top_impact = impact_analysis.head(10)
                fig.add_trace(
                    go.Bar(x=top_impact['author'], y=top_impact['impact_score'],
                          name='Impact Score', marker_color='coral'),
                    row=2, col=2
                )
            
            # Update layout
            fig.update_layout(
                title_text="Contributor Analysis Dashboard",
                showlegend=False,
                height=800
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=45)
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved contributor analysis charts to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating contributor analysis charts: {e}")
            return go.Figure()
    
    def create_file_analysis_visualization(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create visualizations for file analysis.
        
        Args:
            save_path (str, optional): Path to save the HTML file
            
        Returns:
            plotly.graph_objects.Figure: File analysis visualizations
        """
        try:
            # Get data
            extensions_dist = self.file_analyzer.get_file_extensions_distribution()
            most_changed = self.file_analyzer.get_most_changed_files(15)
            directory_analysis = self.file_analyzer.get_directory_analysis()
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['File Extensions Distribution', 'Most Changed Files',
                              'Directory Activity', 'File Change Patterns'],
                specs=[[{"type": "pie"}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # File extensions pie chart
            if not extensions_dist.empty:
                top_extensions = extensions_dist.head(10)
                fig.add_trace(
                    go.Pie(labels=top_extensions['extension'], 
                          values=top_extensions['count'],
                          name="Extensions"),
                    row=1, col=1
                )
            
            # Most changed files
            if not most_changed.empty:
                fig.add_trace(
                    go.Bar(x=most_changed['change_count'], 
                          y=most_changed['file_path'],
                          orientation='h',
                          name='Changes',
                          marker_color='lightgreen'),
                    row=1, col=2
                )
            
            # Directory activity
            if not directory_analysis.empty:
                top_dirs = directory_analysis.head(10)
                fig.add_trace(
                    go.Bar(x=top_dirs['directory'], 
                          y=top_dirs['total_changes'],
                          name='Directory Changes',
                          marker_color='purple'),
                    row=2, col=1
                )
            
            # File complexity (if available)
            try:
                complexity = self.file_analyzer.get_file_complexity_metrics()
                if not complexity.empty:
                    top_complex = complexity.head(15)
                    fig.add_trace(
                        go.Scatter(x=top_complex['total_changes'],
                                  y=top_complex['unique_authors'],
                                  mode='markers',
                                  text=top_complex['file_path'].apply(lambda x: x.split('/')[-1]),  # Just filename
                                  name='File Complexity',
                                  marker=dict(size=top_complex['complexity_score']/10,
                                            color=top_complex['complexity_score'],
                                            colorscale='Reds', showscale=True)),
                        row=2, col=2
                    )
            except Exception as e:
                logger.warning(f"Could not create complexity chart: {e}")
            
            # Update layout
            fig.update_layout(
                title_text="File Analysis Dashboard",
                showlegend=False,
                height=800
            )
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved file analysis visualization to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating file analysis visualization: {e}")
            return go.Figure()
    
    def create_enhanced_file_analysis_dashboard(self, save_path: Optional[str] = None) -> go.Figure:
        """
        Create enhanced file analysis dashboard with new frequency and size metrics.
        
        Args:
            save_path (str, optional): Path to save the HTML file
            
        Returns:
            plotly.graph_objects.Figure: Enhanced file analysis dashboard
        """
        try:
            # Get enhanced data
            frequency_analysis = self.file_analyzer.get_file_change_frequency_analysis()
            commit_size_analysis = self.file_analyzer.get_commit_size_distribution_analysis()
            hotspots = self.file_analyzer.get_file_hotspots_analysis()
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=[
                    'File Change Frequency (Lines vs Commits)', 'Commit Size Distribution (Lines)',
                    'File Hotspots Risk Assessment', 'Commit Size Distribution (Files)',
                    'Change Intensity Over Time', 'Lines vs Files per Commit'
                ],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # 1. File Change Frequency (Lines vs Commits)
            if not frequency_analysis.empty:
                top_frequency = frequency_analysis.head(20)
                fig.add_trace(
                    go.Scatter(
                        x=top_frequency['commit_count'],
                        y=top_frequency['total_lines_changed'],
                        mode='markers',
                        text=top_frequency['file_path'].apply(lambda x: x.split('/')[-1]),
                        name='File Frequency',
                        marker=dict(
                            size=top_frequency['unique_authors'] * 5,
                            color=top_frequency['change_intensity'],
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="Change Intensity")
                        )
                    ),
                    row=1, col=1
                )
            
            # 2. Commit Size Distribution (Lines)
            if 'lines_distribution' in commit_size_analysis:
                lines_dist = commit_size_analysis['lines_distribution']
                fig.add_trace(
                    go.Bar(
                        x=list(lines_dist.keys()),
                        y=list(lines_dist.values()),
                        name='Lines Distribution',
                        marker_color='lightblue'
                    ),
                    row=1, col=2
                )
            
            # 3. File Hotspots Risk Assessment
            if not hotspots.empty:
                top_hotspots = hotspots.head(15)
                colors = {'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'lightgreen', 'Minimal': 'green'}
                fig.add_trace(
                    go.Bar(
                        x=top_hotspots['hotspot_score'],
                        y=top_hotspots['file_path'].apply(lambda x: x.split('/')[-1]),
                        orientation='h',
                        name='Hotspot Score',
                        marker_color=[colors.get(risk, 'gray') for risk in top_hotspots['risk_level']],
                        text=top_hotspots['risk_level']
                    ),
                    row=2, col=1
                )
            
            # 4. Commit Size Distribution (Files)
            if 'files_distribution' in commit_size_analysis:
                files_dist = commit_size_analysis['files_distribution']
                fig.add_trace(
                    go.Bar(
                        x=list(files_dist.keys()),
                        y=list(files_dist.values()),
                        name='Files Distribution',
                        marker_color='lightcoral'
                    ),
                    row=2, col=2
                )
            
            # 5. Change Intensity Over Time (if we have date data)
            if not frequency_analysis.empty and 'last_change_date' in frequency_analysis.columns:
                # Create time-based analysis
                time_data = frequency_analysis.copy()
                time_data['change_month'] = pd.to_datetime(time_data['last_change_date'], unit='s').dt.to_period('M')
                monthly_intensity = time_data.groupby('change_month')['change_intensity'].sum().reset_index()
                monthly_intensity['change_month'] = monthly_intensity['change_month'].dt.start_time
                
                # Normalize marker sizes based on change intensity (6-20 range)
                max_intensity = monthly_intensity['change_intensity'].max()
                min_intensity = monthly_intensity['change_intensity'].min()
                if max_intensity > min_intensity:
                    normalized_sizes = 6 + 14 * (monthly_intensity['change_intensity'] - min_intensity) / (max_intensity - min_intensity)
                else:
                    normalized_sizes = [10] * len(monthly_intensity)
                
                fig.add_trace(
                    go.Scatter(
                        x=monthly_intensity['change_month'],
                        y=monthly_intensity['change_intensity'],
                        mode='lines+markers',
                        name='Monthly Change Intensity',
                        line=dict(color='purple'),
                        marker=dict(
                            size=normalized_sizes,
                            color='purple',
                            opacity=0.7
                        )
                    ),
                    row=3, col=1
                )
            
            # 6. Lines vs Files per Commit Correlation
            if 'detailed_data' in commit_size_analysis:
                commit_data = pd.DataFrame(commit_size_analysis['detailed_data'][:100])  # Limit for performance
                if not commit_data.empty:
                    # Calculate marker sizes based on total lines changed (6-20 range)
                    max_lines = commit_data['total_lines'].max()
                    min_lines = commit_data['total_lines'].min()
                    if max_lines > min_lines:
                        normalized_sizes = 6 + 14 * (commit_data['total_lines'] - min_lines) / (max_lines - min_lines)
                    else:
                        normalized_sizes = [10] * len(commit_data)
                    
                    fig.add_trace(
                        go.Scatter(
                            x=commit_data['files_changed'],
                            y=commit_data['total_lines'],
                            mode='markers',
                            name='Commits',
                            text=commit_data['message'],
                            marker=dict(
                                size=normalized_sizes,
                                color=commit_data['total_lines'],
                                colorscale='Blues',
                                opacity=0.7
                            )
                        ),
                        row=3, col=2
                    )
            
            # Update layout
            fig.update_layout(
                title_text="Enhanced File Analysis Dashboard",
                showlegend=False,
                height=1200
            )
            
            # Update axes labels
            fig.update_xaxes(title_text="Number of Commits", row=1, col=1)
            fig.update_yaxes(title_text="Total Lines Changed", row=1, col=1)
            fig.update_xaxes(title_text="Commit Size Category", row=1, col=2)
            fig.update_yaxes(title_text="Number of Commits", row=1, col=2)
            fig.update_xaxes(title_text="Hotspot Score", row=2, col=1)
            fig.update_yaxes(title_text="File", row=2, col=1)
            fig.update_xaxes(title_text="Files Changed Category", row=2, col=2)
            fig.update_yaxes(title_text="Number of Commits", row=2, col=2)
            fig.update_xaxes(title_text="Time", row=3, col=1)
            fig.update_yaxes(title_text="Change Intensity", row=3, col=1)
            fig.update_xaxes(title_text="Files Changed", row=3, col=2)
            fig.update_yaxes(title_text="Lines Changed", row=3, col=2)
            
            if save_path:
                fig.write_html(save_path)
                logger.info(f"Saved enhanced file analysis dashboard to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating enhanced file analysis dashboard: {e}")
            return go.Figure()
    
    def export_metrics_to_csv(self, output_dir: str) -> Dict[str, str]:
        """
        Export all metrics to CSV files.
        
        Args:
            output_dir (str): Directory to save CSV files
            
        Returns:
            Dict[str, str]: Mapping of metric names to file paths
        """
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        exported_files = {}
        
        try:
            # Export contributor statistics
            contributor_stats = self.contributor_analyzer.get_contributor_statistics()
            if not contributor_stats.empty:
                contributor_path = os.path.join(output_dir, 'contributor_statistics.csv')
                contributor_stats.to_csv(contributor_path, index=False)
                exported_files['contributor_statistics'] = contributor_path
            
            # Export commit frequency
            commit_freq = self.commit_analyzer.get_commit_frequency_by_date()
            if not commit_freq.empty:
                commit_path = os.path.join(output_dir, 'commit_frequency.csv')
                commit_freq.to_csv(commit_path, index=False)
                exported_files['commit_frequency'] = commit_path
            
            # Export file analysis
            file_extensions = self.file_analyzer.get_file_extensions_distribution()
            if not file_extensions.empty:
                files_path = os.path.join(output_dir, 'file_extensions.csv')
                file_extensions.to_csv(files_path, index=False)
                exported_files['file_extensions'] = files_path
            
            most_changed = self.file_analyzer.get_most_changed_files(50)
            if not most_changed.empty:
                changed_path = os.path.join(output_dir, 'most_changed_files.csv')
                most_changed.to_csv(changed_path, index=False)
                exported_files['most_changed_files'] = changed_path
            
            # Export enhanced file analysis data
            try:
                file_frequency = self.file_analyzer.get_file_change_frequency_analysis()
                if not file_frequency.empty:
                    freq_path = os.path.join(output_dir, 'file_change_frequency.csv')
                    file_frequency.to_csv(freq_path, index=False)
                    exported_files['file_change_frequency'] = freq_path
                
                hotspots = self.file_analyzer.get_file_hotspots_analysis()
                if not hotspots.empty:
                    hotspots_path = os.path.join(output_dir, 'file_hotspots.csv')
                    hotspots.to_csv(hotspots_path, index=False)
                    exported_files['file_hotspots'] = hotspots_path
                
                commit_size_analysis = self.file_analyzer.get_commit_size_distribution_analysis()
                if 'detailed_data' in commit_size_analysis:
                    commit_size_df = pd.DataFrame(commit_size_analysis['detailed_data'])
                    size_path = os.path.join(output_dir, 'commit_size_analysis.csv')
                    commit_size_df.to_csv(size_path, index=False)
                    exported_files['commit_size_analysis'] = size_path
                    
            except Exception as e:
                logger.warning(f"Could not export enhanced file analysis data: {e}")
            
            # Export branch statistics
            branch_stats = self.branch_analyzer.get_branch_statistics()
            if not branch_stats.empty:
                branch_path = os.path.join(output_dir, 'branch_statistics.csv')
                branch_stats.to_csv(branch_path, index=False)
                exported_files['branch_statistics'] = branch_path
            
            logger.info(f"Exported {len(exported_files)} metric files to {output_dir}")
            return exported_files
            
        except Exception as e:
            logger.error(f"Error exporting metrics to CSV: {e}")
            return exported_files
    
    def create_comprehensive_report(self, output_path: str) -> bool:
        """
        Create a comprehensive HTML report with all analyses and visualizations.
        
        Args:
            output_path (str): Path to save the HTML report
            
        Returns:
            bool: Success status
        """
        try:
            # Generate summary
            summary = self.generate_repository_summary()
            
            # Create visualizations
            commit_dashboard = self.create_commit_activity_dashboard()
            contributor_charts = self.create_contributor_analysis_charts()
            file_viz = self.create_file_analysis_visualization()
            
            # Create HTML report
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Git Repository Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 15px; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .chart-container {{ margin: 30px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Git Repository Analysis Report</h1>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Repository: {summary.get('repository_info', {}).get('path', 'Unknown')}</p>
                </div>
                
                <div class="summary">
                    <h2>Repository Summary</h2>
                    <div class="metric">
                        <h3>Contributors</h3>
                        <p>Total: {summary.get('contributors', {}).get('total_contributors', 0)}</p>
                        <p>Avg Commits: {summary.get('contributors', {}).get('avg_commits_per_contributor', 0):.1f}</p>
                    </div>
                    <div class="metric">
                        <h3>Commits</h3>
                        <p>Total: {summary.get('commits', {}).get('total_commits', 0)}</p>
                        <p>Merge %: {summary.get('commits', {}).get('merge_percentage', 0):.1f}%</p>
                    </div>
                    <div class="metric">
                        <h3>Branches</h3>
                        <p>Total: {summary.get('branches', {}).get('total_branches', 0)}</p>
                        <p>Model: {summary.get('branches', {}).get('branching_model', 'Unknown')}</p>
                    </div>
                    <div class="metric">
                        <h3>Files</h3>
                        <p>Extensions: {summary.get('files', {}).get('total_unique_extensions', 0)}</p>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h2>Commit Activity Analysis</h2>
                    {commit_dashboard.to_html(include_plotlyjs='cdn', div_id='commit-dashboard')}
                </div>
                
                <div class="chart-container">
                    <h2>Contributor Analysis</h2>
                    {contributor_charts.to_html(include_plotlyjs='cdn', div_id='contributor-charts')}
                </div>
                
                <div class="chart-container">
                    <h2>File Analysis</h2>
                    {file_viz.to_html(include_plotlyjs='cdn', div_id='file-analysis')}
                </div>
                
                <div class="summary">
                    <h2>Recommendations</h2>
                    <ul>
            """
            
            # Add recommendations
            recommendations = summary.get('branches', {}).get('recommendations', [])
            for rec in recommendations:
                html_content += f"<li>{rec}</li>"
            
            html_content += """
                    </ul>
                </div>
            </body>
            </html>
            """
            
            # Save report
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Created comprehensive report at {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating comprehensive report: {e}")
            return False
