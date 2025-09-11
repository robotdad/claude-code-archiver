#!/usr/bin/env python3
"""Test the continuation detector with the actual failing conversation."""

import json
from pathlib import Path
from src.claude_code_archiver.continuation_detector import _detect_explicit_continuation_content
from src.claude_code_archiver.continuation_detector import detect_continuation_pattern
from src.claude_code_archiver.continuation_detector import determine_continuation_type
from src.claude_code_archiver.continuation_detector import SummaryPattern

# Test conversation 96812c5b that has explicit continuation text
test_file = Path(".data/archiver/conversations/96812c5b-f962-46d6-b124-6c2e61a4d2ab.jsonl")

print(f"Testing conversation: {test_file}")
print("=" * 80)

# Test explicit content detection
has_explicit, content_confidence = _detect_explicit_continuation_content(test_file)
print(f"Explicit continuation detected: {has_explicit}")
print(f"Content confidence: {content_confidence}")
print()

# Let's manually check what _detect_explicit_continuation_content actually finds
print("Checking what the detector sees:")
print("-" * 40)

# Read the file and look for the continuation text ourselves
with open(test_file, 'r') as f:
    for i, line in enumerate(f):
        if i >= 25:  # Check first 25 lines
            break
        try:
            data = json.loads(line)
            
            # Check for user messages with continuation text
            if data.get('type') == 'user':
                msg = data.get('message', {})
                content = msg.get('content', [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            text = item.get('text', '')
                            if 'session is being continued' in text.lower():
                                print(f"FOUND at line {i}: Continuation text in user message!")
                                print(f"  isCompactSummary: {data.get('isCompactSummary')}")
                                print(f"  Full text preview: {text[:200]}...")
                                
            # Check compact summary flag
            if data.get('isCompactSummary'):
                print(f"Line {i}: Found isCompactSummary=True, type={data.get('type')}")
                
        except json.JSONDecodeError:
            pass

print()
print("Testing why confidence might be 0.85 instead of 0.95:")
print("-" * 40)

# The detector returns 0.95 for user messages in first 5 lines
# Let's check what line the continuation text is on
with open(test_file, 'r') as f:
    for i, line in enumerate(f):
        if i >= 10:
            break
        data = json.loads(line)
        print(f"Line {i}: type={data.get('type')}, isCompactSummary={data.get('isCompactSummary', False)}")
        
print()        
print("Now testing the full detect_continuation_pattern function:")
print("-" * 40)

# Create a mock ConversationFile-like object
class MockConvFile:
    def __init__(self, path):
        self.path = path
        self.starts_with_summary = True  # We know this from the data
        self.parent_session_id = None
        self.is_sdk_generated = False
        
mock_conv = MockConvFile(test_file)
pattern = detect_continuation_pattern(mock_conv)

print(f"Pattern analysis results:")
print(f"  confidence_score: {pattern.confidence_score}")
print(f"  summary_type: {pattern.summary_type}")
print(f"  is_single_continuation_summary: {pattern.is_single_continuation_summary}")
print(f"  has_session_transitions: {pattern.has_session_transitions}")
print(f"  session_ids_found: {pattern.session_ids_found}")

continuation_type = determine_continuation_type(pattern)
print(f"  continuation_type: {continuation_type}")

# Check conversation 30ea3608 too
print()
print("=" * 80)
test_file2 = Path(".data/archiver/conversations/30ea3608-ac58-4466-9f4f-417b13bb3644.jsonl")
print(f"Testing conversation: {test_file2}")

has_explicit2, content_confidence2 = _detect_explicit_continuation_content(test_file2)
print(f"Explicit continuation detected: {has_explicit2}")
print(f"Content confidence: {content_confidence2}")