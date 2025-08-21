"""
FileAnalyzer module for analyzing files in a Git repository.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import pandas as pd
import logging
import os

from ..core.git_repository import GitRepository
from ..models.file import (
    FileInfo, FileStats, FileChange, HotspotFile, CodeQuality,
    DirectoryStats, FileNetwork, CodeOwnership, FileType, ChangeType
)

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
                        # Ensure file_stat is a dictionary and has the expected keys
                        if isinstance(file_stat, dict) and 'insertions' in file_stat and 'deletions' in file_stat:
                            file_metrics[file_path]['total_lines_added'] += file_stat['insertions']
                            file_metrics[file_path]['total_lines_deleted'] += file_stat['deletions']
                            file_metrics[file_path]['total_lines_changed'] += (file_stat['insertions'] + file_stat['deletions'])
                        else:
                            logger.debug(f"Unexpected file_stat format for {file_path}: {type(file_stat)}")
                        
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

    def get_code_churn_analysis(self) -> Dict[str, Any]:
        """
        Analyze code churn rate (lines changed vs total lines).
        
        Returns:
            Dict[str, Any]: Code churn metrics and analysis
        """
        try:
            commits = self.git_repo.get_all_commits()
            if not commits:
                return {
                    'overall_churn_rate': 0,
                    'file_churn_rates': pd.DataFrame(),
                    'churn_trend': pd.DataFrame(),
                    'high_churn_files': [],
                    'churn_by_extension': pd.DataFrame()
                }
            
            # Get current repository stats to estimate total lines
            repo_stats = self.git_repo.get_repository_stats()
            total_files = repo_stats.get('total_files', 1)
            
            # Estimate total lines in repository (rough calculation)
            estimated_total_lines = total_files * 50  # Average 50 lines per file estimate
            
            # Calculate cumulative line changes
            total_lines_changed = 0
            file_changes = defaultdict(lambda: {'additions': 0, 'deletions': 0, 'net_changes': 0})
            monthly_churn = defaultdict(lambda: {'lines_changed': 0, 'estimated_total': estimated_total_lines})
            
            for commit in commits:
                try:
                    commit_date = commit.committed_date
                    month_key = pd.Timestamp(commit_date, unit='s').strftime('%Y-%m')
                    
                    # Get commit statistics properly
                    commit_stats = commit.stats
                    
                    for file_path, file_stat in commit_stats.files.items():
                        # Ensure file_stat is a dictionary with the expected keys
                        if isinstance(file_stat, dict) and 'insertions' in file_stat and 'deletions' in file_stat:
                            additions = file_stat['insertions']
                            deletions = file_stat['deletions']
                            
                            file_changes[file_path]['additions'] += additions
                            file_changes[file_path]['deletions'] += deletions
                            file_changes[file_path]['net_changes'] += (additions - deletions)
                            
                            monthly_churn[month_key]['lines_changed'] += (additions + deletions)
                            total_lines_changed += (additions + deletions)
                        
                except Exception as e:
                    logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                    continue
            
            # Calculate overall churn rate
            overall_churn_rate = (total_lines_changed / estimated_total_lines * 100) if estimated_total_lines > 0 else 0
            
            # Create file churn rates DataFrame
            file_churn_data = []
            for file_path, stats in file_changes.items():
                total_changes = stats['additions'] + stats['deletions']
                # Estimate file size (rough calculation based on net changes)
                estimated_file_size = max(abs(stats['net_changes']), 50)  # Minimum 50 lines
                churn_rate = (total_changes / estimated_file_size * 100) if estimated_file_size > 0 else 0
                
                file_churn_data.append({
                    'file_path': file_path,
                    'total_additions': stats['additions'],
                    'total_deletions': stats['deletions'],
                    'total_changes': total_changes,
                    'net_changes': stats['net_changes'],
                    'estimated_size': estimated_file_size,
                    'churn_rate': churn_rate,
                    'extension': Path(file_path).suffix.lower() or 'no_extension'
                })
            
            file_churn_rates = pd.DataFrame(file_churn_data)
            
            # Create monthly churn trend
            trend_data = []
            for month, data in sorted(monthly_churn.items()):
                churn_rate = (data['lines_changed'] / data['estimated_total'] * 100) if data['estimated_total'] > 0 else 0
                trend_data.append({
                    'month': month,
                    'lines_changed': data['lines_changed'],
                    'estimated_total_lines': data['estimated_total'],
                    'churn_rate': churn_rate
                })
            
            churn_trend = pd.DataFrame(trend_data)
            if not churn_trend.empty:
                churn_trend['month'] = pd.to_datetime(churn_trend['month'])
            
            # Identify high churn files (top 10% by churn rate)
            high_churn_files = []
            if not file_churn_rates.empty:
                threshold = file_churn_rates['churn_rate'].quantile(0.9)
                high_churn = file_churn_rates[file_churn_rates['churn_rate'] >= threshold]
                high_churn_files = high_churn.nlargest(20, 'churn_rate').to_dict('records')
            
            # Calculate churn by file extension
            churn_by_extension = pd.DataFrame()
            if not file_churn_rates.empty:
                churn_by_extension = file_churn_rates.groupby('extension').agg({
                    'churn_rate': ['mean', 'std', 'count'],
                    'total_changes': 'sum'
                }).round(2)
                churn_by_extension.columns = ['avg_churn_rate', 'churn_rate_std', 'file_count', 'total_changes']
                churn_by_extension = churn_by_extension.reset_index()
                churn_by_extension = churn_by_extension.sort_values('avg_churn_rate', ascending=False)
            
            logger.info(f"Calculated code churn analysis: {overall_churn_rate:.2f}% overall churn rate")
            return {
                'overall_churn_rate': overall_churn_rate,
                'file_churn_rates': file_churn_rates,
                'churn_trend': churn_trend,
                'high_churn_files': high_churn_files,
                'churn_by_extension': churn_by_extension,
                'total_lines_changed': total_lines_changed,
                'estimated_total_lines': estimated_total_lines
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code churn: {e}")
            return {
                'overall_churn_rate': 0,
                'file_churn_rates': pd.DataFrame(),
                'churn_trend': pd.DataFrame(),
                'high_churn_files': [],
                'churn_by_extension': pd.DataFrame()
            }

    def get_documentation_coverage_analysis(self) -> Dict[str, Any]:
        """
        Analyze documentation coverage in the repository.
        
        Returns:
            Dict[str, Any]: Documentation coverage metrics
        """
        try:
            commits = self.git_repo.get_all_commits()
            if not commits:
                return {
                    'documentation_ratio': 0,
                    'doc_files_count': 0,
                    'total_files_count': 0,
                    'doc_file_types': {},
                    'missing_doc_dirs': []
                }
            
            # Documentation file patterns
            doc_extensions = {'.md', '.rst', '.txt', '.pdf', '.doc', '.docx'}
            doc_filenames = {'readme', 'changelog', 'license', 'contributing', 'authors', 'install', 'usage'}
            doc_directories = {'docs', 'doc', 'documentation', 'wiki'}
            
            all_files = set()
            doc_files = set()
            directories_with_files = set()
            
            # Collect all files from repository
            for commit in commits:
                try:
                    changed_files = self.git_repo.get_changed_files(commit.hexsha)
                    for file_path in changed_files.keys():
                        all_files.add(file_path)
                        
                        # Check if it's a documentation file
                        path_obj = Path(file_path)
                        file_ext = path_obj.suffix.lower()
                        file_name = path_obj.stem.lower()
                        dir_parts = [part.lower() for part in path_obj.parts]
                        
                        # Add directory info
                        if len(path_obj.parts) > 1:
                            directories_with_files.add(path_obj.parts[0].lower())
                        
                        # Check if it's a documentation file
                        is_doc_file = (
                            file_ext in doc_extensions or
                            file_name in doc_filenames or
                            any(doc_dir in dir_parts for doc_dir in doc_directories)
                        )
                        
                        if is_doc_file:
                            doc_files.add(file_path)
                            
                except Exception as e:
                    logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                    continue
            
            # Calculate metrics
            total_files_count = len(all_files)
            doc_files_count = len(doc_files)
            documentation_ratio = (doc_files_count / total_files_count * 100) if total_files_count > 0 else 0
            
            # Analyze documentation file types
            doc_file_types = Counter()
            for doc_file in doc_files:
                ext = Path(doc_file).suffix.lower() or 'no_extension'
                doc_file_types[ext] += 1
            
            # Check for missing documentation in directories
            missing_doc_dirs = []
            for directory in directories_with_files:
                # Check if directory has any documentation files
                has_docs = any(
                    directory in Path(doc_file).parts[0].lower() 
                    for doc_file in doc_files
                )
                if not has_docs and directory not in ['__pycache__', '.git', '.github', 'node_modules']:
                    missing_doc_dirs.append(directory)
            
            logger.info(f"Documentation coverage: {documentation_ratio:.1f}%")
            return {
                'documentation_ratio': documentation_ratio,
                'doc_files_count': doc_files_count,
                'total_files_count': total_files_count,
                'doc_file_types': dict(doc_file_types),
                'missing_doc_dirs': missing_doc_dirs[:10],  # Top 10
                'doc_files_list': list(doc_files)[:20],  # Sample of doc files
                'recommendations': self._generate_doc_recommendations(documentation_ratio, missing_doc_dirs, dict(doc_file_types))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing documentation coverage: {e}")
            return {
                'documentation_ratio': 0,
                'doc_files_count': 0,
                'total_files_count': 0,
                'doc_file_types': {},
                'missing_doc_dirs': []
            }
    
    def _generate_doc_recommendations(self, doc_ratio: float, missing_dirs: List[str], doc_types: Dict[str, int]) -> List[str]:
        """Generate recommendations for improving documentation coverage."""
        recommendations = []
        
        if doc_ratio < 5:
            recommendations.append("Very low documentation coverage - consider adding README files")
        elif doc_ratio < 15:
            recommendations.append("Low documentation coverage - add documentation for key components")
        elif doc_ratio < 30:
            recommendations.append("Moderate documentation - consider expanding existing docs")
        else:
            recommendations.append("Good documentation coverage - maintain current standards")
        
        if missing_dirs:
            recommendations.append(f"Add documentation to directories: {', '.join(missing_dirs[:3])}")
        
        if '.md' not in doc_types:
            recommendations.append("Consider using Markdown files for better documentation")
        
        if len(doc_types) == 1:
            recommendations.append("Diversify documentation formats for different audiences")
        
        return recommendations
    
    def _classify_file_type(self, file_path: str) -> FileType:
        """Classify file type based on path and extension."""
        path = Path(file_path)
        extension = path.suffix.lower()
        name = path.name.lower()
        path_str = str(path).lower()
        
        # Test files
        if ('test' in path_str or 'spec' in path_str or 
            name.startswith('test_') or name.endswith('_test.py') or
            extension in ['.test.js', '.spec.js', '.test.ts', '.spec.ts']):
            return FileType.TEST
        
        # Documentation
        if extension in ['.md', '.rst', '.txt', '.adoc'] or 'doc' in path_str:
            return FileType.DOCUMENTATION
        
        # Configuration
        if (extension in ['.json', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.toml'] or
            name in ['dockerfile', 'makefile', '.gitignore', '.gitattributes']):
            return FileType.CONFIGURATION
        
        # Build files
        if (extension in ['.xml', '.gradle'] or 
            name in ['pom.xml', 'build.gradle', 'setup.py', 'package.json']):
            return FileType.BUILD
        
        # Assets
        if extension in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.scss', '.less']:
            return FileType.ASSET
        
        # Data files
        if extension in ['.csv', '.json', '.xml', '.sql', '.db']:
            return FileType.DATA
        
        # Source code
        if extension in ['.py', '.java', '.js', '.ts', '.c', '.cpp', '.h', '.cs', '.go', '.rb', '.php']:
            return FileType.SOURCE_CODE
        
        return FileType.UNKNOWN
    
    def _extract_file_info(self, file_path: str) -> FileInfo:
        """Extract structured file information."""
        path = Path(file_path)
        
        # Try to get file size from current working tree
        size_bytes = 0
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
        except (OSError, IOError):
            pass
        
        return FileInfo(
            path=file_path,
            name=path.name,
            extension=path.suffix.lower(),
            size_bytes=size_bytes,
            file_type=self._classify_file_type(file_path),
            language=self._detect_language(path.suffix.lower())
        )
    
    def _detect_language(self, extension: str) -> Optional[str]:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'Python',
            '.java': 'Java',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.c': 'C',
            '.cpp': 'C++',
            '.h': 'C/C++',
            '.cs': 'C#',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.rs': 'Rust',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.ps1': 'PowerShell',
            '.r': 'R',
            '.m': 'MATLAB',
            '.pl': 'Perl'
        }
        return language_map.get(extension)
    
    def get_file_stats_analysis(self, file_path: str) -> FileStats:
        """Get comprehensive file statistics."""
        try:
            commits = self.git_repo.get_all_commits()
            
            total_commits = 0
            contributors = set()
            total_insertions = 0
            total_deletions = 0
            commit_dates = []
            
            for commit in commits:
                try:
                    changed_files = self.git_repo.get_changed_files(commit.hexsha)
                    if file_path in changed_files:
                        total_commits += 1
                        contributors.add((commit.author.name, commit.author.email))
                        commit_dates.append(datetime.fromtimestamp(commit.committed_date))
                        
                        # Get insertion/deletion counts from commit stats
                        commit_stats = commit.stats
                        if file_path in commit_stats.files:
                            file_data = commit_stats.files[file_path]
                            if isinstance(file_data, dict) and 'insertions' in file_data and 'deletions' in file_data:
                                total_insertions += file_data['insertions']
                                total_deletions += file_data['deletions']
                            
                except Exception as e:
                    logger.warning(f"Error processing commit {commit.hexsha} for file {file_path}: {e}")
                    continue
            
            first_commit_date = min(commit_dates) if commit_dates else None
            last_commit_date = max(commit_dates) if commit_dates else None
            
            # Get current line count (simplified)
            current_lines = 0
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        current_lines = sum(1 for _ in f)
            except (IOError, UnicodeDecodeError):
                pass
            
            return FileStats(
                path=file_path,
                total_commits=total_commits,
                total_contributors=len(contributors),
                total_insertions=total_insertions,
                total_deletions=total_deletions,
                first_commit_date=first_commit_date,
                last_commit_date=last_commit_date,
                current_lines=current_lines
            )
            
        except Exception as e:
            logger.error(f"Error analyzing file stats for {file_path}: {e}")
            return FileStats(
                path=file_path,
                total_commits=0,
                total_contributors=0,
                total_insertions=0,
                total_deletions=0,
                current_lines=0
            )
    
    def get_hotspot_files_analysis(self, limit: int = 20) -> List[HotspotFile]:
        """Get hotspot files analysis."""
        try:
            commits = self.git_repo.get_all_commits()
            file_changes = defaultdict(lambda: {
                'change_count': 0,
                'contributors': set(),
                'recent_changes': 0,
                'total_changes': 0
            })
            
            # Analyze recent activity (last 30 days)
            now = datetime.now()
            recent_cutoff = now - timedelta(days=30)
            
            for commit in commits:
                try:
                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    changed_files = self.git_repo.get_changed_files(commit.hexsha)
                    commit_stats = commit.stats
                    
                    for file_path in changed_files.keys():
                        file_changes[file_path]['change_count'] += 1
                        file_changes[file_path]['contributors'].add((commit.author.name, commit.author.email))
                        
                        if commit_date >= recent_cutoff:
                            file_changes[file_path]['recent_changes'] += 1
                        
                        # Get insertions/deletions from commit stats
                        if file_path in commit_stats.files:
                            file_data = commit_stats.files[file_path]
                            if isinstance(file_data, dict) and 'insertions' in file_data and 'deletions' in file_data:
                                insertions = file_data['insertions']
                                deletions = file_data['deletions']
                                file_changes[file_path]['total_changes'] += insertions + deletions
                            
                except Exception as e:
                    logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                    continue
            
            # Calculate hotspot files
            hotspots = []
            for file_path, data in file_changes.items():
                if data['change_count'] < 3:  # Minimum threshold
                    continue
                
                # Calculate risk score
                change_frequency = data['change_count']
                unique_contributors = len(data['contributors'])
                recent_activity = data['recent_changes']
                
                # Simple complexity score (based on file extension)
                complexity_score = self._estimate_file_complexity(file_path)
                
                # Risk calculation
                risk_score = (
                    change_frequency * 2 +
                    unique_contributors * 1.5 +
                    recent_activity * 3 +
                    complexity_score * 1
                ) / 7.5 * 100  # Normalize to 0-100
                
                hotspot = HotspotFile(
                    path=file_path,
                    change_frequency=change_frequency,
                    unique_contributors=unique_contributors,
                    complexity_score=complexity_score,
                    risk_score=min(100, risk_score),
                    recent_activity=recent_activity
                )
                hotspots.append(hotspot)
            
            # Sort by risk score and return top N
            hotspots.sort(key=lambda x: x.risk_score, reverse=True)
            return hotspots[:limit]
            
        except Exception as e:
            logger.error(f"Error analyzing hotspot files: {e}")
            return []
    
    def _estimate_file_complexity(self, file_path: str) -> float:
        """Estimate file complexity based on various factors."""
        path = Path(file_path)
        
        # Base complexity by file type
        complexity_map = {
            '.py': 5.0,
            '.java': 6.0,
            '.js': 4.0,
            '.ts': 5.0,
            '.c': 7.0,
            '.cpp': 8.0,
            '.cs': 6.0,
            '.go': 4.0,
            '.rb': 4.0,
            '.php': 5.0,
            '.html': 2.0,
            '.css': 2.0,
            '.json': 1.0,
            '.yaml': 1.0,
            '.md': 1.0
        }
        
        base_complexity = complexity_map.get(path.suffix.lower(), 3.0)
        
        # Adjust for file size (if available)
        try:
            if os.path.exists(file_path):
                size_kb = os.path.getsize(file_path) / 1024
                if size_kb > 100:  # Large files are more complex
                    base_complexity *= 1.5
                elif size_kb > 50:
                    base_complexity *= 1.2
        except (OSError, IOError):
            pass
        
        return min(10.0, base_complexity)
    
    def get_directory_stats_analysis(self) -> List[DirectoryStats]:
        """Get directory-level statistics."""
        try:
            commits = self.git_repo.get_all_commits()
            directory_data = defaultdict(lambda: {
                'files': set(),
                'commits': set(),
                'contributors': set(),
                'lines': 0,
                'file_types': defaultdict(int),
                'languages': defaultdict(int)
            })
            
            # Collect data from all commits
            for commit in commits:
                try:
                    changed_files = self.git_repo.get_changed_files(commit.hexsha)
                    
                    for file_path in changed_files.keys():
                        directory = str(Path(file_path).parent)
                        if directory == '.':
                            directory = 'root'
                        
                        directory_data[directory]['files'].add(file_path)
                        directory_data[directory]['commits'].add(commit.hexsha)
                        directory_data[directory]['contributors'].add((commit.author.name, commit.author.email))
                        
                        # File type and language
                        file_info = self._extract_file_info(file_path)
                        directory_data[directory]['file_types'][file_info.file_type] += 1
                        if file_info.language:
                            directory_data[directory]['languages'][file_info.language] += 1
                        
                except Exception as e:
                    logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                    continue
            
            # Create DirectoryStats objects
            directory_stats = []
            for directory, data in directory_data.items():
                # Calculate average file size and complexity
                avg_file_size = 0
                avg_complexity = 0
                file_count = len(data['files'])
                
                if file_count > 0:
                    total_size = 0
                    total_complexity = 0
                    valid_files = 0
                    
                    for file_path in data['files']:
                        try:
                            if os.path.exists(file_path):
                                total_size += os.path.getsize(file_path)
                                total_complexity += self._estimate_file_complexity(file_path)
                                valid_files += 1
                        except (OSError, IOError):
                            continue
                    
                    if valid_files > 0:
                        avg_file_size = total_size / valid_files
                        avg_complexity = total_complexity / valid_files
                
                stats = DirectoryStats(
                    path=directory,
                    total_files=file_count,
                    total_lines=data['lines'],  # This would need actual line counting
                    total_commits=len(data['commits']),
                    unique_contributors=len(data['contributors']),
                    file_types=dict(data['file_types']),
                    languages=dict(data['languages']),
                    avg_file_size=avg_file_size,
                    avg_complexity=avg_complexity
                )
                directory_stats.append(stats)
            
            return directory_stats
            
        except Exception as e:
            logger.error(f"Error analyzing directory stats: {e}")
            return []
