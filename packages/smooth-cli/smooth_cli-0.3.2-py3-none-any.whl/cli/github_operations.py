"""GitHub write operations for creating and updating PRs and releases.

This module provides GitHub API operations for creating pull requests,
updating PR content, and managing releases.

Principles Applied:
- Single Responsibility: Each function handles one GitHub operation
- Dependency Inversion: Uses requests abstraction for HTTP calls
- KISS: Simple, focused implementation
- Security: Validates inputs, uses token authentication
"""

from __future__ import annotations

import os
import subprocess  # nosec B404 - Safe: only calls gh CLI with hardcoded args
from typing import Any

import requests

from cli.errors import GitHubErrors


class GitHubOperationError(Exception):
    """Raised when GitHub operation fails."""


class PRCreationError(GitHubOperationError):
    """Raised when PR creation fails."""


class PRUpdateError(GitHubOperationError):
    """Raised when PR update fails."""


def _get_github_token() -> str | None:
    """Get GitHub token from environment or gh CLI."""
    # Try environment variable first
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token

    # Try gh CLI
    try:
        result = subprocess.run(  # nosec B603, B607 - Safe: hardcoded gh CLI command
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "main",
    draft: bool = False,
    maintainer_can_modify: bool = True,
) -> dict[str, Any]:
    """Create a pull request on GitHub.

    Args:
        owner: Repository owner
        repo: Repository name
        title: PR title
        body: PR description/body
        head: Branch name containing changes
        base: Base branch to merge into (default: main)
        draft: Create as draft PR (default: False)
        maintainer_can_modify: Allow maintainer edits (default: True)

    Returns:
        Dictionary with PR data including number, url, html_url

    Raises:
        PRCreationError: If PR creation fails
    """
    token = _get_github_token()
    if not token:
        raise PRCreationError(GitHubErrors.NO_TOKEN)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"

    payload = {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
        "draft": draft,
        "maintainer_can_modify": maintainer_can_modify,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        pr_data = response.json()

        return {
            "number": pr_data["number"],
            "url": pr_data["url"],
            "html_url": pr_data["html_url"],
            "state": pr_data["state"],
            "title": pr_data["title"],
            "body": pr_data["body"],
        }

    except requests.exceptions.HTTPError as e:
        error_msg = GitHubErrors.FAILED_TO_CREATE_PR.format(e)
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = GitHubErrors.FAILED_TO_CREATE_PR.format(
                    error_data.get("message", str(e))
                )
            except Exception:  # nosec B110 - Fallback to generic error if JSON parsing fails
                pass
        raise PRCreationError(error_msg) from e
    except Exception as e:
        raise PRCreationError(GitHubErrors.FAILED_TO_CREATE_PR.format(e)) from e


def update_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    title: str | None = None,
    body: str | None = None,
    state: str | None = None,
    base: str | None = None,
) -> dict[str, Any]:
    """Update an existing pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number to update
        title: New PR title (optional)
        body: New PR body (optional)
        state: New state: 'open' or 'closed' (optional)
        base: New base branch (optional)

    Returns:
        Dictionary with updated PR data

    Raises:
        PRUpdateError: If PR update fails
    """
    token = _get_github_token()
    if not token:
        msg = (
            "GitHub token not found. Set GITHUB_TOKEN environment variable "
            "or authenticate with 'gh auth login'"
        )
        raise PRUpdateError(msg)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    payload: dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if state is not None:
        payload["state"] = state
    if base is not None:
        payload["base"] = base

    if not payload:
        msg = "No update parameters provided"
        raise PRUpdateError(msg)

    try:
        response = requests.patch(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        pr_data = response.json()

        return {
            "number": pr_data["number"],
            "url": pr_data["url"],
            "html_url": pr_data["html_url"],
            "state": pr_data["state"],
            "title": pr_data["title"],
            "body": pr_data["body"],
        }

    except requests.exceptions.HTTPError as e:
        error_msg = GitHubErrors.FAILED_TO_UPDATE_PR.format(e)
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = GitHubErrors.FAILED_TO_UPDATE_PR.format(
                    error_data.get("message", str(e))
                )
            except Exception:  # nosec B110 - Fallback to generic error if JSON parsing fails
                pass
        raise PRUpdateError(error_msg) from e
    except Exception as e:
        raise PRUpdateError(GitHubErrors.FAILED_TO_UPDATE_PR.format(e)) from e


def create_release(
    owner: str,
    repo: str,
    tag_name: str,
    name: str | None = None,
    body: str | None = None,
    draft: bool = False,
    prerelease: bool = False,
    target_commitish: str | None = None,
) -> dict[str, Any]:
    """Create a release on GitHub.

    Args:
        owner: Repository owner
        repo: Repository name
        tag_name: Tag name for the release
        name: Release name (default: tag_name)
        body: Release notes/description
        draft: Create as draft release (default: False)
        prerelease: Mark as prerelease (default: False)
        target_commitish: Commit SHA or branch (default: repo default branch)

    Returns:
        Dictionary with release data including id, url, html_url

    Raises:
        GitHubOperationError: If release creation fails
    """
    token = _get_github_token()
    if not token:
        msg = (
            "GitHub token not found. Set GITHUB_TOKEN environment variable "
            "or authenticate with 'gh auth login'"
        )
        raise GitHubOperationError(msg)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    payload: dict[str, Any] = {
        "tag_name": tag_name,
        "name": name or tag_name,
        "draft": draft,
        "prerelease": prerelease,
    }

    if body is not None:
        payload["body"] = body
    if target_commitish is not None:
        payload["target_commitish"] = target_commitish

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        release_data = response.json()

        return {
            "id": release_data["id"],
            "url": release_data["url"],
            "html_url": release_data["html_url"],
            "tag_name": release_data["tag_name"],
            "name": release_data["name"],
            "draft": release_data["draft"],
            "prerelease": release_data["prerelease"],
        }

    except requests.exceptions.HTTPError as e:
        error_msg = GitHubErrors.FAILED_TO_CREATE_RELEASE.format(e)
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = GitHubErrors.FAILED_TO_CREATE_RELEASE.format(
                    error_data.get("message", str(e))
                )
            except Exception:  # nosec B110 - Fallback to generic error if JSON parsing fails
                pass
        raise GitHubOperationError(error_msg) from e
    except Exception as e:
        raise GitHubOperationError(GitHubErrors.FAILED_TO_CREATE_RELEASE.format(e)) from e


def get_current_branch(repo_path: str | None = None) -> str:
    """Get the current git branch name.

    Args:
        repo_path: Path to repository (default: current directory)

    Returns:
        Current branch name

    Raises:
        GitHubOperationError: If unable to determine branch
    """
    try:
        import subprocess  # nosec B404 - Safe: only calls git with controlled args

        cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        if repo_path:
            cmd = ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"]

        result = subprocess.run(  # nosec B603 - Safe: controlled git command
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception as e:
        raise GitHubOperationError(GitHubErrors.FAILED_TO_GET_BRANCH.format(e)) from e
