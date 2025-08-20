"""
BranchAnalyzer module for analyzing Git branches and branching patterns.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
import logging

from .git_repository import GitRepository

logger = logging.getLogger(__name__)


class BranchAnalyzer:
    """
    Analyzer for Git branch-related metrics and patterns.
    
    This class provides methods to analyze branch activity, merge patterns,
    and branching strategies.
    """
    
    def __init__(self, git_repo: GitRepository):
        """
        Initialize the BranchAnalyzer.
        
        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        logger.info("Initialized BranchAnalyzer")
    
    def get_branch_statistics(self) -> pd.DataFrame:
        """
        Get comprehensive statistics for all branches.
        
        Returns:
            pd.DataFrame: Branch statistics including commits, contributors, etc.
        """
        branches = self.git_repo.get_branches()
        branch_stats = []
        
        for branch_name in branches:
            try:
                # Get commits for this branch
                commits = self.git_repo.get_all_commits(branch=branch_name)
                
                if not commits:
                    continue
                
                # Analyze commits
                authors = set()
                commit_dates = []
                total_insertions = 0
                total_deletions = 0
                
                for commit in commits:
                    authors.add(commit.author.name)
                    commit_dates.append(datetime.fromtimestamp(commit.committed_date))
                    
                    try:
                        stats = commit.stats
                        total_insertions += stats.total['insertions']
                        total_deletions += stats.total['deletions']
                    except:
                        pass
                
                # Calculate metrics
                first_commit = min(commit_dates) if commit_dates else None
                last_commit = max(commit_dates) if commit_dates else None
                activity_span = (last_commit - first_commit).days if first_commit and last_commit else 0
                
                branch_stats.append({
                    'branch_name': branch_name,
                    'total_commits': len(commits),
                    'unique_contributors': len(authors),
                    'total_insertions': total_insertions,
                    'total_deletions': total_deletions,
                    'net_lines': total_insertions - total_deletions,
                    'first_commit_date': first_commit,
                    'last_commit_date': last_commit,
                    'activity_span_days': activity_span,
                    'avg_commits_per_day': len(commits) / max(activity_span, 1) if activity_span > 0 else len(commits)
                })
                
            except Exception as e:
                logger.warning(f"Error analyzing branch {branch_name}: {e}")
                continue
        
        df = pd.DataFrame(branch_stats)
        if not df.empty:
            df = df.sort_values('total_commits', ascending=False)
        
        logger.info(f"Analyzed statistics for {len(df)} branches")
        return df
    
    def get_branch_divergence_analysis(self) -> Dict[str, Any]:
        """
        Analyze how branches diverge from the main branch.
        
        Returns:
            Dict[str, Any]: Divergence analysis
        """
        try:
            # Try to identify main branch
            main_branch = None
            branches = self.git_repo.get_branches()
            
            for possible_main in ['main', 'master', 'develop']:
                if possible_main in branches:
                    main_branch = possible_main
                    break
            
            if not main_branch:
                main_branch = branches[0] if branches else None
            
            if not main_branch:
                return {'error': 'No branches found'}
            
            main_commits = set(commit.hexsha for commit in self.git_repo.get_all_commits(branch=main_branch))
            
            divergence_data = []
            
            for branch_name in branches:
                if branch_name == main_branch:
                    continue
                
                try:
                    branch_commits = self.git_repo.get_all_commits(branch=branch_name)
                    branch_commit_shas = set(commit.hexsha for commit in branch_commits)
                    
                    # Calculate divergence metrics
                    unique_to_branch = branch_commit_shas - main_commits
                    shared_commits = branch_commit_shas & main_commits
                    
                    divergence_data.append({
                        'branch_name': branch_name,
                        'total_commits': len(branch_commits),
                        'shared_with_main': len(shared_commits),
                        'unique_commits': len(unique_to_branch),
                        'divergence_percentage': (len(unique_to_branch) / len(branch_commits) * 100) if branch_commits else 0
                    })
                    
                except Exception as e:
                    logger.warning(f"Error analyzing divergence for branch {branch_name}: {e}")
                    continue
            
            analysis = {
                'main_branch': main_branch,
                'main_branch_commits': len(main_commits),
                'divergence_data': divergence_data,
                'most_divergent_branch': max(divergence_data, key=lambda x: x['divergence_percentage'])['branch_name'] if divergence_data else None
            }
            
            logger.info(f"Analyzed divergence for {len(divergence_data)} branches from {main_branch}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in branch divergence analysis: {e}")
            return {'error': str(e)}
    
    def get_merge_pattern_analysis(self) -> Dict[str, Any]:
        """
        Analyze merge patterns in the repository.
        
        Returns:
            Dict[str, Any]: Merge pattern analysis
        """
        commits = self.git_repo.get_all_commits()
        
        merge_commits = []
        regular_commits = []
        
        for commit in commits:
            if len(commit.parents) > 1:  # Merge commit
                merge_commits.append(commit)
            else:
                regular_commits.append(commit)
        
        # Analyze merge commit patterns
        merge_authors = Counter([commit.author.name for commit in merge_commits])
        merge_times = [datetime.fromtimestamp(commit.committed_date) for commit in merge_commits]
        
        # Analyze merge frequency over time
        merge_by_month = defaultdict(int)
        for merge_time in merge_times:
            month_key = merge_time.strftime('%Y-%m')
            merge_by_month[month_key] += 1
        
        # Calculate average time between merges
        if len(merge_times) > 1:
            merge_times.sort()
            time_diffs = [(merge_times[i+1] - merge_times[i]).days for i in range(len(merge_times)-1)]
            avg_days_between_merges = sum(time_diffs) / len(time_diffs)
        else:
            avg_days_between_merges = 0
        
        analysis = {
            'total_commits': len(commits),
            'merge_commits': len(merge_commits),
            'regular_commits': len(regular_commits),
            'merge_percentage': (len(merge_commits) / len(commits) * 100) if commits else 0,
            'top_merge_authors': merge_authors.most_common(10),
            'avg_days_between_merges': avg_days_between_merges,
            'merge_frequency_by_month': dict(merge_by_month),
            'first_merge': min(merge_times) if merge_times else None,
            'last_merge': max(merge_times) if merge_times else None
        }
        
        logger.info(f"Analyzed {len(merge_commits)} merge commits")
        return analysis
    
    def get_branch_lifecycle_analysis(self) -> pd.DataFrame:
        """
        Analyze the lifecycle of branches (creation, activity, potential staleness).
        
        Returns:
            pd.DataFrame: Branch lifecycle information
        """
        branch_stats = self.get_branch_statistics()
        
        if branch_stats.empty:
            return pd.DataFrame()
        
        current_date = datetime.now()
        
        # Calculate additional lifecycle metrics
        branch_stats['days_since_last_commit'] = branch_stats['last_commit_date'].apply(
            lambda x: (current_date - x).days if x else float('inf')
        )
        
        # Classify branch status
        def classify_branch_status(row):
            days_since_last = row['days_since_last_commit']
            total_commits = row['total_commits']
            
            if days_since_last <= 7:
                return 'active'
            elif days_since_last <= 30:
                return 'recent'
            elif days_since_last <= 90:
                return 'stale'
            elif total_commits == 1:
                return 'abandoned_single'
            else:
                return 'abandoned'
        
        branch_stats['status'] = branch_stats.apply(classify_branch_status, axis=1)
        
        # Add risk assessment
        def assess_merge_risk(row):
            if row['status'] in ['active', 'recent']:
                return 'low'
            elif row['unique_contributors'] == 1 and row['total_commits'] < 5:
                return 'low'
            elif row['activity_span_days'] > 30 and row['status'] == 'stale':
                return 'high'
            else:
                return 'medium'
        
        branch_stats['merge_risk'] = branch_stats.apply(assess_merge_risk, axis=1)
        
        logger.info(f"Analyzed lifecycle for {len(branch_stats)} branches")
        return branch_stats
    
    def get_branching_strategy_insights(self) -> Dict[str, Any]:
        """
        Provide insights about the branching strategy used in the repository.
        
        Returns:
            Dict[str, Any]: Branching strategy insights
        """
        branch_stats = self.get_branch_statistics()
        merge_analysis = self.get_merge_pattern_analysis()
        
        if branch_stats.empty:
            return {'error': 'No branch data available'}
        
        # Analyze branch naming patterns
        branch_names = branch_stats['branch_name'].tolist()
        naming_patterns = {
            'feature_branches': len([b for b in branch_names if 'feature' in b.lower() or 'feat' in b.lower()]),
            'bugfix_branches': len([b for b in branch_names if 'bugfix' in b.lower() or 'fix' in b.lower() or 'hotfix' in b.lower()]),
            'release_branches': len([b for b in branch_names if 'release' in b.lower() or 'rel' in b.lower()]),
            'develop_branches': len([b for b in branch_names if 'develop' in b.lower() or 'dev' in b.lower()]),
            'main_branches': len([b for b in branch_names if b.lower() in ['main', 'master', 'trunk']])
        }
        
        # Calculate branch metrics
        avg_branch_lifetime = branch_stats['activity_span_days'].mean()
        avg_commits_per_branch = branch_stats['total_commits'].mean()
        avg_contributors_per_branch = branch_stats['unique_contributors'].mean()
        
        # Determine likely branching model
        def determine_branching_model():
            if naming_patterns['main_branches'] > 0 and naming_patterns['develop_branches'] > 0:
                if naming_patterns['feature_branches'] > 2:
                    return 'Git Flow'
                else:
                    return 'Git Flow (simplified)'
            elif naming_patterns['main_branches'] > 0 and naming_patterns['feature_branches'] > 0:
                return 'GitHub Flow'
            elif len(branch_names) <= 3:
                return 'Centralized'
            else:
                return 'Custom/Mixed'
        
        branching_model = determine_branching_model()
        
        insights = {
            'total_branches': len(branch_names),
            'branching_model': branching_model,
            'naming_patterns': naming_patterns,
            'avg_branch_lifetime_days': avg_branch_lifetime,
            'avg_commits_per_branch': avg_commits_per_branch,
            'avg_contributors_per_branch': avg_contributors_per_branch,
            'merge_frequency': merge_analysis.get('merge_percentage', 0),
            'branch_diversity_score': len(set([b.split('/')[0] if '/' in b else b.split('-')[0] for b in branch_names])),
            'recommendations': self._generate_branching_recommendations(branch_stats, merge_analysis, naming_patterns)
        }
        
        logger.info(f"Generated branching strategy insights for {len(branch_names)} branches")
        return insights
    
    def _generate_branching_recommendations(self, branch_stats: pd.DataFrame, 
                                         merge_analysis: Dict[str, Any], 
                                         naming_patterns: Dict[str, int]) -> List[str]:
        """Generate recommendations based on branching analysis."""
        recommendations = []
        
        # Check for stale branches
        if not branch_stats.empty:
            if 'days_since_last_commit' in branch_stats.columns:
                stale_condition = branch_stats['days_since_last_commit'] > 90
                stale_branches = len(branch_stats[stale_condition])
                if stale_branches > 3:
                    recommendations.append(f"Consider cleaning up {stale_branches} stale branches to improve repository hygiene")
            else:
                logger.warning("Column 'days_since_last_commit' not found in branch_stats")
        
        # Check merge frequency
        merge_percentage = merge_analysis.get('merge_percentage', 0)
        if merge_percentage < 10:
            recommendations.append("Low merge frequency detected - consider using feature branches and pull requests")
        elif merge_percentage > 50:
            recommendations.append("High merge frequency - ensure proper code review processes are in place")
        
        # Check naming consistency
        total_branches = sum(naming_patterns.values())
        if total_branches > 0:
            pattern_coverage = (naming_patterns['feature_branches'] + naming_patterns['bugfix_branches']) / total_branches
            if pattern_coverage < 0.5:
                recommendations.append("Consider adopting consistent branch naming conventions (feature/, bugfix/, etc.)")
        
        # Check branch complexity
        if not branch_stats.empty:
            avg_commits = branch_stats['total_commits'].mean()
            if avg_commits > 50:
                recommendations.append("Branches have many commits on average - consider more frequent merging")
            elif avg_commits < 3:
                recommendations.append("Many short-lived branches detected - good for feature development")
        
        return recommendations
