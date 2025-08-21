"""
GitRepository module for handling Git repository operations.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# Try to import GitPython, but don't hard-fail at import time so tests can patch Repo
try:  # pragma: no cover - environment dependent
    from git import Repo, InvalidGitRepositoryError  # type: ignore
    from git.objects import Commit, Blob, Tree  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - graceful fallback
    Repo = None  # type: ignore

    class InvalidGitRepositoryError(Exception):
        pass

    class Commit:  # minimal placeholders for typing/instance checks
        pass

    class Blob:  # used in isinstance checks when traversing trees
        pass

    class Tree:
        pass


logger = logging.getLogger(__name__)


class GitRepository:
    """
    Core class for interacting with a Git repository.

    This class provides low-level access to Git repository data and serves
    as the foundation for other analyzer classes.
    """

    def __init__(self, repo_path: str):
        """
        Initialize the GitRepository.

        Args:
            repo_path (str): Path to the Git repository

        Raises:
            InvalidGitRepositoryError: If the path is not a valid Git repository
            FileNotFoundError: If the repository path doesn't exist
        """
        self.repo_path = Path(repo_path).resolve()

        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.repo_path}")

        # Defer hard dependency error until initialization time to allow tests to patch Repo
        if Repo is None:
            raise ImportError(
                "GitPython is required but not installed. Install with 'pip install GitPython' or "
                "add it to your requirements.txt."
            )

        try:
            self.repo = Repo(str(self.repo_path))
        except InvalidGitRepositoryError as e:
            raise InvalidGitRepositoryError(f"Invalid Git repository at {self.repo_path}: {e}")

        logger.info(f"Initialized GitRepository for: {self.repo_path}")

    @property
    def is_bare(self) -> bool:
        """Check if the repository is bare."""
        return self.repo.bare

    @property
    def active_branch(self) -> str:
        """Get the currently active branch name."""
        try:
            return self.repo.active_branch.name
        except (TypeError, Exception):
            # Handle detached HEAD state or other issues
            try:
                return f"HEAD ({self.repo.head.commit.hexsha[:8]})"
            except Exception:
                return "HEAD (unknown)"

    @property
    def remote_urls(self) -> Dict[str, str]:
        """Get all remote URLs."""
        return {remote.name: list(remote.urls)[0] for remote in self.repo.remotes}

    def get_all_commits(
        self, branch: Optional[str] = None, max_count: Optional[int] = None
    ) -> List[Commit]:
        """
        Get all commits from the repository.

        Args:
            branch (str, optional): Specific branch to get commits from. Defaults to all branches.
            max_count (int, optional): Maximum number of commits to retrieve.

        Returns:
            List[Commit]: List of commit objects
        """
        try:
            if branch:
                commits = list(self.repo.iter_commits(branch, max_count=max_count))
            else:
                commits = list(self.repo.iter_commits("--all", max_count=max_count))

            logger.info(f"Retrieved {len(commits)} commits")
            return commits
        except Exception as e:
            logger.error(f"Error retrieving commits: {e}")
            return []

    def get_branches(self, remote: bool = False) -> List[str]:
        """
        Get all branch names.

        Args:
            remote (bool): Include remote branches if True

        Returns:
            List[str]: List of branch names
        """
        try:
            if remote:
                branches = [ref.name for ref in self.repo.refs if ref.name.startswith("origin/")]
            else:
                branches = [branch.name for branch in self.repo.branches]

            logger.info(f"Found {len(branches)} branches")
            return branches
        except Exception as e:
            logger.error(f"Error retrieving branches: {e}")
            return []

    def get_tags(self) -> List[str]:
        """
        Get all tag names.

        Returns:
            List[str]: List of tag names
        """
        try:
            tags = [tag.name for tag in self.repo.tags]
            logger.info(f"Found {len(tags)} tags")
            return tags
        except Exception as e:
            logger.error(f"Error retrieving tags: {e}")
            return []

    def get_file_content(self, file_path: str, commit_sha: Optional[str] = None) -> Optional[str]:
        """
        Get the content of a file at a specific commit.

        Args:
            file_path (str): Path to the file relative to repository root
            commit_sha (str, optional): Commit SHA. If None, uses HEAD.

        Returns:
            str: File content or None if file doesn't exist
        """
        try:
            if commit_sha:
                commit = self.repo.commit(commit_sha)
            else:
                commit = self.repo.head.commit

            try:
                blob = commit.tree[file_path]
                if isinstance(blob, Blob):
                    return blob.data_stream.read().decode("utf-8", errors="ignore")
            except KeyError:
                logger.warning(f"File {file_path} not found in commit {commit_sha or 'HEAD'}")
                return None

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def get_file_history(self, file_path: str) -> List[Commit]:
        """
        Get the commit history for a specific file.

        Args:
            file_path (str): Path to the file relative to repository root

        Returns:
            List[Commit]: List of commits that modified the file
        """
        try:
            commits = list(self.repo.iter_commits(paths=file_path))
            logger.info(f"Found {len(commits)} commits for file {file_path}")
            return commits
        except Exception as e:
            logger.error(f"Error retrieving file history for {file_path}: {e}")
            return []

    def get_changed_files(self, commit_sha: str) -> Dict[str, str]:
        """
        Get files changed in a specific commit.

        Args:
            commit_sha (str): Commit SHA

        Returns:
            Dict[str, str]: Dictionary mapping file paths to change types (A/M/D)
        """
        try:
            commit = self.repo.commit(commit_sha)
            changed_files = {}

            # Handle the first commit (no parents)
            if not commit.parents:
                for item in commit.tree.traverse():
                    if isinstance(item, Blob):
                        changed_files[item.path] = "A"  # Added
            else:
                # Compare with parent commit
                parent = commit.parents[0]
                diff = parent.diff(commit)

                for diff_item in diff:
                    if diff_item.new_file:
                        changed_files[diff_item.b_path] = "A"  # Added
                    elif diff_item.deleted_file:
                        changed_files[diff_item.a_path] = "D"  # Deleted
                    elif diff_item.renamed_file:
                        changed_files[diff_item.b_path] = "R"  # Renamed
                    else:
                        changed_files[diff_item.b_path] = "M"  # Modified

            return changed_files

        except Exception as e:
            logger.error(f"Error getting changed files for commit {commit_sha}: {e}")
            return {}

    def get_all_files_at_head(self) -> List[str]:
        """List all file paths in the repository at HEAD (working tree snapshot).

        Returns:
            List[str]: Relative file paths at HEAD
        """
        try:
            commit = self.repo.head.commit
            files: List[str] = []
            for item in commit.tree.traverse():
                if isinstance(item, Blob):
                    files.append(item.path)
            logger.info(f"Found {len(files)} files at HEAD")
            return files
        except Exception as e:
            logger.error(f"Error listing files at HEAD: {e}")
            return []

    def get_repository_stats(self) -> Dict[str, Any]:
        """
        Get basic repository statistics.

        Returns:
            Dict[str, Any]: Repository statistics
        """
        try:
            # Get basic info with error handling for each component
            total_commits = 0
            try:
                total_commits = len(list(self.repo.iter_commits("--all")))
            except Exception as e:
                logger.warning(f"Could not count commits: {e}")

            total_branches = 0
            try:
                total_branches = len(self.get_branches())
            except Exception as e:
                logger.warning(f"Could not count branches: {e}")

            total_tags = 0
            try:
                total_tags = len(self.get_tags())
            except Exception as e:
                logger.warning(f"Could not count tags: {e}")

            head_commit = None
            try:
                if not self.is_bare:
                    head_commit = self.repo.head.commit.hexsha
            except Exception as e:
                logger.warning(f"Could not get head commit: {e}")

            active_branch = "Unknown"
            try:
                active_branch = self.active_branch
            except Exception as e:
                logger.warning(f"Could not get active branch: {e}")

            remote_urls = []
            try:
                remote_urls = self.remote_urls
            except Exception as e:
                logger.warning(f"Could not get remote URLs: {e}")

            # Attempt to count files at HEAD
            total_files = 0
            try:
                files_at_head = self.get_all_files_at_head()
                total_files = len(files_at_head)
            except Exception as e:
                logger.warning(f"Could not list files at HEAD: {e}")

            stats = {
                "path": str(self.repo_path),
                "is_bare": self.is_bare,
                "active_branch": active_branch,
                "total_commits": total_commits,
                "total_branches": total_branches,
                "total_tags": total_tags,
                "remotes": remote_urls,
                "head_commit": head_commit,
                "total_files": total_files,
            }

            logger.info("Retrieved repository statistics")
            return stats

        except Exception as e:
            logger.error(f"Error getting repository stats: {e}")
            return {}

    def close(self):
        """Close the repository connection."""
        if hasattr(self, "repo"):
            self.repo.close()
            logger.info("Repository connection closed")
