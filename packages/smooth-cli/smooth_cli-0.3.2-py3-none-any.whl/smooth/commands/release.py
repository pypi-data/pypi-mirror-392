from __future__ import annotations

import logging

import typer

# Force fallback to non-rich help formatting to avoid environment-dependent differences
try:  # pragma: no cover - environment dependent
    import typer as _typer

    if hasattr(_typer, "rich_utils"):
        _typer.rich_utils = None  # type: ignore[attr-defined]
except (ImportError, AttributeError) as _e:  # narrow and log for security tooling
    logging.debug("Typer rich utils disable not applied: %s", _e)

from cli import api_client as api
from cli import gh_integration as gh
from cli.context_resolver import (
    ContextResolutionError,
    format_resolution_log,
    resolve_release_context,
)
from cli.git_commit import find_git_root
from cli.git_tag import (
    GitTagError,
    InvalidTagNameError,
    TagExistsError,
    create_tag,
    push_tag,
)
from cli.github_client import fetch_release_data

app = typer.Typer(help="Release notes utilities (API-first)", rich_markup_mode=None)


@app.command()
def generate(
    owner: str | None = typer.Option(None, help="GitHub owner/org (auto-detected from git)"),
    repo: str | None = typer.Option(None, help="GitHub repo (auto-detected from git)"),
    from_tag: str | None = typer.Option(None, help="Starting tag/ref"),
    to_tag: str | None = typer.Option(None, help="Ending tag/ref (default: HEAD)"),
    output: str | None = typer.Option(None, help="Output format: text or json"),
    verbose: bool | None = typer.Option(
        None, "--verbose", "-v", help="Show detailed progress messages"
    ),
    push: bool = typer.Option(False, "--push", help="Create/update GitHub release"),
    tag: str | None = typer.Option(None, help="Release tag (required with --push)"),
    name: str | None = typer.Option(None, help="Release name override"),
    draft: bool = typer.Option(False, help="Create as draft release"),
    prerelease: bool = typer.Option(False, help="Mark as prerelease"),
    skip_judging: bool = typer.Option(
        False,
        "--skip-judging",
        help="Skip quality judging for faster generation (use for very large releases)",
    ),
) -> None:
    """
    Generate release notes between two refs.

    Smart defaults are applied in this order:
    1. CLI flags (highest priority)
    2. Git context (auto-detected)
    3. Repository config (.smoothdev.json)
    4. User config (~/.smoothdevio/config.json)
    """
    # Resolve context using four-tier precedence
    try:
        ctx = resolve_release_context(
            cli_owner=owner,
            cli_repo=repo,
            cli_from_tag=from_tag,
            cli_to_tag=to_tag,
            cli_output=output,
            cli_verbose=verbose,
        )
    except ContextResolutionError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    # Show resolution details if verbose
    if ctx.verbose:
        typer.echo("📋 Context Resolution:", err=True)
        for line in format_resolution_log(ctx):
            typer.echo(f"  {line}", err=True)
        typer.echo("", err=True)

    # Require from_tag (should be auto-detected or provided)
    if not ctx.from_tag:
        msg = (
            "Starting tag/ref could not be determined. "
            "Provide --from-tag flag or ensure repository has tags."
        )
        raise typer.BadParameter(msg)

    if ctx.verbose:
        typer.echo("Fetching release data from GitHub...", err=True)

    # Fetch release data (PRs and commits between refs)
    release_data = fetch_release_data(ctx.owner, ctx.repo, ctx.from_tag, ctx.to_tag)

    if ctx.verbose:
        typer.echo("Generating release notes...", err=True)
        if skip_judging:
            typer.echo("  ⚠️  Skipping quality judging (faster, lower quality)", err=True)

    # Call API with encoded payload (consistent with PR generation)
    result = api.generate_release_notes(payload=release_data, skip_judging=skip_judging)

    # Output handling (consistent with PR generation)
    if ctx.output.lower() == "json":
        import json as _json

        typer.echo(_json.dumps(result, indent=2))
    else:
        # Use generated_text key (consistent with backend response)
        typer.echo(result.get("generated_text", result.get("notes", "")))

    # Push to GitHub if requested
    if push:
        if not tag:
            msg = "--push requires --tag"
            raise typer.BadParameter(msg)
        if ctx.verbose:
            typer.echo("Creating/updating GitHub release...", err=True)
        gh.create_or_update_release(
            ctx.owner,
            ctx.repo,
            tag,
            name=name or tag,
            body=str(result.get("generated_text", result.get("notes", ""))),
            draft=draft,
            prerelease=prerelease,
        )
        if ctx.verbose:
            typer.echo("✅ Successfully created/updated release on GitHub", err=True)


@app.command()
def tag_create(
    tag_name: str = typer.Argument(..., help="Tag name to create"),
    message: str | None = typer.Option(
        None, "-m", "--message", help="Tag message (for annotated tags)"
    ),
    commit: str | None = typer.Option(
        None, "-c", "--commit", help="Commit SHA to tag (default: HEAD)"
    ),
    push: bool = typer.Option(False, "--push", help="Push tag to remote after creation"),
    remote: str = typer.Option("origin", help="Remote name for push"),
    lightweight: bool = typer.Option(
        False, "--lightweight", help="Create lightweight tag (default: annotated)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
) -> None:
    """
    Create a git tag locally (and optionally push to remote).

    Examples:
        smooth release tag-create v1.0.0
        smooth release tag-create v1.0.0 --push
        smooth release tag-create v1.0.0 -m "Release 1.0.0" --push
    """
    try:
        # Find git root
        repo_path = find_git_root()

        if verbose:
            typer.echo(f"📂 Repository: {repo_path}", err=True)
            typer.echo(f"🏷️  Creating tag: {tag_name}", err=True)

        # Create tag
        created_tag = create_tag(
            repo_path=repo_path,
            tag_name=tag_name,
            message=message,
            commit_sha=commit,
            annotated=not lightweight,
        )

        typer.echo(f"✅ Created {'lightweight' if lightweight else 'annotated'} tag: {created_tag}")

        # Push if requested
        if push:
            if verbose:
                typer.echo(f"📤 Pushing tag to {remote}...", err=True)

            push_tag(repo_path=repo_path, tag_name=tag_name, remote=remote)
            typer.echo(f"✅ Pushed tag '{tag_name}' to {remote}")

    except TagExistsError as e:
        typer.echo(f"❌ Tag already exists: {e}", err=True)
        raise typer.Exit(code=1) from e
    except InvalidTagNameError as e:
        typer.echo(f"❌ Invalid tag name: {e}", err=True)
        raise typer.Exit(code=1) from e
    except GitTagError as e:
        typer.echo(f"❌ Tag operation failed: {e}", err=True)
        raise typer.Exit(code=1) from e


@app.command()
def notes(
    owner: str | None = typer.Option(None, help="GitHub owner/org (auto-detected from git)"),
    repo: str | None = typer.Option(None, help="GitHub repo (auto-detected from git)"),
    from_tag: str | None = typer.Option(None, help="Starting tag/ref"),
    to_tag: str | None = typer.Option(None, help="Ending tag/ref (default: HEAD)"),
    output: str | None = typer.Option(None, help="Output format: text or json"),
    verbose: bool | None = typer.Option(
        None, "--verbose", "-v", help="Show detailed progress messages"
    ),
    push: bool = typer.Option(False, "--push", help="Create/update GitHub release"),
    tag: str | None = typer.Option(None, help="Release tag (required with --push)"),
    name: str | None = typer.Option(None, help="Release name override"),
    draft: bool = typer.Option(False, help="Create as draft release"),
    prerelease: bool = typer.Option(False, help="Mark as prerelease"),
) -> None:
    """Alias for 'generate' command (deprecated - use 'generate' instead)."""
    generate(
        owner=owner,
        repo=repo,
        from_tag=from_tag,
        to_tag=to_tag,
        output=output,
        verbose=verbose,
        push=push,
        tag=tag,
        name=name,
        draft=draft,
        prerelease=prerelease,
    )
