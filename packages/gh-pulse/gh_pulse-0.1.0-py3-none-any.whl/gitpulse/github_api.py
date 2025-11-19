"""GitHub REST API client with caching support."""

import os
from pathlib import Path
from typing import Optional

import httpx
from rich.console import Console

from .cache import get_cache
from .models import Release, RepoStats, TopRepo, UserStats

console = Console()


class GitHubAPIError(Exception):
    """GitHub API error."""

    pass


class GitHubClient:
    """GitHub REST API client."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, use_cache: bool = True):
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token
            use_cache: Whether to use cache (default: True)
        """
        self.token = token or self._load_token()
        self.use_cache = use_cache
        self.cache = get_cache()

        # Setup HTTP client
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "gitpulse-cli",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        self.client = httpx.Client(headers=headers, timeout=30.0)

    def _load_token(self) -> Optional[str]:
        """Load token from config file or environment."""
        # Try environment variable first
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token

        # Try config file
        config_path = Path.home() / ".gitpulse" / "config"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return f.read().strip()

        return None

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to GitHub API.

        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for httpx

        Returns:
            Response JSON

        Raises:
            GitHubAPIError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise GitHubAPIError(
                    "Unauthorized. Please set GitHub token with 'gitpulse auth'"
                ) from e
            elif e.response.status_code == 404:
                raise GitHubAPIError("Resource not found") from e
            elif e.response.status_code == 403:
                raise GitHubAPIError(
                    "Rate limit exceeded or access forbidden. Try again later."
                ) from e
            else:
                raise GitHubAPIError(f"API error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise GitHubAPIError(f"Request failed: {str(e)}") from e

    def get_repo_stats(self, repo: str, no_cache: bool = False) -> RepoStats:
        """Get repository statistics.

        Args:
            repo: Repository in format 'owner/name'
            no_cache: Force refresh from API

        Returns:
            Repository statistics
        """
        cache_key = f"repo:{repo}"

        # Try cache first
        if self.use_cache and not no_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return RepoStats(**cached)

        # Fetch from API
        data = self._request("GET", f"/repos/{repo}")

        # Cache result
        if self.use_cache:
            self.cache.set(cache_key, data)

        return RepoStats(**data)

    def get_repo_releases(self, repo: str, limit: int = 5) -> list[Release]:
        """Get repository releases.

        Args:
            repo: Repository in format 'owner/name'
            limit: Maximum number of releases to fetch

        Returns:
            List of releases
        """
        data = self._request("GET", f"/repos/{repo}/releases", params={"per_page": limit})
        return [Release(**item) for item in data]

    def get_latest_release(self, repo: str) -> Optional[Release]:
        """Get latest release for repository.

        Args:
            repo: Repository in format 'owner/name'

        Returns:
            Latest release or None if no releases
        """
        try:
            data = self._request("GET", f"/repos/{repo}/releases/latest")
            return Release(**data)
        except GitHubAPIError:
            return None

    def get_user_stats(self, username: str, no_cache: bool = False) -> UserStats:
        """Get user statistics.

        Args:
            username: GitHub username
            no_cache: Force refresh from API

        Returns:
            User statistics
        """
        cache_key = f"user:{username}"

        # Try cache first
        if self.use_cache and not no_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return UserStats(**cached)

        # Fetch from API
        data = self._request("GET", f"/users/{username}")

        # Cache result
        if self.use_cache:
            self.cache.set(cache_key, data)

        return UserStats(**data)

    def get_user_repos(
        self, username: str, limit: int = 100, sort: str = "updated"
    ) -> list[dict]:
        """Get user repositories.

        Args:
            username: GitHub username
            limit: Maximum number of repos to fetch
            sort: Sort field (updated, pushed, created, full_name)

        Returns:
            List of repository data
        """
        data = self._request(
            "GET",
            f"/users/{username}/repos",
            params={"per_page": limit, "sort": sort},
        )
        return data

    def get_top_repos(self, username: str, limit: int = 3) -> list[TopRepo]:
        """Get top repositories by stars.

        Args:
            username: GitHub username
            limit: Number of top repos to return

        Returns:
            List of top repositories
        """
        repos = self.get_user_repos(username, limit=100)

        # Sort by stars
        sorted_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)

        # Get top N
        top_repos = sorted_repos[:limit]

        return [
            TopRepo(
                name=r["name"],
                full_name=r["full_name"],
                stars=r["stargazers_count"],
                description=r.get("description"),
                language=r.get("language"),
                html_url=r["html_url"],
            )
            for r in top_repos
        ]

    def close(self):
        """Close HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
