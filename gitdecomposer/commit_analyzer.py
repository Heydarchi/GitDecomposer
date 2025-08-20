"""
CommitAnalyzer module for analyzing Git commits.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
from git.objects import Commit
import logging

from .git_repository import GitRepository

logger = logging.getLogger(__name__)


class CommitAnalyzer:
    """
    Analyzer for Git commit data and patterns.
    
    This class provides methods to analyze commit patterns, frequency,
    and other commit-related metrics.
    """
    
    def __init__(self, git_repo: GitRepository):
        """
        Initialize the CommitAnalyzer.
        
        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        self._commits_cache = None
        logger.info("Initialized CommitAnalyzer")
    
    def _get_commits(self, force_refresh: bool = False) -> List[Commit]:
        """Get cached commits or fetch them if not cached."""
        if self._commits_cache is None or force_refresh:
            self._commits_cache = self.git_repo.get_all_commits()
        return self._commits_cache
    
    def get_commit_frequency_by_date(self, 
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get commit frequency grouped by date.
        
        Args:
            start_date (datetime, optional): Start date filter
            end_date (datetime, optional): End date filter
            
        Returns:
            pd.DataFrame: DataFrame with dates and commit counts
        """
        commits = self._get_commits()
        
        commit_dates = []
        for commit in commits:
            commit_date = datetime.fromtimestamp(commit.committed_date)
            
            # Apply date filters
            if start_date and commit_date < start_date:
                continue
            if end_date and commit_date > end_date:
                continue
                
            commit_dates.append(commit_date.date())
        
        # Count commits by date
        date_counts = Counter(commit_dates)
        
        df = pd.DataFrame(list(date_counts.items()), columns=['date', 'commit_count'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        logger.info(f"Analyzed commit frequency for {len(df)} dates")
        return df
    
    def get_commit_frequency_by_hour(self) -> pd.DataFrame:
        """
        Get commit frequency grouped by hour of day.
        
        Returns:
            pd.DataFrame: DataFrame with hours and commit counts
        """
        commits = self._get_commits()
        
        commit_hours = [datetime.fromtimestamp(commit.committed_date).hour for commit in commits]
        hour_counts = Counter(commit_hours)
        
        # Ensure all hours (0-23) are represented
        all_hours = {hour: hour_counts.get(hour, 0) for hour in range(24)}
        
        df = pd.DataFrame(list(all_hours.items()), columns=['hour', 'commit_count'])
        df = df.sort_values('hour')
        
        logger.info("Analyzed commit frequency by hour")
        return df
    
    def get_commit_frequency_by_weekday(self) -> pd.DataFrame:
        """
        Get commit frequency grouped by day of week.
        
        Returns:
            pd.DataFrame: DataFrame with weekdays and commit counts
        """
        commits = self._get_commits()
        
        weekdays = [datetime.fromtimestamp(commit.committed_date).strftime('%A') for commit in commits]
        weekday_counts = Counter(weekdays)
        
        # Order weekdays properly
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ordered_counts = {day: weekday_counts.get(day, 0) for day in weekday_order}
        
        df = pd.DataFrame(list(ordered_counts.items()), columns=['weekday', 'commit_count'])
        
        logger.info("Analyzed commit frequency by weekday")
        return df
    
    def get_commit_size_distribution(self) -> pd.DataFrame:
        """
        Get distribution of commit sizes (lines added/deleted).
        
        Returns:
            pd.DataFrame: DataFrame with commit info and size metrics
        """
        commits = self._get_commits()
        commit_data = []
        
        for commit in commits:
            try:
                stats = commit.stats
                total_lines = stats.total['lines']
                insertions = stats.total['insertions']
                deletions = stats.total['deletions']
                files_changed = stats.total['files']
                
                commit_data.append({
                    'sha': commit.hexsha[:8],
                    'author': commit.author.name,
                    'date': datetime.fromtimestamp(commit.committed_date),
                    'message': commit.message.strip().split('\n')[0][:100],  # First line, max 100 chars
                    'total_lines': total_lines,
                    'insertions': insertions,
                    'deletions': deletions,
                    'files_changed': files_changed
                })
            except Exception as e:
                logger.warning(f"Error processing commit {commit.hexsha}: {e}")
                continue
        
        df = pd.DataFrame(commit_data)
        logger.info(f"Analyzed size distribution for {len(df)} commits")
        return df
    
    def get_commit_messages_analysis(self) -> Dict[str, Any]:
        """
        Analyze commit messages for patterns and statistics.
        
        Returns:
            Dict[str, Any]: Analysis results including common words, message lengths, etc.
        """
        commits = self._get_commits()
        
        messages = [commit.message.strip() for commit in commits]
        message_lengths = [len(msg) for msg in messages]
        
        # Extract first lines (commit summaries)
        summaries = [msg.split('\n')[0] for msg in messages]
        summary_lengths = [len(summary) for summary in summaries]
        
        # Find common words in commit messages (simple analysis)
        all_words = []
        for msg in summaries:
            words = msg.lower().split()
            # Filter out common but not meaningful words
            filtered_words = [word for word in words if len(word) > 2 and word.isalpha()]
            all_words.extend(filtered_words)
        
        common_words = Counter(all_words).most_common(20)
        
        # Categorize commits by common prefixes
        prefixes = defaultdict(int)
        for summary in summaries:
            if ':' in summary:
                prefix = summary.split(':')[0].lower().strip()
                prefixes[prefix] += 1
        
        analysis = {
            'total_commits': len(commits),
            'avg_message_length': sum(message_lengths) / len(message_lengths) if message_lengths else 0,
            'avg_summary_length': sum(summary_lengths) / len(summary_lengths) if summary_lengths else 0,
            'common_words': common_words,
            'common_prefixes': dict(prefixes),
            'empty_messages': sum(1 for msg in messages if not msg.strip())
        }
        
        logger.info("Completed commit message analysis")
        return analysis
    
    def get_merge_commit_analysis(self) -> Dict[str, Any]:
        """
        Analyze merge commits in the repository.
        
        Returns:
            Dict[str, Any]: Merge commit statistics
        """
        commits = self._get_commits()
        
        merge_commits = [commit for commit in commits if len(commit.parents) > 1]
        regular_commits = [commit for commit in commits if len(commit.parents) <= 1]
        
        merge_authors = Counter([commit.author.name for commit in merge_commits])
        
        analysis = {
            'total_commits': len(commits),
            'merge_commits': len(merge_commits),
            'regular_commits': len(regular_commits),
            'merge_percentage': (len(merge_commits) / len(commits) * 100) if commits else 0,
            'top_merge_authors': merge_authors.most_common(10)
        }
        
        logger.info(f"Analyzed {len(merge_commits)} merge commits")
        return analysis
    
    def get_commit_timeline(self, group_by: str = 'month') -> pd.DataFrame:
        """
        Get commit timeline grouped by specified time period.
        
        Args:
            group_by (str): Time period to group by ('day', 'week', 'month', 'year')
            
        Returns:
            pd.DataFrame: Timeline data
        """
        commits = self._get_commits()
        
        commit_dates = [datetime.fromtimestamp(commit.committed_date) for commit in commits]
        df = pd.DataFrame({'date': commit_dates})
        
        if group_by == 'day':
            df['period'] = df['date'].dt.date
        elif group_by == 'week':
            df['period'] = df['date'].dt.to_period('W').dt.start_time
        elif group_by == 'month':
            df['period'] = df['date'].dt.to_period('M').dt.start_time
        elif group_by == 'year':
            df['period'] = df['date'].dt.to_period('Y').dt.start_time
        else:
            raise ValueError("group_by must be one of: 'day', 'week', 'month', 'year'")
        
        timeline = df.groupby('period').size().reset_index(name='commit_count')
        timeline = timeline.sort_values('period')
        
        logger.info(f"Created commit timeline grouped by {group_by}")
        return timeline
    
    def get_commit_authors_over_time(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get commit activity by top authors over time.
        
        Args:
            top_n (int): Number of top authors to include
            
        Returns:
            pd.DataFrame: Author activity over time
        """
        commits = self._get_commits()
        
        # Get top authors
        author_counts = Counter([commit.author.name for commit in commits])
        top_authors = [author for author, _ in author_counts.most_common(top_n)]
        
        # Build timeline for top authors
        data = []
        for commit in commits:
            if commit.author.name in top_authors:
                data.append({
                    'date': datetime.fromtimestamp(commit.committed_date).date(),
                    'author': commit.author.name
                })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            # Group by month and author
            timeline = df.groupby([df['date'].dt.to_period('M'), 'author']).size().reset_index(name='commit_count')
            timeline['date'] = timeline['date'].dt.start_time
        else:
            timeline = pd.DataFrame(columns=['date', 'author', 'commit_count'])
        
        logger.info(f"Created timeline for top {top_n} authors")
        return timeline
