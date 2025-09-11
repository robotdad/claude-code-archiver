"""Tests for the conversation analysis cache module."""

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from claude_code_archiver.cache import CACHE_VERSION
from claude_code_archiver.cache import CacheEntry
from claude_code_archiver.cache import ConversationAnalysisCache
from claude_code_archiver.discovery import ConversationFile


class TestCacheEntry:
    """Test cache entry functionality."""

    def testcache_entry_creation(self, tmp_path: Path) -> None:
        """Test creating a cache entry."""
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        entry = CacheEntry(
            file_path=test_file,
            last_modified=1234567890.0,
            file_size=1024,
            analysis_result={"session_id": "test", "message_count": 5},
            analysis_version="1.0.0",
            cached_at="2024-01-01T10:00:00Z",
        )

        assert entry.file_path == test_file
        assert entry.last_modified == 1234567890.0
        assert entry.file_size == 1024
        assert entry.analysis_result["session_id"] == "test"

    def testcache_entry_serialization(self, tmp_path: Path) -> None:
        """Test cache entry to/from dict conversion."""
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        entry = CacheEntry(
            file_path=test_file,
            last_modified=1234567890.0,
            file_size=1024,
            analysis_result={"session_id": "test"},
            analysis_version="1.0.0",
            cached_at="2024-01-01T10:00:00Z",
        )

        # Test to_dict
        dict_data = entry.to_dict()
        assert isinstance(dict_data["file_path"], str)
        assert dict_data["file_path"] == str(test_file)

        # Test from_dict
        restored_entry = CacheEntry.from_dict(dict_data)
        assert restored_entry.file_path == test_file
        assert restored_entry.last_modified == entry.last_modified


class TestConversationAnalysisCache:
    """Test conversation analysis cache functionality."""

    def testcache_initialization(self, tmp_path: Path) -> None:
        """Test cache initialization."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)

        assert cache.cache_dir == tmp_path
        assert cache.cache_file == tmp_path / "conversation_analysis.json"
        assert cache.cache == {}  # Should start empty

    def test_should_reanalyze_nocache_entry(self, tmp_path: Path) -> None:
        """Test should_reanalyze with no existing cache entry."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        assert cache.should_reanalyze(test_file)

    def test_should_reanalyze_version_mismatch(self, tmp_path: Path) -> None:
        """Test should_reanalyze with version mismatch."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        # Add cache entry with old version
        old_entry = CacheEntry(
            file_path=test_file,
            last_modified=test_file.stat().st_mtime,
            file_size=test_file.stat().st_size,
            analysis_result={"session_id": "test"},
            analysis_version="0.9.0",  # Old version
            cached_at="2024-01-01T10:00:00Z",
        )
        cache.cache[test_file] = old_entry

        assert cache.should_reanalyze(test_file)

    def test_should_reanalyze_file_modified(self, tmp_path: Path) -> None:
        """Test should_reanalyze with modified file."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        # Add cache entry with old modification time
        old_entry = CacheEntry(
            file_path=test_file,
            last_modified=test_file.stat().st_mtime - 100,  # 100 seconds ago
            file_size=test_file.stat().st_size,
            analysis_result={"session_id": "test"},
            analysis_version=CACHE_VERSION,
            cached_at="2024-01-01T10:00:00Z",
        )
        cache.cache[test_file] = old_entry

        assert cache.should_reanalyze(test_file)

    def test_should_reanalyze_validcache(self, tmp_path: Path) -> None:
        """Test should_reanalyze with valid cache entry."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        # Add valid cache entry
        valid_entry = CacheEntry(
            file_path=test_file,
            last_modified=test_file.stat().st_mtime,
            file_size=test_file.stat().st_size,
            analysis_result={
                "path": str(test_file),
                "session_id": "test",
                "size": test_file.stat().st_size,
                "message_count": 5,
                "message_uuids": [],
                "session_transitions": [],
            },
            analysis_version=CACHE_VERSION,
            cached_at="2024-01-01T10:00:00Z",
        )
        cache.cache[test_file] = valid_entry

        assert not cache.should_reanalyze(test_file)

    def testcache_result(self, tmp_path: Path) -> None:
        """Test caching a conversation analysis result."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.write_text("test content")

        conv_file = ConversationFile(
            path=test_file, session_id="test_session", size=test_file.stat().st_size, message_count=10
        )

        cache.cache_result(conv_file)

        assert test_file in cache.cache
        entry = cache.cache[test_file]
        assert entry.analysis_version == CACHE_VERSION
        assert entry.analysis_result["session_id"] == "test_session"

    def test_get_cached_result(self, tmp_path: Path) -> None:
        """Test retrieving cached analysis result."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        # Cache a result first
        conv_file = ConversationFile(
            path=test_file, session_id="test_session", size=test_file.stat().st_size, message_count=5
        )
        cache.cache_result(conv_file)

        # Retrieve cached result
        cached_result = cache.get_cached_result(test_file)

        assert cached_result is not None
        assert cached_result.session_id == "test_session"
        assert cached_result.message_count == 5

    def test_get_cached_result_invalid_data(self, tmp_path: Path) -> None:
        """Test getting cached result with invalid data."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        # Add invalid cache entry
        invalid_entry = CacheEntry(
            file_path=test_file,
            last_modified=test_file.stat().st_mtime,
            file_size=test_file.stat().st_size,
            analysis_result={"invalid": "data"},  # Missing required fields
            analysis_version=CACHE_VERSION,
            cached_at="2024-01-01T10:00:00Z",
        )
        cache.cache[test_file] = invalid_entry

        cached_result = cache.get_cached_result(test_file)

        assert cached_result is None
        assert test_file not in cache.cache  # Should be removed

    def test_cleanup_stale_entries(self, tmp_path: Path) -> None:
        """Test cleaning up stale cache entries."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)

        # Create test files
        existing_file = tmp_path / "existing.jsonl"
        existing_file.touch()
        removed_file = tmp_path / "removed.jsonl"

        # Add cache entries for both files
        cache.cache[existing_file] = CacheEntry(
            file_path=existing_file,
            last_modified=1234567890.0,
            file_size=100,
            analysis_result={"session_id": "existing"},
            analysis_version=CACHE_VERSION,
            cached_at="2024-01-01T10:00:00Z",
        )
        cache.cache[removed_file] = CacheEntry(
            file_path=removed_file,
            last_modified=1234567890.0,
            file_size=200,
            analysis_result={"session_id": "removed"},
            analysis_version=CACHE_VERSION,
            cached_at="2024-01-01T10:00:00Z",
        )

        # Clean up with only existing file as valid
        cache.cleanup_stale_entries({existing_file})

        assert existing_file in cache.cache
        assert removed_file not in cache.cache

    def testcache_persistence(self, tmp_path: Path) -> None:
        """Test cache persistence across instances."""
        # First cache instance
        cache1 = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        conv_file = ConversationFile(
            path=test_file, session_id="persistent_test", size=test_file.stat().st_size, message_count=7
        )
        cache1.cache_result(conv_file)
        cache1.save()

        # Second cache instance should load the saved data
        cache2 = ConversationAnalysisCache(cache_dir=tmp_path)
        cached_result = cache2.get_cached_result(test_file)

        assert cached_result is not None
        assert cached_result.session_id == "persistent_test"
        assert cached_result.message_count == 7

    def testcache_stats(self, tmp_path: Path) -> None:
        """Test cache statistics generation."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)

        # Add some test entries
        for i in range(3):
            test_file = tmp_path / f"test{i}.jsonl"
            test_file.touch()

            entry = CacheEntry(
                file_path=test_file,
                last_modified=1234567890.0,
                file_size=100 * (i + 1),
                analysis_result={"session_id": f"test{i}"},
                analysis_version=CACHE_VERSION if i < 2 else "1.9.0",
                cached_at=f"2024-01-0{i + 1}T10:00:00Z",
            )
            cache.cache[test_file] = entry

        stats = cache.get_cache_stats()

        assert stats["total_entries"] == 3
        assert stats["current_version_entries"] == 2
        assert CACHE_VERSION in stats["version_distribution"]
        assert "1.9.0" in stats["version_distribution"]
        assert stats["oldest_entry"] == "2024-01-01T10:00:00Z"
        assert stats["newest_entry"] == "2024-01-03T10:00:00Z"

    def testcache_clear(self, tmp_path: Path) -> None:
        """Test clearing the cache."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        test_file = tmp_path / "test.jsonl"
        test_file.touch()

        # Add cache entry
        conv_file = ConversationFile(path=test_file, session_id="to_be_cleared", size=100, message_count=1)
        cache.cache_result(conv_file)
        cache.save()

        assert len(cache.cache) == 1
        assert cache.cache_file.exists()

        # Clear cache
        cache.clear()

        assert len(cache.cache) == 0
        assert not cache.cache_file.exists()

    @patch("claude_code_archiver.cache.logger")
    def test_error_handling(self, mock_logger: MagicMock, tmp_path: Path) -> None:
        """Test error handling in cache operations."""
        cache = ConversationAnalysisCache(cache_dir=tmp_path)

        # Test with file that doesn't exist (no cache entry)
        non_existent = tmp_path / "does_not_exist.jsonl"
        assert cache.should_reanalyze(non_existent)

        # Test with file that has cache entry but file doesn't exist (triggers warning)
        missing_file = tmp_path / "missing.jsonl"
        cache_entry = CacheEntry(
            file_path=missing_file,
            last_modified=1234567890.0,
            file_size=100,
            analysis_result={"session_id": "test"},
            analysis_version=CACHE_VERSION,
            cached_at="2024-01-01T10:00:00Z",
        )
        cache.cache[missing_file] = cache_entry

        # This should trigger a warning because file.stat() will fail
        assert cache.should_reanalyze(missing_file)

        # Verify warning was logged
        mock_logger.warning.assert_called()

    def test_load_corruptedcache(self, tmp_path: Path) -> None:
        """Test loading corrupted cache file."""
        cache_file = tmp_path / "conversation_analysis.json"

        # Create corrupted cache file
        with open(cache_file, "w") as f:
            f.write("invalid json content")

        # Should handle corrupted cache gracefully
        cache = ConversationAnalysisCache(cache_dir=tmp_path)
        assert cache.cache == {}
