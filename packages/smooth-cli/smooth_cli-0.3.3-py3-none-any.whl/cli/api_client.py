from __future__ import annotations

import base64
import json
import logging
import os
import zlib
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

import requests

# centralized config is not used for base URL or paths in the CLI
from .auth import effective_auth_mode, get_auth_header

# HTTP timeout configuration constants
_DEFAULT_HTTP_TIMEOUT = 60
_HTTP_TIMEOUT_MIN = 5
_HTTP_TIMEOUT_MAX = 300


def _read_user_cfg() -> dict[str, Any]:
    candidates = [
        Path("~/.smoothdevio/config.json").expanduser(),
        Path("~/.smoothdevio/config.json.bkp").expanduser(),
        Path("~/.smoothdev/config.json").expanduser(),
    ]
    for path in candidates:
        try:
            if path.exists():
                return cast("dict[str, Any]", json.loads(path.read_text()))
        except Exception as exc:
            logging.debug("Failed reading user config at %s: %s", path, exc)
    return {}


def _read_default_cfg() -> dict[str, Any]:
    """Read bundled default_config.json shipped with the CLI (production)."""
    try:
        cfg_path = (Path(__file__).parent / "default_config.json").resolve()
        if cfg_path.exists():
            return cast("dict[str, Any]", json.loads(cfg_path.read_text()))
    except Exception as exc:
        logging.debug("Failed reading bundled default config: %s", exc)
    return {}


def _api_base_url() -> str:
    """Return API base URL with fallbacks.

    Precedence:
    1) Env vars: SMOOTHDEV_API_URL or SMOOTHDEV_API_DOMAIN
    2) ~/.smoothdevio/config.json: api_url or api_domain
    3) Bundled default_config.json in this package
    """
    url = ""
    domain = ""

    # 1) Environment variables
    url = os.getenv("SMOOTHDEV_API_URL") or ""
    domain = os.getenv("SMOOTHDEV_API_DOMAIN") or ""

    # 2) User config file
    if not (url or domain):
        cfg = _read_user_cfg()
        url = str(cfg.get("api_url", "") or "")
        domain = str(cfg.get("api_domain", "") or "")

    # 3) Bundled default config
    if not (url or domain):
        cfg = _read_default_cfg()
        url = str(cfg.get("api_url", "") or "")
        domain = str(cfg.get("api_domain", "") or "")

    # Normalize to full URL
    base = url.strip() if url else domain.strip()
    if not base:
        # Hard fallback to production domain if all else fails
        base = "rest.production.smoothdev.io"
    if "://" not in base:
        base = f"https://{base}"
    return base


def _http_timeout() -> int:
    """Resolve HTTP timeout from env, user config, or defaults.

    Order: env SMOOTHDEV_HTTP_TIMEOUT -> ~/.smoothdev*/config.json -> bundled default -> fallback.
    Bounded to [_HTTP_TIMEOUT_MIN, _HTTP_TIMEOUT_MAX].
    """
    val = os.getenv("SMOOTHDEV_HTTP_TIMEOUT") or ""
    t = 0
    try:
        if val:
            t = int(val)
    except Exception:
        t = 0
    if t <= 0:
        try:
            t = int(_read_user_cfg().get("http_timeout_seconds") or 0)
        except Exception:
            t = 0
    if t <= 0:
        try:
            t = int(_read_default_cfg().get("http_timeout_seconds") or 0)
        except Exception:
            t = 0
    if t <= 0:
        t = _DEFAULT_HTTP_TIMEOUT
    if t < _HTTP_TIMEOUT_MIN:
        t = _HTTP_TIMEOUT_MIN
    if t > _HTTP_TIMEOUT_MAX:
        t = _HTTP_TIMEOUT_MAX
    return t


def _maybe_retry_with_api_key(
    url: str,
    payload: Mapping[str, Any],
    first_resp: requests.Response,
    headers: dict[str, str],
    timeout_val: int,
) -> requests.Response:
    """Retry with API key if gateway rejects Authorization in auto mode.

    Returns the successful response or the last response if retry not applicable or fails.
    """
    if (
        first_resp.status_code == HTTPStatus.FORBIDDEN
        and "Invalid key=value pair (missing equal-sign) in Authorization header" in first_resp.text
        and effective_auth_mode(None) == "auto"
        and "Authorization" in headers
    ):
        try:
            api_key_hdr = get_auth_header(auth_mode="api-key")
        except Exception as e:
            logging.debug("Failed to get API key header: %s", e)
            return first_resp
        try:
            return requests.post(url, json=dict(payload), headers=api_key_hdr, timeout=timeout_val)
        except Exception as e:
            logging.debug("Failed to retry with API key: %s", e)
    return first_resp


def _encode_payload(payload: dict[str, Any]) -> str:
    """Encode payload using zlib compression and base64 to bypass WAF inspection.

    This matches the legacy CLI encoding strategy to prevent WAF from blocking
    legitimate diff content that may contain patterns resembling SQL injection,
    command injection, or other security threats.
    """
    # Use shorter field names for better compression
    compact_payload = {
        "d": payload.get("diff", ""),
        "f": payload.get("files_changed", []),
        "h": payload.get("head"),
        "i": payload.get("issue"),
        "l": payload.get("latency_profile", "balanced"),
    }
    # Minify JSON by removing whitespace
    payload_json = json.dumps(compact_payload, separators=(",", ":"))
    # Use maximum zlib compression level (9)
    compressed_payload = zlib.compress(payload_json.encode("utf-8"), level=9)
    # Use URL-safe base64 without padding
    encoded_bytes = base64.urlsafe_b64encode(compressed_payload).rstrip(b"=")
    return encoded_bytes.decode("utf-8")


def _encode_pr_payload(
    pr_data: dict[str, Any], operation_type: str = "pr_summary", pr_number: int | None = None
) -> tuple[str, str]:
    """Encode PR data using zlib compression and base64 to bypass WAF inspection.

    This matches the commit encoding strategy to prevent WAF from blocking
    PR diffs that may contain patterns resembling security threats.

    Args:
        pr_data: PR data dictionary
        operation_type: Type of operation - "pr_title" or "pr_summary"
        pr_number: PR number (required for pr_title operation)

    Returns:
        Tuple of (operation_type, encoded_payload)
    """
    # Use shorter field names for better compression
    compact_payload = {
        "t": pr_data.get("title", ""),
        "b": pr_data.get("body", ""),
        "c": pr_data.get("commits", []),
        "f": pr_data.get("files", []),
        "d": pr_data.get("diff", ""),
    }
    # Add pr_number if provided (needed for pr_title operation)
    if pr_number is not None:
        compact_payload["n"] = pr_number
    # Minify JSON by removing whitespace
    payload_json = json.dumps(compact_payload, separators=(",", ":"))
    # Use maximum zlib compression level (9)
    compressed_payload = zlib.compress(payload_json.encode("utf-8"), level=9)
    # Use URL-safe base64 without padding
    encoded_bytes = base64.urlsafe_b64encode(compressed_payload).rstrip(b"=")
    return operation_type, encoded_bytes.decode("utf-8")


def _encode_release_payload(release_data: dict[str, Any]) -> str:
    """Encode release data using zlib compression and base64 to bypass WAF inspection.

    Args:
        release_data: Release data dictionary with version, from_ref, to_ref, prs, commits

    Returns:
        Base64-encoded compressed payload
    """
    # Backend expects full field names for release_notes
    # operation_type is sent at root level, not in the payload
    compact_payload = {
        "version": release_data.get("version", ""),
        "release_date": release_data.get("release_date", ""),
        "prs": release_data.get("prs", []),
        "commits": release_data.get("commits", []),
    }
    # Minify JSON by removing whitespace
    payload_json = json.dumps(compact_payload, separators=(",", ":"))
    # Use maximum zlib compression level (9)
    compressed_payload = zlib.compress(payload_json.encode("utf-8"), level=9)
    # Use URL-safe base64 without padding
    encoded_bytes = base64.urlsafe_b64encode(compressed_payload).rstrip(b"=")
    return encoded_bytes.decode("utf-8")


def _decode_commit_message(encoded_message: str) -> str:
    """Decode a base64 and zlib compressed commit message."""
    try:
        # Decode base64 (add padding if needed)
        compressed_data = base64.b64decode(encoded_message + "==")
        # Decompress with zlib
        decompressed_data = zlib.decompress(compressed_data)
        # Decode bytes to string
        return decompressed_data.decode("utf-8")
    except Exception as e:
        logging.debug("Failed to decode commit message: %s", e)
        # If decoding fails, return as-is (might be unencoded response)
        return encoded_message


def _route_endpoint(base_path: str, auth_mode: str) -> str:
    """Route endpoint based on auth mode.

    JWT mode: /commit/generate, /pr/generate, /release/generate
    API Key mode: /api/commit/generate, /api/pr/generate, /api/release/generate
    Auto mode: try JWT first, will fallback via retry logic
    """
    # API key endpoints have /api prefix
    if auth_mode == "api-key" and not base_path.startswith("/api/"):
        return f"/api{base_path}"
    # JWT and auto mode use non-prefixed endpoints
    return base_path


def _post_json(path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    base = _api_base_url().rstrip("/")
    auth_mode = effective_auth_mode(None)
    routed_path = _route_endpoint(path, auth_mode)
    url = f"{base}/{routed_path.lstrip('/')}"
    headers = get_auth_header()
    timeout_val = _http_timeout()
    resp = requests.post(url, json=dict(payload), headers=headers, timeout=timeout_val)

    # Auto mode safety net: if we sent Authorization and gateway expects x-api-key
    # This will retry with /api/* endpoint if JWT fails
    if auth_mode == "auto" and resp.status_code == HTTPStatus.FORBIDDEN:
        # Try API key path
        api_key_path = _route_endpoint(path, "api-key")
        if api_key_path != routed_path:
            api_key_url = f"{base}/{api_key_path.lstrip('/')}"
            try:
                api_key_hdr = get_auth_header(auth_mode="api-key")
                resp = requests.post(
                    api_key_url, json=dict(payload), headers=api_key_hdr, timeout=timeout_val
                )
            except Exception as e:
                logging.debug("Failed to retry with API key: %s", e)

    if resp.status_code == HTTPStatus.OK:
        content_type = resp.headers.get("Content-Type")
        if content_type and "application/json" in content_type:
            try:
                data: dict[str, Any] = resp.json()
                return data  # noqa: TRY300
            except json.JSONDecodeError as e:
                logging.debug("Failed to decode JSON response: %s", e)
    if resp.status_code != HTTPStatus.OK:
        from click import ClickException

        msg = f"API error {resp.status_code} calling {url}: {resp.text}"
        raise ClickException(msg)
    # Should not reach here due to early returns, but keep defensive path
    data = resp.json()
    if not isinstance(data, dict):  # defensive
        from click import ClickException

        msg = f"Invalid API response format from {url}"
        raise ClickException(msg)
    return data


# Repository documentation (existing endpoints)


def analyze_repository(repo_path: str, git_url: str, branch: str) -> dict[str, Any]:
    return _post_json(
        "/analyze",
        {"repo_path": repo_path, "git_url": git_url, "branch": branch},
    )


def generate_repository_documentation(
    repo_path: str, git_url: str, branch: str, directory: str
) -> dict[str, Any]:
    return _post_json(
        "/generate",
        {
            "repo_path": repo_path,
            "git_url": git_url,
            "branch": branch,
            "directory": directory,
        },
    )


def submit_feedback(artifact: str, ref: str, rating: int, feedback: str) -> dict[str, Any]:
    return _post_json(
        "/feedback",
        {
            "artifact": artifact,
            "ref": ref,
            "rating": rating,
            "feedback": feedback,
        },
    )


# Commit / PR / Release generation (API-first; endpoints provided by backend)


def suggest_commit_message(
    *, payload: dict[str, Any] | None = None, **kwargs: Any
) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if payload:
        data.update(payload)
    # Allow callers passing legacy named args; only accept known keys
    for key in ("owner", "repo", "base", "head", "diff", "files_changed", "issue"):
        if key in kwargs and kwargs[key] is not None:
            data[key] = kwargs[key]

    # Encode payload to bypass WAF inspection of diff content
    encoded_payload = _encode_payload(data)
    response = _post_json("/commit/generate", {"payload": encoded_payload})

    # Decode the commit message if it's encoded
    if "commit_message" in response and isinstance(response["commit_message"], str):
        response["commit_message"] = _decode_commit_message(response["commit_message"])

    return response


def generate_pr_title(  # noqa: PLR0913
    *,
    payload: dict[str, Any] | None = None,
    owner: str | None = None,
    repo: str | None = None,
    pr_number: int | None = None,
    base: str | None = None,
    head: str | None = None,
    skip_judging: bool = False,
) -> dict[str, Any]:
    """Generate PR title from PR data.

    Args:
        payload: Full PR data dict with title, body, commits, files, diff
        owner/repo/pr_number/base/head: Legacy parameters (deprecated)
        skip_judging: Skip quality judging for faster generation
    """
    if payload is not None:
        # New path: encode full PR data with operation_type="pr_title"
        # Pass pr_number if available (required by backend)
        operation_type, encoded_payload = _encode_pr_payload(
            payload, operation_type="pr_title", pr_number=pr_number
        )
        request_payload: dict[str, Any] = {
            "operation_type": operation_type,
            "body": encoded_payload,
        }
        if skip_judging:
            request_payload["skip_judging"] = True
        return _post_json("/pr/generate", request_payload)

    # Legacy path: send coordinates (will likely fail without backend support)
    legacy_payload: dict[str, Any] = {}
    if owner:
        legacy_payload["owner"] = owner
    if repo:
        legacy_payload["repo"] = repo
    if pr_number is not None:
        legacy_payload["pr_number"] = pr_number
    if base is not None:
        legacy_payload["base"] = base
    if head is not None:
        legacy_payload["head"] = head
    return _post_json("/pr/generate", legacy_payload)


def generate_pr_summary(  # noqa: PLR0913
    *,
    payload: dict[str, Any] | None = None,
    owner: str | None = None,
    repo: str | None = None,
    pr_number: int | None = None,
    base: str | None = None,
    head: str | None = None,
    skip_judging: bool = False,
) -> dict[str, Any]:
    """Generate PR summary from PR data.

    Args:
        payload: Full PR data dict with title, body, commits, files, diff
        owner/repo/pr_number/base/head: Legacy parameters (deprecated)
        skip_judging: Skip quality judging for faster generation
    """
    if payload is not None:
        # New path: encode full PR data with operation_type="pr_summary"
        operation_type, encoded_payload = _encode_pr_payload(payload, operation_type="pr_summary")
        request_payload: dict[str, Any] = {
            "operation_type": operation_type,
            "body": encoded_payload,
        }
        if skip_judging:
            request_payload["skip_judging"] = True
        return _post_json("/pr/generate", request_payload)

    # Legacy path: send coordinates (will likely fail without backend support)
    legacy_payload: dict[str, Any] = {}
    if owner:
        legacy_payload["owner"] = owner
    if repo:
        legacy_payload["repo"] = repo
    if pr_number is not None:
        legacy_payload["pr_number"] = pr_number
    if base is not None:
        legacy_payload["base"] = base
    if head is not None:
        legacy_payload["head"] = head
    return _post_json("/pr/generate", legacy_payload)


def generate_release_notes(
    payload: dict[str, Any],
    latency_profile: str = "balanced",
    skip_judging: bool = False,
) -> dict[str, Any]:
    """
    Generate release notes from release data.

    Following DRY principle: Reuses payload encoding pattern.
    Following KISS principle: Simple interface matching PR generation.

    Args:
        payload: Release data dictionary (will be encoded)
        latency_profile: Performance profile (fastest/balanced/quality)
        skip_judging: Skip quality judging for faster generation

    Returns:
        Dictionary with generated_text, tokens_used, validation_status
    """
    # Encode release payload with appropriate structure
    encoded_payload = _encode_release_payload(payload)

    request_payload: dict[str, Any] = {
        "operation_type": "release_notes",
        "body": encoded_payload,
        "latency_profile": latency_profile,
    }
    if skip_judging:
        request_payload["skip_judging"] = True

    return _post_json("/release/generate", request_payload)
