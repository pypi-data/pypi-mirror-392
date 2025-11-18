from __future__ import annotations

from pathlib import Path
from typing import Any, NoReturn

import git
import typer

from cli import api_client as api
from cli.config_manager import load_repository_config, load_user_config, merge_configs
from cli.git_commit import (
    GitCommitError,
    InvalidRepositoryError,
    NoStagedChangesError,
    commit_staged_changes,
    find_git_root,
    validate_commit_message,
)

# Error message constants
COMPARE_PARSE_ERROR = "--compare must contain '..' or '...' e.g., main..feature"
COMPARE_USAGE_ERROR = "--compare must be in the form base..head (or base...head)"
REPO_USAGE_ERROR = "--repo must be in the form owner/repo"
GIT_REPO_ERROR = (
    "Unable to determine git repository. Run from within a repo or provide --repo/--compare."
)
NO_STAGED_ERROR = "No staged changes detected. Stage files (git add) or provide --repo/--compare."


def _invalid_compare() -> NoReturn:
    msg = COMPARE_PARSE_ERROR
    raise ValueError(msg)


def _parse_compare(compare: str) -> tuple[str, str]:
    if "..." in compare:
        a, b = compare.split("...", 1)
        return (a, b)
    if ".." in compare:
        a, b = compare.split("..", 1)
        return (a, b)
    _invalid_compare()
    raise ValueError(COMPARE_PARSE_ERROR)


def _split_owner_repo_slug(slug: str) -> tuple[str, str]:
    owner, repo_name = slug.split("/", 1)
    return owner, repo_name


def _generate_from_compare(
    repo: str, compare: str, issue: str | None, latency_profile: str
) -> dict[str, Any]:
    try:
        base, head = _parse_compare(compare)
    except ValueError as e:
        _die(COMPARE_USAGE_ERROR, e)
    try:
        owner_name2, repo_name2 = _split_owner_repo_slug(repo or "")
    except ValueError as e:
        _die(REPO_USAGE_ERROR, e)
    detected_issue2 = issue or _detect_issue_from_branch(head)
    return api.suggest_commit_message(
        payload={
            "owner": owner_name2,
            "repo": repo_name2,
            "base": base,
            "head": head,
            "issue": detected_issue2,
            "latency_profile": latency_profile,
        }
    )


def _generate_from_staged(issue: str | None, latency_profile: str) -> dict[str, Any]:
    # Detect repository; only map repository-related failures to the repo error message.
    try:
        repo_obj, head = _get_repo_and_head(None)
    except (git.InvalidGitRepositoryError, git.NoSuchPathError, git.GitError) as err:
        _die(GIT_REPO_ERROR, err)

    # Compute staged diff outside of the repo detection try/except so Typer.Exit is not masked.
    staged_diff, files_changed = _get_staged(repo_obj)
    detected_issue = issue or _detect_issue_from_branch(head)
    if not staged_diff or not any(files_changed):
        _die(NO_STAGED_ERROR)
    return api.suggest_commit_message(
        payload={
            "diff": staged_diff,
            "head": head,
            "issue": detected_issue,
            "latency_profile": latency_profile,
        }
    )


# (imports and constants moved to top)


def _detect_issue_from_branch(head: str | None) -> str | None:
    try:
        import re as _re

        if head:
            m = _re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", str(head))
            if m:
                return m.group(1)
            m2 = _re.search(r"\b(?:gh|issue|fix|bug|task)[-/]?(\d+)\b", str(head), _re.I)
            if m2:
                return f"#{m2.group(1)}"
    except Exception:
        return None
    return None


def _get_repo_and_head(head: str | None) -> tuple[git.Repo, str | None]:
    repo_obj = git.Repo(Path.cwd(), search_parent_directories=True)
    current_head = head or repo_obj.git.rev_parse("--abbrev-ref", "HEAD") or None
    return repo_obj, current_head


def _get_staged(repo_obj: git.Repo) -> tuple[str, list[str]]:
    staged_diff = repo_obj.git.diff("--cached")
    files_changed = repo_obj.git.diff("--cached", "--name-only").splitlines()
    return staged_diff, [f for f in files_changed if f]


def _die(msg: str, err: Exception | None = None) -> None:
    typer.echo(msg, err=True)
    if err is not None:
        raise typer.Exit(code=1) from err
    raise typer.Exit(code=1)


app = typer.Typer(help="Commit message utilities (API-first)")


@app.command("generate")
def generate(
    repo: str | None = typer.Option(
        None, help="Repository slug as owner/repo (use with --compare)"
    ),
    compare: str | None = typer.Option(
        None, help="Compare range as base..head or base...head (server mode)"
    ),
    issue: str | None = typer.Option(
        None,
        help=(
            "Issue reference (e.g., PROJ-123 or #123). If omitted, will try to detect "
            "from branch or head ref"
        ),
    ),
    output: str = typer.Option("text", help="Output format: text or json"),
    latency_profile: str = typer.Option(
        "fast", help="Latency profile: fast, low_latency, or quality"
    ),
    commit: bool = typer.Option(
        False,
        "--commit",
        help="Automatically commit staged changes with generated message (opt-in)",
    ),
) -> None:
    """Generate a Conventional Commit message using the backend API.

    By default, generates and prints the commit message.
    Use --commit flag to automatically commit staged changes (requires staged files).
    """

    # Load config to check auto_commit setting
    user_config = load_user_config()
    repo_config = load_repository_config()
    merged_config = merge_configs(user_config, repo_config)

    # Determine if we should auto-commit (flag takes precedence over config)
    should_commit = commit or merged_config.get("auto_commit", False)

    # If server-mode coordinates are provided, use them; otherwise use staged diff
    if repo and compare:
        result = _generate_from_compare(repo, compare, issue, latency_profile)
    else:
        result = _generate_from_staged(issue, latency_profile)

    if output.lower() == "json":
        import json

        typer.echo(json.dumps(result, indent=2))
        return

    # Try different response field names (API may return different formats)
    # Priority: message > commit_message > subject/body  # noqa: ERA001
    full_message = str(result.get("message") or result.get("commit_message") or "").strip()
    if not full_message:
        # Fallback to subject/body fields
        subject = str(result.get("subject", ""))
        body = str(result.get("body", ""))
        if subject:
            full_message = subject
            if body:
                full_message += "\n\n" + body

    if not full_message:
        typer.echo("Error: No commit message generated", err=True)
        raise typer.Exit(code=1)

    # Handle auto-commit if enabled
    if should_commit:
        # Cannot auto-commit in server mode (no local repo)
        if repo and compare:
            typer.echo(
                "⚠️  Warning: --commit flag ignored in server mode (--repo/--compare)", err=True
            )
            typer.echo(full_message)
            return

        try:
            # Find git repository root
            git_root = find_git_root()

            # Validate the message
            validate_commit_message(full_message)

            # Perform the commit
            commit_sha = commit_staged_changes(git_root, full_message)

            typer.echo(f"✅ Committed successfully: {commit_sha[:8]}")
            typer.echo("")
            typer.echo(full_message)

        except NoStagedChangesError as e:
            typer.echo(
                "⚠️  No staged changes to commit. Stage files with 'git add' first.", err=True
            )
            typer.echo("")
            typer.echo("Generated message:")
            typer.echo(full_message)
            raise typer.Exit(code=1) from e

        except InvalidRepositoryError as e:
            typer.echo(f"❌ {e}", err=True)
            typer.echo("")
            typer.echo("Generated message:")
            typer.echo(full_message)
            raise typer.Exit(code=1) from e

        except GitCommitError as e:
            typer.echo(f"❌ Commit failed: {e}", err=True)
            typer.echo("")
            typer.echo("Generated message:")
            typer.echo(full_message)
            raise typer.Exit(code=1) from e

    else:
        # Just print the message
        typer.echo(full_message)
