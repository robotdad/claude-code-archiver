"""Project discovery and mapping module."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)


class ConversationFile(BaseModel):
    """Represents a conversation JSONL file."""

    path: Path
    session_id: str
    size: int
    message_count: int = 0
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    starts_with_summary: bool = False
    leaf_uuid: str | None = None
    # Snapshot detection fields
    is_snapshot: bool = False
    snapshot_group: str | None = None
    snapshot_type: str | None = None  # "intermediate" or "complete"
    message_uuids: set[str] = set()
    # For post-compaction continuations
    parent_session_id: str | None = None
    # Sidechain detection
    has_sidechains: bool = False
    sidechain_count: int = 0
    # Completion marker detection
    is_completion_marker: bool = False
    # SDK detection fields
    is_sdk_generated: bool = False
    sdk_pattern_score: float = 0.0
    # Enhanced continuation detection
    continuation_confidence: float = 0.0
    continuation_type: str | None = None  # "post_compaction", "true_continuation", "context_history"
    session_transitions: set[str] = set()
    summary_pattern_type: str | None = None  # "single_summary", "multi_summary", "none"
    # Enhanced subagent sidechain fields
    is_subagent_sidechain: bool = False
    parent_session_ids: list[str] = []  # Can have multiple parents
    child_session_ids: list[str] = []  # Can spawn multiple children
    subagent_invocations: list[str] = []  # UUIDs of Task invocations in this conversation
    spawned_by_invocation: str | None = None  # Task invocation UUID that created this sidechain
    sidechain_metadata: dict[str, Any] = {}  # Additional metadata
    # Error handling fields
    has_error: bool = False
    error_message: str | None = None


class ProjectDiscovery:
    """Discovers and maps Claude Code project conversations."""

    def __init__(self, claude_projects_dir: Path | None = None, use_cache: bool = True):
        """Initialize discovery with optional custom Claude projects directory.

        Args:
            claude_projects_dir: Custom Claude projects directory
            use_cache: Whether to use incremental processing cache
        """
        self.claude_projects_dir = claude_projects_dir or Path.home() / ".claude" / "projects"
        self.use_cache = use_cache
        self._cache = None
        if use_cache:
            from .cache import ConversationAnalysisCache

            self._cache = ConversationAnalysisCache()

    def project_path_to_folder_name(self, project_path: Path) -> str:
        """Convert a project path to Claude's folder naming convention.

        Args:
            project_path: Path to convert

        Returns:
            Folder name with slashes replaced by dashes

        Example:
            /Users/robotdad/Source/SelfServe -> -Users-robotdad-Source-SelfServe
        """
        # Convert to absolute path and replace separators
        absolute_path = Path(project_path).absolute()
        return str(absolute_path).replace("/", "-")

    def discover_project_conversations(
        self,
        project_path: Path,
        exclude_snapshots: bool = False,  # Changed default to include all
    ) -> list[ConversationFile]:
        """Discover all conversation files for a given project.

        Args:
            project_path: Path to the project directory
            exclude_snapshots: If True, exclude intermediate conversation snapshots

        Returns:
            List of ConversationFile objects

        Raises:
            ValueError: If project folder doesn't exist
        """
        folder_name = self.project_path_to_folder_name(project_path)
        project_folder = self.claude_projects_dir / folder_name

        if not project_folder.exists():
            raise ValueError(f"No Claude conversations found for project: {project_path}")

        conversations: list[ConversationFile] = []
        jsonl_files = list(project_folder.glob("*.jsonl"))

        logger.info(f"Analyzing {len(jsonl_files)} conversation files...")

        # Clean up stale cache entries if using cache
        if self._cache:
            valid_paths = set(jsonl_files)
            self._cache.cleanup_stale_entries(valid_paths)

        # Track cache performance
        cache_hits = 0
        cache_misses = 0

        # Process files in smaller batches for better memory management
        batch_size = 50  # Process 50 files at a time
        for i in range(0, len(jsonl_files), batch_size):
            batch = jsonl_files[i : i + batch_size]
            logger.debug(f"Processing batch {i // batch_size + 1}/{(len(jsonl_files) + batch_size - 1) // batch_size}")

            for jsonl_file in batch:
                # Try to get cached result first
                if self._cache:
                    cached_result = self._cache.get_cached_result(jsonl_file)
                    if cached_result:
                        conversations.append(cached_result)
                        cache_hits += 1
                        continue
                    cache_misses += 1

                # Analyze file and cache result
                conv_file = self._analyze_conversation_file(jsonl_file)
                conversations.append(conv_file)

                if self._cache:
                    self._cache.cache_result(conv_file)

        # Save cache if used
        if self._cache:
            self._cache.save()
            cache_total = cache_hits + cache_misses
            if cache_total > 0:
                hit_rate = (cache_hits / cache_total) * 100
                logger.info(f"Cache performance: {cache_hits}/{cache_total} hits ({hit_rate:.1f}%)")

        logger.info(f"Successfully analyzed {len(conversations)} conversations")

        # Detect and filter snapshots if requested
        if exclude_snapshots and conversations:
            conversations = self.detect_and_filter_snapshots(conversations)

        # Import subagent detection modules
        from .subagent_detector import detect_cross_session_relationships
        from .subagent_detector import get_subagent_metadata

        # Build cross-session relationships after all conversations are analyzed
        # Skip if too many conversations to avoid O(n²) complexity issues
        if len(conversations) > 500:
            logger.info(
                f"Skipping cross-session relationship analysis for {len(conversations)} conversations (performance optimization)"
            )
            sidechain_relationships = {}
        else:
            logger.info("Building cross-session relationships...")
            sidechain_relationships = detect_cross_session_relationships(conversations)

        # Update conversation objects with relationships
        for parent_id, relationships in sidechain_relationships.items():
            parent_conv = next((c for c in conversations if c.session_id == parent_id), None)
            if parent_conv:
                parent_conv.child_session_ids = [rel.child_session_id for rel in relationships]

            for rel in relationships:
                child_conv = next((c for c in conversations if c.session_id == rel.child_session_id), None)
                if child_conv:
                    child_conv.is_subagent_sidechain = True
                    child_conv.parent_session_ids = [parent_id]
                    child_conv.spawned_by_invocation = rel.invocation_uuid

                    # Update sidechain metadata with relationship info
                    child_conv.sidechain_metadata = get_subagent_metadata(child_conv, sidechain_relationships)

        # Log cache statistics if available
        if self._cache:
            cache_stats = self._cache.get_cache_stats()
            logger.info(f"Analysis cache contains {cache_stats['total_entries']} entries")

        return sorted(conversations, key=lambda x: x.first_timestamp or "")

    def _analyze_conversation_file(self, file_path: Path) -> ConversationFile:
        """Analyze a single conversation file for metadata.

        Args:
            file_path: Path to the JSONL file

        Returns:
            ConversationFile object with metadata
        """
        # Default to filename as session_id
        session_id = file_path.stem
        message_count, size = self._get_file_stats_fast(file_path)
        # message_count already set from _get_file_stats_fast
        first_timestamp = None
        last_timestamp = None
        starts_with_summary = False
        leaf_uuid = None
        actual_session_id = None
        has_sidechains = False
        sidechain_count = 0
        is_completion_marker = False

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
                # Verify message count matches our fast count
                actual_count = len(lines)
                if actual_count != message_count:
                    logger.debug(f"Message count mismatch in {file_path}: fast={message_count}, actual={actual_count}")
                    message_count = actual_count

                if lines:
                    try:
                        # Check first line
                        first_data = json.loads(lines[0])
                        if first_data.get("type") == "summary":
                            starts_with_summary = True
                            leaf_uuid = first_data.get("leafUuid")

                            # Detect completion markers (single line summary files)
                            if len(lines) == 1 or (len(lines) == 2 and not lines[1].strip()):
                                is_completion_marker = True
                        elif first_data.get("isCompactSummary") is True:
                            # Post-compaction continuation starts with user message
                            starts_with_summary = True

                        # Get the actual session ID from the data
                        # For continuation files, this might differ from the filename
                        if first_data.get("sessionId"):
                            actual_session_id = first_data["sessionId"]
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Malformed first line in {file_path}: {e}")
                        # Continue processing without first line data

                    # Find first timestamp and check for sidechains
                    for i, line in enumerate(lines[: min(20, len(lines))]):
                        try:
                            data = json.loads(line)
                            if data.get("timestamp") and not first_timestamp:
                                first_timestamp = data["timestamp"]
                            # Check for sidechain messages
                            if data.get("isSidechain") is True:
                                has_sidechains = True
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.debug(f"Skipping malformed line {i} in {file_path}: {e}")
                            continue

                    # Count total sidechains if any were detected
                    if has_sidechains:
                        for _i, line in enumerate(lines):
                            try:
                                data = json.loads(line)
                                if data.get("isSidechain") is True:
                                    sidechain_count += 1
                            except (json.JSONDecodeError, KeyError):
                                # Skip malformed lines silently during counting
                                continue

                    # Get last timestamp
                    if len(lines) > 0:
                        try:
                            last_data = json.loads(lines[-1])
                            last_timestamp = last_data.get("timestamp")
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.debug(f"Unable to parse last line in {file_path}: {e}")
                            # Try previous lines working backwards
                            for i in range(len(lines) - 2, max(-1, len(lines) - 6), -1):
                                try:
                                    fallback_data = json.loads(lines[i])
                                    if fallback_data.get("timestamp"):
                                        last_timestamp = fallback_data["timestamp"]
                                        break
                                except (json.JSONDecodeError, KeyError, IndexError):
                                    continue

        except OSError as e:
            logger.error(f"Unable to read conversation file {file_path}: {e}")
            # Return a minimal file with error flag
            return ConversationFile(
                path=file_path,
                session_id=session_id,
                size=0,
                message_count=0,
                has_error=True,
                error_message=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error analyzing {file_path}: {e}")
            # Return a fallback ConversationFile
            return ConversationFile(
                path=file_path,
                session_id=session_id,
                size=size,
                message_count=0,
                has_error=True,
                error_message=str(e),
            )

        # Extract UUIDs for snapshot detection
        try:
            message_uuids: set[str] = self._extract_message_uuids(file_path)
        except Exception as e:
            logger.warning(f"Failed to extract UUIDs from {file_path}: {e}")
            message_uuids = set()

        # For post-compaction continuations, keep the filename as session_id
        # to maintain uniqueness, but store the parent session ID separately
        parent_session_id = None
        if starts_with_summary and actual_session_id and actual_session_id != session_id:
            # This is a continuation file with a different internal session ID
            parent_session_id = actual_session_id
            # Keep using the filename-based session_id for uniqueness

        # Create initial ConversationFile object to use for SDK detection
        conv_file = ConversationFile(
            path=file_path,
            session_id=session_id,
            size=size,
            message_count=message_count,
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
            starts_with_summary=starts_with_summary,
            leaf_uuid=leaf_uuid,
            message_uuids=message_uuids,
            parent_session_id=parent_session_id,
            has_sidechains=has_sidechains,
            sidechain_count=sidechain_count,
            is_completion_marker=is_completion_marker,
        )

        # Detect SDK pattern
        try:
            from .sdk_detector import detect_sdk_pattern

            sdk_pattern = detect_sdk_pattern(conv_file)
            conv_file.is_sdk_generated = sdk_pattern.confidence_score > 0.8
            conv_file.sdk_pattern_score = sdk_pattern.confidence_score
        except Exception as e:
            logger.warning(f"SDK pattern detection failed for {file_path}: {e}")
            conv_file.is_sdk_generated = False
            conv_file.sdk_pattern_score = 0.0

        # Enhanced continuation detection
        try:
            from .continuation_detector import detect_continuation_pattern
            from .continuation_detector import determine_continuation_type

            continuation_pattern = detect_continuation_pattern(conv_file)
            conv_file.continuation_confidence = continuation_pattern.confidence_score
            conv_file.continuation_type = determine_continuation_type(continuation_pattern)
            conv_file.session_transitions = continuation_pattern.session_ids_found
            conv_file.summary_pattern_type = continuation_pattern.summary_type
        except Exception as e:
            logger.warning(f"Continuation detection failed for {file_path}: {e}")
            conv_file.continuation_confidence = 0.0
            conv_file.continuation_type = None
            conv_file.session_transitions = set()
            conv_file.summary_pattern_type = "none"

        # Extract Task tool invocations for subagent detection
        try:
            from .subagent_detector import extract_task_invocations
            from .subagent_detector import get_subagent_metadata

            task_invocations = extract_task_invocations(conv_file)
            conv_file.subagent_invocations = [inv.message_uuid for inv in task_invocations]

            # Get initial subagent metadata (relationships will be built later)
            sidechain_metadata = get_subagent_metadata(conv_file, {})
            conv_file.sidechain_metadata = sidechain_metadata
        except Exception as e:
            logger.warning(f"Subagent detection failed for {file_path}: {e}")
            conv_file.subagent_invocations = []
            conv_file.sidechain_metadata = {}

        return conv_file

    def _extract_message_uuids(self, file_path: Path) -> set[str]:
        """Extract all message UUIDs from a conversation file.

        Optimized to read only the first 100 lines for performance,
        as UUIDs are typically in the early messages.

        Args:
            file_path: Path to the JSONL file

        Returns:
            Set of UUIDs found in the file
        """
        uuids: set[str] = set()
        try:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f):
                    # Limit reading to first 100 lines for performance
                    if line_num >= 100:
                        break

                    try:
                        data = json.loads(line)
                        if uuid := data.get("uuid"):
                            uuids.add(uuid)
                    except (json.JSONDecodeError, KeyError):
                        continue
        except OSError as e:
            logger.debug(f"Unable to read UUIDs from {file_path}: {e}")
        return uuids

    def detect_and_filter_snapshots(self, conversations: list[ConversationFile]) -> list[ConversationFile]:
        """Detect conversation snapshots and filter out intermediates.

        Understanding the conversation types:
        1. Original conversations - normal conversation files
        2. Intermediate snapshots - partial copies during long conversations
        3. Pre-compaction conversations - complete conversations that may have continuations
        4. Post-compaction continuations - continuations after compaction (isCompactSummary: true)
        5. New conversations that start with summary - unrelated to previous

        The goal: Keep post-compaction continuations, pre-compaction conversations,
        and new conversations. Exclude only intermediate snapshots.

        Args:
            conversations: List of all discovered conversations

        Returns:
            Filtered list with intermediate snapshots excluded
        """
        # First, identify post-compaction continuations
        continuations: list[ConversationFile] = []
        for conv in conversations:
            if self._is_compaction_continuation(conv.path):
                continuations.append(conv)

        # Start with all continuations (always included)
        result: list[ConversationFile] = continuations.copy()

        # Now process non-continuation files for snapshot detection
        non_continuations = [c for c in conversations if c not in continuations]

        # Group conversations by significant UUID overlap
        processed: set[Path] = set()

        for conv in non_continuations:
            if conv.path in processed:
                continue

            # Skip files with no UUIDs
            if not conv.message_uuids:
                result.append(conv)
                processed.add(conv.path)
                continue

            # Find all files with significant UUID overlap (potential snapshots)
            group = [conv]
            processed.add(conv.path)

            for other in non_continuations:
                if other.path in processed:
                    continue
                if not other.message_uuids:
                    continue

                # Check for significant overlap
                overlap = conv.message_uuids & other.message_uuids
                if overlap:
                    # Calculate overlap percentage based on smaller set
                    smaller_size = min(len(conv.message_uuids), len(other.message_uuids))
                    if len(overlap) > smaller_size * 0.8:  # 80% threshold
                        group.append(other)
                        processed.add(other.path)

            # Process the group
            if len(group) == 1:
                # No snapshots, include the file
                result.append(conv)
            else:
                # Multiple files with overlap - these are likely snapshots
                # Sort by message count (smallest to largest)
                group.sort(key=lambda x: x.message_count)

                # Keep the most complete version (largest or with summary)
                selected: ConversationFile | None = None

                # Prefer files that start with summary (more complete)
                for g in reversed(group):  # Start from largest
                    if g.starts_with_summary:
                        selected = g
                        break

                # If no summary file, take the largest
                if not selected:
                    selected = group[-1]

                # Add selected, mark others as snapshots
                result.append(selected)
                for g in group:
                    if g != selected:
                        g.is_snapshot = True
                        g.snapshot_type = "intermediate"

        return result

    def _is_compaction_continuation(self, file_path: Path) -> bool:
        """Check if a file is a post-compaction continuation.

        These files have isCompactSummary: true in the first user message.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                first_line = f.readline()
                if first_line:
                    data = json.loads(first_line)
                    return data.get("isCompactSummary", False) is True
        except (OSError, json.JSONDecodeError):
            pass
        return False

    def find_continuation_chains(self, conversations: list[ConversationFile]) -> dict[str, list[str]]:
        """Find continuation chains in conversations.

        Args:
            conversations: List of conversation files

        Returns:
            Dictionary mapping conversation IDs to their continuation chain
        """
        chains: dict[str, list[str]] = {}

        # For post-compaction continuations, use parent_session_id
        for conv in conversations:
            if conv.parent_session_id:
                # This is a post-compaction continuation
                if conv.parent_session_id not in chains:
                    chains[conv.parent_session_id] = []
                chains[conv.parent_session_id].append(conv.session_id)

        # Build UUID maps PER CONVERSATION FILE (not global)
        # UUIDs are only unique within a single conversation file
        # When multiple conversations have the same last UUID, prefer the earlier one (by timestamp)
        uuid_to_session: dict[str, str] = {}

        # Sort conversations by timestamp to handle conflicts predictably
        sorted_convs = sorted(conversations, key=lambda c: c.first_timestamp or "")

        # First pass: collect last UUIDs from each conversation
        # Use optimized approach to find last UUID without reading entire file
        for conv in sorted_convs:
            try:
                last_uuid = self._get_last_uuid_optimized(conv.path)
                # Map the last UUID of this conversation to its session ID
                # If UUID already exists, keep the first (earliest) mapping
                if last_uuid and last_uuid not in uuid_to_session:
                    uuid_to_session[last_uuid] = conv.session_id
            except Exception as e:
                logger.debug(f"Failed to extract last UUID from {conv.path}: {e}")
                continue

        # Now build chains for non-compaction continuations
        for conv in conversations:
            if conv.starts_with_summary and conv.leaf_uuid and not conv.is_completion_marker:
                # This conversation continues from another (exclude completion markers)
                parent_id = uuid_to_session.get(conv.leaf_uuid)
                # Only add to chains if parent exists and is different from self
                if parent_id and parent_id != conv.session_id:
                    if parent_id not in chains:
                        chains[parent_id] = []
                    chains[parent_id].append(conv.session_id)

        return chains

    def _get_last_uuid_optimized(self, file_path: Path) -> str | None:
        """Get the last UUID from a file by reading from the end.

        Args:
            file_path: Path to the JSONL file

        Returns:
            Last UUID found in the file, or None if not found
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                # Read file in reverse to find last UUID faster
                # For very large files, this avoids reading the entire content
                lines = f.readlines()

                # Check last 20 lines in reverse order for UUID
                for line in reversed(lines[-20:]):
                    try:
                        data = json.loads(line)
                        if uuid := data.get("uuid"):
                            return uuid
                    except (json.JSONDecodeError, KeyError):
                        continue

                # Fallback: check earlier lines if no UUID found in last 20
                for line in reversed(lines[:-20]):
                    try:
                        data = json.loads(line)
                        if uuid := data.get("uuid"):
                            return uuid
                    except (json.JSONDecodeError, KeyError):
                        continue

        except (OSError, Exception) as e:
            logger.debug(f"Error reading last UUID from {file_path}: {e}")

        return None

    def _get_file_stats_fast(self, file_path: Path) -> tuple[int, int]:
        """Get basic file statistics without full parsing.

        Args:
            file_path: Path to the JSONL file

        Returns:
            Tuple of (message_count, file_size)
        """
        try:
            file_size = file_path.stat().st_size

            # Count lines efficiently
            with open(file_path, encoding="utf-8") as f:
                message_count = sum(1 for _ in f)

            return message_count, file_size
        except (OSError, Exception) as e:
            logger.debug(f"Error getting file stats for {file_path}: {e}")
            return 0, 0
