"""Tests for the sanitizer module."""

import json
from pathlib import Path
from typing import Any

from claude_code_archiver.sanitizer import SanitizationPattern
from claude_code_archiver.sanitizer import Sanitizer


def test_sanitize_openai_key() -> None:
    """Test sanitizing OpenAI API keys."""
    sanitizer = Sanitizer()

    text = "My API key is sk-1234567890abcdef1234567890abcdef1234567890abcdef"
    sanitized, count = sanitizer.sanitize_text(text)

    assert "[REDACTED_OPENAI_API_KEY]" in sanitized
    assert "sk-1234567890" not in sanitized
    assert count == 1


def test_sanitize_multiple_patterns() -> None:
    """Test sanitizing multiple sensitive patterns."""
    sanitizer = Sanitizer()

    text = """
    API_KEY=sk-1234567890abcdef1234567890abcdef1234567890abcdef
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U
    GitHub Token: ghp_1234567890abcdef1234567890abcdef123
    """

    sanitized, count = sanitizer.sanitize_text(text)

    assert "[REDACTED_OPENAI_API_KEY]" in sanitized
    assert "Bearer [REDACTED_TOKEN]" in sanitized
    assert "[REDACTED_GITHUB_TOKEN]" in sanitized
    assert count >= 3


def test_sanitize_json_value() -> None:
    """Test sanitizing JSON values recursively."""
    sanitizer = Sanitizer()

    data = {
        "config": {
            "api_key": "sk-1234567890abcdef1234567890abcdef1234567890abcdef",
            "safe_value": "This is safe",
        },
        "tokens": ["ghp_1234567890abcdef1234567890abcdef123"],
    }

    sanitized = sanitizer.sanitize_json_value(data)

    assert sanitized["config"]["api_key"] == "[REDACTED_OPENAI_API_KEY]"
    assert sanitized["config"]["safe_value"] == "This is safe"
    assert sanitized["tokens"][0] == "[REDACTED_GITHUB_TOKEN]"


def test_sanitize_file(tmp_path: Path, sample_conversation_data: list[dict[str, Any]]) -> None:
    """Test sanitizing a JSONL file."""
    sanitizer = Sanitizer()

    # Create input file with sensitive data
    input_file = tmp_path / "input.jsonl"
    output_file = tmp_path / "output.jsonl"

    # Modify sample data to include sensitive content
    sample_conversation_data[2]["message"]["content"] = (
        "My API key is sk-1234567890abcdef1234567890abcdef1234567890abcdef"
    )

    with open(input_file, "w") as f:
        for entry in sample_conversation_data:
            f.write(json.dumps(entry) + "\n")

    # Sanitize file
    stats = sanitizer.sanitize_file(input_file, output_file)

    # Check output
    with open(output_file) as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

    assert "[REDACTED_OPENAI_API_KEY]" in last_entry["message"]["content"]
    assert stats.total_redactions > 0


def test_custom_pattern() -> None:
    """Test adding custom sanitization patterns."""
    sanitizer = Sanitizer()

    # Add custom pattern
    custom = SanitizationPattern(
        name="custom_secret",
        pattern=r"CUSTOM-[A-Z0-9]{10}",
        replacement="[REDACTED_CUSTOM]",
        description="Custom secret pattern",
    )
    sanitizer.add_custom_pattern(custom)

    text = "My custom secret is CUSTOM-ABC1234567"
    sanitized, count = sanitizer.sanitize_text(text)

    assert "[REDACTED_CUSTOM]" in sanitized
    assert "CUSTOM-ABC1234567" not in sanitized
    assert count == 1
