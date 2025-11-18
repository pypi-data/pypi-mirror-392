"""Git utilities for extracting changed files from diffs."""

from pathlib import Path
from typing import List
import git
import fnmatch


def get_changed_files(repo_path: str, base_branch: str = "main") -> List[Path]:
    """Get list of files changed in current branch compared to base branch."""
    repo = git.Repo(repo_path)

    # Get current branch
    current_branch = repo.active_branch.name

    if current_branch == base_branch:
        raise ValueError(f"Cannot compare branch to itself: {base_branch}")

    # Get diff between base branch and current branch
    # Use current.diff(base) to get files added/changed in current vs base
    base_commit = repo.commit(base_branch)
    current_commit = repo.head.commit

    diff = current_commit.diff(base_commit)

    # Extract changed file paths from diff
    changed_files = []
    for item in diff:
        # Handle both a_path (deleted) and b_path (added/modified)
        file_path = item.b_path if item.b_path else item.a_path
        if file_path:
            full_path = Path(repo_path) / file_path
            if full_path.exists():
                changed_files.append(full_path)

    # Also include untracked files
    untracked = repo.untracked_files
    for file_path in untracked:
        full_path = Path(repo_path) / file_path
        if full_path.exists():
            changed_files.append(full_path)

    return changed_files


class GitDiffExtractor:
    """Extract and filter changed files from git diff."""

    def __init__(
        self,
        repo_path: str,
        file_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ):
        self.repo_path = Path(repo_path)
        self.file_patterns = file_patterns or ["**/*"]
        self.exclude_patterns = exclude_patterns or []

    def _matches_pattern(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file matches any of the given glob patterns."""
        relative_path = file_path.relative_to(self.repo_path)

        for pattern in patterns:
            if fnmatch.fnmatch(str(relative_path), pattern) or \
               fnmatch.fnmatch(str(relative_path), pattern.replace('**/', '')):
                return True
        return False

    def get_changed_files(self, base_branch: str = "main") -> List[Path]:
        """Get filtered list of changed files."""
        all_changed = get_changed_files(str(self.repo_path), base_branch)

        filtered = []
        for file_path in all_changed:
            # Check if matches include patterns
            if not self._matches_pattern(file_path, self.file_patterns):
                continue

            # Check if matches exclude patterns
            if self.exclude_patterns and self._matches_pattern(file_path, self.exclude_patterns):
                continue

            filtered.append(file_path)

        return filtered
