"""Configuration management commands.

Provides commands to view and manage user and repository configurations
for smart defaults.
"""

from __future__ import annotations

import json
from contextlib import suppress
from pathlib import Path
from typing import cast

import typer

from cli.config_manager import (
    ConfigDefaults,
    ConfigValidationError,
    RepositoryConfig,
    UserConfig,
    get_config_value,
    get_user_config_path,
    load_repository_config,
    load_user_config,
    save_repository_config,
    save_user_config,
    set_config_value,
)

app = typer.Typer(
    help=(
        "Configuration management for smart defaults. "
        "Precedence: flags > git context > repo (.smoothdev.json) > "
        "user (~/.smoothdevio/config.json)."
    )
)


def _backup(path: Path) -> None:
    """Create a .bak backup of the given file if it exists.

    Best-effort: swallow any exceptions, used for recovery paths.
    """
    if path.exists():
        if path.name == ".smoothdev.json":
            backup = path.parent / ".smoothdev.json.bak"
        else:
            backup = path.with_suffix(".bak")
        with suppress(Exception):
            path.replace(backup)


@app.command()
def show(
    scope: str = typer.Option("all", help="Scope: user, repo, or all"),
    format: str = typer.Option("text", help="Output format: text or json"),
) -> None:
    """Show current configuration settings.

    Displays user config, repository config, or both depending on scope.
    """
    user_config = load_user_config()
    repo_config = load_repository_config()

    if format == "json":
        output = {}
        if scope in ("user", "all"):
            output["user"] = user_config.to_dict()
        if scope in ("repo", "all"):
            # Avoid None to satisfy static typing; omit key or use empty object
            output["repository"] = repo_config.to_dict() if repo_config else {}
        typer.echo(json.dumps(output, indent=2))
    else:
        # Text format
        if scope in ("user", "all"):
            typer.echo("📁 User Configuration")
            typer.echo(f"   Location: {get_user_config_path()}")
            typer.echo("")
            _print_config_text(user_config.to_dict())
            typer.echo("")

        if scope in ("repo", "all"):
            if repo_config:
                typer.echo("📦 Repository Configuration")
                typer.echo("   Location: .smoothdev.json")
                typer.echo("")
                _print_config_text(repo_config.to_dict())
            elif scope == "repo":
                typer.echo("No repository configuration found (.smoothdev.json)", err=True)


@app.command()
def get(
    key: str = typer.Argument(..., help="Configuration key (e.g., defaults.owner)"),
    scope: str = typer.Option("user", help="Scope: user or repo"),
) -> None:
    """Get a specific configuration value.

    Examples:
        smooth config get defaults.owner
        smooth config get defaults.output --scope repo
    """
    config: UserConfig | RepositoryConfig
    if scope == "user":
        config = load_user_config()
    elif scope == "repo":
        repo_cfg = load_repository_config()
        if not repo_cfg:
            typer.echo("No repository configuration found", err=True)
            raise typer.Exit(code=1)
        config = repo_cfg
    else:
        typer.echo(f"Invalid scope: {scope}. Use 'user' or 'repo'", err=True)
        raise typer.Exit(code=1)

    value = get_config_value(config, key)
    if value is None:
        typer.echo(f"Key '{key}' not found", err=True)
        raise typer.Exit(code=1)

    typer.echo(str(value))


@app.command()
def set(  # noqa: A001
    key: str = typer.Argument(..., help="Configuration key (e.g., defaults.owner)"),
    value: str = typer.Argument(..., help="Value to set"),
    scope: str = typer.Option("user", help="Scope: user or repo"),
) -> None:
    """Set a configuration value.

    Examples:
        smooth config set defaults.owner smoothdev-io
        smooth config set defaults.output json --scope repo
    """
    config: UserConfig | RepositoryConfig
    if scope == "user":
        try:
            config = load_user_config()
        except ConfigValidationError:
            cfg_path = get_user_config_path()
            _backup(cfg_path)
            config = UserConfig()
    elif scope == "repo":
        try:
            repo_cfg = load_repository_config()
        except ConfigValidationError:
            repo_cfg = None
            _backup(Path(".smoothdev.json"))
        if not repo_cfg:
            repo_cfg = RepositoryConfig()
        config = repo_cfg
    else:
        typer.echo(f"Invalid scope: {scope}. Use 'user' or 'repo'", err=True)
        raise typer.Exit(code=1)

    try:
        # Convert boolean strings
        actual_value: str | bool
        if value.lower() in ("true", "false"):
            actual_value = value.lower() == "true"
        else:
            actual_value = value

        set_config_value(config, key, actual_value)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    # Save config
    if scope == "user":
        save_user_config(cast(UserConfig, config))
        typer.echo(f"✅ Updated user config: {key} = {value}")
    else:
        save_repository_config(cast(RepositoryConfig, config))
        typer.echo(f"✅ Updated repository config: {key} = {value}")


@app.command()
def init(
    owner: str | None = typer.Option(None, help="Repository owner"),
    repo: str | None = typer.Option(None, help="Repository name"),
    output: str | None = typer.Option(None, help="Default output format"),
    verbose: bool | None = typer.Option(None, help="Default verbose mode"),
    scope: str = typer.Option("repo", help="Scope: user or repo"),
    merge: bool = typer.Option(True, help="Merge with existing config if present"),
    force: bool = typer.Option(False, help="Force overwrite existing file (no merge)"),
) -> None:
    """Initialize a configuration file with defaults.

    Creates a new configuration file with the specified values.
    """
    if scope == "user":
        cfg_path = get_user_config_path()
        if force and cfg_path.exists():
            with suppress(Exception):
                cfg_path.unlink()
        user_config = UserConfig(
            defaults=ConfigDefaults(
                owner=owner,
                repo=repo,
                output=output or "text",
                verbose=verbose if verbose is not None else False,
            )
        )
        if not merge and cfg_path.exists():
            _backup(cfg_path)
            with suppress(Exception):
                cfg_path.unlink()
        save_user_config(user_config)
        typer.echo(f"✅ Created user config at {get_user_config_path()}")
    elif scope == "repo":
        cfg_path = Path(".smoothdev.json")
        if force and cfg_path.exists():
            with suppress(Exception):
                cfg_path.unlink()
        repo_config = RepositoryConfig(
            owner=owner,
            repo=repo,
            defaults=ConfigDefaults(
                output=output or "text",
                verbose=verbose if verbose is not None else False,
            ),
        )
        if not merge and cfg_path.exists():
            _backup(cfg_path)
            with suppress(Exception):
                cfg_path.unlink()
        save_repository_config(repo_config)
        typer.echo("✅ Created repository config at .smoothdev.json")
    else:
        typer.echo(f"Invalid scope: {scope}. Use 'user' or 'repo'", err=True)
        raise typer.Exit(code=1)


@app.command()
def path(
    scope: str = typer.Option("user", help="Scope: user or repo"),
) -> None:
    """Show the path to the configuration file."""
    if scope == "user":
        typer.echo(str(get_user_config_path()))
    elif scope == "repo":
        typer.echo(".smoothdev.json")
    else:
        typer.echo(f"Invalid scope: {scope}. Use 'user' or 'repo'", err=True)
        raise typer.Exit(code=1)


def _print_config_text(config_dict: dict, indent: int = 0) -> None:
    """Print configuration dictionary in readable text format."""
    for key, value in config_dict.items():
        if value is None:
            continue

        prefix = "  " * indent
        if isinstance(value, dict):
            typer.echo(f"{prefix}{key}:")
            _print_config_text(value, indent + 1)
        else:
            typer.echo(f"{prefix}{key}: {value}")
