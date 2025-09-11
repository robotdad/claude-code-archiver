"""Command-Only Conversation Detection Module.

A self-contained module for detecting conversations that contain only commands
and meta messages, with no actual conversational content or assistant responses.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from .discovery import ConversationFile

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class CommandPattern:
    """Results of command-only pattern detection analysis."""

    message_count: int
    user_message_count: int
    assistant_message_count: int
    command_message_count: int
    meta_message_count: int
    has_real_conversation: bool
    confidence_score: float


def detect_command_only_pattern(conversation_file: ConversationFile) -> CommandPattern:
    """Detect if conversation contains only commands and meta messages.

    Command-only conversations have these characteristics:
    1. No assistant messages
    2. Only user messages containing:
       - Caveat/meta messages (isMeta: true)
       - Command executions (<command-name> tags)
       - Command output messages
    3. No actual conversational content
    4. Usually very short (< 10 messages)

    Args:
        conversation_file: ConversationFile object to analyze

    Returns:
        CommandPattern object with detection results and confidence score
    """
    message_count = 0
    user_message_count = 0
    assistant_message_count = 0
    command_message_count = 0
    meta_message_count = 0
    has_real_conversation = False

    try:
        with open(conversation_file.path, encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                message_type = data.get("type")

                if message_type == "user":
                    user_message_count += 1
                    message_count += 1

                    # Check if this is a meta message
                    if data.get("isMeta", False):
                        meta_message_count += 1
                        continue

                    # Check message content
                    message_content = data.get("message", {})
                    content: Any = message_content.get("content", "")

                    # Convert to string if it's a list format
                    if isinstance(content, list):
                        content_parts: list[str] = []
                        for item in content:  # type: ignore
                            item_typed: Any = item  # type: ignore
                            if isinstance(item_typed, dict) and item_typed.get("type") == "text":  # type: ignore
                                text_value: Any = item_typed.get("text", "")  # type: ignore
                                if isinstance(text_value, str):
                                    content_parts.append(text_value)
                        content = " ".join(content_parts)

                    # Ensure content is a string
                    if not isinstance(content, str):
                        content = str(content)

                    # Check for command patterns
                    if "<command-name>" in content or "<local-command-stdout>" in content:
                        command_message_count += 1
                    elif "Caveat:" in content and "DO NOT respond" in content:
                        meta_message_count += 1
                    else:
                        # This appears to be real conversational content
                        if len(content.strip()) > 20:  # Minimal length for real content
                            has_real_conversation = True

                elif message_type == "assistant":
                    assistant_message_count += 1
                    message_count += 1

                    # If there's an assistant message, it's likely a real conversation
                    message_content = data.get("message", {})
                    content: Any = message_content.get("content", [])

                    # Check if assistant has substantial content
                    if isinstance(content, list) and len(content) > 0:  # type: ignore
                        for item in content:  # type: ignore
                            item_typed: Any = item  # type: ignore
                            if isinstance(item_typed, dict):
                                text_content: Any = item_typed.get("text", "")  # type: ignore
                                if isinstance(text_content, str) and len(text_content.strip()) > 10:
                                    has_real_conversation = True
                                    break

                elif message_type in ["summary", "system"]:
                    # These don't count as conversational content
                    message_count += 1

            except (json.JSONDecodeError, KeyError) as e:
                logger.debug(f"Failed to parse line in {conversation_file.path}: {e}")
                continue

    except OSError as e:
        logger.error(f"Unable to read conversation file {conversation_file.path}: {e}")
        return CommandPattern(
            message_count=0,
            user_message_count=0,
            assistant_message_count=0,
            command_message_count=0,
            meta_message_count=0,
            has_real_conversation=True,  # Assume it's real if we can't read it
            confidence_score=0.0,
        )
    except Exception as e:
        logger.error(f"Unexpected error during command pattern detection for {conversation_file.path}: {e}")
        return CommandPattern(
            message_count=0,
            user_message_count=0,
            assistant_message_count=0,
            command_message_count=0,
            meta_message_count=0,
            has_real_conversation=True,  # Assume it's real if we can't read it
            confidence_score=0.0,
        )

    # Calculate confidence score
    confidence_score = _calculate_confidence_score(
        message_count,
        user_message_count,
        assistant_message_count,
        command_message_count,
        meta_message_count,
        has_real_conversation,
    )

    return CommandPattern(
        message_count=message_count,
        user_message_count=user_message_count,
        assistant_message_count=assistant_message_count,
        command_message_count=command_message_count,
        meta_message_count=meta_message_count,
        has_real_conversation=has_real_conversation,
        confidence_score=confidence_score,
    )


def is_command_only(conversation_file: ConversationFile) -> bool:
    """Simple boolean check for command-only conversations.

    Args:
        conversation_file: ConversationFile object to check

    Returns:
        True if conversation is command-only (confidence > 0.8)
    """
    pattern = detect_command_only_pattern(conversation_file)
    return pattern.confidence_score > 0.8


def _calculate_confidence_score(
    message_count: int,
    user_message_count: int,
    assistant_message_count: int,
    command_message_count: int,
    meta_message_count: int,
    has_real_conversation: bool,
) -> float:
    """Calculate confidence score for command-only pattern detection.

    High Confidence Indicators (0.9+):
    - No assistant messages
    - All user messages are commands or meta
    - No real conversational content
    - Very short conversation (< 10 messages)

    Medium Confidence Indicators (0.6-0.8):
    - Mostly commands and meta messages
    - Minimal assistant responses
    - Short conversation

    Low Confidence Indicators (< 0.6):
    - Has real conversational content
    - Multiple assistant responses
    - Longer conversations

    Args:
        Various count and boolean indicators from pattern detection

    Returns:
        Confidence score between 0.0 and 1.0
    """
    # If there's real conversation, it's not command-only
    if has_real_conversation:
        return 0.0

    # If there are assistant messages, reduce confidence significantly
    if assistant_message_count > 0:
        return max(0.0, 0.3 - (assistant_message_count * 0.1))

    # Check if all user messages are commands or meta
    total_command_and_meta = command_message_count + meta_message_count

    # If all user messages are commands/meta, high confidence
    if user_message_count > 0 and total_command_and_meta >= user_message_count:
        score = 0.9

        # Boost for very short conversations
        if message_count < 10:
            score += 0.05
        if message_count < 7:
            score += 0.05

        return min(score, 1.0)

    # If most messages are commands/meta
    if user_message_count > 0:
        command_ratio = total_command_and_meta / user_message_count
        if command_ratio > 0.8:
            return 0.7
        if command_ratio > 0.6:
            return 0.5

    # Default to low confidence
    return 0.2
