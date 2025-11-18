from __future__ import annotations

import json
import logging
from typing import Any

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
from cli.context_resolver import ContextResolutionError, format_resolution_log, resolve_pr_context
from cli.errors import CommandErrors
from cli.github_client import fetch_pr_data

# Import create command from separate module
from smooth.commands import pr_create

app = typer.Typer(help="Pull Request utilities (API-first)", rich_markup_mode=None)

# Register create command
app.command(name="create")(pr_create.create)


def _show_context_resolution(ctx: Any, verbose: bool) -> None:
    """Display context resolution details if verbose mode is enabled."""
    if verbose:
        typer.echo("📋 Context Resolution:", err=True)
        for line in format_resolution_log(ctx):
            typer.echo(f"  {line}", err=True)
        typer.echo("", err=True)


def _fetch_pr_data_with_logging(
    owner: str, repo: str, pr_number: int, verbose: bool
) -> dict[str, Any]:
    """Fetch PR data from GitHub with optional logging."""
    if verbose:
        typer.echo("Fetching PR data from GitHub...", err=True)
    try:
        return fetch_pr_data(owner, repo, pr_number)
    except Exception as e:
        typer.echo(f"Error fetching PR data: {e}", err=True)
        raise typer.Exit(code=1) from e


def _generate_pr_content(
    pr_data: dict[str, Any],
    pr_number: int,
    gen_title: bool,
    gen_summary: bool,
    verbose: bool,
    skip_judging: bool = False,
) -> tuple[str, str]:
    """Generate PR title and/or summary based on flags.

    Returns:
        Tuple of (title_text, summary_text)
    """
    title_text = ""
    summary_text = ""

    if gen_title:
        if verbose:
            typer.echo("Generating PR title...", err=True)
            if skip_judging:
                typer.echo("  ⚠️  Skipping quality judging (faster, lower quality)", err=True)
        title_res = api.generate_pr_title(
            payload=pr_data, pr_number=pr_number, skip_judging=skip_judging
        )
        title_text = title_res.get("generated_text", title_res.get("text", ""))

    if gen_summary:
        if verbose:
            typer.echo("Generating PR summary...", err=True)
            if skip_judging:
                typer.echo("  ⚠️  Skipping quality judging (faster, lower quality)", err=True)
        summary_res = api.generate_pr_summary(payload=pr_data, skip_judging=skip_judging)
        summary_text = summary_res.get("generated_text", summary_res.get("text", ""))

    return title_text, summary_text


def _output_pr_content(
    title_text: str,
    summary_text: str,
    gen_title: bool,
    gen_summary: bool,
    output_format: str,
) -> None:
    """Output PR content in the specified format."""
    if output_format.lower() == "json":
        import json as _json

        typer.echo(
            _json.dumps(
                {
                    "title": title_text,
                    "summary": summary_text,
                },
                indent=2,
            )
        )
    else:
        # Clean text output with clear section headers
        if gen_title and title_text:
            typer.echo("PR TITLE:")
            typer.echo(title_text)
        if gen_summary and summary_text:
            if gen_title:
                typer.echo("")  # Blank line between sections
            typer.echo("PR SUMMARY:")
            typer.echo(summary_text)


def _truncate_title_if_needed(title: str, verbose: bool) -> str:
    """Truncate title if it exceeds GitHub's limit (256 chars)."""
    max_title_length = 250  # Leave buffer for safety
    if len(title) > max_title_length:
        if verbose:
            typer.echo(
                f"⚠️  Warning: Title exceeds {max_title_length} characters, truncating...",
                err=True,
            )
        return title[:max_title_length].rstrip() + "..."
    return title


def _push_to_github(
    owner: str,
    repo: str,
    pr_number: int,
    title_text: str,
    summary_text: str,
    gen_title: bool,
    gen_summary: bool,
    verbose: bool,
) -> None:
    """Push generated content to GitHub."""
    # Truncate title if needed
    if gen_title and title_text:
        title_text = _truncate_title_if_needed(title_text, verbose)
        if verbose:
            typer.echo("Updating PR title on GitHub...", err=True)
        gh.update_pull_request(owner, repo, pr_number, title=title_text)

    if gen_summary and summary_text:
        if verbose:
            typer.echo("Updating PR summary on GitHub...", err=True)
        gh.update_pull_request(owner, repo, pr_number, body=summary_text)

    if verbose:
        typer.echo("✅ Successfully updated PR on GitHub", err=True)


@app.command()
def title(
    base: str | None = typer.Option(None, help="Base ref (e.g., main)"),
    head: str | None = typer.Option(None, help="Head ref (e.g., branch)"),
    output: str = typer.Option("text", help="Output format: text or json"),
    push: bool = typer.Option(False, "--push", help="Update PR title on GitHub"),
    owner: str | None = typer.Option(None, help="GitHub owner/org (required with --push)"),
    repo: str | None = typer.Option(None, help="GitHub repo (required with --push)"),
    pr_number: int | None = typer.Option(None, help="Pull request number (required with --push)"),
) -> None:
    result = api.generate_pr_title(
        owner=owner, repo=repo, pr_number=pr_number, base=base, head=head
    )
    if output.lower() == "json":
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(result.get("title", ""))
    if push:
        if not (owner and repo and pr_number):
            raise typer.BadParameter(CommandErrors.PUSH_REQUIRES_PARAMS)
        gh.update_pull_request(owner, repo, pr_number, title=str(result.get("title", "")))


@app.command()
def summary(
    base: str | None = typer.Option(None, help="Base ref (e.g., main)"),
    head: str | None = typer.Option(None, help="Head ref (e.g., branch)"),
    output: str = typer.Option("text", help="Output format: text or json"),
    push: bool = typer.Option(False, "--push", help="Update PR body on GitHub"),
    owner: str | None = typer.Option(None, help="GitHub owner/org (required with --push)"),
    repo: str | None = typer.Option(None, help="GitHub repo (required with --push)"),
    pr_number: int | None = typer.Option(None, help="Pull request number (required with --push)"),
) -> None:
    result = api.generate_pr_summary(
        owner=owner, repo=repo, pr_number=pr_number, base=base, head=head
    )
    if output.lower() == "json":
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(result.get("summary", ""))
    if push:
        if not (owner and repo and pr_number):
            raise typer.BadParameter(CommandErrors.PUSH_REQUIRES_PARAMS)
        gh.update_pull_request(owner, repo, pr_number, body=str(result.get("summary", "")))


@app.command()
def generate(
    base: str | None = typer.Option(None, help="Base ref (e.g., main)"),  # noqa: ARG001
    head: str | None = typer.Option(None, help="Head ref (e.g., branch)"),  # noqa: ARG001
    output: str | None = typer.Option(None, help="Output format: text or json"),
    owner: str | None = typer.Option(None, help="Repository owner (auto-detected from git)"),
    repo: str | None = typer.Option(None, help="Repository name (auto-detected from git)"),
    pr_number: int | None = typer.Option(None, help="PR number"),
    push: bool = typer.Option(False, help="Push generated content to GitHub"),
    verbose: bool | None = typer.Option(
        None, "--verbose", "-v", help="Show detailed progress messages"
    ),
    title: bool = typer.Option(False, "--title", help="Generate PR title"),
    summary: bool = typer.Option(False, "--summary", help="Generate PR summary"),
    skip_judging: bool = typer.Option(
        False,
        "--skip-judging",
        help="Skip quality judging for faster generation (use for very large PRs)",
    ),
) -> None:
    """Generate PR title and/or summary. By default, generates both.

    Smart defaults are applied in this order:
    1. CLI flags (highest priority)
    2. Git context (auto-detected)
    3. Repository config (.smoothdev.json)
    4. User config (~/.smoothdevio/config.json)
    """
    # Resolve context using four-tier precedence
    try:
        ctx = resolve_pr_context(
            cli_owner=owner,
            cli_repo=repo,
            cli_pr_number=pr_number,
            cli_output=output,
            cli_verbose=verbose,
        )
    except ContextResolutionError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    # Show resolution details if verbose
    _show_context_resolution(ctx, ctx.verbose)

    # Require PR number
    if not ctx.pr_number:
        raise typer.BadParameter(CommandErrors.PR_NUMBER_REQUIRED)

    # Fetch PR data from GitHub
    pr_data = _fetch_pr_data_with_logging(ctx.owner, ctx.repo, ctx.pr_number, ctx.verbose)

    # Default behavior: both if neither flag provided
    gen_title = title or (not title and not summary)
    gen_summary = summary or (not title and not summary)

    # Generate content
    title_text, summary_text = _generate_pr_content(
        pr_data, ctx.pr_number, gen_title, gen_summary, ctx.verbose, skip_judging
    )

    # Output content
    _output_pr_content(title_text, summary_text, gen_title, gen_summary, ctx.output)

    # Push to GitHub if requested
    if push:
        _push_to_github(
            ctx.owner,
            ctx.repo,
            ctx.pr_number,
            title_text,
            summary_text,
            gen_title,
            gen_summary,
            ctx.verbose,
        )
