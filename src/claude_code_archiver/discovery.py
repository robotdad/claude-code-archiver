"""Project discovery and mapping module."""

import json
from pathlib import Path

from pydantic import BaseModel


class ConversationFile(BaseModel):
    """Represents a conversation JSONL file."""

    path: Path
    session_id: str
    size: int
    message_count: int = 0
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    starts_with_summary: bool = False
    leaf_uuid: str | None = None


class ProjectDiscovery:
    """Discovers and maps Claude Code project conversations."""

    def __init__(self, claude_projects_dir: Path | None = None):
        """Initialize discovery with optional custom Claude projects directory."""
        self.claude_projects_dir = claude_projects_dir or Path.home() / ".claude" / "projects"

    def project_path_to_folder_name(self, project_path: Path) -> str:
        """Convert a project path to Claude's folder naming convention.

        Args:
            project_path: Path to the project directory

        Returns:
            Folder name used by Claude Code

        Example:
            /Users/robotdad/Source/SelfServe -> -Users-robotdad-Source-SelfServe
        """
        # Convert to absolute path and replace separators
        absolute_path = Path(project_path).absolute()
        return str(absolute_path).replace("/", "-")

    def discover_project_conversations(self, project_path: Path) -> list[ConversationFile]:
        """Discover all conversation files for a given project.

        Args:
            project_path: Path to the project directory

        Returns:
            List of ConversationFile objects

        Raises:
            ValueError: If project folder doesn't exist
        """
        folder_name = self.project_path_to_folder_name(project_path)
        project_folder = self.claude_projects_dir / folder_name

        if not project_folder.exists():
            raise ValueError(f"No Claude conversations found for project: {project_path}")

        conversations: list[ConversationFile] = []
        for jsonl_file in project_folder.glob("*.jsonl"):
            conv_file = self._analyze_conversation_file(jsonl_file)
            conversations.append(conv_file)

        return sorted(conversations, key=lambda x: x.first_timestamp or "")

    def _analyze_conversation_file(self, file_path: Path) -> ConversationFile:
        """Analyze a single conversation file for metadata.

        Args:
            file_path: Path to the JSONL file

        Returns:
            ConversationFile with metadata
        """
        session_id = file_path.stem
        size = file_path.stat().st_size
        message_count = 0
        first_timestamp = None
        last_timestamp = None
        starts_with_summary = False
        leaf_uuid = None

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
                message_count = len(lines)

                if lines:
                    # Check first line
                    first_data = json.loads(lines[0])
                    if first_data.get("type") == "summary":
                        starts_with_summary = True
                        leaf_uuid = first_data.get("leafUuid")

                    # Find first timestamp (look deeper for conversations starting with summaries)
                    for line in lines[: min(20, len(lines))]:
                        data = json.loads(line)
                        if data.get("timestamp"):
                            first_timestamp = data["timestamp"]
                            break

                    # Get last timestamp
                    if len(lines) > 0:
                        last_data = json.loads(lines[-1])
                        last_timestamp = last_data.get("timestamp")

        except (OSError, json.JSONDecodeError):
            pass  # Handle malformed files gracefully

        return ConversationFile(
            path=file_path,
            session_id=session_id,
            size=size,
            message_count=message_count,
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
            starts_with_summary=starts_with_summary,
            leaf_uuid=leaf_uuid,
        )

    def find_continuation_chains(self, conversations: list[ConversationFile]) -> dict[str, list[str]]:
        """Find continuation chains in conversations.

        Args:
            conversations: List of conversation files

        Returns:
            Dictionary mapping conversation IDs to their continuation chain
        """
        chains: dict[str, list[str]] = {}

        # Build a map of leaf_uuid to session_id for quick lookup
        leaf_to_session: dict[str, str] = {}
        for conv in conversations:
            # Find all UUIDs in the conversation that might be leafUuids
            try:
                with open(conv.path, encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        if uuid := data.get("uuid"):
                            leaf_to_session[uuid] = conv.session_id
            except (OSError, json.JSONDecodeError):
                continue

        # Now build chains
        for conv in conversations:
            if conv.starts_with_summary and conv.leaf_uuid and (parent_id := leaf_to_session.get(conv.leaf_uuid)):
                if parent_id not in chains:
                    chains[parent_id] = []
                chains[parent_id].append(conv.session_id)

        return chains
