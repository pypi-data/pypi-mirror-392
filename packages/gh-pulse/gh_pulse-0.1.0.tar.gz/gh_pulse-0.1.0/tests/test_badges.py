"""Tests for badge generation."""

import pytest
from gitpulse.badges import BadgeGenerator


def test_stars_badge():
    """Test stars badge generation."""
    badge = BadgeGenerator.stars("owner/repo", count=100)
    assert "stars-100" in badge
    assert "![Stars]" in badge


def test_forks_badge():
    """Test forks badge generation."""
    badge = BadgeGenerator.forks("owner/repo", count=50)
    assert "forks-50" in badge
    assert "![Forks]" in badge


def test_issues_badge():
    """Test issues badge generation."""
    badge = BadgeGenerator.issues("owner/repo", count=10)
    assert "issues-10" in badge
    assert "![Issues]" in badge


def test_release_badge():
    """Test release badge generation."""
    badge = BadgeGenerator.release("owner/repo", tag="v1.0.0")
    assert "release-v1.0.0" in badge
    assert "![Release]" in badge


def test_custom_badges():
    """Test custom badge generation."""
    badges = BadgeGenerator.generate_custom("owner/repo", ["stars", "forks"])
    assert "![Stars]" in badges
    assert "![Forks]" in badges


def test_full_badge_set():
    """Test full badge set generation."""
    badges = BadgeGenerator.generate_full_set("owner/repo")
    assert "![Stars]" in badges
    assert "![Forks]" in badges
    assert "![License]" in badges
