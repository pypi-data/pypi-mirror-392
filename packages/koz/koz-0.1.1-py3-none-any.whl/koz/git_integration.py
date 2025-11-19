"""Git history integration for extracting patch metadata."""

from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from git import Repo
    from git.exc import GitCommandError, InvalidGitRepositoryError

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


class GitMetadataExtractor:
    """Extracts git metadata for patch locations."""

    def __init__(self, repo_path: Path) -> None:
        """Initialize the git metadata extractor.

        Args:
            repo_path: Path to the git repository root
        """
        self.repo_path = repo_path
        self.repo: Optional[Repo] = None

        if GIT_AVAILABLE:
            try:
                self.repo = Repo(repo_path)
            except (InvalidGitRepositoryError, GitCommandError):
                # Not a git repository, continue without git metadata
                pass

    def get_file_metadata(
        self, file_path: Path, line_number: int
    ) -> tuple[Optional[datetime], Optional[str]]:
        """Get git metadata for a specific line in a file.

        Args:
            file_path: Path to the file
            line_number: Line number to get metadata for

        Returns:
            Tuple of (timestamp, author) or (None, None) if not available
        """
        if not self.repo or not GIT_AVAILABLE:
            return None, None

        try:
            # Get relative path from repo root
            rel_path = file_path.relative_to(self.repo_path)

            # Get the most recent commit that modified this file
            commits = list(self.repo.iter_commits(paths=str(rel_path), max_count=10))

            if not commits:
                return None, None

            # Use the most recent commit
            latest_commit = commits[0]

            timestamp = datetime.fromtimestamp(latest_commit.committed_date)
            author = f"{latest_commit.author.name} <{latest_commit.author.email}>"

            return timestamp, author

        except (GitCommandError, ValueError, OSError):
            return None, None

    def is_git_available(self) -> bool:
        """Check if git integration is available.

        Returns:
            True if git is available and repo is valid
        """
        return self.repo is not None and GIT_AVAILABLE
