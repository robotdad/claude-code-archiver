"""Enhanced subagent and sidechain detection with conversation flow patterns."""

import json
import logging
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

from .discovery import ConversationFile

# Configure logging
logger = logging.getLogger(__name__)


class DetectionMethod(Enum):
    """Methods used for subagent detection."""

    STRUCTURAL = "structural"  # Based on isSidechain, parentUuid, etc.
    FLOW_PATTERN = "flow_pattern"  # Based on message count and Task call patterns
    HYBRID = "hybrid"  # Combination of both methods
    INFRASTRUCTURE_FILTER = "infrastructure_filter"  # Single message filter


class AgentType(Enum):
    """Known subagent types from Claude Code ecosystem."""

    CONCEPT_EXTRACTOR = "concept-extractor"
    BUG_HUNTER = "bug-hunter"
    INSIGHT_SYNTHESIS = "insight-synthesis"
    CODE_ANALYZER = "code-analyzer"
    PATTERN_DETECTOR = "pattern-detector"
    SECURITY_AUDITOR = "security-auditor"
    PERFORMANCE_OPTIMIZER = "performance-optimizer"
    UNKNOWN = "unknown"


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
    # Enhanced flow detection fields
    message_count_before: int = 0
    message_count_after: int = 0
    is_context_switch: bool = False
    agent_type: AgentType = AgentType.UNKNOWN


@dataclass
class SidechainRelationship:
    """Represents a parent-child relationship between sessions via Task invocation."""

    parent_session_id: str
    child_session_id: str
    invocation_uuid: str
    subagent_type: str
    created_timestamp: str
    temporal_gap_seconds: float
    # Enhanced detection metadata
    detection_method: DetectionMethod = DetectionMethod.STRUCTURAL
    confidence_score: float = 0.0
    agent_type: AgentType = AgentType.UNKNOWN
    is_infrastructure: bool = False
    message_count_pattern: dict[str, int] = field(default_factory=lambda: {})


@dataclass
class ConversationFlowContext:
    """Tracks conversation flow patterns for subagent detection."""

    session_id: str
    message_counts: list[int] = field(default_factory=lambda: [])  # Message count at each significant point
    task_invocation_indices: list[int] = field(default_factory=lambda: [])  # Indices where Task calls occurred
    context_switches: list[dict[str, Any]] = field(default_factory=lambda: [])  # Detected context switches
    active_subagent: str | None = None  # Currently active subagent type
    is_infrastructure_session: bool = False
    flow_confidence: float = 0.0


def analyze_conversation_flow(conversation_file: ConversationFile) -> ConversationFlowContext:
    """Analyze conversation flow patterns for subagent detection.

    This is the revolutionary insight: Message count patterns reveal subagent context switches
    more reliably than structural markers alone.

    Args:
        conversation_file: ConversationFile object to analyze

    Returns:
        ConversationFlowContext with detected patterns
    """
    context = ConversationFlowContext(session_id=conversation_file.session_id)

    try:
        with open(conversation_file.path, encoding="utf-8") as f:
            lines = f.readlines()
            total_messages = len(lines)

            # Track message counts and Task invocations
            message_count = 0

            for i, line in enumerate(lines):
                try:
                    data = json.loads(line)
                    message_count = i + 1

                    # Detect Task tool invocations
                    if data.get("type") == "message" and data.get("role") == "assistant":
                        tool_calls = data.get("tool_calls", [])

                        for tool_call in tool_calls:
                            if tool_call.get("function", {}).get("name") == "Task":
                                # Record the Task invocation point
                                context.task_invocation_indices.append(i)
                                context.message_counts.append(message_count)

                                # Check for context switch pattern (message count drop after Task)
                                if i < len(lines) - 10:  # Look ahead for pattern
                                    next_messages = lines[i + 1 : i + 11]  # Check next 10 messages
                                    reset_detected = False

                                    for j, next_line in enumerate(next_messages, 1):
                                        try:
                                            next_data = json.loads(next_line)
                                            # Look for new conversation start pattern
                                            if (
                                                next_data.get("type") == "message"
                                                and next_data.get("role") == "user"
                                                and j <= 3
                                            ):  # Within first few messages
                                                reset_detected = True
                                                break
                                        except (json.JSONDecodeError, KeyError):
                                            continue

                                    if reset_detected:
                                        context.context_switches.append(
                                            {
                                                "task_index": i,
                                                "message_count_before": message_count,
                                                "message_count_after": 1,  # Reset to 1
                                                "detection_method": DetectionMethod.FLOW_PATTERN.value,
                                            }
                                        )

                except (json.JSONDecodeError, KeyError):
                    continue

            # Analyze patterns
            if len(context.context_switches) > 0:
                context.flow_confidence = 0.8
                context.active_subagent = "detected"

            # Infrastructure detection: single message sessions are likely infrastructure
            if total_messages <= 2:
                context.is_infrastructure_session = True
                context.flow_confidence = 0.9

    except OSError as e:
        logger.error(f"Unable to read conversation file {conversation_file.path}: {e}")

    return context


def classify_agent_type(subagent_type: str) -> AgentType:
    """Classify subagent type string into AgentType enum.

    Args:
        subagent_type: String from Task invocation

    Returns:
        Corresponding AgentType enum value
    """
    type_mapping = {
        "concept-extractor": AgentType.CONCEPT_EXTRACTOR,
        "bug-hunter": AgentType.BUG_HUNTER,
        "insight-synthesis": AgentType.INSIGHT_SYNTHESIS,
        "code-analyzer": AgentType.CODE_ANALYZER,
        "pattern-detector": AgentType.PATTERN_DETECTOR,
        "security-auditor": AgentType.SECURITY_AUDITOR,
        "performance-optimizer": AgentType.PERFORMANCE_OPTIMIZER,
    }

    return type_mapping.get(subagent_type.lower(), AgentType.UNKNOWN)


def detect_infrastructure_noise(conversation_file: ConversationFile, flow_context: ConversationFlowContext) -> bool:
    """Filter infrastructure noise using message count and context patterns.

    Infrastructure requests are typically:
    - Single messages or very short conversations
    - No complex tool usage patterns
    - No sustained interaction

    Args:
        conversation_file: ConversationFile to analyze
        flow_context: Flow analysis context

    Returns:
        True if this appears to be infrastructure noise
    """
    # Single message filter
    if conversation_file.message_count <= 1:
        return True

    # Very short conversations with no Task invocations
    if conversation_file.message_count <= 3 and len(flow_context.task_invocation_indices) == 0:
        return True

    # Use flow context infrastructure detection
    return bool(flow_context.is_infrastructure_session)


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

                                    # Enhanced with flow detection
                                    agent_type = classify_agent_type(subagent_type)

                                    invocation = SubagentInvocation(
                                        message_uuid=str(data.get("uuid", "")),
                                        timestamp=str(data.get("timestamp", "")),
                                        subagent_type=subagent_type,
                                        description=description,
                                        session_id=conversation_file.session_id,
                                        tool_use_id=str(tool_call.get("id", "")),
                                        input_parameters=input_params,
                                        message_count_before=line_num,
                                        agent_type=agent_type,
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
    """Map parent-sidechain relationships with enhanced flow-based detection.

    Revolutionary approach: Combines structural analysis with conversation flow patterns
    for dramatically improved detection accuracy.

    Args:
        conversations: List of all conversation files to analyze

    Returns:
        Dictionary mapping parent session IDs to lists of sidechain relationships
    """
    # Phase 1: Analyze conversation flows for all sessions
    flow_contexts: dict[str, ConversationFlowContext] = {}
    for conv in conversations:
        flow_contexts[conv.session_id] = analyze_conversation_flow(conv)

    # Phase 2: Extract all Task invocations from all conversations
    all_invocations: list[SubagentInvocation] = []
    for conv in conversations:
        # Skip infrastructure noise early
        flow_context = flow_contexts[conv.session_id]
        if detect_infrastructure_noise(conv, flow_context):
            continue

        invocations = extract_task_invocations(conv)
        all_invocations.extend(invocations)

    # Phase 3: Build relationship map with enhanced detection
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

                # Enhanced detection with flow context
                child_flow = flow_contexts.get(child_session_id)
                detection_method = (
                    DetectionMethod.HYBRID
                    if child_flow and child_flow.flow_confidence > 0.5
                    else DetectionMethod.STRUCTURAL
                )
                confidence_score = child_flow.flow_confidence if child_flow else 0.5

                # Check if infrastructure
                is_infrastructure = False
                if child_conv and child_flow:
                    is_infrastructure = detect_infrastructure_noise(child_conv, child_flow)

                relationship = SidechainRelationship(
                    parent_session_id=invocation.session_id,
                    child_session_id=child_session_id,
                    invocation_uuid=invocation.message_uuid,
                    subagent_type=invocation.subagent_type,
                    created_timestamp=child_conv.first_timestamp if child_conv and child_conv.first_timestamp else "",
                    temporal_gap_seconds=temporal_gap,
                    detection_method=detection_method,
                    confidence_score=confidence_score,
                    agent_type=invocation.agent_type,
                    is_infrastructure=is_infrastructure,
                    message_count_pattern={
                        "parent_count": invocation.message_count_before,
                        "child_count": child_conv.message_count if child_conv else 0,
                    },
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
    """Extract enhanced metadata about subagent activity with flow-based insights.

    Args:
        conversation: ConversationFile to analyze
        relationships: Sidechain relationships mapping

    Returns:
        Dictionary with enhanced subagent metadata including flow patterns
    """
    # Revolutionary enhancement: Add flow analysis
    flow_context = analyze_conversation_flow(conversation)
    invocations = extract_task_invocations(conversation)
    session_type = classify_subagent_session_type(conversation)

    # Get child relationships
    child_relationships = relationships.get(conversation.session_id, [])

    # Extract subagent types and agent types used
    subagent_types = list({inv.subagent_type for inv in invocations})
    agent_types = list({inv.agent_type.value for inv in invocations})

    # Flow-based detection insights
    detection_methods = list({rel.detection_method.value for rel in child_relationships})
    confidence_scores = [rel.confidence_score for rel in child_relationships if rel.confidence_score > 0]

    metadata = {
        # Traditional metadata
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
        # Revolutionary flow-based enhancements
        "agent_types": agent_types,
        "flow_confidence": flow_context.flow_confidence,
        "context_switches": len(flow_context.context_switches),
        "is_infrastructure": flow_context.is_infrastructure_session,
        "detection_methods": detection_methods,
        "average_confidence": (sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0),
        "message_count_patterns": {
            "total_messages": conversation.message_count,
            "task_invocation_indices": flow_context.task_invocation_indices,
            "context_switch_count": len(flow_context.context_switches),
        },
        "subagent_info": {
            "active_subagent": flow_context.active_subagent,
            "is_subagent": flow_context.flow_confidence > 0.5,
            "primary_detection_method": detection_methods[0] if detection_methods else "none",
        },
    }

    return metadata
