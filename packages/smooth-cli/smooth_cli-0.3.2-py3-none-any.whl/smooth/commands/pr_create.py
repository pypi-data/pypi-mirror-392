"""PR creation command - separate module to keep pr.py focused on generation."""

from __future__ import annotations

import logging

import typer

# Force fallback to non-rich help formatting
try:  # pragma: no cover
    import typer as _typer

    if hasattr(_typer, "rich_utils"):
        _typer.rich_utils = None  # type: ignore[attr-defined]
except (ImportError, AttributeError) as _e:
    logging.debug("Typer rich utils disable not applied: %s", _e)

from cli import api_client as api
from cli.context_resolver import ContextResolutionError, format_resolution_log, resolve_pr_context
from cli.git_commit import InvalidRepositoryError, find_git_root
from cli.github_operations import PRCreationError, create_pull_request, get_current_branch


def create(
    title: str | None = typer.Option(
        None, "--title", "-t", help="PR title (auto-generated if not provided)"
    ),
    body: str | None = typer.Option(
        None, "--body", "-b", help="PR body (auto-generated if not provided)"
    ),
    base: str = typer.Option("main", "--base", help="Base branch to merge into"),
    head: str | None = typer.Option(None, "--head", help="Head branch (default: current branch)"),
    owner: str | None = typer.Option(None, help="GitHub owner/org (auto-detected from git)"),
    repo: str | None = typer.Option(None, help="GitHub repo (auto-detected from git)"),
    draft: bool = typer.Option(False, "--draft", help="Create as draft PR"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed progress"),
    auto_generate: bool = typer.Option(True, help="Auto-generate title/body if not provided"),
) -> None:
    """
    Create a pull request on GitHub.

    If title or body are not provided, they will be auto-generated using AI
    based on the changes in the PR.

    Examples:
        smooth pr create
        smooth pr create --title "feat: new feature" --body "Description"
        smooth pr create --base develop --draft
    """
    try:
        # Resolve context
        try:
            ctx = resolve_pr_context(
                cli_owner=owner,
                cli_repo=repo,
                cli_pr_number=None,
                cli_output=None,
                cli_verbose=verbose,
            )
        except ContextResolutionError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1) from e

        # Get current branch if head not provided
        if not head:
            try:
                repo_path = find_git_root()
                head = get_current_branch(str(repo_path))
                if verbose:
                    typer.echo(f"📍 Using current branch: {head}", err=True)
            except (InvalidRepositoryError, Exception) as e:
                typer.echo(f"❌ Failed to detect current branch: {e}", err=True)
                raise typer.Exit(code=1) from e

        # Show resolution details if verbose
        if verbose:
            typer.echo("📋 Context Resolution:", err=True)
            for line in format_resolution_log(ctx):
                typer.echo(f"  {line}", err=True)
            typer.echo("", err=True)

        # Auto-generate title and/or body if not provided
        generated_title = title
        generated_body = body

        if auto_generate and (not title or not body):
            if verbose:
                typer.echo("🤖 Auto-generating PR content...", err=True)

            # We need to generate content based on the diff
            # For now, use a simple approach - in production you'd want to fetch the actual diff
            try:
                # Generate title if needed
                if not title:
                    if verbose:
                        typer.echo("  Generating title...", err=True)
                    title_result = api.generate_pr_title(
                        owner=ctx.owner,
                        repo=ctx.repo,
                        base=base,
                        head=head,
                    )
                    generated_title = title_result.get("title", "")

                # Generate body if needed
                if not body:
                    if verbose:
                        typer.echo("  Generating summary...", err=True)
                    summary_result = api.generate_pr_summary(
                        payload={
                            "owner": ctx.owner,
                            "repo": ctx.repo,
                            "base": base,
                            "head": head,
                        }
                    )
                    generated_body = summary_result.get("generated_text", "")

            except Exception as e:
                typer.echo(f"⚠️  Failed to auto-generate content: {e}", err=True)
                if not title or not body:
                    typer.echo(
                        "❌ Title and body are required when auto-generation fails", err=True
                    )
                    raise typer.Exit(code=1) from e

        # Validate we have title and body
        if not generated_title:
            typer.echo(
                "❌ PR title is required (provide --title or enable --auto-generate)", err=True
            )
            raise typer.Exit(code=1)

        if verbose:
            typer.echo(f"📝 Title: {generated_title}", err=True)
            typer.echo(f"📄 Creating PR: {head} → {base}", err=True)

        # Create PR
        pr_data = create_pull_request(
            owner=ctx.owner,
            repo=ctx.repo,
            title=generated_title,
            body=generated_body or "",
            head=head,
            base=base,
            draft=draft,
        )

        # Output success
        typer.echo(f"✅ Created PR #{pr_data['number']}: {generated_title}")
        typer.echo(f"🔗 {pr_data['html_url']}")

        if draft:
            typer.echo("📝 PR created as draft")

    except PRCreationError as e:
        typer.echo(f"❌ Failed to create PR: {e}", err=True)
        raise typer.Exit(code=1) from e
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(code=1) from e
