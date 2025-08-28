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
    # Snapshot detection fields
    is_snapshot: bool = False
    snapshot_group: str | None = None
    snapshot_type: str | None = None  # "intermediate" or "complete"
    message_uuids: set[str] = set()
    # For post-compaction continuations
    parent_session_id: str | None = None
    # Sidechain detection
    has_sidechains: bool = False
    sidechain_count: int = 0


class ProjectDiscovery:
    """Discovers and maps Claude Code project conversations."""

    def __init__(self, claude_projects_dir: Path | None = None):
        """Initialize discovery with optional custom Claude projects directory."""
        self.claude_projects_dir = claude_projects_dir or Path.home() / ".claude" / "projects"

    def project_path_to_folder_name(self, project_path: Path) -> str:
        """Convert a project path to Claude's folder naming convention.

        Args:
            project_path: Path to convert

        Returns:
            Folder name with slashes replaced by dashes

        Example:
            /Users/robotdad/Source/SelfServe -> -Users-robotdad-Source-SelfServe
        """
        # Convert to absolute path and replace separators
        absolute_path = Path(project_path).absolute()
        return str(absolute_path).replace("/", "-")

    def discover_project_conversations(
        self,
        project_path: Path,
        exclude_snapshots: bool = False,  # Changed default to include all
    ) -> list[ConversationFile]:
        """Discover all conversation files for a given project.

        Args:
            project_path: Path to the project directory
            exclude_snapshots: If True, exclude intermediate conversation snapshots

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

        # Detect and filter snapshots if requested
        if exclude_snapshots and conversations:
            conversations = self.detect_and_filter_snapshots(conversations)

        return sorted(conversations, key=lambda x: x.first_timestamp or "")

    def _analyze_conversation_file(self, file_path: Path) -> ConversationFile:
        """Analyze a single conversation file for metadata.

        Args:
            file_path: Path to the JSONL file

        Returns:
            ConversationFile object with metadata
        """
        # Default to filename as session_id
        session_id = file_path.stem
        size = file_path.stat().st_size
        message_count = 0
        first_timestamp = None
        last_timestamp = None
        starts_with_summary = False
        leaf_uuid = None
        actual_session_id = None
        has_sidechains = False
        sidechain_count = 0

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
                    elif first_data.get("isCompactSummary") is True:
                        # Post-compaction continuation starts with user message
                        starts_with_summary = True

                    # Get the actual session ID from the data
                    # For continuation files, this might differ from the filename
                    if first_data.get("sessionId"):
                        actual_session_id = first_data["sessionId"]

                    # Find first timestamp and check for sidechains
                    for line in lines[: min(20, len(lines))]:
                        data = json.loads(line)
                        if data.get("timestamp") and not first_timestamp:
                            first_timestamp = data["timestamp"]
                        # Check for sidechain messages
                        if data.get("isSidechain") is True:
                            has_sidechains = True

                    # Count total sidechains if any were detected
                    if has_sidechains:
                        for line in lines:
                            data = json.loads(line)
                            if data.get("isSidechain") is True:
                                sidechain_count += 1

                    # Get last timestamp
                    if len(lines) > 0:
                        last_data = json.loads(lines[-1])
                        last_timestamp = last_data.get("timestamp")

        except (OSError, json.JSONDecodeError):
            pass  # Handle malformed files gracefully

        # Extract UUIDs for snapshot detection
        message_uuids = self._extract_message_uuids(file_path)

        # For post-compaction continuations, keep the filename as session_id
        # to maintain uniqueness, but store the parent session ID separately
        parent_session_id = None
        if starts_with_summary and actual_session_id and actual_session_id != session_id:
            # This is a continuation file with a different internal session ID
            parent_session_id = actual_session_id
            # Keep using the filename-based session_id for uniqueness

        return ConversationFile(
            path=file_path,
            session_id=session_id,
            size=size,
            message_count=message_count,
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
            starts_with_summary=starts_with_summary,
            leaf_uuid=leaf_uuid,
            message_uuids=message_uuids,
            parent_session_id=parent_session_id,
            has_sidechains=has_sidechains,
            sidechain_count=sidechain_count,
        )

    def _extract_message_uuids(self, file_path: Path) -> set[str]:
        """Extract all message UUIDs from a conversation file.

        Args:
            file_path: Path to the JSONL file

        Returns:
            Set of UUIDs found in the file
        """
        uuids: set[str] = set()
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    if uuid := data.get("uuid"):
                        uuids.add(uuid)
        except (OSError, json.JSONDecodeError):
            pass
        return uuids

    def detect_and_filter_snapshots(self, conversations: list[ConversationFile]) -> list[ConversationFile]:
        """Detect conversation snapshots and filter out intermediates.

        Understanding the conversation types:
        1. Original conversations - normal conversation files
        2. Intermediate snapshots - partial copies during long conversations
        3. Pre-compaction conversations - complete conversations that may have continuations
        4. Post-compaction continuations - continuations after compaction (isCompactSummary: true)
        5. New conversations that start with summary - unrelated to previous

        The goal: Keep post-compaction continuations, pre-compaction conversations,
        and new conversations. Exclude only intermediate snapshots.

        Args:
            conversations: List of all discovered conversations

        Returns:
            Filtered list with intermediate snapshots excluded
        """
        # First, identify post-compaction continuations
        continuations: list[ConversationFile] = []
        for conv in conversations:
            if self._is_compaction_continuation(conv.path):
                continuations.append(conv)

        # Start with all continuations (always included)
        result: list[ConversationFile] = continuations.copy()

        # Now process non-continuation files for snapshot detection
        non_continuations = [c for c in conversations if c not in continuations]

        # Group conversations by significant UUID overlap
        processed: set[Path] = set()

        for conv in non_continuations:
            if conv.path in processed:
                continue

            # Skip files with no UUIDs
            if not conv.message_uuids:
                result.append(conv)
                processed.add(conv.path)
                continue

            # Find all files with significant UUID overlap (potential snapshots)
            group = [conv]
            processed.add(conv.path)

            for other in non_continuations:
                if other.path in processed:
                    continue
                if not other.message_uuids:
                    continue

                # Check for significant overlap
                overlap = conv.message_uuids & other.message_uuids
                if overlap:
                    # Calculate overlap percentage based on smaller set
                    smaller_size = min(len(conv.message_uuids), len(other.message_uuids))
                    if len(overlap) > smaller_size * 0.8:  # 80% threshold
                        group.append(other)
                        processed.add(other.path)

            # Process the group
            if len(group) == 1:
                # No snapshots, include the file
                result.append(conv)
            else:
                # Multiple files with overlap - these are likely snapshots
                # Sort by message count (smallest to largest)
                group.sort(key=lambda x: x.message_count)

                # Keep the most complete version (largest or with summary)
                selected: ConversationFile | None = None

                # Prefer files that start with summary (more complete)
                for g in reversed(group):  # Start from largest
                    if g.starts_with_summary:
                        selected = g
                        break

                # If no summary file, take the largest
                if not selected:
                    selected = group[-1]

                # Add selected, mark others as snapshots
                result.append(selected)
                for g in group:
                    if g != selected:
                        g.is_snapshot = True
                        g.snapshot_type = "intermediate"

        return result

    def _is_compaction_continuation(self, file_path: Path) -> bool:
        """Check if a file is a post-compaction continuation.

        These files have isCompactSummary: true in the first user message.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                first_line = f.readline()
                if first_line:
                    data = json.loads(first_line)
                    return data.get("isCompactSummary", False) is True
        except (OSError, json.JSONDecodeError):
            pass
        return False

    def find_continuation_chains(self, conversations: list[ConversationFile]) -> dict[str, list[str]]:
        """Find continuation chains in conversations.

        Args:
            conversations: List of conversation files

        Returns:
            Dictionary mapping conversation IDs to their continuation chain
        """
        chains: dict[str, list[str]] = {}

        # For post-compaction continuations, use parent_session_id
        for conv in conversations:
            if conv.parent_session_id:
                # This is a post-compaction continuation
                if conv.parent_session_id not in chains:
                    chains[conv.parent_session_id] = []
                chains[conv.parent_session_id].append(conv.session_id)

        # Build UUID maps PER CONVERSATION FILE (not global)
        # UUIDs are only unique within a single conversation file
        # When multiple conversations have the same last UUID, prefer the earlier one (by timestamp)
        uuid_to_session: dict[str, str] = {}

        # Sort conversations by timestamp to handle conflicts predictably
        sorted_convs = sorted(conversations, key=lambda c: c.first_timestamp or "")

        # First pass: collect last UUIDs from each conversation
        for conv in sorted_convs:
            try:
                with open(conv.path, encoding="utf-8") as f:
                    last_uuid = None
                    for line in f:
                        data = json.loads(line)
                        if uuid := data.get("uuid"):
                            last_uuid = uuid
                    # Map the last UUID of this conversation to its session ID
                    # If UUID already exists, keep the first (earliest) mapping
                    if last_uuid and last_uuid not in uuid_to_session:
                        uuid_to_session[last_uuid] = conv.session_id
            except (OSError, json.JSONDecodeError):
                continue

        # Now build chains for non-compaction continuations
        for conv in conversations:
            if conv.starts_with_summary and conv.leaf_uuid:
                # This conversation continues from another
                parent_id = uuid_to_session.get(conv.leaf_uuid)
                # Only add to chains if parent exists and is different from self
                if parent_id and parent_id != conv.session_id:
                    if parent_id not in chains:
                        chains[parent_id] = []
                    chains[parent_id].append(conv.session_id)

        return chains
