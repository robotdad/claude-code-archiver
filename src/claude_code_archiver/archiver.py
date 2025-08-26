"""Archive generation module."""

import json
import shutil
import zipfile
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .discovery import ConversationFile
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
    todos: dict[str, Any] | None = None


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
        include_snapshots: bool = False,
        include_todos: bool = True,
    ) -> Path:
        """Create an archive for a project's conversations.

        Args:
            project_path: Path to the project
            sanitize: Whether to sanitize sensitive data
            output_name: Optional custom archive name
            include_snapshots: Whether to include intermediate conversation snapshots
            include_todos: Whether to include todo files from ~/.claude/todos/

        Returns:
            Path to the created archive

        Raises:
            ValueError: If project has no conversations
        """
        # Discover all conversations and tag them appropriately
        conversations = self.discovery.discover_project_conversations(
            project_path,
            exclude_snapshots=False,  # Always get all files, tag them in manifest
        )

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

            # Create todos directory if including todos
            todos_metadata = {}
            if include_todos:
                todos_dir = temp_dir / "todos"
                todos_dir.mkdir(parents=True, exist_ok=True)
                todos_metadata = self._collect_todo_files(conversations, todos_dir)

            # Process conversations
            manifest_conversations: list[dict[str, Any]] = []
            total_messages = 0
            sanitization_stats = SanitizationStats()

            for conv in conversations:
                # Copy and optionally sanitize conversation file
                # Use the original filename to avoid confusion with continuations
                # that have different internal session IDs
                output_filename = conv.path.name
                output_file = conversations_dir / output_filename

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

                # Extract conversation title from first meaningful user message
                conversation_title = self._extract_conversation_title(output_file)

                # Add to manifest with proper conversation type tagging
                manifest_conv = {
                    "session_id": conv.session_id,
                    "file": f"conversations/{output_filename}",
                    "title": conversation_title,
                    "message_count": conv.message_count,
                    "first_timestamp": conv.first_timestamp,
                    "last_timestamp": conv.last_timestamp,
                    "starts_with_summary": conv.starts_with_summary,
                    "is_post_compaction": conv.parent_session_id is not None,  # Has parent from compaction
                    "parent_session_id": conv.parent_session_id,  # For post-compaction continuations
                    "statistics": stats,
                }

                # We'll mark is_continuation after building chains

                # Add snapshot metadata if present
                if conv.is_snapshot:
                    manifest_conv["is_snapshot"] = conv.is_snapshot
                    manifest_conv["snapshot_group"] = conv.snapshot_group
                    manifest_conv["snapshot_type"] = conv.snapshot_type

                manifest_conversations.append(manifest_conv)

            # Find continuation chains
            chains = self.discovery.find_continuation_chains(conversations)

            # Mark conversations that are continuations (appear in chains as values)
            continuation_ids: set[str] = set()
            for _parent_id, child_ids in chains.items():
                continuation_ids.update(child_ids)

            # Run snapshot detection to identify which files are snapshots
            self.discovery.detect_and_filter_snapshots(conversations)
            snapshot_ids = {c.session_id for c in conversations if c.is_snapshot}

            # Update manifest conversations with proper tagging
            for idx, manifest_conv in enumerate(manifest_conversations):
                session_id = manifest_conv["session_id"]
                manifest_conv["is_continuation"] = session_id in continuation_ids
                manifest_conv["is_snapshot"] = session_id in snapshot_ids

                # Get the corresponding conversation object
                conv = conversations[idx]

                # Check for internal compaction (new pattern discovered in e22b2cf8)
                has_internal_compaction = self._has_internal_compaction(conv.path)

                # Check if this is auto-linked vs true continuation
                is_auto_linked = False
                if manifest_conv["is_continuation"] and not manifest_conv.get("is_post_compaction"):
                    # Check if it's auto-linked (brief summary) vs true continuation
                    is_auto_linked = self._is_auto_linked_conversation(conv.path)

                # Determine conversation type for viewer
                if session_id in snapshot_ids:
                    manifest_conv["conversation_type"] = "snapshot"
                    manifest_conv["display_by_default"] = False
                elif manifest_conv.get("is_post_compaction"):
                    # True continuation after compaction
                    manifest_conv["conversation_type"] = "post_compaction"
                    manifest_conv["display_by_default"] = True
                elif is_auto_linked and has_internal_compaction:
                    # Auto-linked conversation that later has internal compaction
                    manifest_conv["conversation_type"] = "auto_linked_with_internal_compaction"
                    manifest_conv["display_by_default"] = True
                elif is_auto_linked:
                    # Auto-linked new conversation in project chain
                    manifest_conv["conversation_type"] = "auto_linked"
                    manifest_conv["display_by_default"] = True
                elif manifest_conv["starts_with_summary"] and not manifest_conv["is_continuation"]:
                    # This is like cfbe2049 - has summary but is not a continuation in chains
                    manifest_conv["conversation_type"] = "pre_compaction"
                    manifest_conv["display_by_default"] = True
                else:
                    manifest_conv["conversation_type"] = "original"
                    manifest_conv["display_by_default"] = True

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
                todos=todos_metadata if include_todos else None,
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

    def _has_internal_compaction(self, file_path: Path) -> bool:
        """Check if a conversation file has internal compaction.

        This looks for isCompactSummary: true anywhere in the file
        (not just the first line).

        Args:
            file_path: Path to the conversation file

        Returns:
            True if internal compaction is detected
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    if data.get("isCompactSummary", False) is True:
                        return True
        except (OSError, json.JSONDecodeError):
            pass
        return False

    def _is_auto_linked_conversation(self, file_path: Path) -> bool:
        """Check if a conversation is auto-linked vs a true continuation.

        Auto-linked conversations have:
        - Brief summary title (<100 chars)
        - No isCompactSummary in first few lines

        True continuations have:
        - isCompactSummary: true (handled separately)
        - OR detailed continuation summary

        Args:
            file_path: Path to the conversation file

        Returns:
            True if this is an auto-linked conversation (not a true continuation)
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

                # Check first line for summary
                if lines:
                    first_data = json.loads(lines[0])
                    if first_data.get("type") == "summary":
                        summary = first_data.get("summary", "")
                        # Brief summaries (<100 chars) indicate auto-linking
                        # Also check if it doesn't contain continuation keywords
                        if len(summary) < 100 and "continued from" not in summary.lower():
                            return True

                # Check first 5 lines for isCompactSummary
                # If found, it's a true continuation, not auto-linked
                for line in lines[:5]:
                    data = json.loads(line)
                    if data.get("isCompactSummary", False) is True:
                        return False

        except (OSError, json.JSONDecodeError):
            pass
        return False

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

    def _collect_todo_files(self, conversations: list[ConversationFile], todos_dir: Path) -> dict[str, dict[str, Any]]:
        """Collect todo files for the conversations.

        Args:
            conversations: List of conversation files
            todos_dir: Directory to copy todo files to

        Returns:
            Dictionary of todo metadata for manifest
        """
        todos_metadata: dict[str, dict[str, Any]] = {}
        claude_todos_dir = Path.home() / ".claude" / "todos"

        if not claude_todos_dir.exists():
            return todos_metadata

        # Collect unique session IDs
        session_ids = {conv.session_id for conv in conversations if conv.session_id}

        for session_id in session_ids:
            # Try different naming patterns
            patterns = [
                f"{session_id}-agent-{session_id}.json",
                f"{session_id}.json",
            ]

            for pattern in patterns:
                todo_file = claude_todos_dir / pattern
                if todo_file.exists():
                    # Copy todo file to archive
                    dest_file = todos_dir / f"{session_id}.json"
                    shutil.copy2(todo_file, dest_file)

                    # Read todo file for metadata
                    try:
                        with open(todo_file, encoding="utf-8") as f:
                            todos = json.load(f)

                        # Calculate statistics
                        status_counts = {"completed": 0, "in_progress": 0, "pending": 0}
                        for todo in todos:
                            status = todo.get("status", "pending")
                            if status in status_counts:
                                status_counts[status] += 1

                        todos_metadata[session_id] = {
                            "file": f"todos/{session_id}.json",
                            "total_count": len(todos),
                            "status_counts": status_counts,
                        }
                    except (OSError, json.JSONDecodeError):
                        pass

                    break  # Found the todo file, no need to check other patterns

        return todos_metadata

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
