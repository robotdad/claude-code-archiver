#!/usr/bin/env python3
"""Debug why the detector isn't working."""

import json
from pathlib import Path
from src.claude_code_archiver.continuation_detector import _detect_explicit_continuation_content

# Test conversation 96812c5b
test_file = Path(".data/archiver/conversations/96812c5b-f962-46d6-b124-6c2e61a4d2ab.jsonl")

print(f"Testing _detect_explicit_continuation_content directly:")
print("=" * 80)

# Test explicit content detection
has_explicit, confidence = _detect_explicit_continuation_content(test_file)
print(f"Result: has_explicit={has_explicit}, confidence={confidence}")
print()

# Now let's trace through what it's actually doing
print("Checking the actual content:")
print("-" * 40)

with open(test_file, 'r') as f:
    found_conversation_start = False
    for i, line in enumerate(f):
        if i > 25:
            break
            
        try:
            data = json.loads(line)
            
            # The detector stops once it finds a user/assistant message and checks it
            if found_conversation_start and data.get("type") in ["user", "assistant"]:
                print(f"Line {i}: Detector would STOP here (already found conversation start)")
                break
                
            if data.get("type") in ["user", "assistant"]:
                found_conversation_start = True
                print(f"Line {i}: Found {data.get('type')} message - detector marks conversation start")
                
                # Check content
                message_content = data.get("message", {})
                content = message_content.get("content", "")
                
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text = item.get("text", "")
                            if "this session is being continued" in text.lower():
                                print(f"  -> Contains 'this session is being continued'")
                                print(f"  -> Should return (True, 0.95)")
                                
                # Check if it's a user message
                if data.get("type") == "user":
                    print(f"  -> This is a USER message")
                    
        except json.JSONDecodeError:
            pass
            
print()
print("The problem might be that the detector is checking the WRONG line!")
print("Let me check what's on line 22 (the first user message after summaries):")