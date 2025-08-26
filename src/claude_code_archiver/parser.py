"""JSONL parser for Claude Code conversations."""

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic import Field


class MessageType(str, Enum):
    """Message types in conversations."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    SUMMARY = "summary"


class ContentType(str, Enum):
    """Content types within messages."""

    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    IMAGE = "image"
    THINKING = "thinking"


class ContentBlock(BaseModel):
    """Content block within a message."""

    type: ContentType
    text: str | None = None
    tool_use_id: str | None = None
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    tool_result: str | None = None
    is_error: bool | None = None  # Can be None, not always False
    thinking: str | None = None
    signature: str | None = None
    image_data: str | None = None  # Base64 encoded image

    # Additional fields for tool use blocks
    id: str | None = None  # Tool use ID
    name: str | None = None  # Tool name (alternative field name)
    input: dict[str, Any] | None = None  # Tool input (alternative field name)


class Message(BaseModel):
    """Represents a message in the conversation."""

    role: str
    content: Any  # Can be string or list of ContentBlock
    id: str | None = None
    type: str | None = None
    model: str | None = None
    stop_reason: str | None = None
    usage: dict[str, Any] | None = None


class ConversationEntry(BaseModel):
    """Represents a single entry in the conversation."""

    type: MessageType
    uuid: str | None = None
    parent_uuid: str | None = Field(None, alias="parentUuid")
    timestamp: str | None = None
    session_id: str | None = Field(None, alias="sessionId")
    version: str | None = None
    cwd: str | None = None
    git_branch: str | None = Field(None, alias="gitBranch")
    message: Message | None = None
    request_id: str | None = Field(None, alias="requestId")

    # Additional fields found in real data
    is_sidechain: bool | None = Field(None, alias="isSidechain")
    user_type: str | None = Field(None, alias="userType")
    tool_use_result: Any | None = Field(None, alias="toolUseResult")

    # For summary entries
    summary: str | None = None
    leaf_uuid: str | None = Field(None, alias="leafUuid")

    # For system entries
    content: str | None = None
    level: str | None = None
    is_meta: bool | None = Field(None, alias="isMeta")
    tool_use_id: str | None = Field(None, alias="toolUseID")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class ConversationParser:
    """Parses Claude Code conversation JSONL files."""

    def parse_file(self, file_path: Path) -> list[ConversationEntry]:
        """Parse a JSONL conversation file.

        Args:
            file_path: Path to the JSONL file

        Returns:
            List of parsed conversation entries

        Raises:
            ValueError: If file cannot be parsed
        """
        entries: list[ConversationEntry] = []

        try:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)
                        entry = self._parse_entry(data)
                        entries.append(entry)
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Warning: Failed to parse line {line_num}: {e}")
                        continue

        except OSError as e:
            raise ValueError(f"Cannot read file {file_path}: {e}") from e

        return entries

    def _parse_entry(self, data: dict[str, Any]) -> ConversationEntry:
        """Parse a single conversation entry.

        Args:
            data: Raw JSON data

        Returns:
            Parsed ConversationEntry
        """
        # Parse message if present
        if "message" in data and isinstance(data["message"], dict):
            message_data: dict[str, Any] = data["message"]  # type: ignore[assignment]

            # Parse content blocks if content is a list
            if isinstance(message_data.get("content"), list):
                content_blocks: list[ContentBlock] = []
                content_list: list[Any] = message_data["content"]  # type: ignore[assignment]
                for item in content_list:
                    if isinstance(item, dict):
                        content_blocks.append(self._parse_content_block(item))  # type: ignore[arg-type]
                message_data["content"] = content_blocks

            data["message"] = Message(**message_data)  # type: ignore[arg-type]

        return ConversationEntry(**data)

    def _parse_content_block(self, data: dict[str, Any]) -> ContentBlock:
        """Parse a content block.

        Args:
            data: Raw content block data

        Returns:
            Parsed ContentBlock
        """
        block_type = data.get("type")

        if block_type == "tool_use":
            return ContentBlock(
                type=ContentType.TOOL_USE,
                tool_use_id=data.get("id"),
                tool_name=data.get("name"),
                tool_input=data.get("input"),
            )
        if block_type == "tool_result":
            content = data.get("content")

            # Handle both string and array content
            if isinstance(content, list):
                # Extract text from content blocks
                text_parts: list[str] = []
                content_list: list[Any] = content  # type: ignore[assignment]
                for item in content_list:
                    if isinstance(item, dict) and item.get("type") == "text":  # type: ignore[union-attr]
                        text_parts.append(str(item.get("text", "")))  # type: ignore[arg-type]
                tool_result = "\n".join(text_parts) if text_parts else ""
            else:
                tool_result = content

            return ContentBlock(
                type=ContentType.TOOL_RESULT,
                tool_use_id=data.get("tool_use_id"),
                tool_result=tool_result,
                is_error=data.get("is_error", False),
            )
        if block_type == "thinking":
            return ContentBlock(
                type=ContentType.THINKING,
                thinking=data.get("thinking"),
                signature=data.get("signature"),
            )
        if block_type == "image":
            return ContentBlock(type=ContentType.IMAGE, image_data=data.get("source", {}).get("data"))
        return ContentBlock(type=ContentType.TEXT, text=data.get("text"))

    def extract_statistics(self, entries: list[ConversationEntry]) -> dict[str, Any]:
        """Extract statistics from parsed conversation.

        Args:
            entries: List of conversation entries

        Returns:
            Dictionary with conversation statistics
        """
        stats: dict[str, Any] = {
            "total_messages": len(entries),
            "user_messages": 0,
            "assistant_messages": 0,
            "system_messages": 0,
            "summary_messages": 0,
            "tool_uses": {},
            "has_images": False,
            "has_thinking": False,
        }

        for entry in entries:
            if entry.type == MessageType.USER:
                stats["user_messages"] += 1
            elif entry.type == MessageType.ASSISTANT:
                stats["assistant_messages"] += 1
            elif entry.type == MessageType.SYSTEM:
                stats["system_messages"] += 1
            elif entry.type == MessageType.SUMMARY:
                stats["summary_messages"] += 1

            # Count tool uses
            if entry.message and isinstance(entry.message.content, list):
                content_list: list[Any] = entry.message.content  # type: ignore[assignment]
                for block in content_list:
                    if isinstance(block, ContentBlock):
                        if block.type == ContentType.TOOL_USE and block.tool_name:
                            tool_uses: dict[str, int] = stats["tool_uses"]  # type: ignore[assignment]
                            tool_uses[block.tool_name] = tool_uses.get(block.tool_name, 0) + 1
                        elif block.type == ContentType.IMAGE:
                            stats["has_images"] = True
                        elif block.type == ContentType.THINKING:
                            stats["has_thinking"] = True

        return stats
