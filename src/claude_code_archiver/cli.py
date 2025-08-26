"""Command-line interface for Claude Code Archiver."""

import sys
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
    "--include-snapshots",
    is_flag=True,
    help="Include intermediate conversation snapshots (excluded by default)",
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
    include_snapshots: bool,
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

            # Convert aliases to list of strings
            project_aliases = list(alias) if alias else None

            refreshed_archive = archiver.refresh_archive(
                archive_path=refresh,
                project_path=project_path,
                project_aliases=project_aliases,
                sanitize=not no_sanitize,
                include_todos=not no_todos,
            )

            console.print(f"\n✅ Archive refreshed: [green]{refreshed_archive}[/green]")
            console.print("  ✓ Updated viewer and server files with latest features")
            console.print("  ✓ Preserved hidden conversations and user preferences")
            return

        # For non-refresh operations, project_path is required
        if project_path is None:
            console.print("[red]Error:[/red] PROJECT_PATH is required when not using --refresh")
            sys.exit(1)

        discovery = ProjectDiscovery()

        # Discover conversations from main project
        console.print(f"\n🔍 Discovering conversations for: [cyan]{project_path}[/cyan]")
        conversations = discovery.discover_project_conversations(project_path, exclude_snapshots=not include_snapshots)

        # Add conversations from aliases
        if alias:
            console.print(f"🔍 Including conversations from {len(alias)} alias(es):")
            for alias_pattern in alias:
                console.print(f"  - [cyan]{alias_pattern}[/cyan]")
                
                # Handle wildcard patterns
                if '*' in alias_pattern or '?' in alias_pattern:
                    from pathlib import Path
                    alias_paths = list(Path(alias_pattern).parent.glob(Path(alias_pattern).name))
                    expanded_paths = [p for p in alias_paths if p.is_dir()]
                    if expanded_paths:
                        console.print(f"    Expanded to {len(expanded_paths)} path(s):")
                        for alias_path in expanded_paths:
                            console.print(f"      → [dim cyan]{alias_path}[/dim cyan]")
                            alias_conversations = discovery.discover_project_conversations(alias_path, exclude_snapshots=not include_snapshots)
                            conversations.extend(alias_conversations)
                            console.print(f"        Found [green]{len(alias_conversations)}[/green] conversation(s)")
                    else:
                        console.print(f"    [yellow]No directories found matching pattern[/yellow]")
                else:
                    # Handle as literal path
                    alias_conversations = discovery.discover_project_conversations(Path(alias_pattern), exclude_snapshots=not include_snapshots)
                    conversations.extend(alias_conversations)
                    console.print(f"    Found [green]{len(alias_conversations)}[/green] conversation(s)")

        # Remove duplicates based on session_id
        unique_conversations = {}
        for conv in conversations:
            unique_conversations[conv.session_id] = conv
        conversations = list(unique_conversations.values())

        if not conversations:
            console.print("[yellow]No conversations found for this project.[/yellow]")
            sys.exit(1)

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
                # Show snapshot info if present
                if conv.is_snapshot:
                    continuation = f"📸 {conv.snapshot_type}"
                elif conv.starts_with_summary:
                    continuation = "✓ continuation"
                else:
                    continuation = ""
                size_kb = conv.size / 1024
                started = conv.first_timestamp[:10] if conv.first_timestamp else "Unknown"

                table.add_row(
                    conv.session_id[:8] + "...",
                    str(conv.message_count),
                    f"{size_kb:.1f} KB",
                    started,
                    continuation,
                )

            console.print(table)

            # Show continuation chains
            chains = discovery.find_continuation_chains(conversations)
            if chains:
                console.print("\n🔗 Continuation chains detected:")
                for parent, children in chains.items():
                    console.print(f"  {parent[:8]}... → {', '.join(c[:8] + '...' for c in children)}")
        else:
            # Create archive
            archiver = Archiver(output_dir=output)
            sanitize = not no_sanitize

            console.print("\n📦 Creating archive...")
            if sanitize:
                console.print("  ✓ Sanitizing sensitive data")
            else:
                console.print("  ⚠️  [yellow]Skipping sanitization (--no-sanitize)[/yellow]")

            if include_snapshots:
                console.print("  ✓ Including intermediate snapshots")
            else:
                console.print("  ✓ Excluding intermediate snapshots (default)")

            if not no_todos:
                console.print("  ✓ Including todo files")

            # Convert aliases to list for archiver
            project_aliases = list(alias) if alias else None

            archive_path = archiver.create_archive(
                project_path=project_path,
                sanitize=sanitize,
                output_name=name,
                include_snapshots=include_snapshots,
                include_todos=not no_todos,
                project_aliases=project_aliases,
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
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
