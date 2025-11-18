import typer

from cli import auth as auth_mod

MIN_API_KEY_PARTS = 4

app = typer.Typer(help="Authentication and API key management")


@app.command()
def login() -> None:
    """Authenticate with Auth0 device flow."""
    typer.echo("Authenticating with Auth0...")
    auth_mod.authenticate()
    typer.echo("Authentication successful! You can now use the CLI.")


@app.command("apikey-set")
def apikey_set(
    api_key: str = typer.Argument(..., help="API key in format sk_live_<id>_<secret>"),
) -> None:
    """Store an API key for authentication."""
    auth_mod.save_api_key(api_key)
    typer.echo("API key saved successfully!")


@app.command("apikey-show")
def apikey_show() -> None:
    """Show the currently stored API key (masked)."""
    api_key = auth_mod.load_api_key()
    if not api_key:
        typer.echo("No API key is currently stored. Use 'smooth auth apikey-set <key>'.")
        return
    parts = api_key.split("_")
    if len(parts) >= MIN_API_KEY_PARTS:
        masked = f"{parts[0]}_{parts[1]}_{parts[2]}_{'*' * 8}"
        typer.echo(f"Stored API key: {masked}")
    else:
        typer.echo("Stored API key: <invalid format>")


@app.command("apikey-clear")
def apikey_clear() -> None:
    """Remove the stored API key."""
    if not auth_mod.load_api_key():
        typer.echo("No API key is currently stored.")
        return
    auth_mod.clear_api_key()
    typer.echo("API key removed successfully!")


@app.command("mode-show")
def mode_show() -> None:
    """Show the effective authentication mode (auto|jwt|api-key)."""
    mode = auth_mod.effective_auth_mode(None)
    typer.echo(mode)


@app.command("mode-set")
def mode_set(mode: str = typer.Argument(..., help="Auth mode: auto|jwt|api-key")) -> None:
    """Persist the authentication mode in ~/.smoothdevio/config.json."""
    auth_mod.set_auth_mode(mode)
    typer.echo(f"Auth mode set to {auth_mod.effective_auth_mode(None)}")
