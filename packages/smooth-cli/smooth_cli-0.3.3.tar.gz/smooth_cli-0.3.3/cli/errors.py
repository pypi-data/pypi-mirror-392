"""Error messages and exception classes for the CLI.

This module centralizes error messages to comply with ruff TRY003/EM101/EM102 rules.
All exception messages should be defined here as constants.

Principles Applied:
- DRY: Single source of truth for error messages
- Maintainability: Easy to update messages in one place
- Testability: Messages can be tested independently
"""

from __future__ import annotations


# Git Tag Error Messages
class GitTagErrors:
    """Error messages for git tag operations."""

    INVALID_TAG_NAME = "Invalid tag name: {}"
    TAG_EXISTS = "Tag '{}' already exists"
    TAG_NOT_FOUND = "Tag '{}' not found"
    FAILED_TO_CREATE = "Failed to create tag: {}"
    FAILED_TO_PUSH = "Failed to push tag: {}"
    FAILED_TO_LIST = "Failed to list tags: {}"
    FAILED_TO_DELETE = "Failed to delete tag: {}"


# GitHub Operations Error Messages
class GitHubErrors:
    """Error messages for GitHub API operations."""

    FAILED_TO_CREATE_PR = "Failed to create PR: {}"
    FAILED_TO_UPDATE_PR = "Failed to update PR: {}"
    FAILED_TO_CREATE_RELEASE = "Failed to create release: {}"
    FAILED_TO_GET_BRANCH = "Failed to get current branch: {}"
    NO_TOKEN = "GitHub token not found. Set GITHUB_TOKEN or GH_TOKEN environment variable."  # nosec B105 - Not a password, just error message
    INVALID_RESPONSE = "Invalid response from GitHub API: {}"


# Git Commit Error Messages
class GitCommitErrors:
    """Error messages for git commit operations."""

    NO_STAGED_CHANGES = "No staged changes to commit"
    FAILED_TO_COMMIT = "Failed to commit changes: {}"
    FAILED_TO_GET_DIFF = "Failed to get diff: {}"


# API Client Error Messages
class APIErrors:
    """Error messages for API client operations."""

    REQUEST_FAILED = "API request failed: {}"
    INVALID_RESPONSE = "Invalid API response: {}"
    TIMEOUT = "API request timed out after {} seconds"
    AUTHENTICATION_FAILED = "Authentication failed: {}"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded. Try again later."


# Configuration Error Messages
class ConfigErrors:
    """Error messages for configuration operations."""

    INVALID_CONFIG = "Invalid configuration: {}"
    CONFIG_NOT_FOUND = "Configuration file not found: {}"
    FAILED_TO_READ = "Failed to read configuration: {}"
    FAILED_TO_WRITE = "Failed to write configuration: {}"
    INVALID_SCOPE = "Invalid scope '{}'. Must be 'user' or 'repo'."


# Context Resolution Error Messages
class ContextErrors:
    """Error messages for context resolution."""

    MISSING_REQUIRED = "Missing required context: {}"
    INVALID_CONTEXT = "Invalid context: {}"
    RESOLUTION_FAILED = "Context resolution failed: {}"


# CLI Command Error Messages
class CommandErrors:
    """Error messages for CLI commands."""

    PUSH_REQUIRES_PARAMS = "--push requires --owner, --repo, and --pr-number"
    PR_NUMBER_REQUIRED = "PR number is required. Provide --pr-number flag."
    INVALID_OUTPUT_FORMAT = "Invalid output format '{}'. Must be 'text' or 'json'."
    FAILED_TO_FETCH_PR = "Error fetching PR data: {}"
    FAILED_TO_FETCH_RELEASE = "Error fetching release data: {}"
