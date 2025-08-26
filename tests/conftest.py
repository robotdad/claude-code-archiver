"""Pytest configuration and fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def sample_conversation_data() -> list[dict[str, Any]]:
    """Sample conversation data for testing."""
    return [
        {
            "type": "user",
            "uuid": "uuid-1",
            "parentUuid": None,
            "timestamp": "2025-01-01T10:00:00Z",
            "sessionId": "session-123",
            "message": {"role": "user", "content": "Hello, Claude!"},
        },
        {
            "type": "assistant",
            "uuid": "uuid-2",
            "parentUuid": "uuid-1",
            "timestamp": "2025-01-01T10:00:01Z",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Hello! How can I help you today?"},
                ],
            },
        },
        {
            "type": "user",
            "uuid": "uuid-3",
            "parentUuid": "uuid-2",
            "timestamp": "2025-01-01T10:00:05Z",
            "message": {
                "role": "user",
                "content": "Can you help me with my API key: sk-1234567890abcdef1234567890abcdef1234567890abcdef",
            },
        },
    ]


@pytest.fixture
def sample_summary_data() -> dict[str, Any]:
    """Sample summary conversation data for testing continuations."""
    return {"type": "summary", "summary": "Previous conversation about Python", "leafUuid": "uuid-previous-last"}


@pytest.fixture
def temp_claude_project(tmp_path: Path, sample_conversation_data: list[dict[str, Any]]) -> tuple[Path, Path]:
    """Create a temporary Claude project structure."""
    # Create Claude projects directory
    claude_dir = tmp_path / ".claude" / "projects" / "-test-project"
    claude_dir.mkdir(parents=True)

    # Write sample conversation
    conv_file = claude_dir / "test-session.jsonl"
    with open(conv_file, "w") as f:
        for entry in sample_conversation_data:
            f.write(json.dumps(entry) + "\n")

    return tmp_path, claude_dir


@pytest.fixture
def temp_continuation_project(
    tmp_path: Path, sample_conversation_data: list[dict[str, Any]], sample_summary_data: dict[str, Any]
) -> tuple[Path, Path]:
    """Create a project with continuation conversations."""
    # Create Claude projects directory
    claude_dir = tmp_path / ".claude" / "projects" / "-test-continuation"
    claude_dir.mkdir(parents=True)

    # Write original conversation
    orig_file = claude_dir / "original-session.jsonl"
    with open(orig_file, "w") as f:
        for entry in sample_conversation_data:
            f.write(json.dumps(entry) + "\n")

    # Write continuation conversation
    cont_file = claude_dir / "continuation-session.jsonl"
    with open(cont_file, "w") as f:
        # Start with summary
        f.write(json.dumps(sample_summary_data) + "\n")
        # Add regular messages
        for entry in sample_conversation_data:
            f.write(json.dumps(entry) + "\n")

    return tmp_path, claude_dir
