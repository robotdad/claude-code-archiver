# Claude Code Archiver

Archive, view, and manage your Claude Code conversations with an interactive viewer and smart curation features.

## Quick Start

Archive conversations from any Claude Code project using `uvx` - no installation required:

```bash
# Basic usage - archive a project's conversations
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/your/project

# Refresh an existing archive with new conversations (auto-detects project paths)
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver --refresh /path/to/archive.zip
```

## View Your Archive

After creating an archive:

```bash
# Extract and start the interactive viewer
unzip your-archive.zip && cd your-archive-folder
python serve.py
```

This opens an interactive web viewer at `http://localhost:8000` where you can:
- Browse conversations with smart titles and metadata
- Hide/unhide conversations to curate your collection  
- Export individual conversations as clean Markdown
- Switch between focused and detailed view modes
- Save changes back to the original ZIP archive

## Core Features

- 🎯 **One-command archiving** via `uvx` - no installation needed
- 🔒 **Automatic sanitization** of sensitive data (API keys, tokens, passwords)  
- 📝 **Smart conversation titles** extracted from your first message
- 🛠️ **Interactive curation** - hide unsuccessful conversations, organize your collection
- 📄 **Clean exports** - focused summaries or detailed technical records
- 🔄 **Smart refresh** - add new conversations while preserving your customizations
- 🧠 **Intelligent detection** - distinguishes true continuations from auto-linked conversations

## Common Options

```bash
# Archive with custom output location
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --output /path/to/archives

# Include snapshot files (excluded by default for cleaner results)
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --include-snapshots

# Skip sensitive data sanitization (not recommended)
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --no-sanitize

# Just list conversations without creating archive
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --list-only
```

## How It Works

Claude Code stores conversations in `~/.claude/projects/` as JSONL files. The archiver:

1. **Discovers** conversations for your project by mapping project paths to Claude's folder structure
2. **Extracts** meaningful titles from your first message in each conversation
3. **Sanitizes** sensitive data like API keys and passwords (enabled by default)
4. **Creates** an interactive ZIP archive with viewer and all conversation data
5. **Preserves** your customizations when refreshing with new conversations

### Project Path Mapping
Claude Code converts your project path into a folder name:
- Project: `/Users/name/Source/my-project` 
- Claude folder: `~/.claude/projects/-Users-name-Source-my-project`

## Advanced Features

### Project Aliases
Include conversations from renamed or moved projects:

```bash
# Include conversations from old project names
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/current-project --alias /path/to/old-name

# Use wildcards to include multiple related projects  
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/amplifier --alias "/path/to/amplifier*"
```

### Archive Management
```bash
# Refresh archive with new conversations (preserves your curation)
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver --refresh /path/to/archive.zip

# Add new project aliases to existing archive
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver --refresh /path/to/archive.zip --alias /path/to/new-branch
```

### Interactive Viewer Features

The web viewer includes:
- **Conversation curation**: Hide unsuccessful attempts, organize your collection
- **Export modes**: Focused summaries or detailed technical records  
- **Persistent storage**: Save your preferences back to the ZIP archive
- **Smart display**: Tool interactions collapsed by default, snapshots hidden
- **View modes**: Switch between clean reading and full technical details

## Data Safety

**Automatic Sanitization** (enabled by default) attempts to remove common sensitive patterns:
- API keys with clear context (OpenAI `sk-...`, Anthropic `sk-ant-...`, GitHub `ghp_/ghs_...`)
- Bearer tokens in Authorization headers
- Database connection strings with passwords
- Environment variables with sensitive names (uppercase only)
- JWT tokens

**Important:** Sanitization is a courtesy feature, not a security guarantee. It cannot catch all possible sensitive data. If you've accidentally included secrets in conversations, consider them potentially compromised. Review your archives and regenerate any exposed credentials.

## Command Reference

```bash
claude-code-archiver [PROJECT_PATH] [OPTIONS]
```

### Common Options
- `--refresh, -r PATH`: Refresh existing archive (PROJECT_PATH optional when using this)
- `--alias, -a TEXT`: Include conversations from additional project paths (supports wildcards)
- `--output, -o PATH`: Custom output directory
- `--include-snapshots`: Include snapshot files (hidden by default)
- `--no-sanitize`: Skip sanitization (not recommended)
- `--list-only, -l`: List conversations without creating archive

### Examples
```bash
# Basic usage
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project

# With project aliases  
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/current-project --alias /path/to/old-name --alias "/path/to/experiments*"

# Refresh existing archive
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver --refresh /path/to/archive.zip
```

## Development

### Project Structure

```
claude-code-archiver/
├── src/claude_code_archiver/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface with enhanced options
│   ├── discovery.py        # Advanced conversation discovery and type detection
│   ├── parser.py           # JSONL parsing with multimodal support
│   ├── sanitizer.py        # Comprehensive sensitive data sanitization
│   ├── archiver.py         # Archive creation with title extraction and todo integration
│   ├── serve_template.py   # Web server template (serves viewer at root path)
│   └── viewer/
│       └── generator.py    # Enhanced HTML viewer with metadata display
├── tests/                  # Comprehensive test suite
├── docs/                   # Documentation and analysis
├── pyproject.toml          # Project configuration
├── ruff.toml              # Linter configuration
└── Makefile               # Development tasks
```

### Development Commands

```bash
# Install dependencies
make install
# or directly with uv
uv sync

# Run the CLI from source
uv run claude-code-archiver --help

# Run tests
make test
# or directly with uv
uv run pytest tests/

# Format code
make format
# or directly with uv
uv run ruff format src/ tests/

# Lint code
make lint
# or directly with uv
uv run ruff check src/ tests/

# Type check
make type
# or directly with uv
uv run pyright

# Run all checks
make check

# Build package for distribution
make build
# or directly with uv
uv build
```

### Testing

The test suite includes:
- Unit tests for each module
- Integration tests for end-to-end workflows
- Fixtures for sample conversation data

Run tests with coverage:
```bash
make test
```

## Requirements

- Python 3.11+
- uv (for development)

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Run `make check` to ensure code quality
4. Submit a pull request

## Support

For issues or questions, please open an issue on GitHub:
https://github.com/robotdad/claude-code-archiver/issues