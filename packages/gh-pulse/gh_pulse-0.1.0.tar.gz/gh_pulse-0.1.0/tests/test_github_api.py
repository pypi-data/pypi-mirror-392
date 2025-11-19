"""Tests for GitHub API client."""

import pytest
from gitpulse.github_api import GitHubClient, GitHubAPIError


def test_github_client_initialization():
    """Test GitHub client can be initialized."""
    client = GitHubClient(token="test_token")
    assert client.token == "test_token"
    assert client.BASE_URL == "https://api.github.com"
    client.close()


def test_github_client_context_manager():
    """Test GitHub client works as context manager."""
    with GitHubClient(token="test_token") as client:
        assert client.token == "test_token"


def test_load_token_from_env(monkeypatch):
    """Test loading token from environment variable."""
    monkeypatch.setenv("GITHUB_TOKEN", "env_token")
    client = GitHubClient()
    assert client.token == "env_token"
    client.close()


# Note: Add more comprehensive tests with mocked API responses in production
