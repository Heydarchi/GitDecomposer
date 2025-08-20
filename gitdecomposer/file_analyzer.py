"""
FileAnalyzer module for analyzing files in a Git repository.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd
import logging

from .git_repository import GitRepository

logger = logging.getLogger(__name__)


class FileAnalyzer:
    """
    Analyzer for file-related metrics in a Git repository.
    
    This class provides methods to analyze file changes, extensions,
    sizes, and modification patterns.
    """
    
    def __init__(self, git_repo: GitRepository):
        """
        Initialize the FileAnalyzer.
        
        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self._file_cache = {}
        logger.info("Initialized FileAnalyzer")
    
    def get_file_extensions_distribution(self) -> pd.DataFrame:
        """
        Get distribution of file extensions in the repository.
        
        Returns:
            pd.DataFrame: DataFrame with extensions and their counts
        """
        commits = self.git_repo.get_all_commits()
        extensions = Counter()
        
        # Get all unique files from all commits
        all_files = set()
        for commit in commits:
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            all_files.update(changed_files.keys())
        
        # Count extensions
        for file_path in all_files:
            ext = Path(file_path).suffix.lower()
            if ext:
                extensions[ext] += 1
            else:
                extensions['<no extension>'] += 1
        
        df = pd.DataFrame(list(extensions.items()), columns=['extension', 'count'])
        df = df.sort_values('count', ascending=False)
        
        logger.info(f"Analyzed {len(df)} file extensions")
        return df
    
    def get_most_changed_files(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get files that have been modified most frequently.
        
        Args:
            top_n (int): Number of top files to return
            
        Returns:
            pd.DataFrame: DataFrame with file paths and modification counts
        """
        commits = self.git_repo.get_all_commits()
        file_changes = Counter()
        
        for commit in commits:
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            for file_path in changed_files.keys():
                file_changes[file_path] += 1
        
        top_files = file_changes.most_common(top_n)
        df = pd.DataFrame(top_files, columns=['file_path', 'change_count'])
        
        # Add file extension info
        df['extension'] = df['file_path'].apply(lambda x: Path(x).suffix.lower() or '<no extension>')
        
        logger.info(f"Found top {len(df)} most changed files")
        return df
    
    def get_file_size_analysis(self, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Analyze file sizes in the repository (samples recent commit).
        
        Args:
            sample_size (int): Maximum number of files to analyze
            
        Returns:
            Dict[str, Any]: File size statistics
        """
        try:
            # Get files from the latest commit
            latest_commit = self.git_repo.repo.head.commit
            file_sizes = []
            files_analyzed = 0
            
            for item in latest_commit.tree.traverse():
                if hasattr(item, 'size') and files_analyzed < sample_size:
                    file_sizes.append({
                        'path': item.path,
                        'size': item.size,
                        'extension': Path(item.path).suffix.lower() or '<no extension>'
                    })
                    files_analyzed += 1
            
            if not file_sizes:
                return {'error': 'No files found or unable to access file sizes'}
            
            df = pd.DataFrame(file_sizes)
            
            analysis = {
                'total_files_analyzed': len(file_sizes),
                'total_size_bytes': df['size'].sum(),
                'average_file_size': df['size'].mean(),
                'median_file_size': df['size'].median(),
                'largest_files': df.nlargest(10, 'size')[['path', 'size']].to_dict('records'),
                'size_by_extension': df.groupby('extension')['size'].agg(['count', 'sum', 'mean']).to_dict('index')
            }
            
            logger.info(f"Analyzed sizes for {len(file_sizes)} files")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file sizes: {e}")
            return {'error': str(e)}
    
    def get_file_lifecycle_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze the lifecycle of a specific file.
        
        Args:
            file_path (str): Path to the file to analyze
            
        Returns:
            Dict[str, Any]: File lifecycle information
        """
        commits = self.git_repo.get_file_history(file_path)
        
        if not commits:
            return {'error': f'No history found for file: {file_path}'}
        
        # Analyze the commits that touched this file
        authors = Counter()
        change_types = Counter()
        commit_dates = []
        
        for commit in commits:
            authors[commit.author.name] += 1
            commit_dates.append(commit.committed_date)
            
            # Get change type for this commit
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            if file_path in changed_files:
                change_types[changed_files[file_path]] += 1
        
        # Calculate metrics
        first_commit = min(commit_dates) if commit_dates else None
        last_commit = max(commit_dates) if commit_dates else None
        
        analysis = {
            'file_path': file_path,
            'total_commits': len(commits),
            'unique_authors': len(authors),
            'top_contributors': authors.most_common(5),
            'change_types': dict(change_types),
            'first_modified': first_commit,
            'last_modified': last_commit,
            'days_active': (last_commit - first_commit) / 86400 if first_commit and last_commit else 0
        }
        
        logger.info(f"Analyzed lifecycle for file: {file_path}")
        return analysis
    
    def get_files_by_author(self, author_name: str) -> pd.DataFrame:
        """
        Get files modified by a specific author.
        
        Args:
            author_name (str): Name of the author
            
        Returns:
            pd.DataFrame: Files and modification counts by the author
        """
        commits = self.git_repo.get_all_commits()
        author_files = Counter()
        
        for commit in commits:
            if commit.author.name == author_name:
                changed_files = self.git_repo.get_changed_files(commit.hexsha)
                for file_path in changed_files.keys():
                    author_files[file_path] += 1
        
        df = pd.DataFrame(list(author_files.items()), columns=['file_path', 'modifications'])
        df = df.sort_values('modifications', ascending=False)
        
        # Add file extension info
        df['extension'] = df['file_path'].apply(lambda x: Path(x).suffix.lower() or '<no extension>')
        
        logger.info(f"Found {len(df)} files modified by {author_name}")
        return df
    
    def get_file_churn_analysis(self, time_window_days: int = 30) -> pd.DataFrame:
        """
        Analyze file churn (files that change frequently in a time window).
        
        Args:
            time_window_days (int): Time window in days to analyze
            
        Returns:
            pd.DataFrame: Files with high churn rates
        """
        from datetime import datetime, timedelta
        
        commits = self.git_repo.get_all_commits()
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        recent_changes = Counter()
        
        for commit in commits:
            commit_date = datetime.fromtimestamp(commit.committed_date)
            if commit_date >= cutoff_date:
                changed_files = self.git_repo.get_changed_files(commit.hexsha)
                for file_path in changed_files.keys():
                    recent_changes[file_path] += 1
        
        df = pd.DataFrame(list(recent_changes.items()), columns=['file_path', 'changes_in_period'])
        df = df.sort_values('changes_in_period', ascending=False)
        
        # Add additional metrics
        df['extension'] = df['file_path'].apply(lambda x: Path(x).suffix.lower() or '<no extension>')
        df['churn_rate'] = df['changes_in_period'] / time_window_days
        
        logger.info(f"Analyzed file churn for {time_window_days} days")
        return df
    
    def get_directory_analysis(self) -> pd.DataFrame:
        """
        Analyze activity by directory structure.
        
        Returns:
            pd.DataFrame: Directory-level statistics
        """
        commits = self.git_repo.get_all_commits()
        directory_stats = defaultdict(lambda: {'files': set(), 'changes': 0})
        
        for commit in commits:
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            for file_path in changed_files.keys():
                directory = str(Path(file_path).parent)
                if directory == '.':
                    directory = '<root>'
                
                directory_stats[directory]['files'].add(file_path)
                directory_stats[directory]['changes'] += 1
        
        # Convert to DataFrame
        data = []
        for directory, stats in directory_stats.items():
            data.append({
                'directory': directory,
                'unique_files': len(stats['files']),
                'total_changes': stats['changes'],
                'avg_changes_per_file': stats['changes'] / len(stats['files']) if stats['files'] else 0
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('total_changes', ascending=False)
        
        logger.info(f"Analyzed {len(df)} directories")
        return df
    
    def get_file_complexity_metrics(self, file_extensions: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get complexity metrics for files (based on change frequency and author count).
        
        Args:
            file_extensions (List[str], optional): Filter by specific extensions
            
        Returns:
            pd.DataFrame: File complexity metrics
        """
        commits = self.git_repo.get_all_commits()
        file_metrics = defaultdict(lambda: {'changes': 0, 'authors': set()})
        
        for commit in commits:
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            for file_path in changed_files.keys():
                file_metrics[file_path]['changes'] += 1
                file_metrics[file_path]['authors'].add(commit.author.name)
        
        # Convert to DataFrame
        data = []
        for file_path, metrics in file_metrics.items():
            extension = Path(file_path).suffix.lower() or '<no extension>'
            
            # Filter by extensions if specified
            if file_extensions and extension not in file_extensions:
                continue
            
            complexity_score = metrics['changes'] * len(metrics['authors'])
            
            data.append({
                'file_path': file_path,
                'extension': extension,
                'total_changes': metrics['changes'],
                'unique_authors': len(metrics['authors']),
                'complexity_score': complexity_score
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('complexity_score', ascending=False)
        
        logger.info(f"Calculated complexity metrics for {len(df)} files")
        return df
    
    def get_file_change_frequency_analysis(self) -> pd.DataFrame:
        """
        Analyze file change frequency based on both commits and lines changed.
        
        Returns:
            pd.DataFrame: Detailed file change frequency analysis
        """
        commits = self.git_repo.get_all_commits()
        file_metrics = defaultdict(lambda: {
            'commit_count': 0,
            'total_lines_added': 0,
            'total_lines_deleted': 0,
            'total_lines_changed': 0,
            'first_change': None,
            'last_change': None,
            'authors': set()
        })
        
        for commit in commits:
            commit_date = commit.committed_date
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            
            # Get detailed stats for this commit
            try:
                commit_stats = commit.stats
                for file_path in changed_files.keys():
                    file_metrics[file_path]['commit_count'] += 1
                    file_metrics[file_path]['authors'].add(commit.author.name)
                    
                    # Update date range
                    if (file_metrics[file_path]['first_change'] is None or 
                        commit_date < file_metrics[file_path]['first_change']):
                        file_metrics[file_path]['first_change'] = commit_date
                    
                    if (file_metrics[file_path]['last_change'] is None or 
                        commit_date > file_metrics[file_path]['last_change']):
                        file_metrics[file_path]['last_change'] = commit_date
                    
                    # Get line changes for this specific file
                    if file_path in commit_stats.files:
                        file_stat = commit_stats.files[file_path]
                        file_metrics[file_path]['total_lines_added'] += file_stat['insertions']
                        file_metrics[file_path]['total_lines_deleted'] += file_stat['deletions']
                        file_metrics[file_path]['total_lines_changed'] += (file_stat['insertions'] + file_stat['deletions'])
                        
            except Exception as e:
                logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                continue
        
        # Convert to DataFrame
        data = []
        for file_path, metrics in file_metrics.items():
            if metrics['commit_count'] == 0:
                continue
                
            # Calculate frequency metrics
            if metrics['first_change'] and metrics['last_change']:
                days_active = (metrics['last_change'] - metrics['first_change']) / 86400  # Convert to days
                commit_frequency = metrics['commit_count'] / max(days_active, 1)
                line_frequency = metrics['total_lines_changed'] / max(days_active, 1)
            else:
                commit_frequency = 0
                line_frequency = 0
            
            data.append({
                'file_path': file_path,
                'extension': Path(file_path).suffix.lower() or '<no extension>',
                'commit_count': metrics['commit_count'],
                'total_lines_added': metrics['total_lines_added'],
                'total_lines_deleted': metrics['total_lines_deleted'],
                'total_lines_changed': metrics['total_lines_changed'],
                'unique_authors': len(metrics['authors']),
                'days_active': days_active if metrics['first_change'] and metrics['last_change'] else 0,
                'commits_per_day': commit_frequency,
                'lines_changed_per_day': line_frequency,
                'avg_lines_per_commit': metrics['total_lines_changed'] / metrics['commit_count'] if metrics['commit_count'] > 0 else 0,
                'change_intensity': metrics['total_lines_changed'] * metrics['commit_count'],  # Combined metric
                'first_change_date': metrics['first_change'],
                'last_change_date': metrics['last_change']
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('change_intensity', ascending=False)
        
        logger.info(f"Analyzed change frequency for {len(df)} files")
        return df
    
    def get_commit_size_distribution_analysis(self) -> Dict[str, Any]:
        """
        Analyze commit size distribution based on lines and number of files.
        
        Returns:
            Dict[str, Any]: Commit size analysis with distribution data
        """
        commits = self.git_repo.get_all_commits()
        commit_data = []
        
        for commit in commits:
            try:
                stats = commit.stats
                changed_files = self.git_repo.get_changed_files(commit.hexsha)
                
                commit_info = {
                    'sha': commit.hexsha[:8],
                    'author': commit.author.name,
                    'date': commit.committed_date,
                    'message': commit.message.strip().split('\n')[0][:100],  # First line, max 100 chars
                    'files_changed': len(changed_files),
                    'total_lines': stats.total['lines'],
                    'lines_added': stats.total['insertions'],
                    'lines_deleted': stats.total['deletions'],
                    'net_lines': stats.total['insertions'] - stats.total['deletions']
                }
                
                commit_data.append(commit_info)
                
            except Exception as e:
                logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                continue
        
        if not commit_data:
            return {'error': 'No commit data available'}
        
        df = pd.DataFrame(commit_data)
        
        # Calculate size categories based on lines changed
        def categorize_by_lines(total_lines):
            if total_lines <= 10:
                return 'XS (≤10 lines)'
            elif total_lines <= 50:
                return 'S (11-50 lines)'
            elif total_lines <= 200:
                return 'M (51-200 lines)'
            elif total_lines <= 500:
                return 'L (201-500 lines)'
            else:
                return 'XL (>500 lines)'
        
        # Calculate size categories based on files changed
        def categorize_by_files(file_count):
            if file_count <= 2:
                return 'Few (≤2 files)'
            elif file_count <= 5:
                return 'Some (3-5 files)'
            elif file_count <= 10:
                return 'Many (6-10 files)'
            else:
                return 'Massive (>10 files)'
        
        df['size_by_lines'] = df['total_lines'].apply(categorize_by_lines)
        df['size_by_files'] = df['files_changed'].apply(categorize_by_files)
        
        # Calculate distributions
        lines_distribution = df['size_by_lines'].value_counts().to_dict()
        files_distribution = df['size_by_files'].value_counts().to_dict()
        
        # Statistical analysis
        analysis = {
            'total_commits': len(df),
            'lines_distribution': lines_distribution,
            'files_distribution': files_distribution,
            'statistics': {
                'avg_lines_per_commit': df['total_lines'].mean(),
                'median_lines_per_commit': df['total_lines'].median(),
                'max_lines_commit': df.loc[df['total_lines'].idxmax()].to_dict() if not df.empty else None,
                'avg_files_per_commit': df['files_changed'].mean(),
                'median_files_per_commit': df['files_changed'].median(),
                'max_files_commit': df.loc[df['files_changed'].idxmax()].to_dict() if not df.empty else None,
            },
            'correlations': {
                'lines_vs_files_correlation': df['total_lines'].corr(df['files_changed']) if len(df) > 1 else 0
            },
            'detailed_data': df.to_dict('records')[:100]  # Top 100 commits for detailed view
        }
        
        logger.info(f"Analyzed commit size distribution for {len(df)} commits")
        return analysis
    
    def get_file_hotspots_analysis(self) -> pd.DataFrame:
        """
        Identify file hotspots based on change frequency and impact.
        
        Returns:
            pd.DataFrame: File hotspots with risk assessment
        """
        frequency_data = self.get_file_change_frequency_analysis()
        
        if frequency_data.empty:
            return pd.DataFrame()
        
        # Calculate hotspot score based on multiple factors
        def calculate_hotspot_score(row):
            # Normalize metrics (0-1 scale)
            max_commits = frequency_data['commit_count'].max()
            max_lines = frequency_data['total_lines_changed'].max()
            max_authors = frequency_data['unique_authors'].max()
            
            commit_score = row['commit_count'] / max_commits if max_commits > 0 else 0
            lines_score = row['total_lines_changed'] / max_lines if max_lines > 0 else 0
            author_score = row['unique_authors'] / max_authors if max_authors > 0 else 0
            
            # Weighted combination
            hotspot_score = (commit_score * 0.4 + lines_score * 0.4 + author_score * 0.2) * 100
            return hotspot_score
        
        frequency_data['hotspot_score'] = frequency_data.apply(calculate_hotspot_score, axis=1)
        
        # Risk assessment
        def assess_risk(row):
            score = row['hotspot_score']
            if score >= 80:
                return 'Critical'
            elif score >= 60:
                return 'High'
            elif score >= 40:
                return 'Medium'
            elif score >= 20:
                return 'Low'
            else:
                return 'Minimal'
        
        frequency_data['risk_level'] = frequency_data.apply(assess_risk, axis=1)
        
        # Add recommendations
        def generate_recommendation(row):
            recommendations = []
            if row['commit_count'] > 50:
                recommendations.append("Consider refactoring - high change frequency")
            if row['total_lines_changed'] > 1000:
                recommendations.append("Large cumulative changes - review complexity")
            if row['unique_authors'] > 5:
                recommendations.append("Many contributors - ensure good documentation")
            if row['avg_lines_per_commit'] > 100:
                recommendations.append("Large commits - consider smaller changes")
                
            return "; ".join(recommendations) if recommendations else "File appears stable"
        
        frequency_data['recommendations'] = frequency_data.apply(generate_recommendation, axis=1)
        
        # Sort by hotspot score
        hotspots = frequency_data.sort_values('hotspot_score', ascending=False)
        
        logger.info(f"Identified {len(hotspots)} file hotspots")
        return hotspots
