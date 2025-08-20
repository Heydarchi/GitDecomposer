"""
ContributorAnalyzer module for analyzing contributor patterns and statistics.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
import logging

from .git_repository import GitRepository
from .models.contributor import (
    ContributorInfo, ContributorStats, ContributorActivity, 
    ContributorCollaboration, ContributorExpertise, TeamDynamics,
    ContributorRole, ActivityLevel
)

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
    
    def _determine_contributor_role(self, commits: int, activity_span: int, files_touched: int) -> ContributorRole:
        """Determine contributor role based on activity patterns."""
        if commits >= 100 and activity_span >= 180:
            return ContributorRole.CORE_MAINTAINER
        elif commits >= 20 and activity_span >= 90:
            return ContributorRole.REGULAR_CONTRIBUTOR
        elif commits >= 5:
            return ContributorRole.OCCASIONAL_CONTRIBUTOR
        else:
            return ContributorRole.ONE_TIME_CONTRIBUTOR
    
    def _extract_contributor_info(self, author_data: Dict[str, Any]) -> ContributorInfo:
        """Extract structured contributor information."""
        name = author_data.get('name', 'Unknown')
        email = author_data.get('email', 'unknown@unknown.com')
        
        # Parse dates safely
        first_commit_date = None
        last_commit_date = None
        
        if 'first_commit' in author_data and author_data['first_commit']:
            try:
                if isinstance(author_data['first_commit'], datetime):
                    first_commit_date = author_data['first_commit']
                else:
                    first_commit_date = datetime.fromtimestamp(author_data['first_commit'])
            except (ValueError, TypeError):
                pass
        
        if 'last_commit' in author_data and author_data['last_commit']:
            try:
                if isinstance(author_data['last_commit'], datetime):
                    last_commit_date = author_data['last_commit']
                else:
                    last_commit_date = datetime.fromtimestamp(author_data['last_commit'])
            except (ValueError, TypeError):
                pass
        
        total_commits = author_data.get('commits', 0)
        total_insertions = author_data.get('total_insertions', 0)
        total_deletions = author_data.get('total_deletions', 0)
        files_touched = set(author_data.get('files_modified', []))
        
        # Calculate activity span
        activity_span = 0
        if first_commit_date and last_commit_date:
            activity_span = (last_commit_date - first_commit_date).days
        
        role = self._determine_contributor_role(total_commits, activity_span, len(files_touched))
        
        return ContributorInfo(
            name=name,
            email=email,
            first_commit_date=first_commit_date,
            last_commit_date=last_commit_date,
            total_commits=total_commits,
            total_insertions=total_insertions,
            total_deletions=total_deletions,
            files_touched=files_touched,
            role=role
        )
    
    def get_contributor_stats_analysis(self) -> ContributorStats:
        """Get comprehensive contributor statistics."""
        try:
            contributor_df = self.get_contributor_statistics()
            
            if contributor_df.empty:
                return ContributorStats(
                    total_contributors=0,
                    active_contributors=0,
                    core_contributors=0,
                    new_contributors=0,
                    retention_rate=0.0,
                    avg_commits_per_contributor=0.0,
                    avg_contribution_span_days=0.0,
                    top_contributor_commits=0,
                    contributor_diversity_index=0.0
                )
            
            total_contributors = len(contributor_df)
            
            # Active contributors (activity in last 90 days)
            now = datetime.now()
            cutoff_date = now - timedelta(days=90)
            active_contributors = len(contributor_df[contributor_df['last_commit'] >= cutoff_date])
            
            # Core contributors (top 20% by commits or contributors with >50 commits)
            total_commits = contributor_df['total_commits'].sum()
            contributor_df_sorted = contributor_df.sort_values('total_commits', ascending=False)
            
            # Calculate cumulative commits percentage
            contributor_df_sorted['cumulative_commits'] = contributor_df_sorted['total_commits'].cumsum()
            contributor_df_sorted['cumulative_percentage'] = (contributor_df_sorted['cumulative_commits'] / total_commits) * 100
            
            # Core contributors are those who account for 80% of commits
            core_contributors = len(contributor_df_sorted[contributor_df_sorted['cumulative_percentage'] <= 80])
            if core_contributors == 0:  # Fallback
                core_contributors = max(1, int(total_contributors * 0.2))
            
            # New contributors (first commit in last 90 days)
            new_contributors = len(contributor_df[contributor_df['first_commit'] >= cutoff_date])
            
            # Retention rate (contributors active in both last 90 days and 90-180 days ago)
            old_cutoff = now - timedelta(days=180)
            old_active = contributor_df[
                (contributor_df['first_commit'] <= cutoff_date) & 
                (contributor_df['last_commit'] >= old_cutoff)
            ]
            retention_rate = len(old_active) / max(1, len(contributor_df[contributor_df['first_commit'] <= cutoff_date]))
            
            # Calculate diversity index (normalized entropy)
            commit_counts = contributor_df['total_commits'].values
            commit_proportions = commit_counts / commit_counts.sum()
            diversity_index = -sum(p * (p.bit_length() / 8) for p in commit_proportions if p > 0)  # Simplified Shannon entropy
            max_diversity = (total_contributors.bit_length() / 8) if total_contributors > 1 else 1
            normalized_diversity = diversity_index / max_diversity if max_diversity > 0 else 0
            
            return ContributorStats(
                total_contributors=total_contributors,
                active_contributors=active_contributors,
                core_contributors=core_contributors,
                new_contributors=new_contributors,
                retention_rate=retention_rate,
                avg_commits_per_contributor=contributor_df['total_commits'].mean(),
                avg_contribution_span_days=contributor_df['activity_span_days'].mean(),
                top_contributor_commits=contributor_df['total_commits'].max(),
                contributor_diversity_index=min(1.0, max(0.0, normalized_diversity))
            )
            
        except Exception as e:
            logger.error(f"Error analyzing contributor stats: {e}")
            return ContributorStats(
                total_contributors=0,
                active_contributors=0,
                core_contributors=0,
                new_contributors=0,
                retention_rate=0.0,
                avg_commits_per_contributor=0.0,
                avg_contribution_span_days=0.0,
                top_contributor_commits=0,
                contributor_diversity_index=0.0
            )
    
    def get_contributor_activity_analysis(self) -> ContributorActivity:
        """Get contributor activity patterns."""
        try:
            commits = self.git_repo.get_all_commits()
            
            commits_by_month = defaultdict(int)
            commits_by_weekday = defaultdict(int)
            commits_by_hour = defaultdict(int)
            
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for commit in commits:
                try:
                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    
                    month_key = commit_date.strftime('%Y-%m')
                    commits_by_month[month_key] += 1
                    
                    weekday_name = weekdays[commit_date.weekday()]
                    commits_by_weekday[weekday_name] += 1
                    
                    commits_by_hour[commit_date.hour] += 1
                    
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error processing commit date: {e}")
                    continue
            
            return ContributorActivity(
                commits_by_month=dict(commits_by_month),
                commits_by_weekday=dict(commits_by_weekday),
                commits_by_hour=dict(commits_by_hour)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing contributor activity: {e}")
            return ContributorActivity()
    
    def get_team_dynamics_analysis(self) -> TeamDynamics:
        """Get team dynamics analysis."""
        try:
            contributor_df = self.get_contributor_statistics()
            
            if contributor_df.empty:
                return TeamDynamics()
            
            # Build contributor network (simplified - contributors who worked on same files)
            contributor_network = defaultdict(set)
            
            # Calculate influence scores based on commits and files touched
            influence_scores = {}
            for _, row in contributor_df.iterrows():
                author = row['author']
                score = (row['total_commits'] * 0.6) + (row['files_touched'] * 0.4)
                influence_scores[author] = score
            
            # Normalize influence scores
            max_influence = max(influence_scores.values()) if influence_scores else 1
            influence_scores = {k: v / max_influence for k, v in influence_scores.items()}
            
            # Identify bottleneck contributors (those with very high influence)
            bottleneck_contributors = [
                contributor for contributor, score in influence_scores.items()
                if score > 0.8
            ]
            
            # Calculate team cohesion (simplified metric)
            total_contributors = len(contributor_df)
            active_contributors = len(contributor_df[contributor_df['total_commits'] >= 5])
            team_cohesion = active_contributors / total_contributors if total_contributors > 0 else 0
            
            # Leadership distribution
            leadership_distribution = {}
            sorted_contributors = sorted(influence_scores.items(), key=lambda x: x[1], reverse=True)
            for i, (contributor, score) in enumerate(sorted_contributors[:5]):  # Top 5 leaders
                leadership_distribution[contributor] = score
            
            return TeamDynamics(
                contributor_network=dict(contributor_network),
                influence_scores=influence_scores,
                bottleneck_contributors=bottleneck_contributors,
                team_cohesion_score=team_cohesion,
                leadership_distribution=leadership_distribution
            )
            
        except Exception as e:
            logger.error(f"Error analyzing team dynamics: {e}")
            return TeamDynamics()
