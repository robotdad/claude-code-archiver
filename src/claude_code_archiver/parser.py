"""JSONL parser that builds ConversationDAG from session files."""

import json
from pathlib import Path
from typing import Any

from .models import ConversationDAG
from .models import EdgeType
from .models import MessageNode


class ConversationParser:
    """Parses Claude Code conversation JSONL files into DAG structure."""

    def parse_file(self, file_path: Path) -> ConversationDAG:
        """Parse a JSONL conversation file into a DAG.

        Args:
            file_path: Path to the JSONL file

        Returns:
            ConversationDAG with all messages
        """
        messages = self._load_messages(file_path)

        if not messages:
            raise ValueError(f"No messages found in {file_path}")

        # Find root (first message with no parent)
        root_msg = next((m for m in messages if m.parent_uuid is None), None)
        if not root_msg:
            raise ValueError(f"No root message found in {file_path}")

        # Build DAG
        dag = ConversationDAG(
            root_uuid=root_msg.uuid, created_at=root_msg.timestamp, updated_at=root_msg.timestamp, message_count=0
        )

        for msg in messages:
            dag.add_message(msg)

        return dag

    def _load_messages(self, file_path: Path) -> list[MessageNode]:
        """Load and parse all messages from JSONL file."""
        messages = []

        with open(file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                try:
                    data = json.loads(line)
                    msg = self._parse_message(data)
                    if msg:
                        messages.append(msg)
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Warning: Skipping line {line_num}: {e}")
                    continue

        return messages

    def _parse_message(self, data: dict[str, Any]) -> MessageNode | None:
        """Parse a single message from JSON data."""
        # Skip summary messages (not part of conversation DAG)
        if data.get("type") == "summary":
            return None

        # Determine edge type
        edge_type = self._determine_edge_type(data)

        # Extract content
        content = self._extract_content(data)

        # Extract role
        role = self._determine_role(data)

        return MessageNode(
            uuid=data.get("uuid", ""),
            timestamp=data.get("timestamp", ""),
            parent_uuid=data.get("parentUuid"),
            edge_type=edge_type,
            role=role,
            content=content,
            model=data.get("message", {}).get("model"),
            tokens=data.get("message", {}).get("usage", {}).get("output_tokens"),
        )

    def _determine_edge_type(self, data: dict[str, Any]) -> EdgeType:
        """Determine edge type from message data."""
        # No parent = root
        if not data.get("parentUuid"):
            return "root"

        # Compact boundary uses logical parent
        if data.get("subtype") == "compact_boundary":
            return "compact"

        # Sidechain messages
        if data.get("isSidechain"):
            return "branch"

        # Default to normal edge
        return "normal"

    def _determine_role(self, data: dict[str, Any]) -> str:
        """Determine message role."""
        msg_type = data.get("type", "user")

        # Map types to roles
        if msg_type == "assistant":
            return "assistant"
        if msg_type == "system":
            return "system"
        return "user"

    def _extract_content(self, data: dict[str, Any]) -> str | list[Any]:
        """Extract message content."""
        message = data.get("message", {})
        content = message.get("content", "")

        # Return as-is (string or list)
        return content if content else "[Empty]"
