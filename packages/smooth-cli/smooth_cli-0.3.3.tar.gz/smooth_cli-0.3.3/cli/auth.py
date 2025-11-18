from __future__ import annotations

import json
import logging
import os
import time
import webbrowser
from http import HTTPStatus
from pathlib import Path
from typing import Any, cast

import click
import requests

TOKEN_FILE_PATH = Path("~/.smoothdevio/token.json").expanduser()
CONFIG_FILE_PATH = Path("~/.smoothdevio/config.json").expanduser()


class AuthError(Exception):
    """Authentication error"""


def save_api_key(api_key: str) -> None:
    config = _read_user_cfg()
    config["api_key"] = api_key
    _write_user_cfg(config)


def load_api_key() -> str | None:
    config = _read_user_cfg()
    return config.get("api_key")


def clear_api_key() -> None:
    config = _read_user_cfg()
    if "api_key" in config:
        del config["api_key"]
    # Write exact config back to file (do not merge) to ensure deletion persists
    dirp = CONFIG_FILE_PATH.parent
    if dirp and not dirp.exists():
        dirp.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE_PATH.write_text(json.dumps(config, indent=2))
    CONFIG_FILE_PATH.chmod(0o600)


def _normalize_mode(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().lower()
    if v in {"auto", "jwt", "api-key", "apikey"}:
        return "api-key" if v == "apikey" else v
    return None


def effective_auth_mode(explicit: str | None = None) -> str:
    """Resolve auth mode with precedence: explicit > env > user config > default(auto)."""
    # 1) explicit (e.g., flags) if provided
    mode = _normalize_mode(explicit)
    if mode:
        return mode

    # 2) environment
    mode = _normalize_mode(os.getenv("SMOOTHDEV_AUTH_MODE"))
    if mode:
        return mode

    # 3) user config
    cfg = _read_user_cfg()
    mode = _normalize_mode(str(cfg.get("auth_mode", "") or ""))
    if mode:
        return mode

    # default
    return "auto"


def set_auth_mode(mode: str) -> None:
    norm = _normalize_mode(mode)
    if not norm:
        msg = "Invalid auth mode. Use one of: auto, jwt, api-key"
        raise click.ClickException(msg)
    _write_user_cfg({"auth_mode": norm})


def _read_user_cfg() -> dict[str, Any]:
    candidates = [
        CONFIG_FILE_PATH,
    ]
    for path in candidates:
        try:
            if path.exists():
                return cast("dict[str, Any]", json.loads(path.read_text()))
        except Exception as exc:
            logging.debug("Failed reading user config at %s: %s", path, exc)
            continue
    return {}


def _write_user_cfg(updates: dict[str, Any]) -> None:
    cfg: dict[str, Any] = {}
    try:
        if CONFIG_FILE_PATH.exists():
            cfg = cast("dict[str, Any]", json.loads(CONFIG_FILE_PATH.read_text()))
    except Exception as exc:
        logging.debug("Failed reading config file %s: %s", CONFIG_FILE_PATH, exc)
        cfg = {}
    cfg.update(updates)
    dirp = CONFIG_FILE_PATH.parent
    if dirp and not dirp.exists():
        dirp.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE_PATH.write_text(json.dumps(cfg, indent=2))
    CONFIG_FILE_PATH.chmod(0o600)


def _read_default_cfg() -> dict[str, Any]:
    try:
        cfg_path = (Path(__file__).parent / "default_config.json").resolve()
        if cfg_path.exists():
            return cast("dict[str, Any]", json.loads(cfg_path.read_text()))
    except Exception as exc:
        logging.debug("Failed reading bundled default config: %s", exc)
    return {}


def _auth0_cfg() -> tuple[str, str, str]:
    """Return (domain, client_id, audience) from config with fallbacks.

    Precedence:
    1) Environment variables: SMOOTHDEV_AUTH0_DOMAIN, _CLIENT_ID, _AUDIENCE
    2) ~/.smoothdevio/config.json keys: auth0_domain, auth0_client_id, auth0_audience
    3) Bundled default_config.json in this package
    """
    domain = os.getenv("SMOOTHDEV_AUTH0_DOMAIN", "") or ""
    client_id = os.getenv("SMOOTHDEV_AUTH0_CLIENT_ID", "") or ""
    audience = os.getenv("SMOOTHDEV_AUTH0_AUDIENCE", "") or ""

    # 2) User config file
    if not (domain and client_id and audience):
        cfg = _read_user_cfg()
        domain = domain or str(cfg.get("auth0_domain", "") or "")
        client_id = client_id or str(cfg.get("auth0_client_id", "") or "")
        audience = audience or str(cfg.get("auth0_audience", "") or "")

    # 3) Bundled default config
    if not (domain and client_id and audience):
        cfg = _read_default_cfg()
        domain = domain or str(cfg.get("auth0_domain", "") or "")
        client_id = client_id or str(cfg.get("auth0_client_id", "") or "")
        audience = audience or str(cfg.get("auth0_audience", "") or "")

    if not domain:
        msg = (
            "Missing Auth0 domain. Set SMOOTHDEV_AUTH0_DOMAIN or configure "
            "auth0_domain in ~/.smoothdevio/config.json or default_config.json"
        )
        raise AuthError(msg)
    if not client_id:
        msg = (
            "Missing Auth0 client_id. Set SMOOTHDEV_AUTH0_CLIENT_ID or configure "
            "auth0_client_id in ~/.smoothdevio/config.json or default_config.json"
        )
        raise AuthError(msg)
    if not audience:
        msg = (
            "Missing Auth0 audience. Set SMOOTHDEV_AUTH0_AUDIENCE or configure "
            "auth0_audience in ~/.smoothdevio/config.json or default_config.json"
        )
        raise AuthError(msg)

    return domain, client_id, audience


def get_device_code() -> dict[str, Any]:
    """
    Initiates the device authorization flow with Auth0.

    Returns:
        Dict containing device_code, user_code, verification_uri, and expires_in
    """
    domain, client_id, audience = _auth0_cfg()
    url = f"https://{domain}/oauth/device/code"
    payload = {
        "client_id": client_id,
        "audience": audience,
        "scope": "openid profile email",
    }

    response = requests.post(url, data=payload, timeout=30)

    if response.status_code != HTTPStatus.OK:
        message = f"Failed to get device code: {response.text}"
        raise AuthError(message)

    return cast("dict[str, Any]", response.json())


def poll_for_token(device_code: str, interval: int, expiry: int) -> dict[str, Any]:
    """
    Polls Auth0 for a token using the device code

    Args:
        device_code: The device code from the initial request
        interval: Number of seconds to wait between polling attempts
        expiry: Total seconds until the device code expires

    Returns:
        Dict containing access_token, id_token, refresh_token, and expires_in
    """
    domain, client_id, _audience = _auth0_cfg()
    url = f"https://{domain}/oauth/token"
    payload = {
        "client_id": client_id,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
    }

    start_time = time.time()

    # Loop until we get a token or time out
    while time.time() - start_time < expiry:
        response = requests.post(url, data=payload, timeout=30)
        data = cast("dict[str, Any]", response.json())

        if response.status_code == HTTPStatus.OK:
            return data

        # If not "slow down" or "authorization pending" error, raise exception
        if data.get("error") not in ["slow_down", "authorization_pending"]:
            message = f"Authentication failed: {data.get('error_description')}"
            raise AuthError(message)

        # Adjust polling interval if needed
        if data.get("error") == "slow_down" and "interval" in data:
            interval = int(data["interval"])  # type: ignore[call-overload]

        # Wait before polling again
        time.sleep(interval)

    message = "Device code expired. Please try again."
    raise AuthError(message)


def save_token(token_data: dict[str, Any]) -> None:
    """Saves token data to TOKEN_FILE_PATH with 0600 permissions."""
    token_file_dir = TOKEN_FILE_PATH.parent
    if token_file_dir and not token_file_dir.exists():
        token_file_dir.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE_PATH.write_text(json.dumps(token_data))
    TOKEN_FILE_PATH.chmod(0o600)


def load_token() -> dict[str, Any] | None:
    """Loads token data and refreshes if expired."""
    path = TOKEN_FILE_PATH
    if not path.exists():
        return None
    try:
        token_data = cast("dict[str, Any]", json.loads(path.read_text()))
    except (OSError, json.JSONDecodeError):
        return None
    else:
        if "expires_at" in token_data and time.time() > token_data["expires_at"]:
            new_token = refresh_token(token_data.get("refresh_token", ""))
            if new_token:
                return new_token
            return None
        return token_data


def refresh_token(refresh_token: str) -> dict[str, Any] | None:
    """Refresh expired token using Auth0."""
    if not refresh_token:
        return None
    domain, client_id, _audience = _auth0_cfg()
    url = f"https://{domain}/oauth/token"
    payload = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    try:
        response = requests.post(url, data=payload, timeout=30)
        if response.status_code == HTTPStatus.OK:
            token_data = cast("dict[str, Any]", response.json())
            if "expires_in" in token_data:
                expires_in = int(token_data["expires_in"])  # type: ignore[call-overload]
                token_data["expires_at"] = time.time() + float(expires_in)
            save_token(token_data)
            return token_data
    except requests.RequestException as exc:
        logging.debug("Failed to refresh token: %s", exc)
    return None


def authenticate() -> str:
    """
    Full Auth0 device-flow authentication.

    Returns:
        Access token string for API calls
    """
    # Check for existing valid token
    token_data = load_token()
    if token_data and "access_token" in token_data:
        return cast("str", token_data["access_token"])

    try:
        # Get device code
        device_data = get_device_code()
        device_code = device_data["device_code"]
        user_code = device_data["user_code"]
        verification_uri = device_data["verification_uri"]
        verification_uri_complete = device_data.get("verification_uri_complete")
        interval = int(device_data.get("interval", 5))
        expires_in = int(device_data.get("expires_in", 900))

        # Display information to user
        click.echo("\nTo authenticate, please follow these steps:")
        click.echo(f"1. Visit: {verification_uri}")
        click.echo(f"2. Enter code: {user_code}\n")

        # Try to open browser automatically
        if verification_uri_complete:
            click.echo("Attempting to open the verification page in your browser...")
            webbrowser.open(verification_uri_complete)
        else:
            webbrowser.open(verification_uri)

        click.echo("Waiting for authentication to complete...\n")

        # Poll for token
        token_data = poll_for_token(device_code, interval, expires_in)

        # Add expiry timestamp
        if "expires_in" in token_data:
            expires_in_val = int(token_data["expires_in"])  # type: ignore[call-overload]
            token_data["expires_at"] = time.time() + float(expires_in_val)

        # Save token for future use
        save_token(token_data)

        click.echo("Authentication successful!")
        return cast("str", token_data["access_token"])

    except AuthError as e:
        message = f"Authentication error: {e!s}"
        raise click.ClickException(message) from e
    except Exception as e:
        message = f"Unexpected error during authentication: {e!s}"
        raise click.ClickException(message) from e


def get_auth_header(api_key: str | None = None, auth_mode: str | None = None) -> dict[str, str]:
    """Return HTTP auth headers based on mode.

    Modes:
    - api-key: send x-api-key header; never attempt device flow.
    - jwt: send Authorization: Bearer <jwt> (from explicit/env/config/stored or device flow).
    - auto: default behavior (compat): send Authorization first (as before).
    """
    mode = effective_auth_mode(auth_mode)

    def _find_api_key() -> str | None:
        # 1) explicit
        if api_key:
            return api_key
        # 2) env
        env_key = os.getenv("SMOOTHDEV_API_KEY")
        if env_key:
            return env_key
        # 3) user config
        cfg = _read_user_cfg()
        cfg_key = str(cfg.get("api_key", "") or "")
        if cfg_key:
            return cfg_key
        # 4) stored key
        stored = load_api_key()
        if stored:
            return stored
        return None

    if mode == "api-key":
        key = _find_api_key()
        if not key:
            msg = "No API key found. Set SMOOTHDEV_API_KEY or run 'smooth auth apikey-set <key>'."
            raise click.ClickException(msg)
        # Send raw API key in x-api-key header
        return {"x-api-key": key}

    # jwt and auto: use JWT access token, never send API key in Authorization
    existing = load_token()
    if existing and "access_token" in existing:
        return {"Authorization": f"Bearer {cast('str', existing['access_token'])}"}
    # Obtain a new token via device flow
    token = authenticate()
    return {"Authorization": f"Bearer {token}"}
