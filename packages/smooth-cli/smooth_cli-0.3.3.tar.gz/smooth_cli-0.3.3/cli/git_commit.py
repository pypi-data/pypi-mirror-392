"""Pure-Python Git commit operations using dulwich.

This module provides Git commit functionality without requiring system git
installation, using the dulwich pure-Python Git implementation.

Principles Applied:
- Single Responsibility: Each function handles one aspect of commit operations
- Dependency Inversion: Uses dulwich abstraction, not concrete git commands
- KISS: Simple, focused implementation
- Security: No shell execution, validates inputs
"""

from __future__ import annotations

import os
from pathlib import Path

from dulwich.porcelain import commit as dulwich_commit
from dulwich.porcelain import open_repo_closing


class GitCommitError(Exception):
    """Raised when git commit operation fails."""


class NoStagedChangesError(GitCommitError):
    """Raised when attempting to commit with no staged changes."""


class InvalidRepositoryError(GitCommitError):
    """Raised when path is not a valid git repository."""


def find_git_root(start_path: Path | None = None) -> Path:
    """Find the root directory of the git repository.

    Args:
        start_path: Starting directory (default: current directory)

    Returns:
        Path to the git repository root

    Raises:
        InvalidRepositoryError: If no git repository is found
    """
    current = start_path or Path.cwd()

    # Search upward for .git directory
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists():
            return current
        current = current.parent

    # Check root directory
    git_dir = current / ".git"
    if git_dir.exists():
        return current

    msg = f"Not a git repository (or any parent up to {current})"
    raise InvalidRepositoryError(msg)


def has_staged_changes(repo_path: Path) -> bool:
    """Check if repository has staged changes.

    Args:
        repo_path: Path to git repository root

    Returns:
        True if there are staged changes, False otherwise
    """
    try:
        from dulwich.porcelain import status as dulwich_status

        # Use dulwich's status command to check for staged changes
        status_result = dulwich_status(str(repo_path))

        # status_result contains staged, unstaged, and untracked
        # We only care about staged changes
        return (
            len(status_result.staged["add"]) > 0
            or len(status_result.staged["delete"]) > 0
            or len(status_result.staged["modify"]) > 0
        )
    except Exception as e:
        msg = f"Failed to check staged changes: {e}"
        raise GitCommitError(msg) from e


def commit_staged_changes(
    repo_path: Path,
    message: str,
    author_name: str | None = None,
    author_email: str | None = None,
) -> str:
    """Commit staged changes using pure-Python Git operations.

    Args:
        repo_path: Path to git repository root
        message: Commit message
        author_name: Author name (default: from git config)
        author_email: Author email (default: from git config)

    Returns:
        Commit SHA as hex string

    Raises:
        NoStagedChangesError: If no changes are staged
        GitCommitError: If commit operation fails
    """
    # Check for staged changes first (fast check before opening repo)
    if not has_staged_changes(repo_path):
        msg = "No staged changes to commit"
        raise NoStagedChangesError(msg)

    try:
        with open_repo_closing(str(repo_path)) as repo:
            # Get author info from git config if not provided
            config = repo.get_config()
            if author_name is None:
                author_name = (
                    config.get((b"user",), b"name").decode("utf-8")
                    if config.has_section((b"user",))
                    else os.environ.get("GIT_AUTHOR_NAME", "Unknown")
                )
            if author_email is None:
                author_email = (
                    config.get((b"user",), b"email").decode("utf-8")
                    if config.has_section((b"user",))
                    else os.environ.get("GIT_AUTHOR_EMAIL", "unknown@example.com")
                )

            # Perform commit
            commit_sha = dulwich_commit(
                repo=str(repo_path),
                message=message,
                author=f"{author_name} <{author_email}>".encode(),
                committer=f"{author_name} <{author_email}>".encode(),
            )

            return commit_sha.decode("utf-8") if isinstance(commit_sha, bytes) else commit_sha

    except Exception as e:
        msg = f"Failed to commit changes: {e}"
        raise GitCommitError(msg) from e


def validate_commit_message(message: str) -> None:
    """Validate commit message format.

    Args:
        message: Commit message to validate

    Raises:
        ValueError: If message is invalid
    """
    if not message or not message.strip():
        msg = "Commit message cannot be empty"
        raise ValueError(msg)

    # Check for reasonable length (subject line)
    MAX_SUBJECT_LENGTH = 100  # noqa: N806
    lines = message.split("\n")
    if lines[0] and len(lines[0]) > MAX_SUBJECT_LENGTH:
        msg = f"Commit message subject line should be {MAX_SUBJECT_LENGTH} characters or less"
        raise ValueError(msg)
