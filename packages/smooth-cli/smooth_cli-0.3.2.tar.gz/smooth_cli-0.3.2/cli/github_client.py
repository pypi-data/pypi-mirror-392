"""GitHub API client for fetching PR data."""

from __future__ import annotations

import logging
import os
import subprocess  # nosec B404 - Safe: only calls gh CLI with hardcoded args
from http import HTTPStatus
from typing import Any

import requests

logger = logging.getLogger(__name__)


def _get_github_token() -> str | None:
    """Get GitHub token from environment or gh CLI."""
    # Try environment variable first
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token

    # Try gh CLI
    try:
        result = subprocess.run(  # nosec B603, B607 - Safe: hardcoded gh CLI command
            ["gh", "auth", "token"],  # noqa: S603, S607
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


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""


def fetch_pr_data(owner: str, repo: str, pr_number: int) -> dict[str, Any]:
    """Fetch PR data from GitHub API.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        Dict with title, body, commits, files, and diff

    Raises:
        GitHubAPIError: If GitHub API request fails
    """
    token = _get_github_token()
    if not token:
        msg = (
            "GitHub token not found. Set GITHUB_TOKEN environment variable "
            "or authenticate with 'gh auth login'"
        )
        raise GitHubAPIError(msg)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    base_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

    # Fetch PR details
    pr_resp = requests.get(base_url, headers=headers, timeout=30)
    pr_resp.raise_for_status()
    pr_data = pr_resp.json()

    # Fetch commits (paginate to include all commits)
    commits_data: list[dict[str, Any]] = []
    page = 1
    per_page = 100
    while True:
        resp = requests.get(
            f"{base_url}/commits",
            headers=headers,
            params={"per_page": per_page, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        page_items = resp.json()
        if not isinstance(page_items, list):
            break
        commits_data.extend(page_items)
        if len(page_items) < per_page:
            break
        page += 1

    # Fetch files (paginate to include all files)
    files_data: list[dict[str, Any]] = []
    page = 1
    while True:
        resp = requests.get(
            f"{base_url}/files",
            headers=headers,
            params={"per_page": per_page, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        page_items = resp.json()
        if not isinstance(page_items, list):
            break
        files_data.extend(page_items)
        if len(page_items) < per_page:
            break
        page += 1

    # Format commits for backend
    commits = [
        {
            "sha": commit["sha"],
            "message": commit["commit"]["message"],
            "author": commit["commit"]["author"]["name"],
            "date": commit["commit"]["author"]["date"],
        }
        for commit in commits_data
    ]

    # Format files for backend
    files = [
        {
            "filename": file["filename"],
            "status": file["status"],
            "additions": file["additions"],
            "deletions": file["deletions"],
            "changes": file["changes"],
            "patch": file.get("patch", ""),
        }
        for file in files_data
    ]

    # Construct full diff from file patches
    diff_parts: list[str] = []
    for file in files_data:
        if "patch" in file:
            diff_parts.append(f"diff --git a/{file['filename']} b/{file['filename']}")
            diff_parts.append(file.get("patch", ""))
    diff = "\n".join(diff_parts)

    return {
        "title": pr_data["title"],
        "body": pr_data["body"] or "",
        "commits": commits,
        "files": files,
        "diff": diff,
    }


def _fetch_pr_files(base_url: str, pr_number: int, headers: dict[str, str]) -> list[dict[str, Any]]:
    """Fetch files changed in a PR."""
    try:
        files_resp = requests.get(
            f"{base_url}/pulls/{pr_number}/files", headers=headers, timeout=30
        )
        if files_resp.status_code == HTTPStatus.OK:
            files_data = files_resp.json()
            return [
                {
                    "filename": f["filename"],
                    "status": f["status"],
                    "additions": f["additions"],
                    "deletions": f["deletions"],
                    "changes": f["changes"],
                }
                for f in files_data
            ]
    except Exception as e:
        logger.debug("Failed to fetch PR files: %s", e)
    return []


def _fetch_pr_summary(base_url: str, pr_number: int, headers: dict[str, str]) -> str | None:
    """Fetch generated PR summary from comments."""
    try:
        comments_resp = requests.get(
            f"{base_url}/issues/{pr_number}/comments", headers=headers, timeout=30
        )
        if comments_resp.status_code == HTTPStatus.OK:
            comments = comments_resp.json()
            for comment in comments:
                body = comment.get("body", "")
                if isinstance(body, str) and (
                    "Generated by: *Smoothdev.io*" in body
                    or "**Generated_by:** **Smoothdev.io**" in body
                ):
                    return body
    except Exception as e:
        logger.debug("Failed to fetch PR summary: %s", e)
    return None


def _fetch_merged_prs(
    base_url: str,
    from_ref: str,
    commit_shas: set[str],
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    """Fetch merged PRs between refs."""
    # Extract owner/repo from base_url
    # base_url format: https://api.github.com/repos/{owner}/{repo}
    parts = base_url.split("/")
    owner, repo = parts[-2], parts[-1]

    prs = []
    try:
        # Get the dates of the refs to filter PRs
        from_date_resp = requests.get(f"{base_url}/commits/{from_ref}", headers=headers, timeout=30)
        from_date_resp.raise_for_status()
        from_date = from_date_resp.json()["commit"]["author"]["date"]

        # Search for merged PRs after from_date
        search_url = f"https://api.github.com/search/issues?q=repo:{owner}/{repo}+type:pr+is:merged+merged:>={from_date}&sort=created&order=asc&per_page=100"
        search_resp = requests.get(search_url, headers=headers, timeout=30)
        search_resp.raise_for_status()
        search_data = search_resp.json()

        # Filter PRs to only those whose merge commit is in our commit range
        for pr in search_data.get("items", []):
            pr_detail_resp = requests.get(
                f"{base_url}/pulls/{pr['number']}", headers=headers, timeout=30
            )
            if pr_detail_resp.status_code == HTTPStatus.OK:
                pr_detail = pr_detail_resp.json()
                merge_commit_sha = pr_detail.get("merge_commit_sha")

                if merge_commit_sha and merge_commit_sha in commit_shas:
                    pr_number = pr["number"]
                    files = _fetch_pr_files(base_url, pr_number, headers)
                    generated_summary = _fetch_pr_summary(base_url, pr_number, headers)

                    prs.append(
                        {
                            "number": pr_number,
                            "title": pr["title"],
                            "body": pr.get("body", ""),
                            "author": pr.get("user", {}).get("login", "Unknown"),
                            "merged_at": pr.get("pull_request", {}).get("merged_at"),
                            "labels": [label["name"] for label in pr.get("labels", [])],
                            "files": files,
                            "generated_summary": generated_summary,
                        }
                    )
    except Exception as e:
        logger.warning("Failed to fetch PRs: %s", e)
    return prs


def fetch_release_data(
    owner: str,
    repo: str,
    from_ref: str,
    to_ref: str | None = None,
) -> dict[str, Any]:
    """
    Fetch release data between two refs (tags or commits).

    Following SoC principle: This function only fetches data from GitHub,
    doesn't know about backend or generation logic.

    Args:
        owner: Repository owner
        repo: Repository name
        from_ref: Starting ref (tag or commit)
        to_ref: Ending ref (tag or commit), defaults to HEAD

    Returns:
        Dictionary with:
            - version: Target version (from to_ref)
            - from_ref: Starting ref
            - to_ref: Ending ref
            - prs: List of merged PRs between refs
            - commits: List of commits between refs
    """
    token = _get_github_token()
    if not token:
        msg = "GitHub token not found"
        raise GitHubAPIError(msg)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    to_ref = to_ref or "HEAD"

    # Fetch commits between refs
    compare_url = f"{base_url}/compare/{from_ref}...{to_ref}"
    compare_resp = requests.get(compare_url, headers=headers, timeout=30)
    compare_resp.raise_for_status()
    compare_data = compare_resp.json()

    # Format commits
    commits = [
        {
            "sha": commit["sha"],
            "message": commit["commit"]["message"],
            "author": commit["commit"]["author"]["name"],
            "date": commit["commit"]["author"]["date"],
        }
        for commit in compare_data.get("commits", [])
    ]

    # Build a set of commit SHAs for PR filtering
    commit_shas = {commit["sha"] for commit in compare_data.get("commits", [])}

    # Fetch merged PRs between refs
    prs = _fetch_merged_prs(base_url, from_ref, commit_shas, headers)

    return {
        "version": to_ref,
        "from_ref": from_ref,
        "to_ref": to_ref,
        "prs": prs,
        "commits": commits,
    }
