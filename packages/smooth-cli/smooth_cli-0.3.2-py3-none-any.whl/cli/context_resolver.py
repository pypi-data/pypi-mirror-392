"""Context resolution with four-tier precedence system.

This module implements the core smart defaults logic by combining:
1. CLI flags (highest precedence)
2. Git context (auto-detected)
3. Repository config (.smoothdev.json)
4. User config (~/.smoothdevio/config.json)

Principles Applied:
- Single Responsibility: Each function resolves one type of context
- Open/Closed: Extensible for new context types without modification
- Interface Segregation: Separate resolvers for PR vs release contexts
- Dependency Inversion: Uses abstractions from git_context and config_manager
- DRY: Shared resolution logic
- KISS: Clear, straightforward precedence rules
- YAGNI: Only implements required resolution logic
- Separation of Concerns: Resolution logic separate from I/O
- Law of Demeter: Minimal coupling with other modules
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from cli.config_manager import (
    load_repository_config,
    load_user_config,
)
from cli.git_context import (
    detect_pr_number_from_branch,
    get_git_context,
    get_latest_tag,
    get_previous_tag,
)


@dataclass
class ResolvedValue:
    """A resolved configuration value with its source.

    Attributes:
        value: The resolved value
        source: Source of the value ('cli', 'git', 'repo_config', 'user_config', 'default')
    """

    value: Any
    source: str


@dataclass
class PRContext:
    """Resolved context for PR commands.

    Attributes:
        owner: Repository owner
        owner_source: Source of owner value
        repo: Repository name
        repo_source: Source of repo value
        pr_number: Pull request number
        pr_source: Source of PR number
        branch: Current branch (optional)
        branch_source: Source of branch value
        output: Output format
        output_source: Source of output format
        verbose: Verbose mode
        verbose_source: Source of verbose flag
    """

    owner: str
    owner_source: str
    repo: str
    repo_source: str
    pr_number: Optional[int]
    pr_source: str
    branch: Optional[str]
    branch_source: str
    output: str
    output_source: str
    verbose: bool
    verbose_source: str


@dataclass
class ReleaseContext:
    """Resolved context for release commands.

    Attributes:
        owner: Repository owner
        owner_source: Source of owner value
        repo: Repository name
        repo_source: Source of repo value
        from_tag: Starting tag/ref
        from_source: Source of from_tag
        to_tag: Ending tag/ref
        to_source: Source of to_tag
        output: Output format
        output_source: Source of output format
        verbose: Verbose mode
        verbose_source: Source of verbose flag
    """

    owner: str
    owner_source: str
    repo: str
    repo_source: str
    from_tag: Optional[str]
    from_source: str
    to_tag: Optional[str]
    to_source: str
    output: str
    output_source: str
    verbose: bool
    verbose_source: str


class ContextResolutionError(Exception):
    """Raised when required context cannot be resolved."""


def _resolve_value(
    field_name: str,
    cli_value: Any,
    git_value: Any,
    repo_value: Any,
    user_value: Any,
    default_value: Any = None,
) -> ResolvedValue:
    """Resolve a single value using four-tier precedence.

    Single Responsibility: Apply precedence rules to one field.

    Precedence order:
    1. CLI flag (explicit user override)
    2. Git context (auto-detected from repository)
    3. Repository config (team settings)
    4. User config (personal defaults)
    5. Default value (fallback)

    Args:
        field_name: Name of the field being resolved
        cli_value: Value from CLI flag
        git_value: Value from git context
        repo_value: Value from repository config
        user_value: Value from user config
        default_value: Default fallback value

    Returns:
        ResolvedValue with value and source
    """
    if cli_value is not None:
        return ResolvedValue(value=cli_value, source="cli")

    if git_value is not None:
        return ResolvedValue(value=git_value, source="git")

    if repo_value is not None:
        return ResolvedValue(value=repo_value, source="repo_config")

    if user_value is not None:
        return ResolvedValue(value=user_value, source="user_config")

    if default_value is not None:
        return ResolvedValue(value=default_value, source="default")

    # No value found
    return ResolvedValue(value=None, source="none")


def resolve_pr_context(
    cli_owner: Optional[str] = None,
    cli_repo: Optional[str] = None,
    cli_pr_number: Optional[int] = None,
    cli_output: Optional[str] = None,
    cli_verbose: Optional[bool] = None,
    path: Optional[Path] = None,
) -> PRContext:
    """Resolve PR command context using four-tier precedence.

    Single Responsibility: Aggregate PR context from all sources.
    Separation of Concerns: Delegates to specialized functions.

    Args:
        cli_owner: Owner from CLI flag
        cli_repo: Repo from CLI flag
        cli_pr_number: PR number from CLI flag
        cli_output: Output format from CLI flag
        cli_verbose: Verbose mode from CLI flag
        path: Path for git/config detection (default: current directory)

    Returns:
        PRContext with all resolved values

    Raises:
        ContextResolutionError: If required values cannot be resolved
    """
    # Load all context sources
    git_ctx = get_git_context(path)
    repo_config = load_repository_config(path)
    user_config = load_user_config()

    # Extract git values
    git_owner = git_ctx.remote.owner if git_ctx else None
    git_repo = git_ctx.remote.repo if git_ctx else None
    git_branch = git_ctx.branch if git_ctx else None

    # Auto-detect PR number from branch name if available
    git_pr_number = None
    if git_branch and not cli_pr_number:
        git_pr_number = detect_pr_number_from_branch(git_branch)

    # Extract repo config values
    repo_owner = repo_config.owner if repo_config else None
    repo_repo = repo_config.repo if repo_config else None
    repo_output = repo_config.defaults.output if repo_config else None
    repo_verbose = repo_config.defaults.verbose if repo_config else None

    # Extract user config values
    user_owner = user_config.defaults.owner if user_config.defaults else None
    user_repo = user_config.defaults.repo if user_config.defaults else None
    user_output = user_config.defaults.output if user_config.defaults else None
    user_verbose = user_config.defaults.verbose if user_config.defaults else None

    # Resolve each field
    owner_resolved = _resolve_value("owner", cli_owner, git_owner, repo_owner, user_owner)
    repo_resolved = _resolve_value("repo", cli_repo, git_repo, repo_repo, user_repo)
    pr_resolved = _resolve_value("pr_number", cli_pr_number, git_pr_number, None, None)
    branch_resolved = _resolve_value("branch", None, git_branch, None, None)
    output_resolved = _resolve_value("output", cli_output, None, repo_output, user_output, "text")
    verbose_resolved = _resolve_value(
        "verbose", cli_verbose, None, repo_verbose, user_verbose, False
    )

    # Validate required fields
    if owner_resolved.value is None:
        raise ContextResolutionError(
            "Repository owner could not be determined. "
            "Please provide --owner flag or run in a git repository."
        )

    if repo_resolved.value is None:
        raise ContextResolutionError(
            "Repository name could not be determined. "
            "Please provide --repo flag or run in a git repository."
        )

    return PRContext(
        owner=owner_resolved.value,
        owner_source=owner_resolved.source,
        repo=repo_resolved.value,
        repo_source=repo_resolved.source,
        pr_number=pr_resolved.value,
        pr_source=pr_resolved.source,
        branch=branch_resolved.value,
        branch_source=branch_resolved.source,
        output=output_resolved.value,
        output_source=output_resolved.source,
        verbose=verbose_resolved.value,
        verbose_source=verbose_resolved.source,
    )


def resolve_release_context(
    cli_owner: Optional[str] = None,
    cli_repo: Optional[str] = None,
    cli_from_tag: Optional[str] = None,
    cli_to_tag: Optional[str] = None,
    cli_output: Optional[str] = None,
    cli_verbose: Optional[bool] = None,
    path: Optional[Path] = None,
) -> ReleaseContext:
    """Resolve release command context using four-tier precedence.

    Single Responsibility: Aggregate release context from all sources.
    Separation of Concerns: Delegates to specialized functions.

    Args:
        cli_owner: Owner from CLI flag
        cli_repo: Repo from CLI flag
        cli_from_tag: From tag from CLI flag
        cli_to_tag: To tag from CLI flag
        cli_output: Output format from CLI flag
        cli_verbose: Verbose mode from CLI flag
        path: Path for git/config detection (default: current directory)

    Returns:
        ReleaseContext with all resolved values

    Raises:
        ContextResolutionError: If required values cannot be resolved
    """
    # Load all context sources
    git_ctx = get_git_context(path)
    repo_config = load_repository_config(path)
    user_config = load_user_config()

    # Extract git values
    git_owner = git_ctx.remote.owner if git_ctx else None
    git_repo = git_ctx.remote.repo if git_ctx else None

    # Auto-detect tags if not provided via CLI
    git_to_tag = None
    git_from_tag = None
    if not cli_to_tag:
        git_to_tag = get_latest_tag(path)
    if not cli_from_tag and git_to_tag:
        git_from_tag = get_previous_tag(git_to_tag, path)

    # Extract repo config values
    repo_owner = repo_config.owner if repo_config else None
    repo_repo = repo_config.repo if repo_config else None
    repo_output = repo_config.defaults.output if repo_config else None
    repo_verbose = repo_config.defaults.verbose if repo_config else None

    # Extract user config values
    user_owner = user_config.defaults.owner if user_config.defaults else None
    user_repo = user_config.defaults.repo if user_config.defaults else None
    user_output = user_config.defaults.output if user_config.defaults else None
    user_verbose = user_config.defaults.verbose if user_config.defaults else None

    # Resolve each field
    owner_resolved = _resolve_value("owner", cli_owner, git_owner, repo_owner, user_owner)
    repo_resolved = _resolve_value("repo", cli_repo, git_repo, repo_repo, user_repo)
    from_resolved = _resolve_value("from_tag", cli_from_tag, git_from_tag, None, None)
    to_resolved = _resolve_value("to_tag", cli_to_tag, git_to_tag, None, None)
    output_resolved = _resolve_value("output", cli_output, None, repo_output, user_output, "text")
    verbose_resolved = _resolve_value(
        "verbose", cli_verbose, None, repo_verbose, user_verbose, False
    )

    # Validate required fields
    if owner_resolved.value is None:
        raise ContextResolutionError(
            "Repository owner could not be determined. "
            "Please provide --owner flag or run in a git repository."
        )

    if repo_resolved.value is None:
        raise ContextResolutionError(
            "Repository name could not be determined. "
            "Please provide --repo flag or run in a git repository."
        )

    return ReleaseContext(
        owner=owner_resolved.value,
        owner_source=owner_resolved.source,
        repo=repo_resolved.value,
        repo_source=repo_resolved.source,
        from_tag=from_resolved.value,
        from_source=from_resolved.source,
        to_tag=to_resolved.value,
        to_source=to_resolved.source,
        output=output_resolved.value,
        output_source=output_resolved.source,
        verbose=verbose_resolved.value,
        verbose_source=verbose_resolved.source,
    )


def format_resolution_log(context: PRContext | ReleaseContext) -> list[str]:
    """Format context resolution for verbose logging.

    Single Responsibility: Create human-readable resolution log.

    Args:
        context: Resolved PR or release context

    Returns:
        List of formatted log lines
    """
    lines = []

    if isinstance(context, PRContext):
        lines.append(f"✓ Using owner: {context.owner} (from {context.owner_source})")
        lines.append(f"✓ Using repo: {context.repo} (from {context.repo_source})")
        if context.pr_number:
            lines.append(f"✓ Using PR: {context.pr_number} (from {context.pr_source})")
        if context.branch:
            lines.append(f"✓ Using branch: {context.branch} (from {context.branch_source})")
        lines.append(f"✓ Using output: {context.output} (from {context.output_source})")

    elif isinstance(context, ReleaseContext):
        lines.append(f"✓ Using owner: {context.owner} (from {context.owner_source})")
        lines.append(f"✓ Using repo: {context.repo} (from {context.repo_source})")
        if context.from_tag:
            lines.append(f"✓ Using from-tag: {context.from_tag} (from {context.from_source})")
        if context.to_tag:
            lines.append(f"✓ Using to-tag: {context.to_tag} (from {context.to_source})")
        lines.append(f"✓ Using output: {context.output} (from {context.output_source})")

    return lines
