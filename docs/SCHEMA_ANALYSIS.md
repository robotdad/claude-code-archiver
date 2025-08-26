# Claude Code Message Schema Analysis

Based on analysis of:
- https://github.com/daaain/claude-code-log
- https://github.com/ljw1004/claude-log
- Real JSONL files from ~/.claude/projects/

## Schema Implementation

### 1. ConversationEntry Fields
- `isSidechain` (bool): Indicates if this is a sidechain/subagent conversation
- `userType` (string): Type of user (e.g., "external")
- `toolUseResult` (Any): Raw tool execution results in user messages

### 2. ContentBlock Fields
- `is_error` as `bool | None` (not always present)
- `id` field for tool use blocks
- `name` and `input` as alternative field names for tools

## Key Findings

### Message Structure
1. **Assistant messages** always have content as array of ContentBlock objects
2. **User messages** can have either:
   - String content (simple text)
   - Array of ContentBlock objects (when containing tool results)
3. **Tool results** in user messages appear both in:
   - `message.content` as formatted text for AI consumption
   - `toolUseResult` field with raw structured data

### Tool Schemas
Both reference projects implement detailed schemas for each tool:
- **File operations**: Read, Edit, MultiEdit, Write
- **Command execution**: Bash, WebSearch, Grep, Glob
- **Task management**: Task, ExitPlanMode, TodoWrite
- **Web operations**: WebFetch
- **File system**: LS
- **MCP tools**: mcp__ide__executeCode, mcp__ide__getDiagnostics

### Content Types
The implementation handles:
- `text`: Plain text content
- `tool_use`: Tool invocation by assistant
- `tool_result`: Tool execution results
- `thinking`: Claude's internal reasoning
- `image`: Base64 encoded images

### Entry Types
The implementation handles:
- `user`: User messages
- `assistant`: Assistant responses
- `system`: System messages and notifications
- `summary`: Conversation summaries for continuations

## Implementation Status

### Current Capabilities
✅ Parser handles all essential fields found in real data
✅ All tests pass

### Potential Future Enhancements
1. **Tool-specific result parsing**: Could add detailed schemas for each tool's result structure
2. **Hook events**: Could add support for PreToolUse, PostToolUse, Stop hooks if needed
3. **Token usage details**: Could extract more granular token usage (cache_read, cache_creation, etc.)

### What We Don't Need
- **Detailed tool schemas**: For archiving/viewing, we don't need to validate tool inputs/outputs
- **Hook event handling**: These are runtime events, not typically in JSONL exports
- **MCP-specific handling**: Our generic approach works fine for MCP tools

## Viewer Design

### Conversation Readability
The viewer prioritizes readable conversations through:

1. **Tool Grouping**: Tool interactions (assistant tool_use → user tool_result) are grouped together and collapsed by default
   - Displays as `[TOOLS: 3] Read, Edit, Bash...` with click-to-expand
   - Tool-only messages don't interrupt conversation flow

2. **Message Filtering**: 
   - User messages containing only tool results are excluded from main flow
   - Assistant messages with both text and tools are split:
     - Text content displays as normal message
     - Tool calls appear in collapsible group below

3. **View Modes**:
   - **Focused mode** (default): Tool groups collapsed for clean reading
   - **Detailed mode**: Tool groups expanded for full visibility

### Visual Design
- Tool groups with distinct dark backgrounds and rounded corners
- Smooth expand/collapse animations with rotation indicators
- Clear visual hierarchy between conversation and tools
- Hover effects on interactive elements
- Terminal-style aesthetic matching Claude Code's CLI nature

## Summary

The implementation provides:
- **Complete schema coverage**: All essential fields from real Claude Code conversations
- **Intelligent viewer**: Clean conversation flow with on-demand tool details  
- **Backwards compatibility**: Works with existing and future JSONL exports
- **User-focused design**: Prioritizes readability while preserving full data access

The combination of comprehensive parsing and intelligent rendering creates an effective viewing experience for Claude Code conversation archives.