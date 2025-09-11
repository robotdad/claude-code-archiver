#!/usr/bin/env python3
"""Run the archiver and check results."""

import json
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.claude_code_archiver.archiver import Archiver
from src.claude_code_archiver.discovery import _discover_claude_conversations

# Discover and archive
archive_path = Path(".data/archiver")
conversations = _discover_claude_conversations(archive_path)

print(f"Found {len(conversations)} conversations")

# Check our target conversation
for conv in conversations:
    if "96812c5b" in conv.session_id:
        print(f"\nConversation {conv.session_id}:")
        print(f"  continuation_confidence: {conv.continuation_confidence}")
        print(f"  continuation_type: {conv.continuation_type}")
        print(f"  starts_with_summary: {conv.starts_with_summary}")

# Create archiver and generate manifest
archiver = Archiver()
manifest = archiver.create_manifest(archive_path, conversations)

# Check manifest
for conv in manifest['conversations']:
    if "96812c5b" in conv['session_id']:
        print(f"\nManifest entry for {conv['session_id']}:")
        print(f"  is_continuation: {conv['is_continuation']}")
        print(f"  continuation_confidence: {conv['continuation_confidence']}")
        print(f"  continuation_type: {conv['continuation_type']}")
        print(f"  conversation_type: {conv['conversation_type']}")
        print(f"  display_by_default: {conv['display_by_default']}")

# Save manifest
output_file = archive_path / "manifest_test.json"
with open(output_file, 'w') as f:
    json.dump(manifest, f, indent=2, default=str)
    
print(f"\nManifest saved to: {output_file}")