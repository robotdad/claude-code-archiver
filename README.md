# Claude Code Archiver

Archive, analyze, and view Claude Code conversations with advanced metadata and intelligent conversation detection.

## Features

- 📦 **Archive conversations** from any Claude Code project
- 🔒 **Automatic sanitization** of sensitive data (API keys, tokens, passwords)
- 🧠 **Intelligent conversation detection** - distinguishes auto-linked vs. true continuations
- 📝 **Smart title extraction** from first user message with intelligent text processing
- 🔗 **Advanced continuation chain tracking** - handles compaction, snapshots, and complex relationships
- 📊 **Rich statistics and metadata** - message counts, timestamps, tool usage, conversation duration
- 🎯 **Enhanced viewer** with conversation titles, timing info, and snapshot filtering
- ✅ **Todo integration** - includes TodoWrite history from ~/.claude/todos/
- 🎯 **Simple usage** via `uvx` - no installation required

## Quick Start

### Running from Repository (Development)

If you want to run the archiver directly from the repository:

```bash
# Clone the repository
git clone https://github.com/robotdad/claude-code-archiver.git
cd claude-code-archiver

# Install dependencies with uv
uv sync

# Run the archiver using uv run
uv run claude-code-archiver /path/to/your/project

# With options
uv run claude-code-archiver /path/to/project --output /path/to/archives
uv run claude-code-archiver /path/to/project --no-sanitize
uv run claude-code-archiver /path/to/project --list-only
```

### Using uvx (Recommended)

Run directly from GitHub without cloning or installation:

```bash
# Archive a project's conversations
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/your/project

# Archive with custom output location  
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --output /path/to/archives

# Include snapshots (hidden by default)
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --include-snapshots

# Skip sanitization (keeps sensitive data)
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --no-sanitize

# Exclude todo files
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --no-todos

# Just list conversations without archiving
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --list-only
```

### Using uvx (After Publishing to PyPI)

Once published to PyPI, you can use the shorter form:

```bash
# Archive a project's conversations
uvx claude-code-archiver /path/to/your/project
```

## How It Works

Claude Code stores conversations in `~/.claude/projects/` as JSONL files. This tool:

1. **Discovers** all conversations for your project
2. **Analyzes** conversation types (snapshots, continuations, auto-linked conversations)
3. **Extracts** intelligent titles from first meaningful user messages  
4. **Collects** todo files from `~/.claude/todos/` for workflow tracking
5. **Parses** the JSONL files to extract messages, metadata, and statistics
6. **Sanitizes** sensitive information (optional but recommended)
7. **Archives** everything into a ZIP file with enhanced manifest and interactive viewer

### Project Path Mapping

Claude Code converts your project path into a folder name by replacing `/` with `-`. For example:
- Project: `/Users/robotdad/Source/my-project`
- Claude folder: `~/.claude/projects/-Users-robotdad-Source-my-project`

## Viewing Archives

After creating an archive, extract it and use the included server:

```bash
# Extract the archive
unzip claude-convos-projectname-*.zip

# Navigate to the extracted folder
cd claude-convos-projectname-*

# Start the viewer server
python serve.py
```

This will automatically:
- 🚀 Start a local web server at `http://localhost:8000`
- 🌐 Open the interactive viewer in your browser
- 📋 Show all conversations with enhanced metadata:
  - **Conversation titles** extracted from first user messages
  - **Start and end timestamps** with duration information
  - **Message counts** and conversation statistics
  - **Continuation markers** for true continuations (not auto-linked)
  - **Snapshot filtering** - snapshots hidden by default with toggle button
  - **Todo integration** when available

### Viewer Features

- **Enhanced Conversation List**: Shows titles, timestamps, and metadata
- **Smart Continuation Detection**: Only marks true continuations, not auto-linked conversations  
- **Snapshot Management**: Hide intermediate snapshots by default, toggle to show all
- **Comprehensive Metadata**: Creation time, last modified, duration, message counts
- **Interactive Display**: Click any conversation to view full message history

Press `Ctrl+C` to stop the server when done.

## Archive Structure

The generated archive contains:

```
claude-convos-projectname-20250101_120000.zip
├── viewer.html                   # Interactive conversation viewer with enhanced UI
├── serve.py                      # Python web server (serves viewer at root path)
├── manifest.json                 # Enhanced metadata and conversation index
├── conversations/
│   ├── session-id-1.jsonl       # Sanitized conversation files
│   ├── session-id-2.jsonl       # (snapshots excluded by default)
│   └── ...
├── todos/                        # Todo files from ~/.claude/todos/
│   ├── session-id-1.json        # TodoWrite history for conversations
│   └── ...
```

### Enhanced Manifest Contents

The `manifest.json` now includes:
- Project path, creation timestamp, and conversation count
- **Conversation titles** extracted from first user messages
- **Conversation types**: `original`, `pre_compaction`, `post_compaction`, `auto_linked`, `snapshot`
- **Enhanced metadata**: first/last timestamps, message counts, duration
- **Continuation chains** with smart detection (true continuations vs auto-linked)
- **Display preferences**: which conversations to show by default
- **Sanitization statistics** (if sanitization was performed)
- **Detailed tool usage statistics** per conversation
- **Todo integration metadata** when available

## Sanitization

By default, the archiver removes sensitive information including:

- OpenAI API keys (`sk-...`)
- Anthropic API keys (`sk-ant-...`)
- GitHub tokens (`ghp_...`, `ghs_...`)
- JWT tokens
- Bearer tokens
- Database connection strings with passwords
- Environment variables with sensitive names (SECRET, TOKEN, KEY, PASSWORD)
- AWS credentials

Sanitized content is replaced with descriptive placeholders like `[REDACTED_API_KEY]`.

## Advanced Conversation Detection

Claude Code handles long conversations in sophisticated ways. The archiver provides intelligent detection of:

### Conversation Types

- **Original**: Standalone conversations with no continuation relationships
- **Snapshots**: Intermediate saves during long conversations (hidden by default)
- **Pre-compaction**: Complete conversations before Claude Code compaction
- **Post-compaction**: True continuations after compaction with detailed context
- **Auto-linked**: New conversations automatically linked to previous ones in the same project

### Smart Continuation Detection  

The archiver distinguishes between:
- **True continuations**: Actually continue previous conversations (marked with `[CONTINUATION]`)
- **Auto-linked conversations**: New topics that Claude Code automatically links for project context (no marker)

### Detection Methods

- **Compaction detection**: Identifies `isCompactSummary` markers for true continuations
- **UUID chain tracking**: Maps `leafUuid` relationships between conversations  
- **Title analysis**: Extracts meaningful titles from first user messages
- **Snapshot identification**: Uses UUID overlap analysis to identify intermediate saves
- **Internal compaction detection**: Handles compaction events within the same file

## Command Line Options

```bash
claude-code-archiver PROJECT_PATH [OPTIONS]
```

### Arguments
- `PROJECT_PATH`: Path to the project directory to archive

### Options
- `--output, -o PATH`: Output directory for archive (default: current directory)
- `--no-sanitize`: Skip sanitization of sensitive data
- `--name, -n NAME`: Custom archive name (without extension)
- `--include-snapshots`: Include intermediate conversation snapshots (hidden by default)
- `--no-todos`: Exclude todo files from archive (included by default)
- `--list-only, -l`: List conversations without creating archive
- `--version`: Show version information
- `--help`: Show help message

### Example Usage

```bash
# Basic archive with all defaults (snapshots hidden, todos included)
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project

# Include everything including snapshots
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --include-snapshots

# Archive without todo files
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --no-todos

# Custom output location and name
uvx --from git+https://github.com/robotdad/claude-code-archiver claude-code-archiver /path/to/project --output /archives --name my-project-convos
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