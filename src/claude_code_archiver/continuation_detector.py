"""Enhanced continuation detection module."""

import json
import logging
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING

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

    # Calculate confidence score
    confidence_score = _calculate_confidence_score(
        is_single_summary=is_single_summary,
        summary_count=summary_count,
        has_session_transitions=has_transitions,
        starts_with_summary=conversation_file.starts_with_summary,
        parent_session_id=conversation_file.parent_session_id,
        is_sdk_generated=conversation_file.is_sdk_generated,
    )

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

            # Look at first 15 lines for pattern analysis
            analysis_lines = lines[: min(15, len(lines))]

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
            # Scan first 15 lines for different sessionId values
            for i, line in enumerate(f):
                if i >= 15:  # Limit search to first 15 lines
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

    if pattern.confidence_score >= 0.8:
        if pattern.has_session_transitions:
            return "post_compaction"
        if pattern.is_single_continuation_summary:
            return "true_continuation"

    if pattern.summary_count > 2:
        return "context_history"

    return "possible_continuation"
