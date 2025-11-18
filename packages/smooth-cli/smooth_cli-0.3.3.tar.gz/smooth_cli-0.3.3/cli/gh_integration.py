from __future__ import annotations

import os
import subprocess  # nosec B404 - Safe: only calls gh CLI with hardcoded args
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

import requests
from click import ClickException


def _gh_token() -> str:
    """Get GitHub token from environment or gh CLI."""
    # Try environment variable first
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok

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

    msg = (
        "GitHub token not found. Set GITHUB_TOKEN or GH_TOKEN environment variable, "
        "or authenticate with 'gh auth login'."
    )
    raise ClickException(msg)


def _headers() -> Mapping[str, str]:
    return {
        "Authorization": f"Bearer {_gh_token()}",
        "Accept": "application/vnd.github+json",
    }


def update_pull_request(
    owner: str, repo: str, pr_number: int, *, title: str | None = None, body: str | None = None
) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    payload: dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if not payload:
        msg = "Nothing to update: provide title and/or body"
        raise ClickException(msg)
    resp = requests.patch(url, json=payload, headers=_headers(), timeout=30)
    if resp.status_code >= HTTPStatus.MULTIPLE_CHOICES:
        msg = f"GitHub API error {resp.status_code}: {resp.text}"
        raise ClickException(msg)
    return cast("dict[str, Any]", resp.json())


def create_or_update_release(
    owner: str,
    repo: str,
    tag: str,
    *,
    name: str | None = None,
    body: str | None = None,
    draft: bool = False,
    prerelease: bool = False,
) -> dict[str, Any]:
    # Try to get release by tag
    get_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
    resp = requests.get(get_url, headers=_headers(), timeout=30)
    if resp.status_code == HTTPStatus.OK:
        rel = resp.json()
        edit_url = rel.get("url")
        if not edit_url:
            msg = "Unexpected GitHub response: missing release url"
            raise ClickException(msg)
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if body is not None:
            payload["body"] = body
        payload["draft"] = draft
        payload["prerelease"] = prerelease
        edit = requests.patch(edit_url, json=payload, headers=_headers(), timeout=30)
        if edit.status_code >= HTTPStatus.MULTIPLE_CHOICES:
            msg = f"GitHub API error {edit.status_code}: {edit.text}"
            raise ClickException(msg)
        return cast("dict[str, Any]", edit.json())
    if resp.status_code == HTTPStatus.NOT_FOUND:
        create_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        payload = {
            "tag_name": tag,
            "name": name or tag,
            "body": body or "",
            "draft": draft,
            "prerelease": prerelease,
        }
        create = requests.post(create_url, json=payload, headers=_headers(), timeout=30)
        if create.status_code >= HTTPStatus.MULTIPLE_CHOICES:
            msg = f"GitHub API error {create.status_code}: {create.text}"
            raise ClickException(msg)
        return cast("dict[str, Any]", create.json())
    msg = f"GitHub API error {resp.status_code}: {resp.text}"
    raise ClickException(msg)
