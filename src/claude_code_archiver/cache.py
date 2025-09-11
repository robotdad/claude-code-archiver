"""Incremental processing cache for conversation analysis."""

import json
import logging
from dataclasses import asdict
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from .discovery import ConversationFile

# Configure logging
logger = logging.getLogger(__name__)

# Cache version - increment when analysis logic changes
CACHE_VERSION = "2.1.0"


@dataclass
class CacheEntry:
    """Single cache entry for a conversation file."""

    file_path: Path
    last_modified: float
    file_size: int
    analysis_result: dict[str, Any]
    analysis_version: str
    cached_at: str

    def to_dict(self) -> dict[str, Any]:
        """Convert cache entry to dictionary for JSON serialization."""
        result = asdict(self)
        result["file_path"] = str(self.file_path)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheEntry":
        """Create cache entry from dictionary."""
        data["file_path"] = Path(data["file_path"])
        return cls(**data)


class ConversationAnalysisCache:
    """Cache for conversation file analysis results."""

    def __init__(self, cache_dir: Path | None = None):
        """Initialize cache with optional custom directory."""
        self.cache_dir = cache_dir or Path.home() / ".claude" / "analysis_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "conversation_analysis.json"
        self.cache: dict[Path, CacheEntry] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load existing cache from disk."""
        if not self.cache_file.exists():
            logger.debug("No existing cache found, starting fresh")
            return

        try:
            with open(self.cache_file, encoding="utf-8") as f:
                cache_data = json.load(f)

            for file_path_str, entry_data in cache_data.items():
                try:
                    entry = CacheEntry.from_dict(entry_data)
                    self.cache[Path(file_path_str)] = entry
                except (KeyError, TypeError, ValueError) as e:
                    logger.debug(f"Skipping invalid cache entry for {file_path_str}: {e}")
                    continue

            logger.info(f"Loaded {len(self.cache)} entries from analysis cache")

        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load analysis cache: {e}")
            self.cache = {}

    def _save_cache(self) -> None:
        """Save current cache to disk."""
        try:
            cache_data = {str(path): entry.to_dict() for path, entry in self.cache.items()}

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"Saved {len(self.cache)} entries to analysis cache")

        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to save analysis cache: {e}")

    def should_reanalyze(self, file_path: Path) -> bool:
        """Check if file needs reanalysis based on modification time and version.

        Args:
            file_path: Path to the conversation file

        Returns:
            True if file needs reanalysis, False if cached result is valid
        """
        cache_entry = self.cache.get(file_path)
        if not cache_entry:
            logger.debug(f"No cache entry found for {file_path}")
            return True

        # Check if analysis version has changed
        if cache_entry.analysis_version != CACHE_VERSION:
            logger.debug(
                f"Analysis version mismatch for {file_path}: cached={cache_entry.analysis_version}, current={CACHE_VERSION}"
            )
            return True

        try:
            # Check if file has been modified
            file_stat = file_path.stat()
            if file_stat.st_mtime > cache_entry.last_modified:
                logger.debug(f"File modified since last analysis: {file_path}")
                return True

            # Check if file size has changed
            if file_stat.st_size != cache_entry.file_size:
                logger.debug(
                    f"File size changed for {file_path}: cached={cache_entry.file_size}, current={file_stat.st_size}"
                )
                return True

        except OSError as e:
            logger.warning(f"Unable to check file stats for {file_path}: {e}")
            return True

        logger.debug(f"Using cached analysis for {file_path}")
        return False

    def get_cached_result(self, file_path: Path) -> ConversationFile | None:
        """Get cached analysis result for a file.

        Args:
            file_path: Path to the conversation file

        Returns:
            ConversationFile object if cached result is valid, None otherwise
        """
        cache_entry = self.cache.get(file_path)
        if not cache_entry:
            return None

        if self.should_reanalyze(file_path):
            return None

        try:
            # Reconstruct ConversationFile from cached data
            return ConversationFile(**cache_entry.analysis_result)
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"Invalid cached data for {file_path}: {e}")
            # Remove invalid cache entry
            del self.cache[file_path]
            return None

    def cache_result(self, conversation_file: ConversationFile) -> None:
        """Cache analysis result for a conversation file.

        Args:
            conversation_file: ConversationFile object to cache
        """
        try:
            file_stat = conversation_file.path.stat()

            # Convert ConversationFile to dict for caching
            # Handle special fields that need serialization
            result_dict = conversation_file.model_dump()
            result_dict["path"] = str(conversation_file.path)
            result_dict["message_uuids"] = list(conversation_file.message_uuids)
            result_dict["session_transitions"] = list(conversation_file.session_transitions)

            cache_entry = CacheEntry(
                file_path=conversation_file.path,
                last_modified=file_stat.st_mtime,
                file_size=file_stat.st_size,
                analysis_result=result_dict,
                analysis_version=CACHE_VERSION,
                cached_at=datetime.now(UTC).isoformat(),
            )

            self.cache[conversation_file.path] = cache_entry
            logger.debug(f"Cached analysis result for {conversation_file.path}")

        except (OSError, ValueError) as e:
            logger.warning(f"Failed to cache result for {conversation_file.path}: {e}")

    def cleanup_stale_entries(self, valid_paths: set[Path]) -> None:
        """Remove cache entries for files that no longer exist.

        Args:
            valid_paths: Set of file paths that still exist
        """
        stale_paths = set(self.cache.keys()) - valid_paths
        for stale_path in stale_paths:
            del self.cache[stale_path]
            logger.debug(f"Removed stale cache entry for {stale_path}")

        if stale_paths:
            logger.info(f"Cleaned up {len(stale_paths)} stale cache entries")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self.cache)
        version_counts: dict[str, int] = {}
        oldest_entry: str | None = None
        newest_entry: str | None = None

        for entry in self.cache.values():
            # Count by version
            version = entry.analysis_version
            version_counts[version] = version_counts.get(version, 0) + 1

            # Track oldest and newest
            cached_at = entry.cached_at
            if oldest_entry is None or cached_at < oldest_entry:
                oldest_entry = cached_at
            if newest_entry is None or cached_at > newest_entry:
                newest_entry = cached_at

        return {
            "total_entries": total_entries,
            "current_version_entries": version_counts.get(CACHE_VERSION, 0),
            "version_distribution": version_counts,
            "oldest_entry": oldest_entry,
            "newest_entry": newest_entry,
            "cache_file_path": str(self.cache_file),
        }

    def save(self) -> None:
        """Save cache to disk."""
        self._save_cache()

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Cleared analysis cache")
