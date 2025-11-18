from __future__ import annotations

import sys
from http import HTTPStatus
from pathlib import Path
from typing import Any, cast

import git
import requests

from .api_client import _api_base_url
from .auth import get_auth_header

# API Configuration
API_URL = _api_base_url()


def analyze_repository(
    repo_path: str,
    output_format: str = "text",
    api_key: str | None = None,
) -> dict[str, Any]:
    """Analyze a Git repository for missing and outdated README files."""
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        # match behavior of legacy functions: print and exit(1)
        sys.stderr.write(f"Error: {repo_path} is not a valid Git repository\n")
        raise SystemExit(1)

    try:
        git_url = repo.remotes.origin.url
    except AttributeError:
        git_url = "local-repository"

    branch = repo.git.rev_parse("--abbrev-ref", "HEAD")

    auth_header = get_auth_header(api_key=api_key)
    payload = {"repo_path": repo_path, "git_url": git_url, "branch": branch}
    response = requests.post(
        f"{API_URL}/analyze",
        json=payload,
        headers=auth_header,
        timeout=30,
    )
    if response.status_code != HTTPStatus.OK:
        sys.stderr.write(f"Error analyzing repository: {response.text}\n")
        raise SystemExit(1)

    result = cast("dict[str, Any]", response.json())
    if output_format == "json":
        return result
    return result


essentially_text = str


def generate_documentation(
    repo_path: str,
    directory: str,
    overwrite: bool = False,
    api_key: str | None = None,
) -> str:
    """Generate README documentation for a repository directory."""
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        sys.stderr.write(f"Error: {repo_path} is not a valid Git repository\n")
        raise SystemExit(1)

    try:
        git_url = repo.remotes.origin.url
    except AttributeError:
        git_url = "local-repository"

    branch = repo.git.rev_parse("--abbrev-ref", "HEAD")

    auth_header = get_auth_header(api_key=api_key)
    payload = {"repo_path": repo_path, "git_url": git_url, "branch": branch, "directory": directory}
    response = requests.post(
        f"{API_URL}/generate",
        json=payload,
        headers=auth_header,
        timeout=60,
    )
    if response.status_code != HTTPStatus.OK:
        sys.stderr.write(f"Error generating documentation: {response.text}\n")
        raise SystemExit(1)

    result = cast("dict[str, Any]", response.json())
    content = cast("str", result.get("content", ""))

    if content:
        readme_path = Path(repo_path) / directory / "README.md"
        readme_dir = readme_path.parent
        if readme_path.exists() and not overwrite:
            sys.stdout.write(
                f"README.md already exists at {readme_path}. Use --overwrite to replace it.\n"
            )
        else:
            if readme_dir and not readme_dir.exists():
                readme_dir.mkdir(parents=True)
            with readme_path.open("w") as f:
                f.write(content)
            sys.stdout.write(f"README.md generated at {readme_path}\n")

    return content


def submit_feedback(
    repo_path: str,
    directory: str,
    generation_id: str,
    rating: int,
    feedback: str,
) -> dict[str, Any]:
    """Submit feedback for generated documentation."""
    auth_header = get_auth_header()
    payload = {
        "repo_path": repo_path,
        "directory": directory,
        "generation_id": generation_id,
        "rating": rating,
        "feedback": feedback,
    }
    response = requests.post(
        f"{API_URL}/feedback",
        json=payload,
        headers=auth_header,
        timeout=30,
    )
    if response.status_code != HTTPStatus.OK:
        sys.stderr.write(f"Error submitting feedback: {response.text}\n")
        raise SystemExit(1)
    return cast("dict[str, Any]", response.json())
