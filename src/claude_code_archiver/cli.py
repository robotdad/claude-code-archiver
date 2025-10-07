"""Command-line interface for Claude Code Archiver."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .archiver import Archiver
from .discovery import ProjectDiscovery

console = Console()


@click.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for archive (default: current directory)",
)
@click.option(
    "--no-sanitize",
    is_flag=True,
    help="Skip sanitization of sensitive data",
)
@click.option(
    "--name",
    "-n",
    help="Custom archive name (without extension)",
)
@click.option(
    "--list-only",
    "-l",
    is_flag=True,
    help="List conversations without creating archive",
)
@click.option(
    "--no-todos",
    is_flag=True,
    help="Don't include todo files from ~/.claude/todos/",
)
@click.option(
    "--alias",
    "-a",
    multiple=True,
    help="Additional project paths/aliases to include conversations from (can be used multiple times)",
)
@click.option(
    "--refresh",
    "-r",
    type=click.Path(exists=True, path_type=Path),
    help="Refresh an existing archive with new conversations",
)
@click.version_option(version=__version__)
def main(
    project_path: Path | None,
    output: Path,
    no_sanitize: bool,
    name: str,
    list_only: bool,
    no_todos: bool,
    alias: tuple[str, ...],
    refresh: Path | None,
) -> None:
    """Archive Claude Code conversations for a project.

    PROJECT_PATH: Path to the project directory to archive conversations for.
                  Optional when using --refresh (uses paths from archive manifest).
    """
    try:
        # Handle refresh mode
        if refresh:
            archiver = Archiver(output_dir=output)
            console.print(f"\n🔄 Refreshing archive: [cyan]{refresh}[/cyan]")

            # Refresh not implemented in simplified version
            console.print("[yellow]Archive refresh not available in simplified version[/yellow]")
            raise SystemExit(1)

        # For non-refresh operations, project_path is required
        if project_path is None:
            console.print("[red]Error:[/red] PROJECT_PATH is required when not using --refresh")
            raise SystemExit(1)

        discovery = ProjectDiscovery()

        # Discover conversations from main project
        console.print(f"\n🔍 Discovering conversations for: [cyan]{project_path}[/cyan]")
        from .models import SessionFile

        conversations: list[SessionFile] = discovery.discover_project_conversations(project_path)

        # Add conversations from aliases
        if alias:
            console.print(f"🔍 Including conversations from {len(alias)} alias(es):")
            for alias_pattern in alias:
                console.print(f"  - [cyan]{alias_pattern}[/cyan]")

                # Handle wildcard patterns
                if "*" in alias_pattern or "?" in alias_pattern:
                    alias_paths = list(Path(alias_pattern).parent.glob(Path(alias_pattern).name))
                    expanded_paths = [p for p in alias_paths if p.is_dir()]
                    if expanded_paths:
                        console.print(f"    Expanded to {len(expanded_paths)} path(s):")
                        for alias_path in expanded_paths:
                            console.print(f"      → [dim cyan]{alias_path}[/dim cyan]")
                            alias_conversations = discovery.discover_project_conversations(
                                alias_path, exclude_snapshots=False
                            )
                            conversations.extend(alias_conversations)
                            console.print(f"        Found [green]{len(alias_conversations)}[/green] conversation(s)")
                    else:
                        console.print("    [yellow]No directories found matching pattern[/yellow]")
                else:
                    # Handle as literal path
                    alias_conversations = discovery.discover_project_conversations(
                        Path(alias_pattern), exclude_snapshots=False
                    )
                    conversations.extend(alias_conversations)
                    console.print(f"    Found [green]{len(alias_conversations)}[/green] conversation(s)")

        # Remove duplicates based on session_id
        unique_conversations: dict[str, SessionFile] = {}
        for conv in conversations:
            unique_conversations[conv.session_id] = conv
        conversations = list(unique_conversations.values())

        if not conversations:
            console.print("[yellow]No conversations found for this project.[/yellow]")
            raise SystemExit(1)

        console.print(f"Found [green]{len(conversations)}[/green] conversation(s)")

        if list_only:
            # Display conversation list
            table = Table(title="Conversations")
            table.add_column("Session ID", style="cyan", no_wrap=True)
            table.add_column("Messages", justify="right")
            table.add_column("Size", justify="right")
            table.add_column("Started", style="green")
            table.add_column("Continuation", style="yellow")

            for conv in conversations:
                # No continuation detection in simplified version
                continuation = ""
                size_kb = conv.size_bytes / 1024
                started = conv.modified_at[:10] if hasattr(conv, "modified_at") else "Unknown"

                table.add_row(
                    conv.session_id[:8] + "...",
                    str(conv.message_count),
                    f"{size_kb:.1f} KB",
                    started,
                    continuation,
                )

            console.print(table)
        else:
            # Create archive
            archiver = Archiver(output_dir=output)
            sanitize = not no_sanitize

            console.print("\n📦 Creating archive...")
            if sanitize:
                console.print("  ✓ Sanitizing sensitive data")
            else:
                console.print("  ⚠️  [yellow]Skipping sanitization (--no-sanitize)[/yellow]")

            console.print("  ✓ Including intermediate snapshots (toggleable in viewer)")

            if not no_todos:
                console.print("  ✓ Including todo files")

            # Aliases not supported in simplified version

            archive_path = archiver.create_archive(
                project_path=project_path,
                sanitize=sanitize,
                output_name=name,
            )

            console.print(f"\n✅ Archive created: [green]{archive_path}[/green]")

            # Show sanitization stats if applicable
            if sanitize and archiver.sanitizer.stats.total_redactions > 0:
                console.print("\n🔒 Sanitization summary:")
                console.print(f"  Total redactions: [yellow]{archiver.sanitizer.stats.total_redactions}[/yellow]")
                for pattern_name, count in archiver.sanitizer.stats.redactions_by_type.items():
                    console.print(f"  - {pattern_name}: {count}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
