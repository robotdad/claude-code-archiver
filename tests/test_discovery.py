"""Tests for the discovery module."""

from pathlib import Path

import pytest

from claude_code_archiver.discovery import ProjectDiscovery


def test_project_path_to_folder_name() -> None:
    """Test project path to folder name conversion."""
    discovery = ProjectDiscovery()

    # Test basic conversion
    path = Path("/Users/robotdad/Source/SelfServe")
    expected = "-Users-robotdad-Source-SelfServe"
    assert discovery.project_path_to_folder_name(path) == expected

    # Test with relative path (should convert to absolute)
    rel_path = Path(".")
    result = discovery.project_path_to_folder_name(rel_path)
    assert result.startswith("-")
    assert "/" not in result


def test_discover_project_conversations(temp_claude_project: tuple[Path, Path]) -> None:
    """Test discovering conversations for a project."""
    tmp_path, _ = temp_claude_project

    discovery = ProjectDiscovery(claude_projects_dir=tmp_path / ".claude" / "projects")

    # Create a test project path
    test_project = Path("/test/project")

    # Discover conversations
    conversations = discovery.discover_project_conversations(test_project)

    assert len(conversations) == 1
    assert conversations[0].session_id == "test-session"
    assert conversations[0].message_count == 3
    assert conversations[0].first_timestamp == "2025-01-01T10:00:00Z"


def test_discover_nonexistent_project() -> None:
    """Test discovering conversations for a non-existent project."""
    discovery = ProjectDiscovery()

    with pytest.raises(ValueError, match="No Claude conversations found"):
        discovery.discover_project_conversations(Path("/nonexistent/project"))


def test_find_continuation_chains(temp_continuation_project: tuple[Path, Path]) -> None:
    """Test finding continuation chains."""
    tmp_path, _ = temp_continuation_project

    discovery = ProjectDiscovery(claude_projects_dir=tmp_path / ".claude" / "projects")

    # Discover conversations
    test_project = Path("/test/continuation")
    conversations = discovery.discover_project_conversations(test_project)

    # Find chains using the new detector
    from src.claude_code_archiver.continuation_detector import find_continuation_chains

    _ = find_continuation_chains(conversations)

    # Should have found the continuation
    assert len(conversations) == 2
    continuation = [c for c in conversations if c.starts_with_summary][0]
    assert continuation.starts_with_summary
    assert continuation.leaf_uuid == "uuid-previous-last"
