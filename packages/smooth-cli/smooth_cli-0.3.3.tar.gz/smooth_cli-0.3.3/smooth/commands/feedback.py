from __future__ import annotations

import json

import typer

from cli import api_client as api

app = typer.Typer(help="Feedback submission for generated artifacts (API-first)")


@app.command()
def submit(
    artifact: str = typer.Option(
        ..., help="Artifact type: commit|pr-title|pr-summary|release-notes|repo-docs"
    ),
    ref: str = typer.Option(..., help="Artifact reference ID (e.g., commit SHA, PR number, tag)"),
    rating: int = typer.Option(..., min=1, max=5, help="Rating from 1 to 5"),
    feedback: str = typer.Option("", help="Feedback text"),
    output: str = typer.Option("json", help="Output format: json or text"),
) -> None:
    result = api.submit_feedback(artifact=artifact, ref=ref, rating=rating, feedback=feedback)
    if output.lower() == "json":
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo("Feedback submitted successfully")
