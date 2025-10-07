# Claude Code JSONL Schema Documentation

## Overview

Claude Code stores conversation data in JSONL (JSON Lines) format, where each line is a valid JSON object representing a message or metadata entry. Files are stored under `~/.claude/projects/` with project-specific subdirectories.

## Exploring Your Claude Code Data

**Note**: Not all features may be present in your system. Features like sidechains, subagents, and continuations only appear if you've used them.

```bash
# Check if you have Claude Code data
ls ~/.claude/projects/ 2>/dev/null || echo "No Claude projects found"

# Count your projects and conversations
find ~/.claude/projects -name "*.jsonl" 2>/dev/null | wc -l

# Find your largest conversation
find ~/.claude/projects -name "*.jsonl" -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -5

# Check for advanced features you've used
echo "Checking for sidechains..."
grep -l '"isSidechain":true' ~/.claude/projects/*/*.jsonl 2>/dev/null | wc -l

echo "Checking for Task tool (subagents)..."
grep -l '"name":"Task"' ~/.claude/projects/*/*.jsonl 2>/dev/null | wc -l

echo "Checking for continuations..."
for f in ~/.claude/projects/*/*.jsonl; do
  head -1 "$f" 2>/dev/null | jq -e '.type == "summary"' >/dev/null 2>&1 && echo "Found"
done | wc -l

echo "Checking for compact operations..."
grep -l '"subtype":"compact_boundary"' ~/.claude/projects/*/*.jsonl 2>/dev/null | wc -l

# Examine a conversation structure (replace with your own file)
file=$(find ~/.claude/projects -name "*.jsonl" 2>/dev/null | head -1)
if [ -n "$file" ]; then
  echo "Sample from: $file"
  head -3 "$file" | jq -c '{type, uuid, parentUuid, sessionId}'
fi
```

## File Organization

### Directory Structure
```
~/.claude/
├── projects/
│   └── {encoded-project-path}/
│       └── {session-uuid}.jsonl
├── todos/
│   └── {session-uuid}-agent-{agent-uuid}.json
├── shell-snapshots/
│   └── snapshot-{shell}-{timestamp}-{id}.sh
├── ide/
│   └── {process-id}.lock
└── statsig/
```

### Path Encoding
Project paths are encoded by replacing `/` with `-`. Example:
- Original: `/path/to/project/folder`
- Encoded: `-path-to-project-folder`

### How to Inspect Your System
```bash
# List your Claude projects
ls ~/.claude/projects/

# Check a specific project's files
ls -la ~/.claude/projects/-your-encoded-project-path/

# View first message of a conversation
head -1 ~/.claude/projects/*/some-uuid.jsonl | jq '.'
```

## Core Message Schema

### Base Fields (Present in All Messages)

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | string | Message type identifier | Yes |
| `uuid` | string (UUID) | Unique identifier for this message | Yes |
| `timestamp` | string (ISO 8601) | When the message was created | Yes |
| `sessionId` | string (UUID) | Session identifier (matches filename) | Yes |
| `parentUuid` | string (UUID) or null | Reference to parent message | Yes |
| `logicalParentUuid` | string (UUID) or null | Logical parent for compact operations | No |
| `subtype` | string or null | Message subtype (e.g., "compact_boundary") | No |
| `isSidechain` | boolean | Whether this is a sidechain conversation | Yes |
| `userType` | string | User type (typically "external") | Yes |
| `cwd` | string | Current working directory | Yes |
| `version` | string | Claude Code version (e.g., "1.0.93") | Yes |
| `gitBranch` | string | Current git branch name | No |

## Message Types

### 1. System Message

System-generated messages including compact operations.

```json
{
  "type": "system",
  "subtype": "compact_boundary",
  "parentUuid": null,
  "logicalParentUuid": "86b9169b-fe6c-4196-9d48-c05558081be3",
  "content": "Conversation compacted",
  "compactMetadata": {
    "trigger": "auto",
    "preTokens": 155159
  },
  "timestamp": "2025-09-19T02:03:02.806Z",
  "uuid": "eb965ed5-3b2a-48d9-8a45-488abab515e9",
  "sessionId": "28474888-f812-4513-b341-712070fb65d2"
}
```

**Compact Boundary Messages:**
- Mark conversation compaction points
- Create new DAG roots (`parentUuid: null`)
- Link to previous segment via `logicalParentUuid`
- Include metadata about trigger and token count
- See [compact-operations.md](compact-operations.md) for details

### 2. Summary Message

Appears at the beginning of continuation conversations OR as completion markers.

```json
{
  "type": "summary",
  "summary": "Brief description of the conversation",
  "leafUuid": "uuid-of-last-message-in-previous-conversation"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Brief conversation summary |
| `leafUuid` | string (UUID) | Reference to conversation endpoint |

**Important**: Summary messages can indicate:
- Continuation from previous conversation (common in multi-file chains)
- Project completion marker (e.g., "GitHub Deployment Complete")
- Can be the only content in a file (as small as 122 bytes)

### 2. User Message

Represents user input or tool results.

```json
{
  "type": "user",
  "parentUuid": "parent-message-uuid",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/working/directory",
  "sessionId": "session-uuid",
  "version": "1.0.93",
  "gitBranch": "main",
  "timestamp": "2025-08-26T23:08:35.100Z",
  "uuid": "unique-message-uuid",
  "message": {
    "role": "user",
    "content": "user input text or content array"
  }
}
```

#### User Message Content Types

Content can be:
1. **Simple text** (human input): `"content": "text string"`
2. **Array of content blocks** (often system-generated):
```json
"content": [
  {
    "type": "text",
    "text": "user input"
  },
  {
    "type": "tool_result",
    "tool_use_id": "tool-id",
    "content": "tool output or array"
  }
]
```

#### Additional User Message Fields

| Field | Type | Description |
|-------|------|-------------|
| `isCompactSummary` | boolean | Indicates a compact summary message |
| `customInstructions` | boolean | Whether custom instructions were used |
| `images` | array | Image attachments |
| `attachments` | array | File attachments |
| `toolUseResult` | object | Tool execution result data |

### 3. Assistant Message

Claude's responses including text and tool usage.

```json
{
  "type": "assistant",
  "parentUuid": "parent-uuid",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/working/directory",
  "sessionId": "session-uuid",
  "version": "1.0.93",
  "gitBranch": "main",
  "timestamp": "2025-08-26T23:08:35.100Z",
  "uuid": "unique-message-uuid",
  "requestId": "req_011CSX7f5huB6UfCd5fdiktq",
  "message": {
    "id": "msg_01XJbUUaAZQJ98KvdRok42oJ",
    "type": "message",
    "role": "assistant",
    "model": "claude-sonnet-4-20250514",
    "content": [...],
    "stop_reason": "stop_sequence or null",
    "stop_sequence": null,
    "usage": {...}
  }
}
```

#### Assistant Content Block Types

1. **Text Block** (visible to user):
```json
{
  "type": "text",
  "text": "Response text"
}
```

2. **Tool Use Block**:
```json
{
  "type": "tool_use",
  "id": "toolu_01ABC...",
  "name": "Bash",
  "input": {
    "command": "ls -la",
    "description": "List directory contents"
  }
}
```

3. **Thinking Block** (hidden from user):
```json
{
  "type": "thinking",
  "thinking": "Internal reasoning and planning content",
  "signature": "cryptographic_signature_string"
}
```

#### Usage Statistics

```json
"usage": {
  "input_tokens": 4,
  "output_tokens": 301,
  "cache_creation_input_tokens": 16653,
  "cache_read_input_tokens": 0,
  "cache_creation": {
    "ephemeral_5m_input_tokens": 16653,
    "ephemeral_1h_input_tokens": 0
  },
  "service_tier": "standard"
}
```

## Tool-Related Schemas

### Tool Use (in Assistant Messages)

```json
{
  "type": "tool_use",
  "id": "toolu_unique_id",
  "name": "ToolName",
  "input": {
    // Tool-specific parameters
  }
}
```

### Tool Result (in User Messages)

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_unique_id",
  "content": "result text or content array",
  "is_error": false
}
```

**Important**: Tool results appear as "user" messages but are system-generated, not human input. They represent the system's response to tool invocations.

### Common Tools

| Tool Name | Purpose | Common Input Fields |
|-----------|---------|-------------------|
| `Bash` | Execute shell commands | `command`, `description`, `timeout`, `run_in_background` |
| `Read` | Read file contents | `file_path`, `limit`, `offset` |
| `Write` | Write file contents | `file_path`, `content` |
| `Edit` | Edit file contents | `file_path`, `old_string`, `new_string`, `replace_all` |
| `MultiEdit` | Multiple edits | `file_path`, `edits` array |
| `Grep` | Search in files | `pattern`, `path`, `glob`, `output_mode` |
| `Glob` | Find files by pattern | `pattern`, `path` |
| `LS` | List directory | `path`, `ignore` |
| `TodoWrite` | Manage todo list | `todos` array |
| `WebSearch` | Search the web | `query`, `allowed_domains`, `blocked_domains` |
| `WebFetch` | Fetch web content | `url`, `prompt` |
| `Task` | Launch sub-agent | `description`, `prompt`, `subagent_type` |
| `NotebookEdit` | Edit Jupyter notebooks | `notebook_path`, `new_source`, `cell_id`, `cell_type` |
| `BashOutput` | Get background shell output | `bash_id`, `filter` |
| `KillBash` | Terminate background shell | `shell_id` |
| `ExitPlanMode` | Exit planning mode | `plan` |

#### Task Tool Subagent Types

Known `subagent_type` values:
- `architecture-reviewer`: Analyzes code architecture and identifies issues
- `synthesis-master`: Creates comprehensive implementation plans
- `zen-code-architect`: Implements code with "ruthless simplicity" philosophy
- `general-purpose`: Open-ended research and analysis tasks

## Special Fields and Patterns

### Sidechain Conversations

Sidechain messages have `"isSidechain": true` and represent parallel processing threads, typically for sub-agents or complex tasks.

**Key Characteristics**:
- Often have `parentUuid: null` despite being sidechains (fresh thread)
- Share same `sessionId` as main conversation
- Commonly triggered by Task tool invocations
- Usage varies significantly by project complexity (from none to extensive use)
- Results integrate back into main conversation thread

### Continuation Chains

When a conversation continues from a previous session:
1. First message is type `"summary"` with `leafUuid`
2. `leafUuid` references the last meaningful message from the previous conversation
3. New messages continue with fresh UUIDs but maintain context

### Tool Result Embedding

Tool results can appear as:
1. Separate user messages with `tool_result` content blocks
2. Embedded in user messages with `toolUseResult` field
3. Arrays of content when multiple results exist

## Metadata and Context

### Session Context

Each message maintains:
- Working directory (`cwd`)
- Git branch information (`gitBranch`)
- Claude Code version (`version`)
- Timestamp for chronological ordering (`timestamp`)
- Platform information (stored in environment context)
- User type (`userType`)
- Session identifier (`sessionId`)

### Request Tracking

Assistant messages include:
- `requestId`: API request identifier
- `message.id`: Unique message ID from the API

### Performance Metrics

Token usage tracking includes:
- Input/output token counts
- Cache creation tokens
- Cache read tokens
- Service tier information

## File Lifecycle

### Creation Triggers

New JSONL files are created when:
1. Starting a new conversation session
2. Switching project contexts
3. Continuing from a previous conversation (with summary)
4. Branch changes or significant context shifts
5. User-initiated new conversation (even minutes after previous)

### File Naming

Files use UUID v4 format: `{uuid}.jsonl`
Example: `xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx.jsonl`

### Size Considerations

- No apparent size-based rollover
- Files can range from very small (hundreds of bytes) to very large (10+ MB)
- Conversations continue until natural completion
- Large files (>10MB) typically contain extensive subagent usage

## Related Files

### Todo Files (`~/.claude/todos/`)

Format: `{sessionId}-agent-{agentId}.json`

```json
[
  {
    "content": "Task description",
    "status": "pending|in_progress|completed",
    "id": "task-id",
    "activeForm": "Active task description"
  }
]
```

### Shell Snapshots (`~/.claude/shell-snapshots/`)

Shell environment captures for debugging and continuity.
Format: `snapshot-{shell}-{timestamp}-{id}.sh`

### IDE Lock Files (`~/.claude/ide/`)

Process lock files for IDE integration.
Format: `{process-id}.lock`

## Schema Version History

| Version | Changes |
|---------|---------|
| 1.0.90 | Initial schema version observed |
| 1.0.93 | Current version with full tool support |

## Notes for Implementers

1. **JSONL Parsing**: Each line must be parsed independently as valid JSON
2. **UUID Validation**: All UUID fields should validate as UUID v4
3. **Timestamp Handling**: All timestamps are ISO 8601 format with timezone
4. **Content Flexibility**: Message content can be string, array, or complex nested structures
5. **Null Handling**: Many fields can be null or absent, handle gracefully
6. **Tool Results**: Can appear in multiple formats, check both content arrays and toolUseResult fields
7. **Summary Messages**: Minimal structure, only contain type, summary, and leafUuid
8. **Branch Information**: May be empty string if not in a git repository
9. **MCP Integration**: Messages may include MCP server interactions (prefixed with `mcp__`)
10. **Hook Events**: System may include hook execution feedback in messages
11. **Environment Context**: System tracks platform, OS version, and working directories