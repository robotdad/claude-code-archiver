"""Sanitizer module for removing sensitive information from conversations."""

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class SanitizationPattern(BaseModel):
    """Represents a pattern for sanitizing sensitive data."""

    name: str
    pattern: str
    replacement: str
    description: str


class SanitizationStats(BaseModel):
    """Statistics about sanitization operations."""

    total_redactions: int = 0
    redactions_by_type: dict[str, int] = {}


class Sanitizer:
    """Sanitizes sensitive information from conversation data."""

    def __init__(self):
        """Initialize sanitizer with default patterns."""
        self.patterns = self._get_default_patterns()
        self.stats = SanitizationStats()

    def _get_default_patterns(self) -> list[SanitizationPattern]:
        """Get default sanitization patterns.

        Returns:
            List of sanitization patterns
        """
        return [
            SanitizationPattern(
                name="openai_api_key",
                pattern=r"sk-[a-zA-Z0-9]{48}",
                replacement="[REDACTED_OPENAI_API_KEY]",
                description="OpenAI API key",
            ),
            SanitizationPattern(
                name="anthropic_api_key",
                pattern=r"sk-ant-[a-zA-Z0-9-]{95}",
                replacement="[REDACTED_ANTHROPIC_API_KEY]",
                description="Anthropic API key",
            ),
            SanitizationPattern(
                name="generic_api_key",
                pattern=r'api[_-]?key["\s:=]+["\'`]?([a-zA-Z0-9-_]{20,})["\']?',
                replacement="[REDACTED_API_KEY]",
                description="Generic API key pattern",
            ),
            SanitizationPattern(
                name="bearer_token",
                pattern=r"Bearer\s+[a-zA-Z0-9-._~+/]+=*",
                replacement="Bearer [REDACTED_TOKEN]",
                description="Bearer authentication token",
            ),
            SanitizationPattern(
                name="aws_access_key",
                pattern=r"AKIA[0-9A-Z]{16}",
                replacement="[REDACTED_AWS_ACCESS_KEY]",
                description="AWS Access Key ID",
            ),
            SanitizationPattern(
                name="aws_secret_key",
                pattern=r"[a-zA-Z0-9/+=]{40}",
                replacement="[REDACTED_AWS_SECRET_KEY]",
                description="AWS Secret Key (context-dependent)",
            ),
            SanitizationPattern(
                name="github_token",
                pattern=r"gh[ps]_[a-zA-Z0-9]{35,40}",
                replacement="[REDACTED_GITHUB_TOKEN]",
                description="GitHub personal access token",
            ),
            SanitizationPattern(
                name="jwt_token",
                pattern=r"eyJ[a-zA-Z0-9-_]+\.eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+",
                replacement="[REDACTED_JWT_TOKEN]",
                description="JSON Web Token",
            ),
            SanitizationPattern(
                name="database_url",
                pattern=r"(postgresql|mysql|mongodb|redis)://[^:]+:([^@]+)@[^/\s]+",
                replacement=r"\1://[REDACTED_USER]:[REDACTED_PASSWORD]@[REDACTED_HOST]",
                description="Database connection string with password",
            ),
            SanitizationPattern(
                name="env_secret",
                pattern=r"(SECRET|TOKEN|KEY|PASSWORD|PASSWD|PWD)[\"\s:=]+[\"\'`]?([a-zA-Z0-9-_/.]{8,})[\"\']?",
                replacement=r"\1=[REDACTED]",
                description="Environment variables with sensitive names",
            ),
        ]

    def sanitize_text(self, text: str) -> tuple[str, int]:
        """Sanitize sensitive information from text.

        Args:
            text: Text to sanitize

        Returns:
            Tuple of (sanitized text, number of redactions)
        """
        sanitized = text
        redaction_count = 0

        for pattern in self.patterns:
            regex = re.compile(pattern.pattern, re.IGNORECASE)
            matches = regex.findall(sanitized)

            if matches:
                sanitized = regex.sub(pattern.replacement, sanitized)
                count = len(matches)
                redaction_count += count
                self.stats.redactions_by_type[pattern.name] = self.stats.redactions_by_type.get(pattern.name, 0) + count

        self.stats.total_redactions += redaction_count
        return sanitized, redaction_count

    def sanitize_json_value(self, value: Any) -> Any:
        """Recursively sanitize JSON values.

        Args:
            value: JSON value to sanitize

        Returns:
            Sanitized value
        """
        if isinstance(value, str):
            sanitized, _ = self.sanitize_text(value)
            return sanitized
        if isinstance(value, dict):
            return {k: self.sanitize_json_value(v) for k, v in value.items()}  # type: ignore[misc]
        if isinstance(value, list):
            return [self.sanitize_json_value(item) for item in value]  # type: ignore[misc]
        return value

    def sanitize_file(self, input_path: Path, output_path: Path) -> SanitizationStats:
        """Sanitize a JSONL file.

        Args:
            input_path: Path to input JSONL file
            output_path: Path to output sanitized file

        Returns:
            Sanitization statistics
        """
        self.stats = SanitizationStats()

        with open(input_path, encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
            for line in infile:
                if not line.strip():
                    outfile.write(line)
                    continue

                try:
                    data = json.loads(line)
                    sanitized_data = self.sanitize_json_value(data)
                    outfile.write(json.dumps(sanitized_data) + "\n")
                except json.JSONDecodeError:
                    # If we can't parse JSON, sanitize as plain text
                    sanitized_line, _ = self.sanitize_text(line)
                    outfile.write(sanitized_line)

        return self.stats

    def add_custom_pattern(self, pattern: SanitizationPattern) -> None:
        """Add a custom sanitization pattern.

        Args:
            pattern: Custom pattern to add
        """
        self.patterns.append(pattern)

    def remove_pattern(self, name: str) -> None:
        """Remove a sanitization pattern by name.

        Args:
            name: Name of pattern to remove
        """
        self.patterns = [p for p in self.patterns if p.name != name]

    def get_stats(self) -> SanitizationStats:
        """Get current sanitization statistics.

        Returns:
            Current statistics
        """
        return self.stats
