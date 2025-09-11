"""Enhanced continuation detection module."""

import json
import logging
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

# Configure logging
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .discovery import ConversationFile


@dataclass
class SummaryPattern:
    """Analysis of summary patterns in a conversation."""

    summary_count: int
    is_single_continuation_summary: bool
    has_session_transitions: bool
    confidence_score: float
    summary_type: str | None = None  # "single_summary", "multi_summary", "none"
    session_ids_found: set[str] = field(default_factory=lambda: set())


def detect_continuation_pattern(conversation_file: "ConversationFile") -> SummaryPattern:
    """Detect true continuation vs context history patterns.

    Args:
        conversation_file: ConversationFile object to analyze

    Returns:
        SummaryPattern with analysis results
    """
    file_path = conversation_file.path

    # Analyze summary context
    is_single_summary, summary_count, _ = _analyze_summary_context(file_path)

    # Detect session transitions
    has_transitions, session_ids = _detect_session_transitions(file_path)

    # Check for explicit continuation content
    _, content_confidence = _detect_explicit_continuation_content(file_path)

    # Calculate confidence score
    structural_confidence = _calculate_confidence_score(
        is_single_summary=is_single_summary,
        summary_count=summary_count,
        has_session_transitions=has_transitions,
        starts_with_summary=conversation_file.starts_with_summary,
        parent_session_id=conversation_file.parent_session_id,
        is_sdk_generated=conversation_file.is_sdk_generated,
    )

    # Use max of structural and content confidence
    confidence_score = max(structural_confidence, content_confidence)

    # Determine summary type
    if summary_count == 0:
        summary_type = "none"
    elif summary_count == 1 and is_single_summary:
        summary_type = "single_summary"
    else:
        summary_type = "multi_summary"

    return SummaryPattern(
        summary_count=summary_count,
        is_single_continuation_summary=is_single_summary,
        has_session_transitions=has_transitions,
        confidence_score=confidence_score,
        summary_type=summary_type,
        session_ids_found=session_ids,
    )


def _analyze_summary_context(file_path: Path) -> tuple[bool, int, bool]:
    """Analyze summary patterns in the conversation file.

    Args:
        file_path: Path to the conversation file

    Returns:
        Tuple of (is_single_continuation_summary, summary_count, has_session_transitions)
    """
    summary_count = 0
    is_single_continuation_summary = False
    has_session_transitions = False
    session_ids_seen: set[str] = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

            # Look at first 30 lines for pattern analysis (some conversations have many summaries)
            analysis_lines = lines[: min(30, len(lines))]

            for i, line in enumerate(analysis_lines):
                try:
                    data = json.loads(line)

                    # Count summaries
                    if data.get("type") == "summary":
                        summary_count += 1

                    # Track session IDs for transition detection
                    if session_id := data.get("sessionId"):
                        session_ids_seen.add(session_id)

                    # Check for compaction summary in first message
                    if i == 0 and data.get("isCompactSummary") is True:
                        summary_count += 1

                except json.JSONDecodeError as e:
                    logger.debug(f"Skipping malformed line {i} in {file_path}: {e}")
                    continue
                except KeyError as e:
                    logger.debug(f"Missing expected field in line {i} of {file_path}: {e}")
                    continue

            # Determine if this is a single continuation summary
            # Single summary at start OR first message has isCompactSummary
            if summary_count == 1 and lines:
                try:
                    first_line_data = json.loads(lines[0])
                    if first_line_data.get("type") == "summary" or first_line_data.get("isCompactSummary") is True:
                        is_single_continuation_summary = True
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"Failed to parse first line for continuation check in {file_path}: {e}")

            # Check for session transitions
            has_session_transitions = len(session_ids_seen) > 1

    except OSError as e:
        logger.error(f"Unable to read conversation file {file_path}: {e}")
        return False, 0, False
    except Exception as e:
        logger.error(f"Unexpected error analyzing summary context in {file_path}: {e}")
        return False, 0, False

    return is_single_continuation_summary, summary_count, has_session_transitions


def _detect_session_transitions(file_path: Path) -> tuple[bool, set[str]]:
    """Check for session ID transitions (strong continuation signal).

    Args:
        file_path: Path to the conversation file

    Returns:
        Tuple of (has_transitions, session_ids_found)
    """
    session_ids: set[str] = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            # Scan first 30 lines for different sessionId values
            for i, line in enumerate(f):
                if i >= 30:  # Limit search to first 30 lines
                    break

                try:
                    data = json.loads(line)
                    if session_id := data.get("sessionId"):
                        session_ids.add(session_id)
                except json.JSONDecodeError as e:
                    logger.debug(f"Skipping malformed line {i} in {file_path}: {e}")
                    continue
                except KeyError as e:
                    logger.debug(f"Missing sessionId field in line {i} of {file_path}: {e}")
                    continue

    except OSError as e:
        logger.error(f"Unable to read conversation file {file_path}: {e}")
        return False, set()
    except Exception as e:
        logger.error(f"Unexpected error detecting session transitions in {file_path}: {e}")
        return False, set()

    return len(session_ids) > 1, session_ids


def _detect_explicit_continuation_content(file_path: Path) -> tuple[bool, float]:
    """Detect explicit continuation statements in conversation content.

    Looks for explicit text indicators like:
    - "This session is being continued from a previous conversation"
    - "ran out of context"
    - "session continues"
    - "continued from previous"

    Args:
        file_path: Path to the conversation file

    Returns:
        Tuple of (has_explicit_continuation, confidence_score)
    """
    # Explicit continuation phrases to look for
    continuation_phrases = [
        "this session is being continued from a previous conversation",
        "ran out of context",
        "session continues",
        "continued from previous",
        "continuing from where we left off",
        "picking up from our last conversation",
        "resuming our previous discussion",
        "context limit reached",
        "hit the context limit",
    ]

    try:
        with open(file_path, encoding="utf-8") as f:
            # Search through file, but focus on first few user/assistant messages
            # Don't stop after just one message - check at least the first 3 user/assistant messages
            messages_checked = 0
            max_messages_to_check = 3

            for _i, line in enumerate(f):
                try:
                    data = json.loads(line)

                    # Stop after checking enough actual messages (not summaries)
                    if messages_checked >= max_messages_to_check:
                        break

                    # Check conversation title
                    if title := data.get("name"):
                        title_lower = title.lower()
                        for phrase in continuation_phrases:
                            if phrase in title_lower:
                                return True, 0.95  # Very high confidence

                    # Check message content (for user or assistant messages)
                    if data.get("type") in ["user", "assistant"]:
                        messages_checked += 1
                        message_content = data.get("message", {})
                        content: Any = message_content.get("content", "")

                        # Handle list format content
                        if isinstance(content, list):
                            content_parts: list[str] = []
                            for item in content:  # type: ignore
                                item_typed: Any = item  # type: ignore
                                if isinstance(item_typed, dict) and item_typed.get("type") == "text":  # type: ignore
                                    text_value: Any = item_typed.get("text", "")  # type: ignore
                                    if isinstance(text_value, str):
                                        content_parts.append(text_value)
                            content = " ".join(content_parts)

                        # Ensure content is string
                        if not isinstance(content, str):
                            content = str(content)

                        content_lower = content.lower()

                        # Check for explicit continuation phrases
                        for phrase in continuation_phrases:
                            if phrase in content_lower:
                                # Very high confidence for explicit continuation text
                                # "This session is being continued" is unambiguous
                                if "this session is being continued" in content_lower:
                                    return True, 0.95
                                # Higher confidence for user messages with continuation text
                                if data.get("type") == "user":
                                    return True, 0.90
                                return True, 0.85

                except (json.JSONDecodeError, KeyError):
                    continue

    except OSError as e:
        logger.debug(f"Unable to read conversation file {file_path}: {e}")
        return False, 0.0
    except Exception as e:
        logger.debug(f"Error detecting explicit continuation content in {file_path}: {e}")
        return False, 0.0

    return False, 0.0


def _calculate_confidence_score(
    is_single_summary: bool,
    summary_count: int,
    has_session_transitions: bool,
    starts_with_summary: bool,
    parent_session_id: str | None,
    is_sdk_generated: bool,
) -> float:
    """Calculate continuation confidence score (0.0 to 1.0).

    High confidence (0.8+): Clear continuation patterns
    Medium confidence (0.5-0.7): Possible continuation but unclear
    Low confidence (0.0-0.4): Likely not a continuation

    Args:
        is_single_summary: Has exactly one summary at start
        summary_count: Total number of summary messages
        has_session_transitions: Multiple session IDs found
        starts_with_summary: File starts with summary content
        parent_session_id: Has a parent session ID
        is_sdk_generated: File appears to be SDK generated

    Returns:
        Confidence score from 0.0 to 1.0
    """
    score = 0.0

    # SDK-generated files are not user continuations
    if is_sdk_generated:
        return 0.0

    # Strong positive signals
    if is_single_summary:
        score += 0.4  # Single summary is strong continuation signal

    if has_session_transitions:
        score += 0.3  # Session transitions indicate continuation

    if parent_session_id:
        score += 0.2  # Parent session ID is continuation evidence

    if starts_with_summary and summary_count == 1:
        score += 0.1  # Summary start with single summary

    # Negative signals
    if summary_count > 2:
        score -= 0.3  # Many summaries suggest context history, not continuation

    if summary_count == 0:
        score -= 0.2  # No summaries make continuation less likely

    # Clamp to valid range
    return max(0.0, min(1.0, score))


def determine_continuation_type(pattern: SummaryPattern) -> str | None:
    """Determine the type of continuation based on pattern analysis.

    Args:
        pattern: SummaryPattern analysis result

    Returns:
        Continuation type or None if not a continuation
    """
    if pattern.confidence_score < 0.5:
        return None

    # High confidence from explicit continuation text overrides structural patterns
    if pattern.confidence_score >= 0.85:
        if pattern.has_session_transitions:
            return "post_compaction"
        # Even with many summaries, if we have explicit continuation text, it's a true continuation
        return "true_continuation"

    if pattern.confidence_score >= 0.8:
        if pattern.has_session_transitions:
            return "post_compaction"
        if pattern.is_single_continuation_summary:
            return "true_continuation"

    if pattern.summary_count > 2:
        return "context_history"

    return "possible_continuation"


def find_continuation_chains(conversations: list["ConversationFile"]) -> dict[str, list[str]]:
    """Find continuation chains in conversations using enhanced detection.

    This replaces the old chain-finding logic with the new detector-based approach.

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
    # Use optimized approach to find last UUID without reading entire file
    for conv in sorted_convs:
        try:
            last_uuid = _get_last_uuid_optimized(conv.path)
            # Map the last UUID of this conversation to its session ID
            # If UUID already exists, keep the first (earliest) mapping
            if last_uuid and last_uuid not in uuid_to_session:
                uuid_to_session[last_uuid] = conv.session_id
        except Exception as e:
            logger.debug(f"Failed to extract last UUID from {conv.path}: {e}")
            continue

    # Now build chains for non-compaction continuations
    for conv in conversations:
        if conv.starts_with_summary and conv.leaf_uuid and not conv.is_completion_marker:
            # This conversation continues from another (exclude completion markers)
            parent_id = uuid_to_session.get(conv.leaf_uuid)
            # Only add to chains if parent exists and is different from self
            if parent_id and parent_id != conv.session_id:
                if parent_id not in chains:
                    chains[parent_id] = []
                chains[parent_id].append(conv.session_id)

    return chains


def _get_last_uuid_optimized(file_path: Path) -> str | None:
    """Get the last UUID from a file by reading from the end.

    Args:
        file_path: Path to the JSONL file

    Returns:
        Last UUID found in the file, or None if not found
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            # Read file in reverse to find last UUID faster
            # For very large files, this avoids reading the entire content
            lines = f.readlines()

            # Check last 20 lines in reverse order for UUID
            for line in reversed(lines[-20:]):
                try:
                    data = json.loads(line)
                    if uuid := data.get("uuid"):
                        return uuid
                except (json.JSONDecodeError, KeyError):
                    continue

            # Fallback: check earlier lines if no UUID found in last 20
            for line in reversed(lines[:-20]):
                try:
                    data = json.loads(line)
                    if uuid := data.get("uuid"):
                        return uuid
                except (json.JSONDecodeError, KeyError):
                    continue

    except (OSError, Exception) as e:
        logger.debug(f"Error reading last UUID from {file_path}: {e}")

    return None
