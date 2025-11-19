"""gitpulse CLI - GitHub productivity analytics tool."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from . import __version__
from .github_api import GitHubClient, GitHubAPIError
from .badges import BadgeGenerator

app = typer.Typer(
    name="gitpulse",
    help="GitHub productivity CLI for analytics, badges, and automation",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"gitpulse version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """gitpulse - GitHub productivity CLI."""
    pass


@app.command()
def auth(
    token: str = typer.Argument(..., help="GitHub personal access token"),
):
    """Save GitHub token for authentication.

    Example:
        gitpulse auth ghp_xxxxxxxxxxxxx
    """
    config_dir = Path.home() / ".gitpulse"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "config"
    config_file.write_text(token, encoding="utf-8")
    config_file.chmod(0o600)  # Secure permissions

    console.print("[green]✓[/green] GitHub token saved successfully!")
    console.print(f"[dim]Stored in: {config_file}[/dim]")


@app.command(name="repo")
def repo_stats(
    repo: str = typer.Argument(..., help="Repository in format 'owner/name'"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Force refresh from API"),
):
    """Show repository statistics.

    Example:
        gitpulse repo ruslanlap/PowerToysRun-QuickAi
    """
    try:
        with GitHubClient() as client:
            console.print(f"[cyan]Fetching stats for {repo}...[/cyan]")
            stats = client.get_repo_stats(repo, no_cache=no_cache)

            # Create table
            table = Table(
                title=f"📊 Repository: {stats.full_name}",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Metric", style="bold")
            table.add_column("Value", justify="right")

            # Add rows
            table.add_row("⭐ Stars", str(stats.stars))
            table.add_row("🍴 Forks", str(stats.forks))
            table.add_row("👀 Watchers", str(stats.watchers))
            table.add_row("📖 Open Issues", str(stats.open_issues))
            if stats.language:
                table.add_row("💻 Language", stats.language)
            table.add_row("📦 Size", f"{stats.size} KB")
            table.add_row("🌿 Default Branch", stats.default_branch)
            table.add_row("📅 Created", stats.created_at.strftime("%Y-%m-%d"))
            table.add_row("🔄 Last Updated", stats.updated_at.strftime("%Y-%m-%d"))
            table.add_row("📤 Last Push", stats.pushed_at.strftime("%Y-%m-%d"))

            console.print(table)

            # Description
            if stats.description:
                console.print(
                    Panel(stats.description, title="Description", border_style="dim")
                )

            # Topics
            if stats.topics:
                console.print("\n[bold]Topics:[/bold]", ", ".join(stats.topics))

            # Get latest release
            try:
                latest = client.get_latest_release(repo)
                if latest:
                    console.print(
                        f"\n[bold]Latest Release:[/bold] {latest.tag_name} "
                        f"[dim]({latest.published_at.strftime('%Y-%m-%d')})[/dim]"
                    )
            except GitHubAPIError:
                pass

    except GitHubAPIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="user")
def user_stats(
    username: str = typer.Argument(..., help="GitHub username"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Force refresh from API"),
    top: int = typer.Option(3, "--top", "-n", help="Number of top repos to show"),
):
    """Show user profile and statistics.

    Example:
        gitpulse user ruslanlap
        gitpulse user ruslanlap --top 5
    """
    try:
        with GitHubClient() as client:
            console.print(f"[cyan]Fetching stats for @{username}...[/cyan]")
            stats = client.get_user_stats(username, no_cache=no_cache)

            # User info
            table = Table(
                title=f"👤 User: @{stats.login}",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Metric", style="bold")
            table.add_column("Value", justify="right")

            if stats.name:
                table.add_row("Name", stats.name)
            table.add_row("📚 Public Repos", str(stats.public_repos))
            table.add_row("📝 Public Gists", str(stats.public_gists))
            table.add_row("👥 Followers", str(stats.followers))
            table.add_row("➡️ Following", str(stats.following))
            if stats.location:
                table.add_row("📍 Location", stats.location)
            if stats.company:
                table.add_row("🏢 Company", stats.company)
            if stats.blog:
                table.add_row("🔗 Blog", stats.blog)
            table.add_row("📅 Joined", stats.created_at.strftime("%Y-%m-%d"))

            console.print(table)

            # Bio
            if stats.bio:
                console.print(Panel(stats.bio, title="Bio", border_style="dim"))

            # Top repositories
            console.print(f"\n[cyan]Fetching top {top} repositories...[/cyan]")
            top_repos = client.get_top_repos(username, limit=top)

            if top_repos:
                repo_table = Table(
                    title=f"⭐ Top {len(top_repos)} Repositories by Stars",
                    box=box.ROUNDED,
                    show_header=True,
                    header_style="bold yellow",
                )
                repo_table.add_column("Repository", style="bold")
                repo_table.add_column("Stars", justify="right")
                repo_table.add_column("Language")
                repo_table.add_column("Description", max_width=50)

                for repo in top_repos:
                    repo_table.add_row(
                        repo.name,
                        str(repo.stars),
                        repo.language or "-",
                        repo.description or "-",
                    )

                console.print(repo_table)

                # Calculate total stars
                total_stars = sum(r.stars for r in top_repos)
                console.print(
                    f"\n[bold]Total stars from top {len(top_repos)} repos:[/bold] "
                    f"⭐ {total_stars}"
                )

    except GitHubAPIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def badges(
    repo: str = typer.Argument(..., help="Repository in format 'owner/name'"),
    custom: Optional[str] = typer.Option(
        None,
        "--custom",
        "-c",
        help="Custom badge types (comma-separated): stars,forks,issues,license,release,language,downloads,commit",
    ),
):
    """Generate Markdown badges for README.

    Example:
        gitpulse badges ruslanlap/gitpulse
        gitpulse badges ruslanlap/gitpulse --custom stars,forks,license
    """
    try:
        gen = BadgeGenerator()

        if custom:
            # Custom badges
            badge_types = [b.strip() for b in custom.split(",")]
            badges_md = gen.generate_custom(repo, badge_types)
        else:
            # Full badge set with stats
            try:
                with GitHubClient() as client:
                    stats = client.get_repo_stats(repo)
                    latest_release = client.get_latest_release(repo)
                    badges_md = gen.generate_full_set(repo, stats, latest_release)
            except GitHubAPIError:
                # Fallback to dynamic badges
                badges_md = gen.generate_full_set(repo)

        # Display
        console.print("\n[bold green]✓ Badges generated![/bold green]\n")
        console.print(Panel(badges_md, title="Markdown Badges", border_style="green"))
        console.print(
            "\n[dim]Copy and paste the above Markdown into your README.md[/dim]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def export(
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository to export"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="User to export"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Export statistics to JSON format.

    Example:
        gitpulse export --repo ruslanlap/gitpulse
        gitpulse export --user ruslanlap --output stats.json
    """
    if not repo and not user:
        console.print("[red]Error:[/red] Specify either --repo or --user")
        raise typer.Exit(1)

    if format != "json":
        console.print(f"[red]Error:[/red] Format '{format}' not supported yet")
        raise typer.Exit(1)

    try:
        with GitHubClient() as client:
            data = {}

            if repo:
                console.print(f"[cyan]Exporting repo stats for {repo}...[/cyan]")
                stats = client.get_repo_stats(repo)
                releases = client.get_repo_releases(repo, limit=5)

                data["repository"] = {
                    "name": stats.name,
                    "full_name": stats.full_name,
                    "description": stats.description,
                    "stats": {
                        "stars": stats.stars,
                        "forks": stats.forks,
                        "watchers": stats.watchers,
                        "open_issues": stats.open_issues,
                        "size_kb": stats.size,
                    },
                    "language": stats.language,
                    "topics": stats.topics,
                    "dates": {
                        "created": stats.created_at.isoformat(),
                        "updated": stats.updated_at.isoformat(),
                        "pushed": stats.pushed_at.isoformat(),
                    },
                    "releases": [
                        {
                            "tag": r.tag_name,
                            "name": r.name,
                            "published_at": r.published_at.isoformat(),
                            "url": r.html_url,
                        }
                        for r in releases
                    ],
                }

            if user:
                console.print(f"[cyan]Exporting user stats for @{user}...[/cyan]")
                stats = client.get_user_stats(user)
                top_repos = client.get_top_repos(user, limit=10)

                data["user"] = {
                    "login": stats.login,
                    "name": stats.name,
                    "bio": stats.bio,
                    "stats": {
                        "public_repos": stats.public_repos,
                        "public_gists": stats.public_gists,
                        "followers": stats.followers,
                        "following": stats.following,
                    },
                    "location": stats.location,
                    "company": stats.company,
                    "blog": stats.blog,
                    "created_at": stats.created_at.isoformat(),
                    "top_repos": [
                        {
                            "name": r.name,
                            "full_name": r.full_name,
                            "stars": r.stars,
                            "description": r.description,
                            "language": r.language,
                            "url": r.html_url,
                        }
                        for r in top_repos
                    ],
                }

            # Output
            json_str = json.dumps(data, indent=2, ensure_ascii=False)

            if output:
                output.write_text(json_str, encoding="utf-8")
                console.print(f"[green]✓[/green] Exported to: {output}")
            else:
                console.print(json_str)

    except GitHubAPIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def clear_cache():
    """Clear all cached data.

    Example:
        gitpulse clear-cache
    """
    from .cache import get_cache

    cache = get_cache()
    cache.clear()
    console.print("[green]✓[/green] Cache cleared successfully!")


if __name__ == "__main__":
    app()
