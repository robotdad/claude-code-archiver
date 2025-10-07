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
from .models import SessionFile
from .parser import ConversationParser
from .sanitizer import SanitizationStats
from .sanitizer import Sanitizer
from .viewer import ViewerGenerator


class ArchiveManifest(BaseModel):
    """Manifest for the archive."""

    version: str = "3.0"  # Bumped for DAG-native redesign
    created_at: str
    project_path: str
    conversation_count: int
    total_messages: int
    date_range: dict[str, str | None]
    conversations: list[dict[str, Any]]
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
        # Discover all sessions
        sessions: list[SessionFile] = self.discovery.discover_project_conversations(project_path)

        if not sessions:
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

            for session_file in sessions:
                # Copy and optionally sanitize conversation file
                output_filename = session_file.path.name
                output_file = conversations_dir / output_filename

                if sanitize:
                    stats = self.sanitizer.sanitize_file(session_file.path, output_file)
                    sanitization_stats.total_redactions += stats.total_redactions
                    for key, value in stats.redactions_by_type.items():
                        sanitization_stats.redactions_by_type[key] = (
                            sanitization_stats.redactions_by_type.get(key, 0) + value
                        )
                else:
                    shutil.copy2(session_file.path, output_file)

                # Parse for statistics
                dag = self.parser.parse_file(output_file)
                message_count = dag.message_count
                total_messages += message_count

                # Extract conversation title from first meaningful user message
                conversation_title = self._extract_conversation_title(output_file)

                # Add to manifest using SessionFile fields
                manifest_conv = {
                    "session_id": session_file.path.stem,  # Use filename as session ID
                    "file": f"conversations/{output_filename}",
                    "title": conversation_title,
                    "message_count": session_file.message_count,
                    "path_count": session_file.path_count,
                    "has_branches": session_file.has_branches,
                    "size_bytes": session_file.size_bytes,
                }

                manifest_conversations.append(manifest_conv)

            # Calculate date range
            timestamps: list[str] = []
            for session in sessions:
                # Parse timestamps from the DAG to get actual date range
                dag = self.parser.parse_file(session.path)
                for node in dag.nodes.values():
                    if node.timestamp:
                        timestamps.append(node.timestamp)

            date_range = {
                "earliest": min(timestamps) if timestamps else None,
                "latest": max(timestamps) if timestamps else None,
            }

            # Create manifest
            manifest = ArchiveManifest(
                created_at=datetime.now(UTC).isoformat(),
                project_path=str(project_path),
                conversation_count=len(sessions),
                total_messages=total_messages,
                date_range=date_range,
                conversations=manifest_conversations,
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

    def _extract_conversation_title(self, file_path: Path) -> str:
        """Extract a meaningful title from the conversation.

        Looks for the first substantial user message and creates a title from it.

        Args:
            file_path: Path to the conversation file

        Returns:
            A short descriptive title for the conversation
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)

                    # Skip summary messages
                    if data.get("type") == "summary":
                        continue

                    # Look for user messages
                    if data.get("type") == "user":
                        message = data.get("message", {})
                        content = message.get("content", "")

                        # Handle both string and array content formats
                        if isinstance(content, list):
                            text_parts: list[str] = []
                            for item in content:  # type: ignore
                                if isinstance(item, dict) and item.get("type") == "text":  # type: ignore
                                    text_content = item.get("text", "")  # type: ignore
                                    if isinstance(text_content, str):
                                        text_parts.append(text_content)
                            text = " ".join(text_parts)
                        else:
                            text = str(content)

                        # Clean and truncate the text
                        text = text.strip()
                        if text:
                            # Remove common prefixes
                            prefixes_to_remove = [
                                "I want you to",
                                "Please help me",
                                "Can you help me",
                                "Help me",
                                "I need help with",
                                "I need you to",
                            ]

                            text_lower = text.lower()
                            for prefix in prefixes_to_remove:
                                if text_lower.startswith(prefix.lower()):
                                    text = text[len(prefix) :].strip()
                                    break

                            # Capitalize first letter
                            if text:
                                text = text[0].upper() + text[1:]

                            # Truncate to reasonable length
                            if len(text) > 80:
                                text = text[:77] + "..."

                            return text or "Conversation"

        except (OSError, json.JSONDecodeError):
            pass

        return "Conversation"

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
