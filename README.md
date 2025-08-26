# Claude Code Archiver

Archive and view Claude Code conversations with multimodal support.

## Features

- 📦 **Archive conversations** from any Claude Code project
- 🔒 **Automatic sanitization** of sensitive data (API keys, tokens, passwords)
- 🔗 **Continuation chain detection** - tracks conversations that continue from previous sessions
- 📊 **Rich statistics** about conversations (message counts, tool usage, etc.)
- 🎯 **Simple one-command usage** via `uvx`

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

### Using uvx (After Publishing to PyPI)

Once published to PyPI, you can run without cloning:

```bash
# Archive a project's conversations
uvx claude-code-archiver /path/to/your/project

# Archive with custom output location
uvx claude-code-archiver /path/to/project --output /path/to/archives

# Skip sanitization (keeps sensitive data)
uvx claude-code-archiver /path/to/project --no-sanitize

# Just list conversations without archiving
uvx claude-code-archiver /path/to/project --list-only
```

## How It Works

Claude Code stores conversations in `~/.claude/projects/` as JSONL files. This tool:

1. **Discovers** all conversations for your project
2. **Parses** the JSONL files to extract messages and metadata
3. **Sanitizes** sensitive information (optional but recommended)
4. **Archives** everything into a ZIP file with a manifest

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

# This will automatically:
# - Start a local web server
# - Open viewer.html in your browser
# - Show all conversations with full interactivity
```

Press `Ctrl+C` to stop the server when done.

## Archive Structure

The generated archive contains:

```
claude-convos-projectname-20250101_120000.zip
├── viewer.html                   # Interactive conversation viewer
├── serve.py                      # Simple Python web server
├── manifest.json                 # Metadata and conversation index
├── conversations/
│   ├── session-id-1.jsonl       # Sanitized conversation
│   ├── session-id-2.jsonl       # Another conversation
│   └── ...
```

### Manifest Contents

The `manifest.json` includes:
- Project path and creation timestamp
- List of all conversations with metadata
- Continuation chains (which conversations continue from others)
- Sanitization statistics (if sanitization was performed)
- Tool usage statistics per conversation

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

## Continuation Chains

Claude Code may split long conversations into multiple sessions. The archiver detects these continuations by:
- Identifying conversations that start with a summary
- Tracking the `leafUuid` that links back to the previous conversation
- Building a chain map showing the relationships

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
- `--list-only, -l`: List conversations without creating archive
- `--version`: Show version information
- `--help`: Show help message

## Development

### Project Structure

```
claude-code-archiver/
├── src/claude_code_archiver/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── discovery.py    # Project and conversation discovery
│   ├── parser.py       # JSONL parsing
│   ├── sanitizer.py    # Sensitive data sanitization
│   └── archiver.py     # Archive creation
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
├── ruff.toml          # Linter configuration
└── Makefile           # Development tasks
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