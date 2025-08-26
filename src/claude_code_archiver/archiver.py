"""Archive generation module."""

import json
import shutil
import zipfile
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .discovery import ProjectDiscovery
from .parser import ConversationParser
from .sanitizer import SanitizationStats
from .sanitizer import Sanitizer
from .viewer import ViewerGenerator


class ArchiveManifest(BaseModel):
    """Manifest for the archive."""

    version: str = "1.0"
    created_at: str
    project_path: str
    conversation_count: int
    total_messages: int
    date_range: dict[str, str | None]
    conversations: list[dict[str, Any]]
    continuation_chains: dict[str, list[str]]
    sanitization_stats: dict[str, Any] | None = None


class Archiver:
    """Creates archives of Claude Code conversations."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize archiver.

        Args:
            output_dir: Directory for output archives (default: current directory)
        """
        self.output_dir = output_dir or Path.cwd()
        self.discovery = ProjectDiscovery()
        self.parser = ConversationParser()
        self.sanitizer = Sanitizer()
        self.viewer = ViewerGenerator()

    def create_archive(
        self,
        project_path: Path,
        sanitize: bool = True,
        output_name: str | None = None,
    ) -> Path:
        """Create an archive for a project's conversations.

        Args:
            project_path: Path to the project
            sanitize: Whether to sanitize sensitive data
            output_name: Optional custom archive name

        Returns:
            Path to the created archive

        Raises:
            ValueError: If project has no conversations
        """
        # Discover conversations
        conversations = self.discovery.discover_project_conversations(project_path)

        if not conversations:
            raise ValueError(f"No conversations found for project: {project_path}")

        # Create temporary directory for archive contents
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        project_name = project_path.name
        archive_name = output_name or f"claude-convos-{project_name}-{timestamp}"
        temp_dir = self.output_dir / f".tmp_{archive_name}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Create archive structure
            conversations_dir = temp_dir / "conversations"
            conversations_dir.mkdir(parents=True, exist_ok=True)

            # Process conversations
            manifest_conversations: list[dict[str, Any]] = []
            total_messages = 0
            sanitization_stats = SanitizationStats()

            for conv in conversations:
                # Copy and optionally sanitize conversation file
                output_file = conversations_dir / f"{conv.session_id}.jsonl"

                if sanitize:
                    stats = self.sanitizer.sanitize_file(conv.path, output_file)
                    sanitization_stats.total_redactions += stats.total_redactions
                    for key, value in stats.redactions_by_type.items():
                        sanitization_stats.redactions_by_type[key] = (
                            sanitization_stats.redactions_by_type.get(key, 0) + value
                        )
                else:
                    shutil.copy2(conv.path, output_file)

                # Parse for statistics
                entries = self.parser.parse_file(output_file)
                stats = self.parser.extract_statistics(entries)
                total_messages += stats["total_messages"]

                # Add to manifest
                manifest_conversations.append(
                    {
                        "session_id": conv.session_id,
                        "file": f"conversations/{conv.session_id}.jsonl",
                        "message_count": conv.message_count,
                        "first_timestamp": conv.first_timestamp,
                        "last_timestamp": conv.last_timestamp,
                        "starts_with_summary": conv.starts_with_summary,
                        "statistics": stats,
                    }
                )

            # Find continuation chains
            chains = self.discovery.find_continuation_chains(conversations)

            # Calculate date range
            timestamps = [c.first_timestamp for c in conversations if c.first_timestamp]
            date_range = {
                "earliest": min(timestamps) if timestamps else None,
                "latest": max([c.last_timestamp for c in conversations if c.last_timestamp], default=None),
            }

            # Create manifest
            manifest = ArchiveManifest(
                created_at=datetime.now(UTC).isoformat(),
                project_path=str(project_path),
                conversation_count=len(conversations),
                total_messages=total_messages,
                date_range=date_range,
                conversations=manifest_conversations,
                continuation_chains=chains,
                sanitization_stats=sanitization_stats.model_dump() if sanitize else None,
            )

            # Write manifest
            manifest_path = temp_dir / "manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest.model_dump(), f, indent=2)

            # Create viewer in root directory
            viewer_path = temp_dir / "viewer.html"
            self.viewer.save_viewer(viewer_path, manifest.model_dump())

            # Copy serve.py script to archive
            serve_template = Path(__file__).parent / "serve_template.py"
            serve_path = temp_dir / "serve.py"
            shutil.copy2(serve_template, serve_path)

            # Create ZIP archive
            zip_path = self.output_dir / f"{archive_name}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)

            return zip_path

        finally:
            # Clean up temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def extract_archive(self, archive_path: Path, extract_to: Path | None = None) -> Path:
        """Extract an archive for viewing.

        Args:
            archive_path: Path to the archive file
            extract_to: Optional directory to extract to

        Returns:
            Path to extracted directory
        """
        extract_dir = extract_to or archive_path.parent / archive_path.stem

        with zipfile.ZipFile(archive_path, "r") as zipf:
            zipf.extractall(extract_dir)

        return extract_dir
