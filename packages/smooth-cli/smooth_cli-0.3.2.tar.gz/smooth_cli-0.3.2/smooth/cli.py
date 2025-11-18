import logging
from contextlib import suppress

import typer

# Force fallback to non-rich help formatting to avoid version incompatibilities
try:  # pragma: no cover - environment dependent
    import typer as _typer

    if hasattr(_typer, "rich_utils"):
        _typer.rich_utils = None  # type: ignore[attr-defined]
except Exception as err:
    logging.debug("Disabling Typer rich_utils failed: %s", err)

from .commands import commit as commit_cmd

__version__ = "0.3.0"

app = typer.Typer(help="SmoothDev CLI", rich_markup_mode=None)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"smooth version {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: ARG001
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """SmoothDev CLI - Generate commit messages, PRs, and release notes."""


app.add_typer(commit_cmd.app, name="commit")

# Optional subcommands (API-first), guarded to avoid crashing when dependencies are absent
with suppress(Exception):
    # Prefer to import after app creation to avoid blocking the CLI if these fail
    from .commands import docs as docs_cmd

    app.add_typer(docs_cmd.app, name="docs")

with suppress(Exception):
    from .commands import auth as auth_cmd

    app.add_typer(auth_cmd.app, name="auth")
with suppress(Exception):
    from .commands import pr as pr_cmd

    app.add_typer(pr_cmd.app, name="pr")

with suppress(Exception):
    from .commands import release as release_cmd

    app.add_typer(release_cmd.app, name="release")

with suppress(Exception):
    from .commands import feedback as feedback_cmd

    app.add_typer(feedback_cmd.app, name="feedback")

with suppress(Exception):
    from .commands import config as config_cmd

    app.add_typer(config_cmd.app, name="config")
