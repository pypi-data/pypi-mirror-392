"""Badge generation for GitHub repositories."""

from typing import Optional

from .models import RepoStats, Release


class BadgeGenerator:
    """Generate Markdown badges for GitHub repositories."""

    SHIELDS_IO = "https://img.shields.io"

    @staticmethod
    def stars(repo: str, count: Optional[int] = None) -> str:
        """Generate stars badge.

        Args:
            repo: Repository in format 'owner/name'
            count: Star count (if None, uses dynamic badge)

        Returns:
            Markdown badge
        """
        if count is not None:
            url = f"{BadgeGenerator.SHIELDS_IO}/badge/stars-{count}-blue?style=flat-square"
        else:
            url = f"{BadgeGenerator.SHIELDS_IO}/github/stars/{repo}?style=flat-square"
        return f"![Stars]({url})"

    @staticmethod
    def forks(repo: str, count: Optional[int] = None) -> str:
        """Generate forks badge."""
        if count is not None:
            url = f"{BadgeGenerator.SHIELDS_IO}/badge/forks-{count}-blue?style=flat-square"
        else:
            url = f"{BadgeGenerator.SHIELDS_IO}/github/forks/{repo}?style=flat-square"
        return f"![Forks]({url})"

    @staticmethod
    def issues(repo: str, count: Optional[int] = None) -> str:
        """Generate open issues badge."""
        if count is not None:
            url = f"{BadgeGenerator.SHIELDS_IO}/badge/issues-{count}-blue?style=flat-square"
        else:
            url = f"{BadgeGenerator.SHIELDS_IO}/github/issues/{repo}?style=flat-square"
        return f"![Issues]({url})"

    @staticmethod
    def license(repo: str) -> str:
        """Generate license badge."""
        url = f"{BadgeGenerator.SHIELDS_IO}/github/license/{repo}?style=flat-square"
        return f"![License]({url})"

    @staticmethod
    def release(repo: str, tag: Optional[str] = None) -> str:
        """Generate latest release badge."""
        if tag:
            url = f"{BadgeGenerator.SHIELDS_IO}/badge/release-{tag}-blue?style=flat-square"
        else:
            url = f"{BadgeGenerator.SHIELDS_IO}/github/v/release/{repo}?style=flat-square"
        return f"![Release]({url})"

    @staticmethod
    def language(repo: str, lang: Optional[str] = None) -> str:
        """Generate top language badge."""
        if lang:
            url = f"{BadgeGenerator.SHIELDS_IO}/badge/language-{lang}-blue?style=flat-square"
        else:
            url = f"{BadgeGenerator.SHIELDS_IO}/github/languages/top/{repo}?style=flat-square"
        return f"![Language]({url})"

    @staticmethod
    def downloads(repo: str) -> str:
        """Generate downloads badge."""
        url = (
            f"{BadgeGenerator.SHIELDS_IO}/github/downloads/{repo}/total?style=flat-square"
        )
        return f"![Downloads]({url})"

    @staticmethod
    def last_commit(repo: str) -> str:
        """Generate last commit badge."""
        url = f"{BadgeGenerator.SHIELDS_IO}/github/last-commit/{repo}?style=flat-square"
        return f"![Last Commit]({url})"

    @classmethod
    def generate_full_set(
        cls,
        repo: str,
        stats: Optional[RepoStats] = None,
        latest_release: Optional[Release] = None,
    ) -> str:
        """Generate full badge set for repository.

        Args:
            repo: Repository in format 'owner/name'
            stats: Repository statistics (optional, for static badges)
            latest_release: Latest release info (optional)

        Returns:
            Markdown block with all badges
        """
        badges = []

        # Basic badges
        if stats:
            badges.append(cls.stars(repo, stats.stars))
            badges.append(cls.forks(repo, stats.forks))
            badges.append(cls.issues(repo, stats.open_issues))
            if stats.language:
                badges.append(cls.language(repo, stats.language))
        else:
            badges.append(cls.stars(repo))
            badges.append(cls.forks(repo))
            badges.append(cls.issues(repo))
            badges.append(cls.language(repo))

        # Release badge
        if latest_release:
            badges.append(cls.release(repo, latest_release.tag_name))
        else:
            badges.append(cls.release(repo))

        # Additional badges
        badges.append(cls.downloads(repo))
        badges.append(cls.last_commit(repo))
        badges.append(cls.license(repo))

        # Format as markdown
        return " ".join(badges)

    @classmethod
    def generate_custom(cls, repo: str, badge_types: list[str]) -> str:
        """Generate custom badge set.

        Args:
            repo: Repository in format 'owner/name'
            badge_types: List of badge types (stars, forks, issues, etc.)

        Returns:
            Markdown block with selected badges
        """
        badge_map = {
            "stars": cls.stars,
            "forks": cls.forks,
            "issues": cls.issues,
            "license": cls.license,
            "release": cls.release,
            "language": cls.language,
            "downloads": cls.downloads,
            "commit": cls.last_commit,
        }

        badges = []
        for badge_type in badge_types:
            if badge_type in badge_map:
                badges.append(badge_map[badge_type](repo))

        return " ".join(badges)
