"""Git repository context detection and parsing.

This module provides functionality to detect and extract context from git repositories,
including owner/repo information from remotes, current branch, and tags.

Principles Applied:
- Single Responsibility: Each function has one clear purpose
- Open/Closed: Extensible for new remote URL formats without modification
- Interface Segregation: Small, focused functions
- Dependency Inversion: Uses abstractions (subprocess) not concrete implementations
- DRY: No code duplication
- KISS: Simple, straightforward implementations
- YAGNI: Only implements what's needed now
- Separation of Concerns: Git operations separate from business logic
- Law of Demeter: Minimal coupling between components
"""

import re
import subprocess  # nosec B404: restricted to invoking 'git' with static arguments; no shell
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class GitRemote:
    """Immutable git remote information.

    Attributes:
        name: Remote name (e.g., 'origin')
        url: Remote URL
        owner: Repository owner/organization
        repo: Repository name
    """

    name: str
    url: str
    owner: str
    repo: str


@dataclass(frozen=True)
class GitContext:
    """Immutable git repository context.

    Attributes:
        remote: Primary git remote information
        branch: Current branch name
        root_path: Repository root directory path
    """

    remote: GitRemote
    branch: Optional[str]
    root_path: Path


class GitCommandError(Exception):
    """Raised when a git command fails."""


class NotAGitRepositoryError(Exception):
    """Raised when the current directory is not a git repository."""


class GitRemoteParseError(Exception):
    """Raised when a git remote URL cannot be parsed."""


def _run_git_command(args: list[str], cwd: Optional[Path] = None) -> str:
    """Run a git command and return stdout.

    Single Responsibility: Execute git commands with error handling.

    Args:
        args: Git command arguments (e.g., ['remote', '-v'])
        cwd: Working directory for command execution

    Returns:
        Command stdout as string

    Raises:
        GitCommandError: If command fails
    """
    try:
        result = subprocess.run(  # nosec B603: arguments are static and controlled; shell=False
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise GitCommandError(f"Git command failed: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise GitCommandError(f"Git command timed out: {' '.join(args)}") from e


def is_git_repository(path: Optional[Path] = None) -> bool:
    """Check if the given path is within a git repository.

    Single Responsibility: Determine git repository status.

    Args:
        path: Directory path to check (default: current directory)

    Returns:
        True if path is in a git repository, False otherwise
    """
    try:
        _run_git_command(["rev-parse", "--git-dir"], cwd=path)
        return True
    except GitCommandError:
        return False


def get_repository_root(path: Optional[Path] = None) -> Path:
    """Get the root directory of the git repository.

    Single Responsibility: Find repository root.

    Args:
        path: Starting path (default: current directory)

    Returns:
        Path to repository root

    Raises:
        NotAGitRepositoryError: If not in a git repository
    """
    try:
        root = _run_git_command(["rev-parse", "--show-toplevel"], cwd=path)
        return Path(root)
    except GitCommandError as e:
        raise NotAGitRepositoryError("Not in a git repository") from e


def get_current_branch(path: Optional[Path] = None) -> Optional[str]:
    """Get the current git branch name.

    Single Responsibility: Retrieve current branch.

    Args:
        path: Repository path (default: current directory)

    Returns:
        Branch name or None if detached HEAD
    """
    try:
        branch = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
        return branch if branch != "HEAD" else None
    except GitCommandError:
        return None


def get_latest_tag(path: Optional[Path] = None) -> Optional[str]:
    """Get the most recent git tag.

    Single Responsibility: Retrieve latest tag.

    Args:
        path: Repository path (default: current directory)

    Returns:
        Latest tag name or None if no tags exist
    """
    try:
        result = _run_git_command(["describe", "--tags", "--abbrev=0"], cwd=path)
        # git describe returns a single tag, extract first line if multiple
        tag = result.split("\n")[0].strip() if result else None
        return tag or None
    except GitCommandError:
        return None


def get_previous_tag(
    current_tag: Optional[str] = None, path: Optional[Path] = None
) -> Optional[str]:
    """Get the tag before the specified tag (or before latest if not specified).

    Single Responsibility: Find previous tag in history.

    Args:
        current_tag: Current tag (default: latest tag)
        path: Repository path (default: current directory)

    Returns:
        Previous tag name or None if no previous tag exists
    """
    try:
        # If no current tag specified, get the latest
        if not current_tag:
            current_tag = get_latest_tag(path)
            if not current_tag:
                return None

        # Get all tags sorted by commit date
        result = _run_git_command(["tag", "--sort=-creatordate"], cwd=path)

        tags = [t.strip() for t in result.split("\n") if t.strip()]

        # Find current tag and return the next one
        try:
            current_index = tags.index(current_tag)
            if current_index + 1 < len(tags):
                return tags[current_index + 1]
        except ValueError:
            pass

        return None
    except GitCommandError:
        return None


def detect_pr_number_from_branch(branch_name: str) -> Optional[int]:
    """Detect PR number from branch name patterns.

    Single Responsibility: Extract PR number from branch name.

    Common patterns:
    - pr-123
    - PR-123
    - pr/123
    - feature/pr-123
    - 123-feature-name

    Args:
        branch_name: Git branch name

    Returns:
        PR number if detected, None otherwise
    """
    import re

    # Pattern 1: pr-123 or PR-123 (case insensitive)
    match = re.search(r"pr[-/](\d+)", branch_name, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Pattern 2: 123-feature-name (number at start)
    match = re.match(r"^(\d+)[-_]", branch_name)
    if match:
        return int(match.group(1))

    return None


def _parse_github_url(url: str) -> tuple[str, str]:
    """Parse GitHub owner and repo from a remote URL.

    Single Responsibility: Extract owner/repo from URL.
    Open/Closed: Supports multiple URL formats without modification.

    Supported formats:
    - SSH: git@github.com:owner/repo.git
    - HTTPS: https://github.com/owner/repo.git
    - Git protocol: git://github.com/owner/repo.git

    Args:
        url: Git remote URL

    Returns:
        Tuple of (owner, repo)

    Raises:
        GitRemoteParseError: If URL format is not recognized
    """
    # SSH format: git@github.com:owner/repo.git
    ssh_pattern = r"git@github\.com:([^/]+)/(.+?)(?:\.git)?$"

    # HTTPS format: https://github.com/owner/repo.git
    https_pattern = r"https://github\.com/([^/]+)/(.+?)(?:\.git)?$"

    # Git protocol: git://github.com/owner/repo.git
    git_pattern = r"git://github\.com/([^/]+)/(.+?)(?:\.git)?$"

    for pattern in [ssh_pattern, https_pattern, git_pattern]:
        match = re.match(pattern, url)
        if match:
            owner, repo = match.groups()
            return owner, repo

    raise GitRemoteParseError(f"Unable to parse GitHub URL: {url}")


def get_remote_url(remote_name: str = "origin", path: Optional[Path] = None) -> Optional[str]:
    """Get the URL for a git remote.

    Single Responsibility: Retrieve remote URL.

    Args:
        remote_name: Name of the remote (default: 'origin')
        path: Repository path (default: current directory)

    Returns:
        Remote URL or None if remote doesn't exist
    """
    try:
        url = _run_git_command(["remote", "get-url", remote_name], cwd=path)
        return url if url else None
    except GitCommandError:
        return None


def parse_github_remote(
    remote_name: str = "origin", path: Optional[Path] = None
) -> Optional[GitRemote]:
    """Parse GitHub owner and repo from a git remote.

    Single Responsibility: Extract and structure remote information.

    Args:
        remote_name: Name of the remote (default: 'origin')
        path: Repository path (default: current directory)

    Returns:
        GitRemote object or None if remote doesn't exist or isn't GitHub
    """
    url = get_remote_url(remote_name, path)
    if not url:
        return None

    try:
        owner, repo = _parse_github_url(url)
        return GitRemote(
            name=remote_name,
            url=url,
            owner=owner,
            repo=repo,
        )
    except GitRemoteParseError:
        return None


def get_git_context(path: Optional[Path] = None) -> Optional[GitContext]:
    """Get complete git repository context.

    Single Responsibility: Aggregate git context information.
    Separation of Concerns: Delegates to specialized functions.

    Args:
        path: Repository path (default: current directory)

    Returns:
        GitContext object or None if not in a git repository or no GitHub remote
    """
    if not is_git_repository(path):
        return None

    try:
        root_path = get_repository_root(path)
    except NotAGitRepositoryError:
        return None

    remote = parse_github_remote("origin", path)
    if not remote:
        return None

    branch = get_current_branch(path)

    return GitContext(
        remote=remote,
        branch=branch,
        root_path=root_path,
    )
