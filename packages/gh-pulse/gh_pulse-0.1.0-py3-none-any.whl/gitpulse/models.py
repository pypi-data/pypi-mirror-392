"""Pydantic models for GitHub API data."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RepoStats(BaseModel):
    """Statistics for a GitHub repository."""

    name: str
    full_name: str
    description: Optional[str] = None
    stars: int = Field(alias="stargazers_count")
    forks: int = Field(alias="forks_count")
    watchers: int = Field(alias="watchers_count")
    open_issues: int = Field(alias="open_issues_count")
    language: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    size: int  # KB
    default_branch: str
    homepage: Optional[str] = None
    topics: list[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class Release(BaseModel):
    """GitHub release information."""

    tag_name: str
    name: Optional[str] = None
    published_at: datetime
    draft: bool = False
    prerelease: bool = False
    html_url: str


class UserStats(BaseModel):
    """Statistics for a GitHub user."""

    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: datetime
    updated_at: datetime
    avatar_url: str
    html_url: str
    blog: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None


class TopRepo(BaseModel):
    """Top repository with star count."""

    name: str
    full_name: str
    stars: int
    description: Optional[str] = None
    language: Optional[str] = None
    html_url: str


class CacheEntry(BaseModel):
    """Cache entry with timestamp."""

    data: dict
    cached_at: datetime
    ttl_seconds: int = 3600  # 1 hour default

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        age = (datetime.now() - self.cached_at).total_seconds()
        return age > self.ttl_seconds
