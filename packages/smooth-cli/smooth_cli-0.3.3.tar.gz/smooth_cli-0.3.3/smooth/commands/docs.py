import json
from pathlib import Path

import typer

import cli.main as cli_main

app = typer.Typer(help="Documentation utilities")


@app.command()
def analyze(
    repo_path: Path = typer.Option(Path(), help="Path to the Git repository"),
    output_format: str = typer.Option("text", help="Output format (text or json)"),
    api_key: str | None = typer.Option(
        None,
        envvar="SMOOTHDEV_API_KEY",
        help="API key for authentication (or set SMOOTHDEV_API_KEY)",
    ),
) -> None:
    result = cli_main.analyze_repository(str(repo_path.resolve()), output_format, api_key=api_key)
    if output_format.lower() == "json":
        typer.echo(json.dumps(result, indent=2))
        return
    typer.echo("\nAnalysis Results:")
    repo_info = result.get("repository_info", {})
    typer.echo(f"Repository: {repo_info.get('git_url')}")
    typer.echo(f"Branch: {repo_info.get('branch')}")
    if result.get("missing_readmes"):
        typer.echo("\nMissing README Files:")
        for p in result["missing_readmes"]:
            typer.echo(f" - {p or 'Repository root'}")
    else:
        typer.echo("\nNo missing README files detected.")
    if result.get("outdated_readmes"):
        typer.echo("\nOutdated README Files:")
        for p in result["outdated_readmes"]:
            typer.echo(f" - {p or 'Repository root'}")
    else:
        typer.echo("\nNo outdated README files detected.")


@app.command()
def generate(
    repo_path: Path = typer.Option(Path(), help="Path to the Git repository"),
    directory: str = typer.Option("", help="Directory within the repository"),
    overwrite: bool = typer.Option(
        False, "--overwrite", is_flag=True, help="Overwrite existing README.md files"
    ),
    api_key: str | None = typer.Option(
        None,
        envvar="SMOOTHDEV_API_KEY",
        help="API key for authentication (or set SMOOTHDEV_API_KEY)",
    ),
) -> None:
    content = cli_main.generate_documentation(
        str(repo_path.resolve()), directory, overwrite, api_key=api_key
    )
    typer.echo("\nGeneration complete!")
    typer.echo(f"Generated {len(content)} characters of documentation.")


@app.command()
def feedback(
    repo_path: Path = typer.Option(Path(), help="Path to the Git repository"),
    directory: str = typer.Option("", help="Directory within the repository"),
    generation_id: str = typer.Option(..., help="ID of the generation to provide feedback for"),
    rating: int = typer.Option(..., min=1, max=5, help="Rating from 1-5"),
    feedback: str = typer.Option("", help="Feedback text"),
) -> None:
    result = cli_main.submit_feedback(
        str(repo_path.resolve()), directory, generation_id, rating, feedback
    )
    typer.echo("\nFeedback submitted successfully!")
    typer.echo(f"Feedback ID: {result.get('feedback_id')}")
