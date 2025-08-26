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
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
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
@click.version_option(version=__version__)
def main(
    project_path: Path,
    output: Path,
    no_sanitize: bool,
    name: str,
    list_only: bool,
    include_snapshots: bool,
    no_todos: bool,
) -> None:
    """Archive Claude Code conversations for a project.

    PROJECT_PATH: Path to the project directory to archive conversations for.
    """
    try:
        discovery = ProjectDiscovery()

        # Discover conversations
        console.print(f"\n🔍 Discovering conversations for: [cyan]{project_path}[/cyan]")
        conversations = discovery.discover_project_conversations(project_path, exclude_snapshots=not include_snapshots)

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

            archive_path = archiver.create_archive(
                project_path=project_path,
                sanitize=sanitize,
                output_name=name,
                include_snapshots=include_snapshots,
                include_todos=not no_todos,
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
