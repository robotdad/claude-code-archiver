"""Simplified DAG-native models for conversation archiver."""

from pathlib import Path
from typing import Any
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

EdgeType = Literal["root", "normal", "compact", "continuation", "branch"]


class MessageNode(BaseModel):
    """Single message node in the conversation DAG."""

    # Identity
    uuid: str = Field(description="Unique message identifier")
    timestamp: str = Field(description="ISO 8601 timestamp")

    # Relationship
    parent_uuid: str | None = Field(default=None, description="Parent message UUID")
    edge_type: EdgeType = Field(description="Type of edge from parent")

    # Content
    role: Literal["user", "assistant", "system"] = Field(description="Message author")
    content: str | list[Any] = Field(description="Message content")
    truncated: bool = Field(default=False, description="Whether content was truncated")

    # Minimal metadata
    model: str | None = Field(default=None, description="Model used")
    tokens: int | None = Field(default=None, description="Token count")


class ConversationDAG(BaseModel):
    """Graph structure of conversation messages."""

    # Core structure
    nodes: dict[str, MessageNode] = Field(default_factory=dict)
    root_uuid: str = Field(description="Starting node UUID")
    leaf_uuids: list[str] = Field(default_factory=list)

    # Metadata
    created_at: str = Field(description="ISO 8601 timestamp of first message")
    updated_at: str = Field(description="ISO 8601 timestamp of last message")
    message_count: int = Field(description="Total messages")

    def add_message(self, message: MessageNode) -> None:
        """Add a message to the DAG."""
        self.nodes[message.uuid] = message
        self.message_count = len(self.nodes)
        self.updated_at = message.timestamp

        # Update leaf nodes
        if message.parent_uuid and message.parent_uuid in self.leaf_uuids:
            self.leaf_uuids.remove(message.parent_uuid)

        # Check if this is a leaf
        is_leaf = not any(node.parent_uuid == message.uuid for node in self.nodes.values())
        if is_leaf and message.uuid not in self.leaf_uuids:
            self.leaf_uuids.append(message.uuid)

    def get_children(self, parent_uuid: str) -> list[MessageNode]:
        """Get all children of a node."""
        return [node for node in self.nodes.values() if node.parent_uuid == parent_uuid]

    def extract_path(self, leaf_uuid: str) -> "ConversationPath":
        """Extract a single path from root to leaf."""
        path: list[MessageNode] = []
        current_uuid: str | None = leaf_uuid

        while current_uuid:
            node = self.nodes[current_uuid]
            path.append(node)
            current_uuid = node.parent_uuid

        path.reverse()

        # Find branch points
        branch_points: list[str] = []
        for node in path:
            if len(self.get_children(node.uuid)) > 1:
                branch_points.append(node.uuid)

        return ConversationPath(
            root_uuid=self.root_uuid,
            leaf_uuid=leaf_uuid,
            messages=path,
            branch_points=branch_points,
            path_length=len(path),
            created_at=path[0].timestamp if path else "",
            updated_at=path[-1].timestamp if path else "",
        )

    def get_all_paths(self) -> list["ConversationPath"]:
        """Extract all paths from root to all leaves."""
        return [self.extract_path(leaf) for leaf in self.leaf_uuids]


class ConversationPath(BaseModel):
    """A single path through the conversation DAG."""

    # Path identity
    root_uuid: str = Field(description="Starting message UUID")
    leaf_uuid: str = Field(description="Ending message UUID")

    # Path content
    messages: list[MessageNode] = Field(description="Ordered messages")
    branch_points: list[str] = Field(description="UUIDs where branches exist")
    path_length: int = Field(description="Number of messages")

    # Metadata
    created_at: str = Field(description="ISO 8601 timestamp of first message")
    updated_at: str = Field(description="ISO 8601 timestamp of last message")

    def to_text(self, include_metadata: bool = False) -> str:
        """Convert path to readable text format."""
        lines: list[str] = []
        for msg in self.messages:
            prefix = f"[{msg.role.upper()}]"
            if include_metadata:
                prefix += f" {msg.timestamp}"
            # Handle both string and structured content
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            lines.append(f"{prefix}: {content}")
        return "\n\n".join(lines)


class SessionFile(BaseModel):
    """Physical file metadata for a conversation session."""

    # File identity
    path: Path = Field(description="Absolute path to session file")
    size_bytes: int = Field(description="File size in bytes")
    modified_at: str = Field(description="ISO 8601 file modification time")

    # DAG references
    root_uuid: str = Field(description="Root message UUID")
    leaf_uuids: list[str] = Field(description="All leaf UUIDs")
    path_count: int = Field(description="Number of distinct paths")

    # Content summary
    message_count: int = Field(description="Total messages")
    has_branches: bool = Field(description="Whether file has branches")

    # Compatibility fields for existing code
    @property
    def session_id(self) -> str:
        """Session ID derived from filename."""
        return self.path.stem

    # These fields need to be populated from analysis
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    starts_with_summary: bool = False
    parent_session_id: str | None = None
    has_sidechains: bool = False
    sidechain_count: int = 0
    is_snapshot: bool = False
    snapshot_group: str | None = None
    snapshot_type: str | None = None
    is_completion_marker: bool = False
    is_sdk_generated: bool = False
    sdk_pattern_score: float = 0.0
    continuation_confidence: float = 0.0
    continuation_type: str | None = None
    is_subagent_sidechain: bool = False
    parent_session_ids: list[str] = Field(default_factory=list)
    child_session_ids: list[str] = Field(default_factory=list)
    subagent_invocations: list[str] = Field(default_factory=list)
    sidechain_metadata: dict[str, Any] = Field(default_factory=dict)
