"""Configuration management for user and repository settings.

This module manages two types of configuration:
1. User config: ~/.smoothdevio/config.json (credentials, global defaults)
2. Repository config: .smoothdev.json (team settings, no credentials)

Principles Applied:
- Single Responsibility: Each function manages one aspect of configuration
- Open/Closed: Extensible for new config fields without modification
- Interface Segregation: Separate functions for user vs repo config
- Dependency Inversion: Uses Path abstraction, not concrete file operations
- DRY: Shared validation and loading logic
- KISS: Simple JSON-based configuration
- YAGNI: Only implements required features
- Separation of Concerns: Config I/O separate from validation
- Law of Demeter: Minimal coupling with other modules
"""

import json
import os
from contextlib import suppress
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ConfigDefaults:
    """Default configuration values.

    Attributes:
        owner: Default GitHub owner/organization
        repo: Default repository name
        base_branch: Default base branch
        output: Default output format
        verbose: Default verbose mode
        auto_commit: Whether to automatically commit after generating commit message
    """

    owner: Optional[str] = None
    repo: Optional[str] = None
    base_branch: Optional[str] = None
    output: str = "text"
    verbose: bool = False
    auto_commit: bool = False


@dataclass
class ReleaseConfig:
    """Release-specific configuration.

    Attributes:
        tag_prefix: Prefix for release tags (e.g., 'v')
        include_prerelease: Whether to include pre-release versions
    """

    tag_prefix: str = "v"
    include_prerelease: bool = False


@dataclass
class UserConfig:
    """User-level configuration (stored in ~/.smoothdevio/config.json).

    Contains credentials and personal preferences.

    Attributes:
        api_key: SmoothDev API key
        github_token: GitHub personal access token
        api_domain: API domain override
        defaults: Default values for commands
        repository_overrides: Per-repository setting overrides
    """

    api_key: Optional[str] = None
    github_token: Optional[str] = None
    api_domain: Optional[str] = None
    defaults: ConfigDefaults = field(default_factory=ConfigDefaults)
    repository_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            k: v
            for k, v in asdict(self).items()
            if v is not None and (not isinstance(v, dict) or v)
        }


@dataclass
class RepositoryConfig:
    """Repository-level configuration (stored in .smoothdev.json).

    Contains team settings, NO credentials allowed.

    Attributes:
        owner: Repository owner/organization
        repo: Repository name
        defaults: Default values for commands
        release: Release-specific settings
    """

    owner: Optional[str] = None
    repo: Optional[str] = None
    defaults: ConfigDefaults = field(default_factory=ConfigDefaults)
    release: ReleaseConfig = field(default_factory=ReleaseConfig)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            k: v
            for k, v in asdict(self).items()
            if v is not None and (not isinstance(v, dict) or v)
        }


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""


class ConfigNotFoundError(Exception):
    """Raised when configuration file is not found."""


def get_user_config_path() -> Path:
    """Get the path to the user configuration file.

    Single Responsibility: Determine user config location.

    Returns:
        Path to ~/.smoothdevio/config.json
    """
    home = Path.home()
    return home / ".smoothdevio" / "config.json"


def find_repository_config_file(start_path: Optional[Path] = None) -> Optional[Path]:
    """Search upward from start_path for .smoothdev.json file.

    Single Responsibility: Locate repository config file.

    Args:
        start_path: Starting directory (default: current directory)

    Returns:
        Path to .smoothdev.json or None if not found
    """
    current = start_path or Path.cwd()

    # Search upward until we hit the root
    while current != current.parent:
        config_file = current / ".smoothdev.json"
        if config_file.exists():
            return config_file
        current = current.parent

    # Check root directory
    config_file = current / ".smoothdev.json"
    if config_file.exists():
        return config_file

    return None


def _validate_no_credentials(config_dict: dict[str, Any]) -> None:
    """Validate that repository config contains no credentials.

    Single Responsibility: Enforce security policy.

    Args:
        config_dict: Configuration dictionary to validate

    Raises:
        ConfigValidationError: If credentials are found
    """
    forbidden_keys = {
        "api_key",
        "github_token",
        "auth_token",
        "token",
        "password",
        "secret",
    }

    def check_dict(d: dict[str, Any], path: str = "") -> None:
        """Recursively check for forbidden keys."""
        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key

            # Check if key is forbidden
            if key.lower() in forbidden_keys:
                raise ConfigValidationError(
                    f"Repository config cannot contain credentials. "
                    f"Found forbidden key: {current_path}"
                )

            # Recursively check nested dictionaries
            if isinstance(value, dict):
                check_dict(value, current_path)

    check_dict(config_dict)


def _read_raw_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    # Let JSON/IO errors propagate to callers so they can handle backups
    return json.loads(path.read_text())  # type: ignore[no-any-return]


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def load_user_config() -> UserConfig:
    """Load user configuration from ~/.smoothdevio/config.json.

    Single Responsibility: Load and parse user config.

    Returns:
        UserConfig object (empty if file doesn't exist)
    """
    config_path = get_user_config_path()

    if not config_path.exists():
        return UserConfig()

    try:
        with open(config_path) as f:
            data = json.load(f)

        # Extract only fields that UserConfig accepts
        valid_fields = {}
        if "api_key" in data:
            valid_fields["api_key"] = data["api_key"]
        if "github_token" in data:
            valid_fields["github_token"] = data["github_token"]
        if "api_domain" in data:
            valid_fields["api_domain"] = data["api_domain"]
        if "defaults" in data:
            valid_fields["defaults"] = ConfigDefaults(**data["defaults"])
        elif any(
            k in data for k in ["owner", "repo", "base_branch", "output", "verbose", "auto_commit"]
        ):
            # Legacy format - extract defaults from top level
            defaults_data = {}
            for key in ["owner", "repo", "base_branch", "output", "verbose", "auto_commit"]:
                if key in data:
                    defaults_data[key] = data[key]
            if defaults_data:
                valid_fields["defaults"] = ConfigDefaults(**defaults_data)
        if "repository_overrides" in data:
            valid_fields["repository_overrides"] = data["repository_overrides"]

        return UserConfig(**valid_fields)
    except (json.JSONDecodeError, TypeError) as e:
        raise ConfigValidationError(f"Invalid user config format: {e}") from e


def load_repository_config(path: Optional[Path] = None) -> Optional[RepositoryConfig]:
    """Load repository configuration from .smoothdev.json.

    Single Responsibility: Load and parse repository config.

    Args:
        path: Starting path for search (default: current directory)

    Returns:
        RepositoryConfig object or None if not found

    Raises:
        ConfigValidationError: If config contains credentials or is invalid
    """
    config_file = find_repository_config_file(path)

    if not config_file:
        return None

    try:
        with open(config_file) as f:
            data = json.load(f)

        # Validate no credentials
        _validate_no_credentials(data)

        # Parse nested structures
        if "defaults" in data and isinstance(data["defaults"], dict):
            data["defaults"] = ConfigDefaults(**data["defaults"])

        if "release" in data and isinstance(data["release"], dict):
            data["release"] = ReleaseConfig(**data["release"])

        return RepositoryConfig(**data)
    except (json.JSONDecodeError, TypeError) as e:
        raise ConfigValidationError(f"Invalid repository config format: {e}") from e


def save_user_config(config: UserConfig) -> None:
    """Save user configuration to ~/.smoothdevio/config.json.

    Single Responsibility: Persist user config.

    Args:
        config: UserConfig object to save
    """
    config_path = get_user_config_path()

    existing: dict[str, Any] = {}
    try:
        existing = _read_raw_json(config_path)
    except Exception:
        if config_path.exists():
            backup = config_path.with_suffix(".bak")
            with suppress(Exception):
                config_path.replace(backup)
        existing = {}

    merged = _deep_merge(existing, config.to_dict())
    _atomic_write_json(config_path, merged)
    with suppress(Exception):
        os.chmod(config_path, 0o600)


def save_repository_config(config: RepositoryConfig, path: Optional[Path] = None) -> None:
    """Save repository configuration to .smoothdev.json.

    Single Responsibility: Persist repository config.

    Args:
        config: RepositoryConfig object to save
        path: Directory to save config in (default: current directory)

    Raises:
        ConfigValidationError: If config contains credentials
    """
    config_dict = config.to_dict()

    target_dir = path or Path.cwd()
    config_file = target_dir / ".smoothdev.json"

    existing: dict[str, Any] = {}
    try:
        if config_file.exists():
            existing = _read_raw_json(config_file)
    except Exception:
        backup = config_file.with_suffix(".bak")
        with suppress(Exception):
            config_file.replace(backup)
        existing = {}

    merged = _deep_merge(existing, config_dict)

    _validate_no_credentials(merged)
    _atomic_write_json(config_file, merged)


def get_config_value(
    config: UserConfig | RepositoryConfig,
    key_path: str,
) -> Any:
    """Get a configuration value using dot notation.

    Single Responsibility: Retrieve nested config values.

    Args:
        config: Configuration object
        key_path: Dot-separated path (e.g., 'defaults.owner')

    Returns:
        Configuration value or None if not found

    Examples:
        >>> config = UserConfig(defaults=ConfigDefaults(owner="smoothdev-io"))
        >>> get_config_value(config, "defaults.owner")
        'smoothdev-io'
    """
    keys = key_path.split(".")
    value: Any = config

    for key in keys:
        if hasattr(value, key):
            value = getattr(value, key)
        elif isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None

    return value


def set_config_value(
    config: UserConfig | RepositoryConfig,
    key_path: str,
    value: Any,
) -> None:
    """Set a configuration value using dot notation.

    Single Responsibility: Update nested config values.

    Args:
        config: Configuration object to modify
        key_path: Dot-separated path (e.g., 'defaults.owner')
        value: Value to set

    Raises:
        ValueError: If key path is invalid

    Examples:
        >>> config = UserConfig()
        >>> set_config_value(config, "defaults.owner", "smoothdev-io")
        >>> config.defaults.owner
        'smoothdev-io'
    """
    keys = key_path.split(".")

    if len(keys) == 1:
        # Top-level attribute
        if hasattr(config, keys[0]):
            setattr(config, keys[0], value)
        else:
            raise ValueError(f"Invalid config key: {keys[0]}")
    else:
        # Nested attribute
        obj: Any = config
        for key in keys[:-1]:
            if hasattr(obj, key):
                obj = getattr(obj, key)
            else:
                raise ValueError(f"Invalid config path: {'.'.join(keys[:-1])}")

        final_key = keys[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        else:
            raise ValueError(f"Invalid config key: {key_path}")


def merge_configs(
    user_config: UserConfig,
    repo_config: Optional[RepositoryConfig],
) -> dict[str, Any]:
    """Merge user and repository configurations.

    Single Responsibility: Combine configuration sources.
    Repository config takes precedence over user config for overlapping keys.

    Args:
        user_config: User configuration
        repo_config: Repository configuration (optional)

    Returns:
        Merged configuration dictionary
    """
    merged: dict[str, Any] = {}

    # Start with user config defaults
    if user_config.defaults:
        merged.update(
            {
                "owner": user_config.defaults.owner,
                "repo": user_config.defaults.repo,
                "base_branch": user_config.defaults.base_branch,
                "output": user_config.defaults.output,
                "verbose": user_config.defaults.verbose,
                "auto_commit": user_config.defaults.auto_commit,
            }
        )

    # Override with repository config if present
    if repo_config:
        if repo_config.owner:
            merged["owner"] = repo_config.owner
        if repo_config.repo:
            merged["repo"] = repo_config.repo
        if repo_config.defaults:
            if repo_config.defaults.base_branch:
                merged["base_branch"] = repo_config.defaults.base_branch
            if repo_config.defaults.output:
                merged["output"] = repo_config.defaults.output
            if repo_config.defaults.verbose is not None:
                merged["verbose"] = repo_config.defaults.verbose
            if repo_config.defaults.auto_commit is not None:
                merged["auto_commit"] = repo_config.defaults.auto_commit

    # Remove None values
    return {k: v for k, v in merged.items() if v is not None}
