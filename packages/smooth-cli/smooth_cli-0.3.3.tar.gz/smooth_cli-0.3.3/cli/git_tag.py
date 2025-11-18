"""Pure-Python Git tag operations using dulwich.

This module provides Git tag creation and push functionality without requiring
system git installation, using the dulwich pure-Python Git implementation.

Principles Applied:
- Single Responsibility: Each function handles one aspect of tag operations
- Dependency Inversion: Uses dulwich abstraction, not concrete git commands
- KISS: Simple, focused implementation
- Security: No shell execution, validates inputs
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from dulwich.client import get_transport_and_path
from dulwich.porcelain import open_repo_closing, tag_create

from cli.errors import GitTagErrors


class GitTagError(Exception):
    """Raised when git tag operation fails."""


class TagExistsError(GitTagError):
    """Raised when attempting to create a tag that already exists."""


class InvalidTagNameError(GitTagError):
    """Raised when tag name is invalid."""


def validate_tag_name(tag_name: str) -> None:
    """Validate tag name format.

    Args:
        tag_name: Tag name to validate

    Raises:
        InvalidTagNameError: If tag name is invalid
    """
    if not tag_name or not tag_name.strip():
        msg = "Tag name cannot be empty"
        raise InvalidTagNameError(msg)

    # Check for invalid characters
    invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\", "..", "@{", "//"]
    for char in invalid_chars:
        if char in tag_name:
            msg = f"Tag name cannot contain '{char}'"
            raise InvalidTagNameError(msg)

    # Cannot start with . or end with .lock
    if tag_name.startswith(".") or tag_name.endswith(".lock"):
        msg = "Tag name cannot start with '.' or end with '.lock'"
        raise InvalidTagNameError(msg)


def tag_exists(repo_path: Path, tag_name: str) -> bool:
    """Check if a tag already exists.

    Args:
        repo_path: Path to git repository root
        tag_name: Tag name to check

    Returns:
        True if tag exists, False otherwise
    """
    try:
        with open_repo_closing(str(repo_path)) as repo:
            tag_ref = f"refs/tags/{tag_name}".encode()
            return tag_ref in repo.refs
    except Exception as e:
        raise GitTagError(GitTagErrors.FAILED_TO_LIST.format(e)) from e


def create_tag(
    repo_path: Path,
    tag_name: str,
    message: str | None = None,
    commit_sha: str | None = None,
    tagger_name: str | None = None,
    tagger_email: str | None = None,
    annotated: bool = True,
) -> str:
    """Create a git tag using pure-Python operations.

    Args:
        repo_path: Path to git repository root
        tag_name: Name of the tag to create
        message: Tag message (required for annotated tags)
        commit_sha: Commit SHA to tag (default: HEAD)
        tagger_name: Tagger name (default: from git config)
        tagger_email: Tagger email (default: from git config)
        annotated: Create annotated tag (default: True)

    Returns:
        Tag name

    Raises:
        TagExistsError: If tag already exists
        GitTagError: If tag creation fails
        InvalidTagNameError: If tag name is invalid
    """
    # Validate tag name
    validate_tag_name(tag_name)

    # Check if tag exists
    if tag_exists(repo_path, tag_name):
        raise TagExistsError(GitTagErrors.TAG_EXISTS.format(tag_name))

    try:
        with open_repo_closing(str(repo_path)) as repo:
            # Get commit to tag (default to HEAD)
            if commit_sha:
                target = commit_sha.encode() if isinstance(commit_sha, str) else commit_sha
            else:
                target = repo.refs[b"HEAD"]

            # Get tagger info from config if not provided
            config = repo.get_config()
            if tagger_name is None:
                tagger_name = (
                    config.get((b"user",), b"name").decode("utf-8")
                    if config.has_section((b"user",))
                    else "Unknown"
                )
            if tagger_email is None:
                tagger_email = (
                    config.get((b"user",), b"email").decode("utf-8")
                    if config.has_section((b"user",))
                    else "unknown@example.com"
                )

            if annotated:
                # Create annotated tag
                if not message:
                    message = f"Release {tag_name}"

                tag_create(
                    str(repo_path),
                    tag=tag_name.encode(),
                    message=message.encode(),
                    author=f"{tagger_name} <{tagger_email}>".encode(),
                    objectish=target,
                    tag_time=int(time.time()),
                    tag_timezone=0,
                )
            else:
                # Create lightweight tag
                tag_ref = f"refs/tags/{tag_name}".encode()
                repo.refs[tag_ref] = target

            return tag_name

    except TagExistsError:
        raise
    except Exception as e:
        raise GitTagError(GitTagErrors.FAILED_TO_CREATE.format(e)) from e


def push_tag(
    repo_path: Path,
    tag_name: str,
    remote: str = "origin",
) -> None:
    """Push a tag to remote repository.

    Args:
        repo_path: Path to git repository root
        tag_name: Name of the tag to push
        remote: Remote name (default: origin)

    Raises:
        GitTagError: If push operation fails
    """
    try:
        with open_repo_closing(str(repo_path)) as repo:
            # Get remote URL
            config = repo.get_config()
            remote_url = config.get((b"remote", remote.encode()), b"url")
            if not remote_url:
                msg = f"Remote '{remote}' not found"
                raise GitTagError(msg)

            remote_url = remote_url.decode("utf-8")

            # Get tag ref
            tag_ref = f"refs/tags/{tag_name}".encode()
            if tag_ref not in repo.refs:
                msg = f"Tag '{tag_name}' not found"
                raise GitTagError(msg)

            tag_sha = repo.refs[tag_ref]

            # Push tag to remote
            client, path = get_transport_and_path(remote_url)

            def determine_wants(refs: dict[bytes, bytes]) -> dict[bytes, bytes]:  # noqa: ARG001
                """Determine what refs to update on remote."""
                return {tag_ref: tag_sha}

            def generate_pack_data(
                have: set[bytes], want: set[bytes], oids: set[bytes] | None = None
            ) -> tuple[int, list[Any]]:
                """Generate pack data for objects to send."""
                result: tuple[int, list[Any]] = repo.object_store.generate_pack_data(
                    have, want, oids=oids
                )  # type: ignore[assignment]
                return result

            client.send_pack(
                path,
                determine_wants,
                generate_pack_data,
            )

    except Exception as e:
        raise GitTagError(GitTagErrors.FAILED_TO_PUSH.format(e)) from e


def list_tags(repo_path: Path) -> list[str]:
    """List all tags in the repository.

    Args:
        repo_path: Path to git repository root

    Returns:
        List of tag names
    """
    try:
        with open_repo_closing(str(repo_path)) as repo:
            tags = []
            for ref in repo.refs:
                if ref.startswith(b"refs/tags/"):
                    tag_name = ref[len(b"refs/tags/") :].decode("utf-8")
                    tags.append(tag_name)
            return sorted(tags)
    except Exception as e:
        raise GitTagError(GitTagErrors.FAILED_TO_LIST.format(e)) from e


def delete_tag(repo_path: Path, tag_name: str) -> None:
    """Delete a local tag.

    Args:
        repo_path: Path to git repository root
        tag_name: Name of the tag to delete

    Raises:
        GitTagError: If tag deletion fails
    """
    try:
        with open_repo_closing(str(repo_path)) as repo:
            tag_ref = f"refs/tags/{tag_name}".encode()
            if tag_ref not in repo.refs:
                raise GitTagError(GitTagErrors.TAG_NOT_FOUND.format(tag_name))

            del repo.refs[tag_ref]
    except Exception as e:
        raise GitTagError(GitTagErrors.FAILED_TO_DELETE.format(e)) from e
