"""
ContributorAnalyzer module for analyzing contributor patterns and statistics.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
import logging

from .git_repository import GitRepository

logger = logging.getLogger(__name__)


class ContributorAnalyzer:
    """
    Analyzer for contributor-related metrics and patterns.
    
    This class provides methods to analyze contributor activity,
    collaboration patterns, and contribution statistics.
    """
    
    def __init__(self, git_repo: GitRepository):
        """
        Initialize the ContributorAnalyzer.
        
        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self._contributors_cache = None
        logger.info("Initialized ContributorAnalyzer")
    
    def get_contributor_statistics(self) -> pd.DataFrame:
        """
        Get comprehensive statistics for all contributors.
        
        Returns:
            pd.DataFrame: Contributor statistics including commits, lines, etc.
        """
        commits = self.git_repo.get_all_commits()
        contributor_stats = defaultdict(lambda: {
            'commits': 0,
            'total_insertions': 0,
            'total_deletions': 0,
            'files_modified': set(),
            'first_commit': None,
            'last_commit': None,
            'commit_dates': []
        })
        
        for commit in commits:
            author = commit.author.name
            commit_date = datetime.fromtimestamp(commit.committed_date)
            
            contributor_stats[author]['commits'] += 1
            contributor_stats[author]['commit_dates'].append(commit_date)
            
            # Update first and last commit dates
            if (contributor_stats[author]['first_commit'] is None or 
                commit_date < contributor_stats[author]['first_commit']):
                contributor_stats[author]['first_commit'] = commit_date
                
            if (contributor_stats[author]['last_commit'] is None or 
                commit_date > contributor_stats[author]['last_commit']):
                contributor_stats[author]['last_commit'] = commit_date
            
            # Get commit statistics
            try:
                stats = commit.stats
                contributor_stats[author]['total_insertions'] += stats.total['insertions']
                contributor_stats[author]['total_deletions'] += stats.total['deletions']
                
                # Track files modified
                changed_files = self.git_repo.get_changed_files(commit.hexsha)
                contributor_stats[author]['files_modified'].update(changed_files.keys())
                
            except Exception as e:
                logger.warning(f"Error processing commit stats for {commit.hexsha}: {e}")
        
        # Convert to DataFrame
        data = []
        for author, stats in contributor_stats.items():
            if stats['commit_dates']:
                activity_span = (stats['last_commit'] - stats['first_commit']).days if stats['first_commit'] != stats['last_commit'] else 0
                avg_commits_per_day = stats['commits'] / max(activity_span, 1)
            else:
                activity_span = 0
                avg_commits_per_day = 0
            
            data.append({
                'author': author,
                'total_commits': stats['commits'],
                'total_insertions': stats['total_insertions'],
                'total_deletions': stats['total_deletions'],
                'net_lines': stats['total_insertions'] - stats['total_deletions'],
                'files_touched': len(stats['files_modified']),
                'first_commit_date': stats['first_commit'],
                'last_commit_date': stats['last_commit'],
                'activity_span_days': activity_span,
                'avg_commits_per_day': avg_commits_per_day
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('total_commits', ascending=False)
        
        logger.info(f"Analyzed statistics for {len(df)} contributors")
        return df
    
    def get_contributor_activity_timeline(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get activity timeline for top contributors.
        
        Args:
            top_n (int): Number of top contributors to include
            
        Returns:
            pd.DataFrame: Timeline of contributor activity
        """
        # Get top contributors by commit count
        contributor_stats = self.get_contributor_statistics()
        top_contributors = contributor_stats.head(top_n)['author'].tolist()
        
        commits = self.git_repo.get_all_commits()
        timeline_data = []
        
        for commit in commits:
            if commit.author.name in top_contributors:
                commit_date = datetime.fromtimestamp(commit.committed_date)
                timeline_data.append({
                    'date': commit_date.date(),
                    'author': commit.author.name,
                    'month': commit_date.strftime('%Y-%m')
                })
        
        df = pd.DataFrame(timeline_data)
        if not df.empty:
            # Group by month and author
            monthly_activity = df.groupby(['month', 'author']).size().reset_index(name='commits')
            monthly_activity['date'] = pd.to_datetime(monthly_activity['month'])
            monthly_activity = monthly_activity.sort_values('date')
        else:
            monthly_activity = pd.DataFrame(columns=['month', 'author', 'commits', 'date'])
        
        logger.info(f"Created activity timeline for top {top_n} contributors")
        return monthly_activity
    
    def get_collaboration_matrix(self, min_shared_files: int = 3) -> pd.DataFrame:
        """
        Get collaboration matrix showing which contributors work on similar files.
        
        Args:
            min_shared_files (int): Minimum number of shared files to consider collaboration
            
        Returns:
            pd.DataFrame: Collaboration matrix
        """
        commits = self.git_repo.get_all_commits()
        contributor_files = defaultdict(set)
        
        # Collect files touched by each contributor
        for commit in commits:
            author = commit.author.name
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            contributor_files[author].update(changed_files.keys())
        
        # Calculate collaboration scores
        contributors = list(contributor_files.keys())
        collaboration_data = []
        
        for i, contrib1 in enumerate(contributors):
            for j, contrib2 in enumerate(contributors):
                if i <= j:  # Avoid duplicates and self-comparison
                    continue
                
                shared_files = contributor_files[contrib1] & contributor_files[contrib2]
                if len(shared_files) >= min_shared_files:
                    collaboration_data.append({
                        'contributor_1': contrib1,
                        'contributor_2': contrib2,
                        'shared_files': len(shared_files),
                        'total_files_1': len(contributor_files[contrib1]),
                        'total_files_2': len(contributor_files[contrib2]),
                        'collaboration_score': len(shared_files) / min(len(contributor_files[contrib1]), len(contributor_files[contrib2]))
                    })
        
        df = pd.DataFrame(collaboration_data)
        if not df.empty:
            df = df.sort_values('collaboration_score', ascending=False)
        
        logger.info(f"Found {len(df)} collaboration relationships")
        return df
    
    def get_contributor_specialization(self) -> pd.DataFrame:
        """
        Analyze what file types/directories each contributor specializes in.
        
        Returns:
            pd.DataFrame: Contributor specialization data
        """
        commits = self.git_repo.get_all_commits()
        contributor_extensions = defaultdict(lambda: defaultdict(int))
        contributor_directories = defaultdict(lambda: defaultdict(int))
        
        for commit in commits:
            author = commit.author.name
            changed_files = self.git_repo.get_changed_files(commit.hexsha)
            
            for file_path in changed_files.keys():
                # File extension
                from pathlib import Path
                extension = Path(file_path).suffix.lower() or '<no extension>'
                contributor_extensions[author][extension] += 1
                
                # Directory
                directory = str(Path(file_path).parent)
                if directory == '.':
                    directory = '<root>'
                contributor_directories[author][directory] += 1
        
        # Create specialization data
        specialization_data = []
        
        for author in contributor_extensions.keys():
            # Get top extensions for this contributor
            extensions = contributor_extensions[author]
            top_extensions = Counter(extensions).most_common(3)
            
            # Get top directories for this contributor
            directories = contributor_directories[author]
            top_directories = Counter(directories).most_common(3)
            
            total_changes = sum(extensions.values())
            
            specialization_data.append({
                'author': author,
                'total_file_changes': total_changes,
                'top_extensions': [f"{ext} ({count})" for ext, count in top_extensions],
                'top_directories': [f"{dir} ({count})" for dir, count in top_directories],
                'primary_extension': top_extensions[0][0] if top_extensions else 'None',
                'extension_focus': (top_extensions[0][1] / total_changes * 100) if top_extensions and total_changes > 0 else 0
            })
        
        df = pd.DataFrame(specialization_data)
        df = df.sort_values('total_file_changes', ascending=False)
        
        logger.info(f"Analyzed specialization for {len(df)} contributors")
        return df
    
    def get_new_vs_experienced_contributors(self, days_threshold: int = 90) -> Dict[str, Any]:
        """
        Classify contributors as new vs experienced based on activity duration.
        
        Args:
            days_threshold (int): Days threshold to classify as experienced
            
        Returns:
            Dict[str, Any]: Classification statistics
        """
        contributor_stats = self.get_contributor_statistics()
        
        new_contributors = contributor_stats[contributor_stats['activity_span_days'] <= days_threshold]
        experienced_contributors = contributor_stats[contributor_stats['activity_span_days'] > days_threshold]
        
        analysis = {
            'total_contributors': len(contributor_stats),
            'new_contributors': len(new_contributors),
            'experienced_contributors': len(experienced_contributors),
            'new_percentage': len(new_contributors) / len(contributor_stats) * 100 if len(contributor_stats) > 0 else 0,
            'new_contributors_avg_commits': new_contributors['total_commits'].mean() if not new_contributors.empty else 0,
            'experienced_contributors_avg_commits': experienced_contributors['total_commits'].mean() if not experienced_contributors.empty else 0,
            'new_contributors_list': new_contributors['author'].tolist(),
            'top_experienced_contributors': experienced_contributors.head(10)['author'].tolist()
        }
        
        logger.info(f"Classified contributors: {analysis['new_contributors']} new, {analysis['experienced_contributors']} experienced")
        return analysis
    
    def get_contributor_consistency(self) -> pd.DataFrame:
        """
        Analyze contributor consistency (regularity of commits over time).
        
        Returns:
            pd.DataFrame: Consistency metrics for contributors
        """
        commits = self.git_repo.get_all_commits()
        contributor_dates = defaultdict(list)
        
        for commit in commits:
            author = commit.author.name
            commit_date = datetime.fromtimestamp(commit.committed_date)
            contributor_dates[author].append(commit_date)
        
        consistency_data = []
        
        for author, dates in contributor_dates.items():
            if len(dates) < 2:
                continue
                
            dates.sort()
            
            # Calculate gaps between commits
            gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            
            avg_gap = sum(gaps) / len(gaps) if gaps else 0
            gap_variance = sum((gap - avg_gap) ** 2 for gap in gaps) / len(gaps) if gaps else 0
            
            # Consistency score (lower variance = more consistent)
            consistency_score = 1 / (1 + gap_variance) if gap_variance > 0 else 1
            
            consistency_data.append({
                'author': author,
                'total_commits': len(dates),
                'activity_span_days': (dates[-1] - dates[0]).days,
                'avg_gap_between_commits': avg_gap,
                'gap_variance': gap_variance,
                'consistency_score': consistency_score,
                'first_commit': dates[0],
                'last_commit': dates[-1]
            })
        
        df = pd.DataFrame(consistency_data)
        df = df.sort_values('consistency_score', ascending=False)
        
        logger.info(f"Analyzed consistency for {len(df)} contributors")
        return df
    
    def get_contributor_impact_analysis(self) -> pd.DataFrame:
        """
        Analyze contributor impact based on various metrics.
        
        Returns:
            pd.DataFrame: Impact analysis for contributors
        """
        contributor_stats = self.get_contributor_statistics()
        
        # Calculate impact scores
        contributor_stats['lines_per_commit'] = (contributor_stats['total_insertions'] + contributor_stats['total_deletions']) / contributor_stats['total_commits']
        contributor_stats['files_per_commit'] = contributor_stats['files_touched'] / contributor_stats['total_commits']
        
        # Normalize metrics for impact score (0-100)
        def normalize_column(col):
            return ((col - col.min()) / (col.max() - col.min()) * 100).fillna(0)
        
        contributor_stats['commit_score'] = normalize_column(contributor_stats['total_commits'])
        contributor_stats['lines_score'] = normalize_column(contributor_stats['total_insertions'] + contributor_stats['total_deletions'])
        contributor_stats['files_score'] = normalize_column(contributor_stats['files_touched'])
        contributor_stats['consistency_score'] = normalize_column(contributor_stats['avg_commits_per_day'])
        
        # Overall impact score (weighted average)
        contributor_stats['impact_score'] = (
            contributor_stats['commit_score'] * 0.3 +
            contributor_stats['lines_score'] * 0.25 +
            contributor_stats['files_score'] * 0.25 +
            contributor_stats['consistency_score'] * 0.2
        )
        
        # Select relevant columns and sort by impact
        impact_df = contributor_stats[[
            'author', 'total_commits', 'total_insertions', 'total_deletions',
            'files_touched', 'lines_per_commit', 'files_per_commit',
            'activity_span_days', 'impact_score'
        ]].sort_values('impact_score', ascending=False)
        
        logger.info(f"Calculated impact scores for {len(impact_df)} contributors")
        return impact_df
