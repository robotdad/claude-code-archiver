# Claude Code Conversation Archiver - Requirements Document

## Executive Summary

A Python-based tool to capture, organize, sanitize, and view Claude Code conversations stored as JSONL files in `~/.claude/projects/`. Built with modern Python tooling (uv, ruff, pyright), the tool creates self-contained archives with a static HTML viewer featuring visual tool indicators and multimodal content support for sharing experiences and analyzing AI-assisted development sessions.

## Background

Claude Code stores conversation history as JSONL files organized by project folders under `~/.claude/projects/`. These files contain rich interaction data including:
- User queries and Claude's responses  
- Tool usage (file operations, searches, bash commands)
- Project context (working directory, git branch)
- Conversation threading and continuations
- System messages and metadata

Current observations from the field:
- 173+ conversation files across multiple projects
- Files range from a few KB to several MB
- Conversations can be continued across multiple sessions through compaction/summary mechanism
- Each project folder maps to a filesystem path with `/` replaced by `-`

## Functional Requirements

### 1. Project Discovery & Mapping

#### 1.1 Input Processing
- Accept a project directory path (e.g., `/Users/user/Source/myproject`)
- Support both absolute and relative paths
- Validate that the path exists

#### 1.2 Folder Mapping
- Convert filesystem path to Claude folder name format
  - Replace `/` with `-` 
  - Example: `/Users/user/Source/myproject` → `-Users-user-Source-myproject`
- Locate corresponding folder in `~/.claude/projects/`
- Handle cases where folder doesn't exist gracefully

#### 1.3 File Discovery
- Enumerate all `*.jsonl` files in the project folder
- Collect file metadata (size, modification date)
- Build initial conversation index

### 2. Conversation Analysis & Relationship Mapping

#### 2.1 Continuation Detection
- Identify conversations starting with `type: "summary"` entries
- Extract `leafUuid` from summary entries to find parent conversations
- Build bidirectional conversation graph

#### 2.2 Conversation Metadata Extraction
- Session ID and timestamps
- Message counts by type (user, assistant, system)
- Tool usage statistics
- Git branch information
- Conversation duration

#### 2.3 Relationship Graph Building
- Map parent-child relationships via `leafUuid` references
- Identify conversation chains (original → continuation 1 → continuation 2...)
- Detect orphaned continuations (parent conversation missing)

### 3. Data Sanitization

#### 3.1 Sensitive Pattern Detection
Scan for and redact the following patterns:
- API keys (various formats):
  - OpenAI: `sk-[a-zA-Z0-9]{48}`
  - Anthropic: `sk-ant-[a-zA-Z0-9-]{95}`
  - Generic: `api[_-]key["\s:=]+["']?[a-zA-Z0-9-_]{20,}`
- Bearer tokens: `Bearer [a-zA-Z0-9-._~+/]+=*`
- AWS credentials:
  - Access Key ID: `AKIA[0-9A-Z]{16}`
  - Secret Key: `[a-zA-Z0-9/+=]{40}`
- Azure credentials
- GCP service account keys
- Database connection strings with passwords
- Environment variables containing "SECRET", "TOKEN", "KEY", "PASSWORD"
- GitHub tokens: `gh[ps]_[a-zA-Z0-9]{36}`

#### 3.2 Redaction Process
- Replace sensitive content with typed placeholders:
  - `[REDACTED_API_KEY]`
  - `[REDACTED_AWS_ACCESS_KEY]`
  - `[REDACTED_DB_PASSWORD]`
- Preserve structure and context
- Log redaction statistics

#### 3.3 Content Preservation
- Never redact code logic, file paths, or technical content
- Preserve all conversation context except sensitive values
- Maintain JSON structure integrity

### 4. Archive Generation

#### 4.1 Archive Structure
```
project-archive-YYYY-MM-DD/
├── conversations/
│   ├── [session-id-1].jsonl (sanitized)
│   ├── [session-id-2].jsonl (sanitized)
│   └── ...
├── viewer/
│   ├── index.html
│   ├── conversation.html
│   ├── styles.css
│   └── viewer.js
├── manifest.json
└── README.md
```

#### 4.2 Manifest File
JSON file containing:
- Archive metadata (creation date, source project, version)
- Conversation index with:
  - File name
  - Session ID  
  - Date range
  - Message count
  - Summary/title (first user message)
  - Continuation relationships
- Conversation graph (parent-child mappings)
- Redaction statistics

#### 4.3 ZIP Packaging
- Compress entire archive directory
- Include option for different compression levels
- Generate meaningful archive name: `claude-convos-[project-name]-[date].zip`

### 5. Static HTML Viewer

#### 5.1 Architecture
- Pure client-side application (HTML + CSS + JavaScript)
- No external dependencies or CDN requirements
- Works with file:// protocol
- Progressive enhancement approach

#### 5.2 Index Page
Display a dashboard of all conversations with:

**Layout:**
- Project name and archive date header
- Statistics summary (total conversations, date range, total messages)
- Sortable/filterable conversation table

**Conversation List Features:**
- Visual indicators for:
  - Regular conversations (standard icon)
  - Continuation conversations (chain icon)
  - Conversation chains (grouped/indented)
- Columns:
  - Date/Time (start)
  - Duration
  - Messages (user/assistant/total)
  - First user message (truncated preview)
  - Continuation status
- Sorting options (date, duration, message count)
- Search/filter by content, date range

#### 5.3 Conversation View Page

**Header Section:**
- Conversation metadata (date, duration, message count)
- Continuation navigation:
  - "← Continued from: [previous conversation]" (if applicable)
  - "Continued in: [next conversation] →" (if applicable)
- Copy conversation button

**Message Display:**
- **User messages**: 
  - Right-aligned with blue background
  - Bold header with timestamp
  - User avatar/icon
- **Assistant messages**: 
  - Left-aligned with standard styling
  - AI avatar/icon
  - Thinking blocks (collapsible, italic with signature verification)
  - Code blocks with syntax highlighting
  - Tool use sections with visual indicators
- **System messages**: Muted styling, collapsible
- **Summary messages**: Special styling (yellow background, chain icon)

**Tool Usage Visual Indicators:**
Each tool type gets a unique emoji icon and color coding:
- 📝 **TodoWrite**: Task management operations
- 💻 **Bash**: Command execution with output
- 📂 **Read**: File reading operations
- ✏️ **Edit/MultiEdit**: File modifications with diff view
- 🔍 **Grep/Glob**: Search operations
- 🌐 **WebFetch/WebSearch**: Web interactions
- 🎯 **Task**: Agent operations
- 📊 **BashOutput**: Background process monitoring
- ❌ **KillBash**: Process termination
- 🖼️ **Image content**: Inline display with click-to-expand

**Multimodal Content Support:**
- **Images**: 
  - Base64 decoding and inline display
  - Thumbnail with click-to-expand functionality
  - Full resolution modal viewer
- **Other files**: 
  - Display filename and file type
  - Show file size and path
  - Note: PDF and Jupyter notebook content shown as text/code blocks (no special rendering)

**Interactive Features:**
- **Conversation view modes:**
  - "Focused" mode: Tool messages collapsed by default (user/assistant only)
  - "Detailed" mode: All messages expanded
  - Toggle button to switch between modes
- Expand/collapse individual tool usage
- Expand/collapse all tool usage at once
- Toggle thinking blocks visibility
- Jump to next/previous user message
- Copy user message content (enables conversation replay)
- Timestamp display (relative and absolute)
- Filter by tool type
- Search within conversation

**Tool Usage Display:**
- Collapsible sections with:
  - Tool name in ASCII format `[TOOL:Name]`
  - Input parameters (formatted JSON)
  - Execution result with appropriate formatting
  - Error states highlighted in amber
  - Tool results that can be either strings OR arrays of content blocks
- Terminal-style diff view for file edits (+ for additions, - for deletions)
- Statistics in header (tool count, message count)

#### 5.4 Visual Design
- Clean, readable typography
- Sufficient contrast for code blocks
- Responsive design for mobile viewing
- Print-friendly styling
- Dark mode support (optional)

### 6. Schema Documentation

#### 6.1 JSON Schema Definition
Formal JSON Schema for:
- Conversation entry types
- Message structures
- Content block types
- Tool usage format

#### 6.2 TypeScript Definitions
```typescript
interface ConversationEntry {
  type: 'user' | 'assistant' | 'system' | 'summary';
  uuid: string;
  parentUuid: string | null;
  timestamp?: string;
  sessionId?: string;
  // ... additional fields
}
```

#### 6.3 Documentation
- Field descriptions and constraints
- Example entries for each type
- Validation rules

## Non-Functional Requirements

### Performance
- Handle conversations with 2000+ messages
- Viewer loads conversation under 2 seconds
- Smooth scrolling with 10MB+ conversations
- Efficient memory usage in browser

### Compatibility
- **Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **File Systems**: Support paths with spaces and special characters
- **Operating Systems**: macOS, Linux, Windows (with WSL)

### Security
- No execution of conversation content
- Sanitization prevents sensitive data leakage
- Viewer operates in sandboxed environment
- No network requests from viewer

### Usability
- Clear error messages with actionable solutions
- Progress indicators for long operations
- Keyboard navigation support
- Basic screen reader compatibility

### Maintainability
- Modular code structure
- Comprehensive error handling
- Logging for debugging
- Version information in archives

## Known Issues & Fixes Required

### Parser: tool_result Content Arrays
The `tool_result` content field in ContentBlock can be:
- **String** (currently handled)
- **Array of objects** with structure: `[{type: "text", text: "..."}]` (needs fix)

This occurs when tools return structured content. The parser should:
1. Check if content is array
2. Extract text from each object where type="text"
3. Join into single string for display

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **Package Management**: uv (modern Python packaging)
- **Code Quality**:
  - **Formatter**: ruff format (line-length: 120, double quotes)
  - **Linter**: ruff (with comprehensive rule set)
  - **Type Checker**: pyright (strict mode)
- **Testing**: pytest with coverage
- **Build System**: Makefile with recursive project discovery

### Project Structure
```
claude-conversation-archiver/
├── pyproject.toml          # uv project configuration
├── ruff.toml               # Ruff configuration
├── Makefile                # Build automation
├── src/
│   └── claude_archiver/
│       ├── __init__.py
│       ├── discovery.py    # Project discovery & mapping
│       ├── parser.py       # JSONL parsing
│       ├── sanitizer.py    # Data sanitization
│       ├── archiver.py     # Archive generation
│       └── viewer/         # Static HTML viewer
│           ├── templates/
│           ├── static/
│           └── generator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytest fixtures
│   ├── test_discovery.py
│   ├── test_parser.py
│   ├── test_sanitizer.py
│   ├── test_archiver.py
│   ├── test_viewer.py
│   └── fixtures/           # Sample JSONL test data
│       └── sample_conversations/
└── tools/
    └── makefiles/
        └── python.mk
```

### Development Workflow
1. **Setup**: `make install` - Install dependencies with uv
2. **Code Quality**: `make check` - Format, lint, and type-check
3. **Testing**: `make test` - Run pytest with coverage
4. **Build**: `make build` - Create distribution package

### Distribution & Usage
The primary distribution method will be via PyPI, enabling users to run the tool directly with uvx without cloning:
```bash
# One-line usage without installation
uvx claude-conversation-archiver /path/to/project

# Or with options
uvx claude-conversation-archiver --output archives --sanitize /path/to/project
```

## Implementation Plan

### Phase 1: Project Setup & Core Infrastructure
1. **Project Bootstrap**
   - Initialize uv project with pyproject.toml
   - Configure ruff and pyright
   - Set up Makefile with standard targets
   - Create project structure

2. **Schema Definition**
   - Create formal JSON Schema from investigation
   - Generate Python dataclasses/TypedDicts
   - Document all message types
   - Validate against sample data

3. **Project Discovery Module**
   - Path to folder mapping logic
   - File enumeration and validation
   - Basic metadata extraction
   - Error handling for missing projects

4. **Conversation Parser**
   - JSONL reading with streaming support
   - Message type identification
   - Basic statistics generation
   - Memory-efficient processing for large files

### Phase 2: Analysis & Sanitization
1. **Relationship Mapper**
   - Continuation detection algorithm
   - Graph building logic
   - Chain identification

2. **Sanitization Engine**
   - Pattern matching implementation
   - Configurable redaction rules
   - Testing with sample data

3. **Manifest Generator**
   - Metadata aggregation
   - Relationship graph serialization
   - Statistics computation

### Phase 3: Archive Generation
1. **Archive Builder**
   - Directory structure creation
   - File copying and sanitization
   - Manifest integration

2. **ZIP Packager**
   - Compression implementation
   - Progress reporting
   - Error handling

### Phase 4: Static Viewer - Foundation
1. **HTML Templates**
   - Index page structure
   - Conversation page structure
   - Responsive layout

2. **Core JavaScript**
   - JSONL parser
   - Data model
   - Navigation logic

3. **Basic Styling**
   - Typography and colors
   - Message type differentiation
   - Code highlighting

### Phase 5: Single-Page Terminal Viewer
1. **Architecture**
   - Single index.html file with all logic inline
   - Dynamically loads and parses JSONL files
   - No pre-generated HTML per conversation
   - Works with file:// protocol

2. **Terminal Aesthetic**
   - Monospace fonts (Cascadia Code, Fira Code, Consolas)
   - Dark background (#0c0c0c) with green text (#00ff00)
   - Box-drawing characters for UI structure
   - ASCII indicators instead of emoji for tools

3. **Core Features**
   - Dynamic JSONL parsing and rendering
   - Conversation view modes (Focused/Detailed)
   - Collapsible tool messages (collapsed by default)
   - Navigation between conversations
   - Continuation chain visualization

4. **Tool Indicators (ASCII)**
   - `[TOOL:Bash]` for command execution
   - `[TOOL:Read]` for file reading
   - `[TOOL:Edit]` for file modifications
   - `[TOOL:Search]` for grep/glob operations
   - Simple, terminal-appropriate styling

### Phase 6: Testing & Polish
1. **Unit Tests**
   - Discovery module tests (path mapping, error cases)
   - Parser tests (JSONL validation, message types)
   - Sanitizer tests (pattern matching, redaction)
   - Archiver tests (zip generation, manifest)
   - Viewer tests (HTML generation)

2. **Integration Tests**
   - End-to-end archive creation
   - Continuation chain detection
   - Large file handling

3. **Code Quality**
   - Full ruff compliance
   - pyright strict mode passing
   - 80%+ test coverage
   - Performance profiling

4. **Edge Cases**
   - Large conversations (1000+ messages)
   - Missing continuations
   - Malformed data
   - Binary content handling

5. **Documentation & Distribution**
   - Complete README.md with usage instructions
   - PyPI package configuration
   - uvx usage validation and examples

## Success Criteria

1. **Functionality**
   - Successfully archives all conversations for a given project
   - Correctly identifies and links continuation conversations
   - Sanitizes sensitive data without breaking conversation flow

2. **Usability**
   - Users can navigate conversations easily
   - Continuation chains are clearly visualized
   - Search and filter work intuitively

3. **Performance**
   - Archives generate in under 30 seconds for typical projects
   - Viewer remains responsive with large conversations

4. **Quality**
   - No sensitive data leaks in archives
   - Viewer works offline without issues
   - Cross-browser compatibility confirmed

## Appendix A: Sample Data Structures

### Summary Entry (Conversation Continuation)
```json
{
  "type": "summary",
  "summary": "Prime Command Setup: Modular AI Development Environment",
  "leafUuid": "4d8b1344-1051-49c9-ab43-f45dbb1d32ce"
}
```

### Standard Message Entry
```json
{
  "type": "user",
  "uuid": "5651e5ec-49d5-4edd-9a50-25ae4051f328",
  "parentUuid": null,
  "timestamp": "2025-08-23T02:18:28.472Z",
  "sessionId": "30f82f70-7fb6-4926-8b00-7e7b2cca2900",
  "version": "1.0.89",
  "cwd": "/Users/user/Source/myproject",
  "gitBranch": "v2-base",
  "message": {
    "role": "user",
    "content": "User message text..."
  }
}
```

## Appendix B: Sanitization Examples

### Before Sanitization
```json
{
  "content": "Set API_KEY=sk-ant-api03-xyz123... in your environment"
}
```

### After Sanitization  
```json
{
  "content": "Set API_KEY=[REDACTED_API_KEY] in your environment"
}
```

---

*Document Version: 1.0*  
*Date: 2025-08-25*  
*Author: Claude Code Assistant*