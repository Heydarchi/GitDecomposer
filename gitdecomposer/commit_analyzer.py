"""
CommitAnalyzer module for analyzing Git commits.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
from git.objects import Commit
import logging
import re

from .git_repository import GitRepository
from .models.commit import (
    CommitInfo, CommitStats, CommitFrequency, CommitVelocity, 
    CommitPattern, CommitQuality, CommitType
)

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
    
    def get_commit_activity_by_date(self) -> pd.DataFrame:
        """
        Get commit activity grouped by date.
        
        Returns:
            pd.DataFrame: DataFrame with dates and commit counts
        """
        # This method is an alias for get_commit_frequency_by_date for compatibility
        return self.get_commit_frequency_by_date()
    
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

    def get_commit_velocity_analysis(self, weeks_back: int = 12) -> Dict[str, Any]:
        """
        Analyze commit velocity trends over time.
        
        Args:
            weeks_back (int): Number of weeks to analyze
            
        Returns:
            Dict[str, Any]: Commit velocity metrics and trends
        """
        try:
            commits = self._get_commits()
            if not commits:
                return {
                    'weekly_velocity': pd.DataFrame(),
                    'avg_commits_per_week': 0,
                    'velocity_trend': 'stable',
                    'current_week_velocity': 0,
                    'velocity_change_percentage': 0
                }
            
            # Get commits from the last specified weeks
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks_back)
            
            # Filter commits by date range
            recent_commits = [
                commit for commit in commits
                if start_date <= datetime.fromtimestamp(commit.committed_date) <= end_date
            ]
            
            # Group commits by week
            weekly_data = []
            for commit in recent_commits:
                commit_date = datetime.fromtimestamp(commit.committed_date)
                week_start = commit_date - timedelta(days=commit_date.weekday())
                weekly_data.append({
                    'week_start': week_start.date(),
                    'commit_count': 1
                })
            
            if not weekly_data:
                return {
                    'weekly_velocity': pd.DataFrame(),
                    'avg_commits_per_week': 0,
                    'velocity_trend': 'stable',
                    'current_week_velocity': 0,
                    'velocity_change_percentage': 0
                }
            
            df = pd.DataFrame(weekly_data)
            weekly_velocity = df.groupby('week_start')['commit_count'].sum().reset_index()
            weekly_velocity['week_start'] = pd.to_datetime(weekly_velocity['week_start'])
            weekly_velocity = weekly_velocity.sort_values('week_start')
            
            # Calculate metrics
            avg_commits_per_week = weekly_velocity['commit_count'].mean()
            current_week_velocity = weekly_velocity['commit_count'].iloc[-1] if len(weekly_velocity) > 0 else 0
            
            # Calculate trend
            if len(weekly_velocity) >= 4:
                recent_avg = weekly_velocity['commit_count'].tail(4).mean()
                older_avg = weekly_velocity['commit_count'].head(4).mean()
                velocity_change_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
                
                if velocity_change_percentage > 10:
                    trend = 'increasing'
                elif velocity_change_percentage < -10:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                velocity_change_percentage = 0
                trend = 'stable'
            
            logger.info(f"Analyzed commit velocity for {weeks_back} weeks")
            return {
                'weekly_velocity': weekly_velocity,
                'avg_commits_per_week': avg_commits_per_week,
                'velocity_trend': trend,
                'current_week_velocity': current_week_velocity,
                'velocity_change_percentage': velocity_change_percentage
            }
            
        except Exception as e:
            logger.error(f"Error analyzing commit velocity: {e}")
            return {
                'weekly_velocity': pd.DataFrame(),
                'avg_commits_per_week': 0,
                'velocity_trend': 'unknown',
                'current_week_velocity': 0,
                'velocity_change_percentage': 0
            }

    def get_bug_fix_ratio_analysis(self) -> Dict[str, Any]:
        """
        Analyze the ratio of bug fix commits to total commits.
        
        Returns:
            Dict[str, Any]: Bug fix ratio metrics and patterns
        """
        try:
            commits = self._get_commits()
            if not commits:
                return {
                    'total_commits': 0,
                    'bug_fix_commits': 0,
                    'bug_fix_ratio': 0,
                    'bug_fix_trend': pd.DataFrame(),
                    'common_bug_keywords': []
                }
            
            # Keywords that typically indicate bug fixes
            bug_keywords = [
                'fix', 'bug', 'issue', 'error', 'problem', 'resolve', 'solve',
                'patch', 'hotfix', 'bugfix', 'correction', 'repair'
            ]
            
            bug_fix_commits = []
            monthly_bug_fixes = defaultdict(int)
            monthly_total = defaultdict(int)
            
            for commit in commits:
                commit_date = datetime.fromtimestamp(commit.committed_date)
                month_key = commit_date.strftime('%Y-%m')
                monthly_total[month_key] += 1
                
                # Check if commit message contains bug-related keywords
                message_lower = commit.message.lower()
                is_bug_fix = any(keyword in message_lower for keyword in bug_keywords)
                
                if is_bug_fix:
                    bug_fix_commits.append({
                        'sha': commit.hexsha,
                        'message': commit.message.strip(),
                        'date': commit_date,
                        'author': commit.author.name
                    })
                    monthly_bug_fixes[month_key] += 1
            
            # Calculate overall metrics
            total_commits = len(commits)
            bug_fix_count = len(bug_fix_commits)
            bug_fix_ratio = (bug_fix_count / total_commits * 100) if total_commits > 0 else 0
            
            # Create trend DataFrame
            trend_data = []
            for month in sorted(monthly_total.keys()):
                bug_fixes = monthly_bug_fixes.get(month, 0)
                total = monthly_total[month]
                ratio = (bug_fixes / total * 100) if total > 0 else 0
                trend_data.append({
                    'month': month,
                    'bug_fix_commits': bug_fixes,
                    'total_commits': total,
                    'bug_fix_ratio': ratio
                })
            
            bug_fix_trend = pd.DataFrame(trend_data)
            if not bug_fix_trend.empty:
                bug_fix_trend['month'] = pd.to_datetime(bug_fix_trend['month'])
            
            # Find most common bug-related keywords
            all_messages = ' '.join([commit['message'].lower() for commit in bug_fix_commits])
            word_counts = Counter(all_messages.split())
            common_bug_keywords = [
                word for word, count in word_counts.most_common(10)
                if word in bug_keywords and len(word) > 2
            ]
            
            logger.info(f"Analyzed bug fix ratio: {bug_fix_ratio:.1f}%")
            return {
                'total_commits': total_commits,
                'bug_fix_commits': bug_fix_count,
                'bug_fix_ratio': bug_fix_ratio,
                'bug_fix_trend': bug_fix_trend,
                'common_bug_keywords': common_bug_keywords,
                'recent_bug_fixes': bug_fix_commits[-10:] if bug_fix_commits else []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing bug fix ratio: {e}")
            return {
                'total_commits': 0,
                'bug_fix_commits': 0,
                'bug_fix_ratio': 0,
                'bug_fix_trend': pd.DataFrame(),
                'common_bug_keywords': []
            }
    
    def _classify_commit_type(self, message: str) -> CommitType:
        """Classify commit type based on message patterns."""
        message_lower = message.lower().strip()
        
        # Conventional commit patterns
        if message_lower.startswith('feat'):
            return CommitType.FEATURE
        elif message_lower.startswith('fix'):
            return CommitType.FIX
        elif message_lower.startswith('docs'):
            return CommitType.DOCS
        elif message_lower.startswith('style'):
            return CommitType.STYLE
        elif message_lower.startswith('refactor'):
            return CommitType.REFACTOR
        elif message_lower.startswith('test'):
            return CommitType.TEST
        elif message_lower.startswith('chore'):
            return CommitType.CHORE
        elif 'merge' in message_lower and ('pull request' in message_lower or 'branch' in message_lower):
            return CommitType.MERGE
        elif message_lower.startswith('initial'):
            return CommitType.INITIAL
        else:
            return CommitType.OTHER
    
    def _extract_commit_info(self, commit: Commit) -> CommitInfo:
        """Extract structured commit information."""
        try:
            # Get file changes
            files_changed = []
            insertions = 0
            deletions = 0
            
            try:
                if commit.parents:
                    # Get diff stats
                    for item in commit.diff(commit.parents[0]):
                        if item.a_path:
                            files_changed.append(item.a_path)
                        elif item.b_path:
                            files_changed.append(item.b_path)
                    
                    # Get stats (this might not work for all Git versions)
                    try:
                        stats = commit.stats.total
                        insertions = stats.get('insertions', 0)
                        deletions = stats.get('deletions', 0)
                    except AttributeError:
                        pass
            except Exception:
                pass
            
            return CommitInfo(
                sha=commit.hexsha,
                message=commit.message.strip(),
                author_name=commit.author.name,
                author_email=commit.author.email,
                committer_name=commit.committer.name,
                committer_email=commit.committer.email,
                authored_date=datetime.fromtimestamp(commit.authored_date),
                committed_date=datetime.fromtimestamp(commit.committed_date),
                parent_shas=[parent.hexsha for parent in commit.parents],
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions,
                is_merge=len(commit.parents) > 1,
                commit_type=self._classify_commit_type(commit.message)
            )
        except Exception as e:
            logger.warning(f"Error extracting commit info for {commit.hexsha}: {e}")
            return CommitInfo(
                sha=commit.hexsha,
                message=commit.message.strip() if commit.message else "",
                author_name=commit.author.name if commit.author else "Unknown",
                author_email=commit.author.email if commit.author else "unknown@unknown.com",
                committer_name=commit.committer.name if commit.committer else "Unknown",
                committer_email=commit.committer.email if commit.committer else "unknown@unknown.com",
                authored_date=datetime.fromtimestamp(commit.authored_date) if commit.authored_date else datetime.now(),
                committed_date=datetime.fromtimestamp(commit.committed_date) if commit.committed_date else datetime.now(),
                commit_type=CommitType.OTHER
            )
    
    def get_commit_stats(self) -> CommitStats:
        """Get comprehensive commit statistics."""
        commits = self._get_commits()
        commit_infos = [self._extract_commit_info(commit) for commit in commits]
        
        if not commit_infos:
            return CommitStats(
                total_commits=0,
                total_insertions=0,
                total_deletions=0,
                total_files_changed=0,
                merge_commits=0,
                unique_authors=0,
                unique_committers=0
            )
        
        total_insertions = sum(c.insertions for c in commit_infos)
        total_deletions = sum(c.deletions for c in commit_infos)
        total_files_changed = len(set(f for c in commit_infos for f in c.files_changed))
        merge_commits = sum(1 for c in commit_infos if c.is_merge)
        
        authors = set((c.author_name, c.author_email) for c in commit_infos)
        committers = set((c.committer_name, c.committer_email) for c in commit_infos)
        
        dates = [c.committed_date for c in commit_infos if c.committed_date]
        first_commit_date = min(dates) if dates else None
        last_commit_date = max(dates) if dates else None
        
        avg_commit_size = (total_insertions + total_deletions) / len(commit_infos) if commit_infos else 0
        avg_files_per_commit = total_files_changed / len(commit_infos) if commit_infos else 0
        
        commit_types = Counter(c.commit_type for c in commit_infos)
        
        return CommitStats(
            total_commits=len(commit_infos),
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            total_files_changed=total_files_changed,
            merge_commits=merge_commits,
            unique_authors=len(authors),
            unique_committers=len(committers),
            first_commit_date=first_commit_date,
            last_commit_date=last_commit_date,
            avg_commit_size=avg_commit_size,
            avg_files_per_commit=avg_files_per_commit,
            commit_types=dict(commit_types)
        )
    
    def get_commit_frequency_analysis(self) -> CommitFrequency:
        """Get commit frequency analysis."""
        commits = self._get_commits()
        commit_infos = [self._extract_commit_info(commit) for commit in commits]
        
        daily_frequencies = defaultdict(int)
        hourly_frequencies = defaultdict(int)
        weekday_frequencies = defaultdict(int)
        monthly_frequencies = defaultdict(int)
        
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for commit_info in commit_infos:
            if not commit_info.committed_date:
                continue
                
            date = commit_info.committed_date
            daily_frequencies[date.strftime('%Y-%m-%d')] += 1
            hourly_frequencies[date.hour] += 1
            weekday_frequencies[weekdays[date.weekday()]] += 1
            monthly_frequencies[date.strftime('%Y-%m')] += 1
        
        return CommitFrequency(
            daily_frequencies=dict(daily_frequencies),
            hourly_frequencies=dict(hourly_frequencies),
            weekday_frequencies=dict(weekday_frequencies),
            monthly_frequencies=dict(monthly_frequencies)
        )
    
    def get_commit_quality_analysis(self) -> CommitQuality:
        """Get commit quality analysis."""
        commits = self._get_commits()
        commit_infos = [self._extract_commit_info(commit) for commit in commits]
        
        if not commit_infos:
            return CommitQuality(
                avg_message_length=0,
                messages_with_body=0,
                total_messages=0,
                conventional_commits=0,
                descriptive_messages=0,
                typos_detected=0,
                empty_messages=0
            )
        
        message_lengths = []
        messages_with_body = 0
        conventional_commits = 0
        descriptive_messages = 0
        empty_messages = 0
        
        # Common typos to check for
        typo_patterns = [
            r'\bthe\s+the\b', r'\bfrom\s+form\b', r'\bteh\b', r'\bwidht\b',
            r'\bheigth\b', r'\blenght\b', r'\bseperate\b'
        ]
        typos_detected = 0
        
        for commit_info in commit_infos:
            message = commit_info.message
            
            if not message.strip():
                empty_messages += 1
                continue
            
            message_lengths.append(len(message))
            
            # Check for body (multiple lines)
            if '\n' in message.strip():
                messages_with_body += 1
            
            # Check for conventional commits
            if commit_info.commit_type != CommitType.OTHER:
                conventional_commits += 1
            
            # Check for descriptive messages (heuristic: > 10 chars, contains verb)
            first_line = message.split('\n')[0].strip()
            if len(first_line) > 10 and any(word in first_line.lower() for word in 
                                          ['add', 'fix', 'update', 'remove', 'create', 'implement', 'refactor']):
                descriptive_messages += 1
            
            # Check for typos
            for pattern in typo_patterns:
                if re.search(pattern, message.lower()):
                    typos_detected += 1
                    break
        
        avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        
        return CommitQuality(
            avg_message_length=avg_message_length,
            messages_with_body=messages_with_body,
            total_messages=len(commit_infos),
            conventional_commits=conventional_commits,
            descriptive_messages=descriptive_messages,
            typos_detected=typos_detected,
            empty_messages=empty_messages
        )
