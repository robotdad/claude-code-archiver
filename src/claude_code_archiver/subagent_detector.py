"""Subagent and sidechain detection module for Task tool invocations."""

import json
import logging
from dataclasses import dataclass
from typing import Any

from .discovery import ConversationFile

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SubagentInvocation:
    """Represents a Task tool invocation that may spawn a subagent session."""

    message_uuid: str
    timestamp: str
    subagent_type: str
    description: str
    session_id: str
    tool_use_id: str
    input_parameters: dict[str, Any]


@dataclass
class SidechainRelationship:
    """Represents a parent-child relationship between sessions via Task invocation."""

    parent_session_id: str
    child_session_id: str
    invocation_uuid: str
    subagent_type: str
    created_timestamp: str
    temporal_gap_seconds: float


def extract_task_invocations(conversation_file: ConversationFile) -> list[SubagentInvocation]:
    """Extract Task tool invocations from a conversation file.

    Args:
        conversation_file: ConversationFile object to analyze

    Returns:
        List of SubagentInvocation objects found in the conversation
    """
    invocations: list[SubagentInvocation] = []

    try:
        with open(conversation_file.path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)

                    # Look for messages with tool_calls containing Task invocations
                    if data.get("type") == "message" and data.get("role") == "assistant":
                        tool_calls = data.get("tool_calls", [])

                        for tool_call in tool_calls:
                            try:
                                if tool_call.get("function", {}).get("name") == "Task":
                                    # Parse the input parameters
                                    input_str = tool_call.get("function", {}).get("arguments", "{}")
                                    try:
                                        input_params: dict[str, Any] = json.loads(input_str)
                                    except json.JSONDecodeError as e:
                                        logger.debug(
                                            f"Failed to parse Task arguments in {conversation_file.path}:{line_num}: {e}"
                                        )
                                        input_params = {}

                                    subagent_type: str = str(input_params.get("subagent_type", "unknown"))
                                    description: str = str(input_params.get("description", ""))

                                    invocation = SubagentInvocation(
                                        message_uuid=str(data.get("uuid", "")),
                                        timestamp=str(data.get("timestamp", "")),
                                        subagent_type=subagent_type,
                                        description=description,
                                        session_id=conversation_file.session_id,
                                        tool_use_id=str(tool_call.get("id", "")),
                                        input_parameters=input_params,
                                    )
                                    invocations.append(invocation)
                            except KeyError as e:
                                logger.debug(
                                    f"Missing expected field in tool_call at {conversation_file.path}:{line_num}: {e}"
                                )
                                continue
                            except Exception as e:
                                logger.warning(
                                    f"Error processing tool_call at {conversation_file.path}:{line_num}: {e}"
                                )
                                continue

                except json.JSONDecodeError as e:
                    logger.debug(f"Skipping malformed line {line_num} in {conversation_file.path}: {e}")
                    continue
                except KeyError as e:
                    logger.debug(f"Missing expected field in line {line_num} of {conversation_file.path}: {e}")
                    continue

    except OSError as e:
        logger.error(f"Unable to read conversation file {conversation_file.path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error extracting Task invocations from {conversation_file.path}: {e}")
        return []

    return invocations


def detect_cross_session_relationships(conversations: list[ConversationFile]) -> dict[str, list[SidechainRelationship]]:
    """Map parent-sidechain relationships across different sessions.

    Args:
        conversations: List of all conversation files to analyze

    Returns:
        Dictionary mapping parent session IDs to lists of sidechain relationships
    """
    # Extract all Task invocations from all conversations
    all_invocations: list[SubagentInvocation] = []
    for conv in conversations:
        invocations = extract_task_invocations(conv)
        all_invocations.extend(invocations)

    # Build relationship map
    relationships: dict[str, list[SidechainRelationship]] = {}

    for invocation in all_invocations:
        # Find potential sidechain sessions for this invocation
        sidechain_sessions = _find_matching_sidechains(invocation, conversations)

        if sidechain_sessions:
            if invocation.session_id not in relationships:
                relationships[invocation.session_id] = []

            for child_session_id in sidechain_sessions:
                # Calculate temporal gap
                child_conv = next((c for c in conversations if c.session_id == child_session_id), None)
                child_timestamp = child_conv.first_timestamp if child_conv and child_conv.first_timestamp else ""
                temporal_gap = _calculate_temporal_gap(invocation.timestamp, child_timestamp)

                relationship = SidechainRelationship(
                    parent_session_id=invocation.session_id,
                    child_session_id=child_session_id,
                    invocation_uuid=invocation.message_uuid,
                    subagent_type=invocation.subagent_type,
                    created_timestamp=child_conv.first_timestamp if child_conv and child_conv.first_timestamp else "",
                    temporal_gap_seconds=temporal_gap,
                )
                relationships[invocation.session_id].append(relationship)

    return relationships


def _find_matching_sidechains(invocation: SubagentInvocation, all_conversations: list[ConversationFile]) -> list[str]:
    """Find conversations that match this Task invocation as potential sidechains.

    Args:
        invocation: The Task invocation to find matches for
        all_conversations: All available conversation files

    Returns:
        List of session IDs that are likely spawned by this invocation
    """
    matching_sessions: list[str] = []

    for conv in all_conversations:
        # Skip same session
        if conv.session_id == invocation.session_id:
            continue

        # Skip if no timestamp data
        if not conv.first_timestamp or not invocation.timestamp:
            continue

        # Check if conversation started after the invocation
        if not _is_timestamp_after(conv.first_timestamp, invocation.timestamp):
            continue

        # Calculate time gap (should be small for spawned sessions)
        time_gap = _calculate_temporal_gap(invocation.timestamp, conv.first_timestamp)

        # Only consider sessions that started within reasonable time window (10 minutes)
        if time_gap > 600:  # 10 minutes in seconds
            continue

        # Check for parent UUID compatibility in the sidechain conversation
        if _has_compatible_parent_chain(invocation.message_uuid, conv):
            matching_sessions.append(conv.session_id)

    return matching_sessions


def _has_compatible_parent_chain(parent_uuid: str, conversation: ConversationFile) -> bool:
    """Check if conversation has references to the parent UUID in its chain.

    Args:
        parent_uuid: UUID from the parent Task invocation
        conversation: ConversationFile to check for parent references

    Returns:
        True if conversation appears to be spawned from parent UUID
    """
    try:
        with open(conversation.path, encoding="utf-8") as f:
            # Check first few messages for parent references
            for line_count, line in enumerate(f, 1):
                if line_count > 5:  # Only check first few messages
                    break

                try:
                    data = json.loads(line)

                    # Check for parentUuid field (common in spawned sessions)
                    if data.get("parentUuid") == parent_uuid:
                        return True

                    # Check for references to parent UUID in message content
                    content = data.get("content", "")
                    if isinstance(content, str) and parent_uuid in content:
                        return True

                    # Check for leaf_uuid matching parent (summary continuations)
                    if data.get("leafUuid") == parent_uuid:
                        return True

                except json.JSONDecodeError as e:
                    logger.debug(f"Skipping malformed line {line_count} in {conversation.path}: {e}")
                    continue
                except KeyError as e:
                    logger.debug(f"Missing expected field in line {line_count} of {conversation.path}: {e}")
                    continue

    except OSError as e:
        logger.error(f"Unable to read conversation file {conversation.path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking parent chain compatibility for {conversation.path}: {e}")
        return False

    return False


def _is_timestamp_after(timestamp1: str, timestamp2: str) -> bool:
    """Check if timestamp1 is after timestamp2."""
    try:
        # Simple string comparison works for ISO timestamps
        return timestamp1 > timestamp2
    except (TypeError, ValueError):
        return False


def _calculate_temporal_gap(start_timestamp: str, end_timestamp: str) -> float:
    """Calculate temporal gap in seconds between two timestamps.

    Args:
        start_timestamp: Earlier timestamp
        end_timestamp: Later timestamp

    Returns:
        Gap in seconds, or 0.0 if calculation fails
    """
    try:
        from datetime import datetime

        # Parse ISO timestamps
        start = datetime.fromisoformat(start_timestamp.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_timestamp.replace("Z", "+00:00"))

        return (end - start).total_seconds()
    except (ValueError, TypeError, AttributeError):
        return 0.0


def classify_subagent_session_type(conversation: ConversationFile) -> str:
    """Classify the type of subagent session based on its characteristics.

    Args:
        conversation: ConversationFile to classify

    Returns:
        String describing the session type
    """
    # Count Task invocations in this conversation
    invocations = extract_task_invocations(conversation)
    task_count = len(invocations)

    # Classify based on patterns
    if task_count >= 3:
        return "multi_agent_workflow"
    if task_count >= 1:
        return "subagent_sidechain"
    if conversation.has_sidechains:
        return "sidechain_container"
    return "standard_session"


def get_subagent_metadata(
    conversation: ConversationFile, relationships: dict[str, list[SidechainRelationship]]
) -> dict[str, Any]:
    """Extract metadata about subagent activity for a conversation.

    Args:
        conversation: ConversationFile to analyze
        relationships: Sidechain relationships mapping

    Returns:
        Dictionary with subagent metadata
    """
    invocations = extract_task_invocations(conversation)
    session_type = classify_subagent_session_type(conversation)

    # Get child relationships
    child_relationships = relationships.get(conversation.session_id, [])

    # Extract subagent types used
    subagent_types = list({inv.subagent_type for inv in invocations})

    metadata = {
        "session_type": session_type,
        "task_invocation_count": len(invocations),
        "subagent_types": subagent_types,
        "spawned_session_count": len(child_relationships),
        "spawned_session_ids": [rel.child_session_id for rel in child_relationships],
        "average_spawn_gap_seconds": (
            sum(rel.temporal_gap_seconds for rel in child_relationships) / len(child_relationships)
            if child_relationships
            else 0.0
        ),
    }

    return metadata
