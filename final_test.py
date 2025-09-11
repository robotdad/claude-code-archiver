#!/usr/bin/env python3
"""Final test of the continuation detection fix."""

import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).parent))

from src.claude_code_archiver.archiver import Archiver

# Create archiver
archiver = Archiver(output_dir=Path("/tmp"))

# Create archive - use absolute path since we're looking for project root
archive_path = Path("/Users/robotdad/Source/claude-code-archiver")

# Just check if we can discover the conversations with the new detector
from src.claude_code_archiver.discovery import ProjectDiscovery

discovery = ProjectDiscovery()
result = discovery.discover_project_conversations(archive_path)

if result:
    print(f"Found {len(result)} conversations")
    
    # Check our target conversation
    for conv in result:
        if "96812c5b" in conv.session_id:
            print(f"\nTarget conversation {conv.session_id}:")
            print(f"  continuation_confidence: {conv.continuation_confidence}")
            print(f"  continuation_type: {conv.continuation_type}")
            print(f"  starts_with_summary: {conv.starts_with_summary}")
            
            # SUCCESS CHECK
            if conv.continuation_confidence >= 0.95 and conv.continuation_type == "true_continuation":
                print("\n✅ FIX VERIFIED: Conversation is now correctly detected as a true continuation!")
            else:
                print("\n❌ FIX FAILED: Conversation still not properly detected")
                
            break
    else:
        print("\n❌ Conversation 96812c5b not found")
else:
    print("No conversations found")