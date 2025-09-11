#!/usr/bin/env python3
"""Trace through the full pipeline to find where it breaks."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Import everything
from src.claude_code_archiver.discovery import ProjectDiscovery, ConversationFile, _analyze_conversation_file
from src.claude_code_archiver.continuation_detector import detect_continuation_pattern, _detect_explicit_continuation_content

# Test file
test_file = Path(".data/archiver/conversations/96812c5b-f962-46d6-b124-6c2e61a4d2ab.jsonl")

print("Step 1: Direct detector test")
print("-" * 40)
has_explicit, confidence = _detect_explicit_continuation_content(test_file)
print(f"_detect_explicit_continuation_content: {has_explicit}, {confidence}")

print("\nStep 2: Create ConversationFile and test pattern detection")
print("-" * 40)

# Analyze the file the same way discovery does
conv_file = _analyze_conversation_file(test_file)
print(f"After _analyze_conversation_file:")
print(f"  continuation_confidence: {conv_file.continuation_confidence}")
print(f"  continuation_type: {conv_file.continuation_type}")

print("\nStep 3: Test pattern detection directly")
print("-" * 40)
pattern = detect_continuation_pattern(conv_file)
print(f"detect_continuation_pattern result:")
print(f"  confidence_score: {pattern.confidence_score}")
print(f"  summary_type: {pattern.summary_type}")

print("\nStep 4: Check what _analyze_conversation_file does internally")
print("-" * 40)
print("Let me check the exact flow...")

# Create a basic ConversationFile
basic_conv = ConversationFile(
    path=test_file,
    session_id="96812c5b-f962-46d6-b124-6c2e61a4d2ab",
    message_count=50,
    first_timestamp="2025-09-10T02:18:27.138Z",
    last_timestamp="2025-09-10T02:19:10.310Z",
    starts_with_summary=True,
    is_post_compaction=False,
    parent_session_id=None,
    is_continuation=False,
    is_snapshot=False,
    size=0
)

# Now test the detector on it
pattern2 = detect_continuation_pattern(basic_conv)
print(f"Pattern detection on basic ConversationFile:")
print(f"  confidence_score: {pattern2.confidence_score}")

# The issue might be in how the confidence scores are combined
from src.claude_code_archiver.continuation_detector import _calculate_confidence_score, _analyze_summary_context

is_single_summary, summary_count, has_transitions = _analyze_summary_context(test_file)
print(f"\nStructural analysis:")
print(f"  is_single_summary: {is_single_summary}")
print(f"  summary_count: {summary_count}")
print(f"  has_transitions: {has_transitions}")

structural_confidence = _calculate_confidence_score(
    is_single_summary=is_single_summary,
    summary_count=summary_count,
    has_session_transitions=has_transitions,
    starts_with_summary=True,
    parent_session_id=None,
    is_sdk_generated=False
)
print(f"  structural_confidence: {structural_confidence}")

print(f"\nFinal confidence should be max({structural_confidence}, {confidence}) = {max(structural_confidence, confidence)}")