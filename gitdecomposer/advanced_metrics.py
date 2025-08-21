"""
AdvancedMetrics module for sophisticated repository analysis.

This module provides advanced analytical capabilities for Git repositories,
including maintainability index calculation, technical debt analysis, and 
test coverage assessment. It's designed to handle edge cases like grafted
repositories and provides robust error handling.

Key Features:
- Maintainability Index: Calculates file-level maintainability scores
- Technical Debt Analysis: Detects and tracks technical debt accumulation 
- Test Coverage Analysis: Analyzes test-to-code ratios and patterns
- Robust Error Handling: Gracefully handles git operation failures
- Performance Optimized: Reduces redundant git operations
- Comprehensive Recommendations: Provides actionable insights

Example:
    ```python
    from gitdecomposer import GitRepository, AdvancedMetrics
    
    repo = GitRepository('/path/to/repo')
    metrics = AdvancedMetrics(repo)
    
    # Calculate maintainability
    maintainability = metrics.calculate_maintainability_index()
    print(f"Overall score: {maintainability['overall_maintainability_score']}")
    
    # Analyze technical debt
    debt = metrics.calculate_technical_debt_accumulation()
    print(f"Debt rate: {debt['debt_accumulation_rate']}%")
    
    # Check test coverage
    tests = metrics.calculate_test_to_code_ratio()
    print(f"Test ratio: {tests['test_to_code_ratio']}")
    ```
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd
import re
import logging
from datetime import datetime, timedelta

from .git_repository import GitRepository

logger = logging.getLogger(__name__)


class AdvancedMetrics:
    """
    Advanced metrics analyzer for sophisticated repository insights.
    
    This class provides advanced analytical capabilities including
    maintainability index, technical debt analysis, and test coverage.
    """
    
    def __init__(self, git_repo: GitRepository):
        """
        Initialize the AdvancedMetrics analyzer.
        
        Args:
            git_repo (GitRepository): GitRepository instance
        """
        self.git_repo = git_repo
        logger.info("Initialized AdvancedMetrics")
    
    def calculate_maintainability_index(self) -> Dict[str, Any]:
        """
        Calculate code maintainability index based on various metrics.
        
        Returns:
            Dict[str, Any]: Maintainability metrics and analysis
        """
        try:
            commits = self.git_repo.get_all_commits()
            if not commits:
                logger.warning("No commits found for maintainability analysis")
                return {
                    'overall_maintainability_score': 0,
                    'file_maintainability': pd.DataFrame(),
                    'maintainability_factors': {},
                    'recommendations': ["No commit data available for analysis"]
                }
            
            logger.info(f"Analyzing maintainability for {len(commits)} commits")
            
            # Collect file metrics efficiently - avoid redundant git operations
            file_metrics = defaultdict(lambda: {
                'commit_count': 0,
                'author_count': 0,
                'total_changes': 0,
                'avg_commit_size': 0,
                'last_change_days': 0,
                'complexity_score': 0,
                'authors': set()
            })
            
            all_authors = set()
            processed_commits = 0
            
            for commit in commits:
                try:
                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    days_since_commit = (datetime.now() - commit_date).days
                    all_authors.add(commit.author.name)
                    
                    # Use safer method to get changed files
                    changed_files = self._get_safe_changed_files(commit)
                    if not changed_files:
                        logger.debug(f"No changed files found for commit {commit.hexsha}")
                        continue
                    
                    # Use commit stats safely
                    changes_by_file = self._get_safe_commit_stats(commit)
                    
                    for file_path in changed_files.keys():
                        # Skip binary files and non-code files
                        if not self._is_analyzable_file(file_path):
                            continue
                            
                        metrics = file_metrics[file_path]
                        
                        # Update basic metrics
                        metrics['commit_count'] += 1
                        
                        # Get changes safely
                        changes = changes_by_file.get(file_path, 1)  # Default to 1 if unknown
                        metrics['total_changes'] += changes
                        
                        # Track unique authors for this file
                        metrics['authors'].add(commit.author.name)
                        
                        # Update last change date (most recent)
                        if metrics['last_change_days'] == 0 or days_since_commit < metrics['last_change_days']:
                            metrics['last_change_days'] = days_since_commit
                        
                        # Calculate complexity score more accurately
                        metrics['complexity_score'] += self._calculate_file_complexity_score(file_path, changes)
                    
                    processed_commits += 1
                        
                except Exception as e:
                    logger.debug(f"Skipping commit {commit.hexsha}: {e}")
                    continue
            
            logger.info(f"Successfully processed {processed_commits} commits with {len(file_metrics)} files")
            
            # Calculate maintainability scores for each file
            maintainability_data = []
            
            for file_path, metrics in file_metrics.items():
                if metrics['commit_count'] == 0:
                    continue
                
                # Calculate average commit size
                metrics['avg_commit_size'] = metrics['total_changes'] / metrics['commit_count']
                metrics['author_count'] = len(metrics['authors'])
                
                # Improved maintainability score calculation with better weights
                # Normalize factors for more accurate scoring
                normalized_complexity = min(metrics['complexity_score'] / (metrics['commit_count'] * 5), 1.0)
                normalized_frequency = min(metrics['commit_count'] / 50, 1.0)  # Adjusted threshold
                normalized_authors = min(metrics['author_count'] / 8, 1.0)  # Adjusted threshold
                normalized_size = min(metrics['avg_commit_size'] / 100, 1.0)  # Adjusted threshold
                
                # Calculate penalties with improved weights
                complexity_penalty = normalized_complexity * 30
                frequency_penalty = normalized_frequency * 25  
                author_penalty = normalized_authors * 20
                size_penalty = normalized_size * 25
                
                maintainability_score = max(0, 100 - complexity_penalty - frequency_penalty - author_penalty - size_penalty)
                
                # Improved categorization with more gradual thresholds
                if maintainability_score >= 85:
                    category = 'Excellent'
                elif maintainability_score >= 70:
                    category = 'Good'
                elif maintainability_score >= 50:
                    category = 'Fair'
                elif maintainability_score >= 30:
                    category = 'Poor'
                else:
                    category = 'Critical'
                
                maintainability_data.append({
                    'file_path': file_path,
                    'maintainability_score': maintainability_score,
                    'category': category,
                    'commit_count': metrics['commit_count'],
                    'author_count': metrics['author_count'],
                    'total_changes': metrics['total_changes'],
                    'avg_commit_size': metrics['avg_commit_size'],
                    'complexity_score': metrics['complexity_score'],
                    'last_change_days': metrics['last_change_days'],
                    'extension': Path(file_path).suffix.lower() or 'no_extension'
                })
            
            file_maintainability = pd.DataFrame(maintainability_data)
            
            # Calculate overall metrics
            if not file_maintainability.empty:
                overall_score = file_maintainability['maintainability_score'].mean()
                
                # Maintainability factors
                factors = {
                    'avg_commits_per_file': file_maintainability['commit_count'].mean(),
                    'avg_authors_per_file': file_maintainability['author_count'].mean(),
                    'avg_complexity': file_maintainability['complexity_score'].mean(),
                    'files_needing_attention': len(file_maintainability[file_maintainability['maintainability_score'] < 40]),
                    'excellent_files': len(file_maintainability[file_maintainability['maintainability_score'] >= 80])
                }
                
                # Generate recommendations
                recommendations = self._generate_maintainability_recommendations(file_maintainability, factors)
            else:
                overall_score = 0
                factors = {}
                recommendations = ["No file data available for analysis"]
            
            logger.info(f"Calculated maintainability index: {overall_score:.1f}")
            return {
                'overall_maintainability_score': overall_score,
                'file_maintainability': file_maintainability,
                'maintainability_factors': factors,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error calculating maintainability index: {e}")
            return {
                'overall_maintainability_score': 0,
                'file_maintainability': pd.DataFrame(),
                'maintainability_factors': {},
                'recommendations': []
            }
    
    def _get_safe_changed_files(self, commit) -> Dict[str, str]:
        """
        Safely get changed files for a commit, handling grafted repos and edge cases.
        
        Args:
            commit: Git commit object
            
        Returns:
            Dict[str, str]: Dictionary mapping file paths to change types
        """
        try:
            changed_files = {}
            
            # Handle the first commit or grafted commits (no accessible parents)
            if not commit.parents:
                # For first commit, all files are added
                for item in commit.tree.traverse():
                    if hasattr(item, 'path') and item.type == 'blob':
                        changed_files[item.path] = 'A'
            else:
                # Try to get changes from parent, but handle missing parents gracefully
                try:
                    parent = commit.parents[0]
                    # Verify parent exists and is accessible
                    _ = parent.tree  # This will fail if parent is inaccessible
                    diff = parent.diff(commit)
                    
                    for diff_item in diff:
                        try:
                            if diff_item.new_file:
                                changed_files[diff_item.b_path] = 'A'
                            elif diff_item.deleted_file:
                                changed_files[diff_item.a_path] = 'D'
                            elif diff_item.renamed_file:
                                changed_files[diff_item.b_path] = 'R'
                            else:
                                changed_files[diff_item.b_path] = 'M'
                        except AttributeError:
                            # Handle cases where diff_item doesn't have expected attributes
                            continue
                            
                except Exception:
                    # If we can't access parent, treat all files in this commit as changed
                    logger.debug(f"Cannot access parent for commit {commit.hexsha}, treating as initial commit")
                    for item in commit.tree.traverse():
                        if hasattr(item, 'path') and item.type == 'blob':
                            changed_files[item.path] = 'M'  # Modified (safer than Added)
            
            return changed_files
            
        except Exception as e:
            logger.debug(f"Error getting changed files for commit {commit.hexsha}: {e}")
            return {}
    
    def _get_safe_commit_stats(self, commit) -> Dict[str, int]:
        """
        Safely get commit statistics, handling cases where stats are unavailable.
        
        Args:
            commit: Git commit object
            
        Returns:
            Dict[str, int]: Dictionary mapping file paths to change counts
        """
        try:
            stats = {}
            commit_stats = commit.stats
            
            for file_path, file_stat in commit_stats.files.items():
                if isinstance(file_stat, dict):
                    insertions = file_stat.get('insertions', 0)
                    deletions = file_stat.get('deletions', 0)
                    stats[file_path] = insertions + deletions
                else:
                    # Fallback for unexpected format
                    stats[file_path] = 1
            
            return stats
            
        except Exception as e:
            logger.debug(f"Error getting commit stats for {commit.hexsha}: {e}")
            return {}
    
    def _is_analyzable_file(self, file_path: str) -> bool:
        """
        Check if a file should be included in analysis.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file should be analyzed
        """
        if not file_path:
            return False
            
        path_lower = file_path.lower()
        
        # Skip common non-code files
        skip_patterns = [
            '.git/', '__pycache__/', '.pyc', '.pyo', '.pyd',
            '.class', '.jar', '.war', '.ear', '.dll', '.exe', '.so',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.pdf', '.zip',
            '.tar', '.gz', '.rar', '.7z', 'node_modules/', '.vscode/',
            '.idea/', '.ds_store', 'thumbs.db'
        ]
        
        for pattern in skip_patterns:
            if pattern in path_lower:
                return False
        
        # Include files with code extensions or no extension (might be scripts)
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
            '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd', '.sql',
            '.html', '.css', '.scss', '.less', '.vue', '.jsx', '.tsx',
            '.xml', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
            '.md', '.rst', '.txt', '.dockerfile', 'makefile', '.r', '.m'
        }
        
        extension = Path(file_path).suffix.lower()
        filename = Path(file_path).name.lower()
        
        return (extension in code_extensions or 
                not extension and not '.' in filename or  # Scripts without extension
                filename in ['makefile', 'dockerfile', 'rakefile', 'gemfile'])
    
    
    def _calculate_file_complexity_score(self, file_path: str, changes: int) -> float:
        """
        Calculate complexity score based on file type, size, and change patterns.
        
        Args:
            file_path (str): Path to the file
            changes (int): Number of changes in this commit
            
        Returns:
            float: Complexity score for this file/commit combination
        """
        extension = Path(file_path).suffix.lower()
        filename = Path(file_path).name.lower()
        
        # Enhanced complexity mapping based on language characteristics
        complexity_map = {
            # High complexity languages (concurrent, systems programming)
            '.cpp': 4.5, '.cc': 4.5, '.cxx': 4.5, '.c': 4.0, '.h': 3.5, '.hpp': 3.5,
            '.rs': 4.0, '.go': 3.5, '.java': 3.8, '.scala': 4.2, '.kt': 3.6,
            
            # Medium-high complexity (functional, complex syntax)
            '.py': 3.2, '.rb': 3.0, '.php': 2.8, '.swift': 3.4, '.cs': 3.6,
            '.ts': 3.0, '.tsx': 3.2, '.js': 2.5, '.jsx': 2.7,
            
            # Medium complexity (scripting, web)
            '.sh': 2.5, '.bash': 2.5, '.zsh': 2.5, '.ps1': 2.3, '.bat': 2.0,
            '.r': 2.8, '.m': 3.0, '.sql': 2.2,
            
            # Lower complexity (markup, config, data)
            '.html': 1.5, '.css': 1.2, '.scss': 1.5, '.less': 1.4,
            '.xml': 1.0, '.json': 0.6, '.yaml': 0.7, '.yml': 0.7, '.toml': 0.8,
            '.ini': 0.5, '.cfg': 0.5, '.conf': 0.5,
            
            # Documentation and text
            '.md': 0.3, '.rst': 0.4, '.txt': 0.2, '.tex': 1.0,
            
            # Special files
            'dockerfile': 1.8, 'makefile': 2.2, 'rakefile': 2.0, 'gemfile': 1.5
        }
        
        # Get base complexity
        if filename in ['dockerfile', 'makefile', 'rakefile', 'gemfile']:
            base_complexity = complexity_map.get(filename, 2.0)
        else:
            base_complexity = complexity_map.get(extension, 2.0)  # Default for unknown types
        
        # Adjust for change size (larger changes suggest higher complexity)
        change_multiplier = 1 + (changes / 200)  # More gradual scaling
        
        # Adjust for file path depth (deeper files often more complex)
        path_depth = len(Path(file_path).parts)
        depth_multiplier = 1 + (path_depth - 1) * 0.1
        
        # Special adjustments for certain patterns
        path_lower = file_path.lower()
        if any(pattern in path_lower for pattern in ['test', 'spec']):
            base_complexity *= 0.8  # Tests are usually less complex
        elif any(pattern in path_lower for pattern in ['config', 'settings']):
            base_complexity *= 0.7  # Config files are usually simpler
        elif any(pattern in path_lower for pattern in ['vendor', 'third_party', 'external']):
            base_complexity *= 0.5  # Third-party code gets lower weight
        
        return base_complexity * change_multiplier * depth_multiplier
    
    def calculate_technical_debt_accumulation(self) -> Dict[str, Any]:
        """
        Calculate technical debt accumulation rate over time.
        
        Returns:
            Dict[str, Any]: Technical debt metrics and trends
        """
        try:
            commits = self.git_repo.get_all_commits()
            if not commits:
                logger.warning("No commits found for technical debt analysis")
                return {
                    'debt_accumulation_rate': 0,
                    'debt_trend': pd.DataFrame(),
                    'debt_hotspots': [],
                    'debt_by_type': {},
                    'total_debt_commits': 0,
                    'total_commits': 0
                }
            
            logger.info(f"Analyzing technical debt for {len(commits)} commits")
            
            # Enhanced technical debt indicators with better patterns
            debt_patterns = {
                'quick_fix': r'\b(quick\s*fix|hotfix|patch|band\s*aid|bandaid|emergency\s*fix)\b',
                'todo': r'\b(todo|fixme|hack|hacky|temporary|temp|kludge|xxx)\b',
                'workaround': r'\b(workaround|work\s*around|bypass|circumvent)\b',
                'technical_debt': r'\b(technical\s*debt|refactor|cleanup|clean\s*up|code\s*smell)\b',
                'code_smell': r'\b(smell|ugly|messy|dirty|gross|awful|terrible)\b',
                'bug_fix': r'\b(fix|fixes|fixed|bug|issue|error|problem|broken)\b',
                'magic_numbers': r'\b(magic\s*number|hard\s*coded|hardcoded)\b'
            }
            
            monthly_debt = defaultdict(lambda: {
                'total_commits': 0,
                'debt_commits': 0,
                'debt_types': Counter()
            })
            
            file_debt_scores = defaultdict(float)
            processed_commits = 0
            
            for commit in commits:
                try:
                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    month_key = commit_date.strftime('%Y-%m')
                    
                    monthly_debt[month_key]['total_commits'] += 1
                    
                    # Analyze commit message for debt indicators
                    message_lower = (commit.message or "").lower()
                    debt_found = False
                    debt_score = 0
                    
                    for debt_type, pattern in debt_patterns.items():
                        matches = len(re.findall(pattern, message_lower))
                        if matches > 0:
                            monthly_debt[month_key]['debt_types'][debt_type] += matches
                            debt_found = True
                            
                            # Weight different types of debt
                            debt_weights = {
                                'quick_fix': 3,
                                'todo': 2,
                                'workaround': 2.5,
                                'technical_debt': 1.5,
                                'code_smell': 2,
                                'bug_fix': 1,
                                'magic_numbers': 1.5
                            }
                            debt_score += matches * debt_weights.get(debt_type, 1)
                    
                    if debt_found:
                        monthly_debt[month_key]['debt_commits'] += 1
                        
                        # Add weighted debt score to changed files
                        changed_files = self._get_safe_changed_files(commit)
                        for file_path in changed_files.keys():
                            if self._is_analyzable_file(file_path):
                                file_debt_scores[file_path] += debt_score
                    
                    processed_commits += 1
                
                except Exception as e:
                    logger.debug(f"Skipping commit {commit.hexsha} in debt analysis: {e}")
                    continue
            
            logger.info(f"Successfully processed {processed_commits} commits for debt analysis")
            
            # Calculate debt accumulation trend
            trend_data = []
            for month in sorted(monthly_debt.keys()):
                data = monthly_debt[month]
                debt_rate = (data['debt_commits'] / data['total_commits'] * 100) if data['total_commits'] > 0 else 0
                
                trend_data.append({
                    'month': month,
                    'total_commits': data['total_commits'],
                    'debt_commits': data['debt_commits'],
                    'debt_rate': debt_rate,
                    'quick_fix': data['debt_types']['quick_fix'],
                    'todo': data['debt_types']['todo'],
                    'workaround': data['debt_types']['workaround'],
                    'technical_debt': data['debt_types']['technical_debt'],
                    'code_smell': data['debt_types']['code_smell'],
                    'bug_fix': data['debt_types']['bug_fix'],
                    'magic_numbers': data['debt_types']['magic_numbers']
                })
            
            debt_trend = pd.DataFrame(trend_data)
            if not debt_trend.empty:
                debt_trend['month'] = pd.to_datetime(debt_trend['month'])
                debt_trend = debt_trend.sort_values('month')
            
            # Calculate overall debt accumulation rate
            total_commits = sum(data['total_commits'] for data in monthly_debt.values())
            total_debt_commits = sum(data['debt_commits'] for data in monthly_debt.values())
            debt_accumulation_rate = (total_debt_commits / total_commits * 100) if total_commits > 0 else 0
            
            # Identify debt hotspots (files with highest debt scores) - top 20
            debt_hotspots = []
            if file_debt_scores:
                sorted_debt = sorted(file_debt_scores.items(), key=lambda x: x[1], reverse=True)
                debt_hotspots = [
                    {'file_path': file_path, 'debt_score': score}
                    for file_path, score in sorted_debt[:20]
                ]
            
            # Aggregate debt by type across all time
            debt_by_type = {}
            for data in monthly_debt.values():
                for debt_type, count in data['debt_types'].items():
                    debt_by_type[debt_type] = debt_by_type.get(debt_type, 0) + count
            
            logger.info(f"Technical debt accumulation rate: {debt_accumulation_rate:.1f}%")
            return {
                'debt_accumulation_rate': debt_accumulation_rate,
                'debt_trend': debt_trend,
                'debt_hotspots': debt_hotspots,
                'debt_by_type': debt_by_type,
                'total_debt_commits': total_debt_commits,
                'total_commits': total_commits,
                'processed_commits': processed_commits
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical debt: {e}")
            return {
                'debt_accumulation_rate': 0,
                'debt_trend': pd.DataFrame(),
                'debt_hotspots': [],
                'debt_by_type': {}
            }
    
    def calculate_test_to_code_ratio(self) -> Dict[str, Any]:
        """
        Calculate the ratio of test files to production code files efficiently.
        
        Returns:
            Dict[str, Any]: Test coverage and ratio metrics
        """
        try:
            # More efficient approach: analyze current repository state instead of all commits
            try:
                # Get all files from the current HEAD
                head_commit = self.git_repo.repo.head.commit
                all_files = {item.path for item in head_commit.tree.traverse() 
                           if item.type == 'blob'}
                
                logger.info(f"Analyzing {len(all_files)} files from current repository state")
                
            except Exception:
                # Fallback to commit-based analysis if HEAD approach fails
                logger.info("Falling back to commit-based file analysis")
                commits = self.git_repo.get_all_commits(max_count=100)  # Limit for performance
                if not commits:
                    logger.warning("No commits found for test analysis")
                    return self._empty_test_analysis()
                
                all_files = set()
                for commit in commits[:10]:  # Only check recent commits for efficiency
                    try:
                        changed_files = self._get_safe_changed_files(commit)
                        all_files.update(changed_files.keys())
                    except Exception as e:
                        logger.debug(f"Skipping commit {commit.hexsha} in test analysis: {e}")
                        continue
            
            if not all_files:
                logger.warning("No files found for analysis")
                return self._empty_test_analysis()
            
            # Enhanced test file patterns with framework-specific detection
            test_patterns = {
                'test_prefix': r'^test_',
                'test_suffix': r'_test\.(py|js|ts|java|cpp|c|go|rs|php|rb)$',
                'spec_prefix': r'^spec_',
                'spec_suffix': r'_spec\.(py|js|ts|java|cpp|c|go|rs|php|rb)$',
                'test_dirs': r'(^|/)tests?/',
                'spec_dirs': r'(^|/)specs?/',
                'unittest_dirs': r'(^|/)unit_?tests?/',
                'integration_dirs': r'(^|/)integration_?tests?/',
                'e2e_dirs': r'(^|/)e2e/',
                'cypress_dirs': r'(^|/)cypress/',
                'jest_pattern': r'\.(test|spec)\.(js|ts|jsx|tsx)$',
                'pytest_pattern': r'test_.*\.py$|.*_test\.py$',
                'java_test': r'Test\.java$|Tests\.java$',
                'go_test': r'_test\.go$',
                'rust_test': r'#\[test\]',  # Special handling needed
                'cpp_test': r'(test|spec).*\.(cpp|cc|cxx)$',
                '__tests__': r'(^|/)__tests__/'
            }
            
            test_files = set()
            code_files = set()
            directories = defaultdict(lambda: {'total': 0, 'tests': 0})
            test_pattern_usage = Counter()
            
            for file_path in all_files:
                # Skip non-analyzable files
                if not self._is_analyzable_file(file_path):
                    continue
                
                path_obj = Path(file_path)
                extension = path_obj.suffix.lower()
                file_name = path_obj.name.lower()
                dir_path = str(path_obj.parent).lower()
                full_path_lower = file_path.lower()
                
                # Track directory statistics
                if len(path_obj.parts) > 1:
                    main_dir = path_obj.parts[0]
                    directories[main_dir]['total'] += 1
                
                # Enhanced test detection with multiple patterns
                is_test = False
                matched_patterns = []
                
                # Check each pattern
                if re.search(test_patterns['test_prefix'], file_name):
                    is_test = True
                    matched_patterns.append('test_prefix')
                    
                if re.search(test_patterns['test_suffix'], file_name):
                    is_test = True
                    matched_patterns.append('test_suffix')
                    
                if re.search(test_patterns['spec_prefix'], file_name):
                    is_test = True
                    matched_patterns.append('spec_prefix')
                    
                if re.search(test_patterns['spec_suffix'], file_name):
                    is_test = True
                    matched_patterns.append('spec_suffix')
                    
                # Directory-based detection
                for pattern_name, pattern in test_patterns.items():
                    if 'dirs' in pattern_name and re.search(pattern, full_path_lower):
                        is_test = True
                        matched_patterns.append(pattern_name)
                        break
                
                # Framework-specific patterns
                if extension == '.js' or extension == '.ts':
                    if re.search(test_patterns['jest_pattern'], file_name):
                        is_test = True
                        matched_patterns.append('jest')
                
                elif extension == '.py':
                    if re.search(test_patterns['pytest_pattern'], file_name):
                        is_test = True
                        matched_patterns.append('pytest')
                
                elif extension == '.java':
                    if re.search(test_patterns['java_test'], file_name):
                        is_test = True
                        matched_patterns.append('java_test')
                
                elif extension == '.go':
                    if re.search(test_patterns['go_test'], file_name):
                        is_test = True
                        matched_patterns.append('go_test')
                
                elif extension in ['.cpp', '.cc', '.cxx']:
                    if re.search(test_patterns['cpp_test'], file_name):
                        is_test = True
                        matched_patterns.append('cpp_test')
                
                # Additional heuristics
                if 'test' in full_path_lower and not is_test:
                    # Catch additional test files that might be missed
                    test_keywords = ['unittest', 'testcase', 'fixture', 'mock']
                    if any(keyword in full_path_lower for keyword in test_keywords):
                        is_test = True
                        matched_patterns.append('heuristic')
                
                if is_test:
                    test_files.add(file_path)
                    if len(path_obj.parts) > 1:
                        directories[path_obj.parts[0]]['tests'] += 1
                    
                    # Track pattern usage
                    for pattern in matched_patterns:
                        test_pattern_usage[pattern] += 1
                else:
                    # Consider it a code file if it has a programming language extension
                    code_extensions = {
                        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
                        '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.cs', '.sh', '.bash'
                    }
                    if extension in code_extensions:
                        code_files.add(file_path)
            
            # Calculate metrics
            test_files_count = len(test_files)
            code_files_count = len(code_files)
            test_to_code_ratio = (test_files_count / code_files_count) if code_files_count > 0 else 0
            
            # Find directories without tests
            untested_directories = []
            for dir_name, counts in directories.items():
                if counts['total'] > 2 and counts['tests'] == 0:  # Directories with multiple files but no tests
                    untested_directories.append({
                        'directory': dir_name,
                        'file_count': counts['total']
                    })
            
            # Sort by file count descending
            untested_directories.sort(key=lambda x: x['file_count'], reverse=True)
            
            # Convert pattern usage to regular dict
            pattern_usage = dict(test_pattern_usage)
            
            logger.info(f"Test analysis complete: {test_files_count} test files, {code_files_count} code files")
            logger.info(f"Test to code ratio: {test_to_code_ratio:.2f}")
            
            return {
                'test_to_code_ratio': test_to_code_ratio,
                'test_files_count': test_files_count,
                'code_files_count': code_files_count,
                'total_files_analyzed': len(all_files),
                'test_patterns': pattern_usage,
                'untested_directories': untested_directories[:10],  # Top 10
                'test_coverage_percentage': (test_to_code_ratio * 100),
                'recommendations': self._generate_test_recommendations(test_to_code_ratio, untested_directories),
                'test_files_sample': list(test_files)[:10],  # Sample for verification
                'code_files_sample': list(code_files)[:10]   # Sample for verification
            }
            
        except Exception as e:
            logger.error(f"Error calculating test to code ratio: {e}")
            return self._empty_test_analysis()
    
    def _empty_test_analysis(self) -> Dict[str, Any]:
        """Return empty test analysis structure."""
        return {
            'test_to_code_ratio': 0,
            'test_files_count': 0,
            'code_files_count': 0,
            'total_files_analyzed': 0,
            'test_patterns': {},
            'untested_directories': [],
            'test_coverage_percentage': 0,
            'recommendations': ["No files available for test analysis"],
            'test_files_sample': [],
            'code_files_sample': []
        }
    
    def _generate_maintainability_recommendations(self, df: pd.DataFrame, factors: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations for improving maintainability."""
        recommendations = []
        
        if df.empty:
            return ["No data available for maintainability recommendations"]
        
        avg_score = df['maintainability_score'].mean()
        
        # Overall assessment
        if avg_score < 30:
            recommendations.append("🚨 Critical: Overall maintainability is very low - urgent refactoring needed")
        elif avg_score < 50:
            recommendations.append("⚠️ Warning: Low maintainability - prioritize code quality improvements")
        elif avg_score < 70:
            recommendations.append("📈 Moderate maintainability - focus on preventing technical debt")
        elif avg_score < 85:
            recommendations.append("✅ Good maintainability - maintain current standards")
        else:
            recommendations.append("🌟 Excellent maintainability - consider sharing best practices")
        
        # Specific actionable recommendations based on data
        if factors.get('avg_commits_per_file', 0) > 30:
            recommendations.append("📂 Consider breaking down frequently modified files into smaller modules")
        
        if factors.get('avg_authors_per_file', 0) > 5:
            recommendations.append("👥 High author count per file - establish code ownership and review guidelines")
        
        critical_files = len(df[df['maintainability_score'] < 30])
        if critical_files > 0:
            recommendations.append(f"🔧 {critical_files} files need immediate refactoring attention")
        
        poor_files = len(df[df['maintainability_score'] < 50])
        if poor_files > critical_files:
            recommendations.append(f"📝 {poor_files - critical_files} additional files would benefit from improvement")
        
        # Language-specific recommendations
        extensions = df['extension'].value_counts()
        if '.py' in extensions.index and extensions['.py'] > 10:
            recommendations.append("🐍 Python files: Consider using tools like pylint, flake8, and black for code quality")
        
        if any(ext in extensions.index for ext in ['.js', '.ts', '.jsx', '.tsx']):
            recommendations.append("🟨 JavaScript/TypeScript: Consider ESLint, Prettier, and TypeScript for better maintainability")
        
        return recommendations
    
    def _generate_test_recommendations(self, ratio: float, untested_dirs: List[Dict]) -> List[str]:
        """Generate actionable recommendations for improving test coverage."""
        recommendations = []
        
        # Coverage-based recommendations
        if ratio < 0.05:
            recommendations.append("🚨 Critical: Very low test coverage - start with testing core functionality")
            recommendations.append("🏁 Quick start: Add tests for main entry points and critical business logic")
        elif ratio < 0.2:
            recommendations.append("📊 Low test coverage - focus on testing high-risk areas")
            recommendations.append("🎯 Priority: Test complex algorithms and edge cases")
        elif ratio < 0.5:
            recommendations.append("📈 Moderate test coverage - expand testing to cover more scenarios")
            recommendations.append("🔍 Focus: Add integration tests and error handling tests")
        elif ratio < 0.8:
            recommendations.append("✅ Good test coverage - focus on test quality and edge cases")
            recommendations.append("🧪 Enhancement: Add property-based testing and performance tests")
        else:
            recommendations.append("🌟 Excellent test coverage - maintain high standards")
            recommendations.append("⚡ Optimization: Review test efficiency and remove redundant tests")
        
        # Directory-specific recommendations
        if untested_dirs:
            top_dirs = [d['directory'] for d in untested_dirs[:3]]
            recommendations.append(f"📁 Add tests to directories with most files: {', '.join(top_dirs)}")
        
        # Framework-specific recommendations
        if ratio > 0:
            recommendations.append("🛠️ Consider using test frameworks: pytest (Python), Jest (JS), JUnit (Java)")
            recommendations.append("📊 Set up test coverage reporting with tools like coverage.py or nyc")
        
        return recommendations
