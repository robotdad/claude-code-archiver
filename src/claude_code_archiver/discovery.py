"""Project discovery using simplified SessionFile model."""

import logging
from datetime import UTC
from datetime import datetime
from pathlib import Path

from .models import SessionFile
from .parser import ConversationParser

# Compatibility alias for existing code
ConversationFile = SessionFile

logger = logging.getLogger(__name__)


class ProjectDiscovery:
    """Discovers and maps Claude Code project conversations."""

    def __init__(self, claude_projects_dir: Path | None = None):
        """Initialize discovery."""
        self.claude_projects_dir = claude_projects_dir or Path.home() / ".claude" / "projects"
        self.parser = ConversationParser()

    def project_path_to_folder_name(self, project_path: Path) -> str:
        """Convert project path to Claude's folder naming."""
        absolute_path = Path(project_path).absolute()
        return str(absolute_path).replace("/", "-")

    def discover_project_conversations(
        self,
        project_path: Path,
        exclude_snapshots: bool = False,  # Keep for compatibility
    ) -> list[SessionFile]:
        """Discover all conversation files for a project.

        Args:
            project_path: Path to the project directory

        Returns:
            List of SessionFile objects
        """
        folder_name = self.project_path_to_folder_name(project_path)
        project_folder = self.claude_projects_dir / folder_name

        if not project_folder.exists():
            raise ValueError(f"No Claude conversations found for: {project_path}")

        jsonl_files = list(project_folder.glob("*.jsonl"))
        logger.info(f"Analyzing {len(jsonl_files)} conversation files...")

        sessions = []
        for jsonl_file in jsonl_files:
            try:
                session = self._analyze_file(jsonl_file)
                sessions.append(session)
            except Exception as e:
                logger.warning(f"Failed to analyze {jsonl_file}: {e}")
                continue

        logger.info(f"Successfully analyzed {len(sessions)} sessions")
        return sorted(sessions, key=lambda x: x.modified_at)

    def _analyze_file(self, file_path: Path) -> SessionFile:
        """Analyze a single conversation file."""
        # Parse into DAG
        dag = self.parser.parse_file(file_path)

        # Get file stats
        stat = file_path.stat()

        # Get first and last timestamps from DAG
        first_timestamp = None
        last_timestamp = None
        if dag.nodes:
            timestamps = [node.timestamp for node in dag.nodes.values() if node.timestamp]
            if timestamps:
                first_timestamp = min(timestamps)
                last_timestamp = max(timestamps)

        return SessionFile(
            path=file_path,
            size_bytes=stat.st_size,
            modified_at=self._get_iso_timestamp(stat.st_mtime),
            root_uuid=dag.root_uuid,
            leaf_uuids=dag.leaf_uuids,
            path_count=len(dag.leaf_uuids),
            message_count=dag.message_count,
            has_branches=len(dag.leaf_uuids) > 1,
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
        )

    def _get_iso_timestamp(self, timestamp: float) -> str:
        """Convert unix timestamp to ISO 8601."""

        return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
