"""SDK Pattern Detection Module.

A self-contained module for detecting Claude Code SDK-generated conversations.
These conversations follow a specific pattern of automated article analysis
and structured knowledge extraction.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from .discovery import ConversationFile

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SDKPattern:
    """Results of SDK pattern detection analysis."""

    has_completion_marker: bool
    has_analyze_instruction: bool
    has_json_requirement: bool
    has_structured_response: bool
    message_count: int
    confidence_score: float

    # Additional pattern indicators
    has_article_processing: bool = False
    has_knowledge_extraction: bool = False
    has_pure_json_response: bool = False
    has_short_conversation: bool = False


def detect_sdk_pattern(conversation_file: ConversationFile) -> SDKPattern:
    """Detect if conversation follows Claude Code SDK pattern.

    SDK conversations have these characteristics:
    1. Line 1: {"type": "summary", "summary": "...", "leafUuid": "..."}
    2. Line 2: User message with "Analyze this article and extract structured knowledge"
    3. Line 3: Assistant response with pure JSON data extraction
    4. Very short conversations (typically 3-4 messages total)
    5. Systematic content processing with JSON extraction requirements

    Args:
        conversation_file: ConversationFile object to analyze

    Returns:
        SDKPattern object with detection results and confidence score
    """
    has_completion_marker = conversation_file.starts_with_summary
    has_analyze_instruction = False
    has_json_requirement = False
    has_structured_response = False
    has_article_processing = False
    has_knowledge_extraction = False
    has_pure_json_response = False
    has_short_conversation = False

    message_count = conversation_file.message_count

    # Short conversations are more likely to be SDK-generated
    has_short_conversation = message_count <= 4

    try:
        with open(conversation_file.path, encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) < 1:
            # Need at least one line to check
            confidence_score = 0.0
            return SDKPattern(
                has_completion_marker=has_completion_marker,
                has_analyze_instruction=has_analyze_instruction,
                has_json_requirement=has_json_requirement,
                has_structured_response=has_structured_response,
                message_count=message_count,
                confidence_score=confidence_score,
                has_article_processing=has_article_processing,
                has_knowledge_extraction=has_knowledge_extraction,
                has_pure_json_response=has_pure_json_response,
                has_short_conversation=has_short_conversation,
            )

        # Check first line for summary pattern
        try:
            first_data = json.loads(lines[0])
            if first_data.get("type") == "summary" and first_data.get("leafUuid"):
                has_completion_marker = True
        except (json.JSONDecodeError, KeyError) as e:
            logger.debug(f"Failed to parse first line in {conversation_file.path}: {e}")

        # Check for user message with SDK patterns (could be line 0 or line 1)
        user_line_idx = 1 if has_completion_marker else 0

        if len(lines) > user_line_idx:
            try:
                user_data = json.loads(lines[user_line_idx])
                if user_data.get("type") == "user":
                    message_content = user_data.get("message", {})
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

                    content_lower = content.lower()

                    # Check for key SDK phrases - exact matches for SDK-generated patterns
                    sdk_exact_phrases = [
                        "analyze this document and extract structured knowledge",
                        "analyze this article and extract structured knowledge",
                    ]

                    for phrase in sdk_exact_phrases:
                        if phrase in content_lower:
                            has_analyze_instruction = True
                            has_knowledge_extraction = True
                            break

                    # Also check for the original pattern
                    if "analyze this article and extract structured knowledge" in content_lower:
                        has_analyze_instruction = True
                        has_knowledge_extraction = True

                    if "return only valid json" in content_lower:
                        has_json_requirement = True

                    # Check for article processing patterns
                    article_patterns = [
                        "extract structured knowledge",
                        "analyze this article",
                    ]

                    # Check for title/content pattern and markdown frontmatter
                    has_title_content = "title:" in content and "content:" in content
                    has_markdown_frontmatter = "---" in content

                    if (
                        any(phrase in content_lower for phrase in article_patterns)
                        or has_title_content
                        or has_markdown_frontmatter
                    ):
                        has_article_processing = True
            except (json.JSONDecodeError, KeyError) as e:
                logger.debug(f"Failed to parse user line in {conversation_file.path}: {e}")

        # Check assistant response for JSON pattern (next line after user)
        assistant_line_idx = user_line_idx + 1
        if len(lines) > assistant_line_idx:
            try:
                assistant_data = json.loads(lines[assistant_line_idx])
                if assistant_data.get("type") == "assistant":
                    message_content = assistant_data.get("message", {})
                    content: Any = message_content.get("content", [])

                    if isinstance(content, list) and len(content) > 0:  # type: ignore
                        first_item: Any = content[0]  # type: ignore
                        if isinstance(first_item, dict):
                            text_content: Any = first_item.get("text", "")  # type: ignore
                            if isinstance(text_content, str):
                                # Check if response starts and ends with JSON structure
                                text_content = text_content.strip()
                                if (text_content.startswith("```json") and text_content.endswith("```")) or (
                                    text_content.startswith("{") and text_content.endswith("}")
                                ):
                                    has_structured_response = True

                                    # Check if it's purely JSON (minimal other text)
                                    if _is_pure_json_response(text_content):
                                        has_pure_json_response = True
            except (json.JSONDecodeError, KeyError) as e:
                logger.debug(f"Failed to parse assistant line in {conversation_file.path}: {e}")

    except OSError as e:
        logger.error(f"Unable to read conversation file {conversation_file.path}: {e}")
        # Return default pattern with zero confidence
        return SDKPattern(
            has_completion_marker=has_completion_marker,
            has_analyze_instruction=has_analyze_instruction,
            has_json_requirement=has_json_requirement,
            has_structured_response=has_structured_response,
            message_count=message_count,
            confidence_score=0.0,
            has_article_processing=has_article_processing,
            has_knowledge_extraction=has_knowledge_extraction,
            has_pure_json_response=has_pure_json_response,
            has_short_conversation=has_short_conversation,
        )
    except Exception as e:
        logger.error(f"Unexpected error during SDK pattern detection for {conversation_file.path}: {e}")
        # Return default pattern with zero confidence
        return SDKPattern(
            has_completion_marker=has_completion_marker,
            has_analyze_instruction=has_analyze_instruction,
            has_json_requirement=has_json_requirement,
            has_structured_response=has_structured_response,
            message_count=message_count,
            confidence_score=0.0,
            has_article_processing=has_article_processing,
            has_knowledge_extraction=has_knowledge_extraction,
            has_pure_json_response=has_pure_json_response,
            has_short_conversation=has_short_conversation,
        )

    # Calculate confidence score based on pattern indicators
    confidence_score = _calculate_confidence_score(
        has_completion_marker,
        has_analyze_instruction,
        has_json_requirement,
        has_structured_response,
        has_article_processing,
        has_knowledge_extraction,
        has_pure_json_response,
        has_short_conversation,
        message_count,
    )

    return SDKPattern(
        has_completion_marker=has_completion_marker,
        has_analyze_instruction=has_analyze_instruction,
        has_json_requirement=has_json_requirement,
        has_structured_response=has_structured_response,
        message_count=message_count,
        confidence_score=confidence_score,
        has_article_processing=has_article_processing,
        has_knowledge_extraction=has_knowledge_extraction,
        has_pure_json_response=has_pure_json_response,
        has_short_conversation=has_short_conversation,
    )


def is_sdk_generated(conversation_file: ConversationFile) -> bool:
    """Simple boolean check for SDK-generated conversations.

    Args:
        conversation_file: ConversationFile object to check

    Returns:
        True if conversation is likely SDK-generated (confidence > 0.8)
    """
    pattern = detect_sdk_pattern(conversation_file)
    return pattern.confidence_score > 0.8


def _is_pure_json_response(text_content: str) -> bool:
    """Check if assistant response is primarily JSON with minimal other text.

    Args:
        text_content: The assistant's response text

    Returns:
        True if response is primarily JSON data
    """
    # Remove code block markers if present
    if text_content.startswith("```json"):
        text_content = text_content[7:]  # Remove ```json
    if text_content.endswith("```"):
        text_content = text_content[:-3]  # Remove ```

    text_content = text_content.strip()

    # Check if it starts and ends with JSON braces
    if not (text_content.startswith("{") and text_content.endswith("}")):
        return False

    try:
        # Try to parse as JSON
        json.loads(text_content)
        return True
    except json.JSONDecodeError:
        return False


def _calculate_confidence_score(
    has_completion_marker: bool,
    has_analyze_instruction: bool,
    has_json_requirement: bool,
    has_structured_response: bool,
    has_article_processing: bool,
    has_knowledge_extraction: bool,
    has_pure_json_response: bool,
    has_short_conversation: bool,
    message_count: int,
) -> float:
    """Calculate confidence score for SDK pattern detection.

    High Confidence Indicators (0.9+):
    - Exact phrase "Analyze this document/article and extract structured knowledge"
    - Response is pure JSON data structure
    - 3-4 message conversation

    Medium Confidence Indicators (0.6-0.8):
    - "Extract structured knowledge" in user message
    - "Return ONLY valid JSON" requirement
    - Systematic content processing patterns

    Low Confidence Indicators (0.3-0.5):
    - Long article content in user message
    - Structured data extraction themes

    Args:
        Various boolean indicators from pattern detection

    Returns:
        Confidence score between 0.0 and 1.0
    """
    score = 0.0

    # Very high confidence for exact SDK phrase match
    if has_analyze_instruction and has_knowledge_extraction:
        # This indicates exact phrase match for SDK pattern
        score += 0.5  # Very strong indicator

        # Additional boost if also has structured response
        if has_structured_response:
            score += 0.2

        # Even more if pure JSON response
        if has_pure_json_response:
            score += 0.2

    # High confidence indicators
    elif has_completion_marker and has_analyze_instruction and has_json_requirement and has_structured_response:
        score += 0.4  # Strong base pattern

    if has_pure_json_response and score < 0.3:
        score += 0.3  # Very strong indicator

    if has_short_conversation and message_count == 3:
        score += 0.2  # Perfect SDK conversation length
    elif has_short_conversation and message_count == 4:
        score += 0.15  # Still very good

    # Medium confidence indicators (only add if not already high)
    if score < 0.6:
        if has_knowledge_extraction:
            score += 0.15

        if has_article_processing:
            score += 0.1

        if has_analyze_instruction:
            score += 0.1

        if has_json_requirement:
            score += 0.1

        if has_structured_response:
            score += 0.1

    # Lower confidence for longer conversations (less likely to be SDK)
    if message_count > 4:
        score *= 0.7  # Reduce confidence
    elif message_count > 6:
        score *= 0.4  # Significantly reduce confidence

    # Ensure score doesn't exceed 1.0
    return min(score, 1.0)
