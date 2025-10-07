# Claude Code JSONL Documentation

## Overview

This repository contains comprehensive documentation of the Claude Code JSONL file format and conversation structure. The documentation is designed to support the development of archival and viewing tools for Claude Code conversation files stored in `~/.claude/projects/`.

## Purpose

Claude Code stores conversation history in JSONL (JSON Lines) format. Understanding this format enables:
- Analyzing development patterns and workflows
- Extracting insights from conversation history
- Preserving important development context

## Documentation Structure

### Core Documentation Files

#### 1. [claude-jsonl-schema.md](claude-jsonl-schema.md)
**Schema Reference**
- Complete message schema with all fields
- System messages and compact boundaries
- Tool schemas and content blocks
- Exploration commands for your data

#### 2. [claude-file-relationships.md](claude-file-relationships.md)
**Session Relationships**
- DAG structure (Directed Acyclic Graphs)
- Conversation types: regular, continuation, compacted, sidechain
- UUID relationships: parentUuid, leafUuid, logicalParentUuid
- Detection algorithms

#### 3. [compact-operations.md](compact-operations.md)
**Compact Operations**
- How compaction works (same-file context management)
- Compact boundary messages and logicalParentUuid
- Trigger conditions (~155k tokens or manual)
- Multiple compacts in single session

#### 4. [message-types.md](message-types.md)
**Message Classification**
- Distinguishing human vs system messages
- Tool orchestration patterns
- Display strategies for different message types

### Additional Documentation

#### 5. [subagent-and-sidechain-patterns.md](subagent-and-sidechain-patterns.md)
**Subagents and Sidechains**
- Task tool for parallel processing
- Sidechain detection and behavior
- Usage patterns

#### 6. [hook-patterns.md](hook-patterns.md)
**Hook System**
- Hook event types
- Message modification patterns
- Integration with tools

### Examples Directory

The [examples/](examples/) folder contains detailed analyses of specific conversation patterns from real projects. These examples illustrate the concepts described in the core documentation.

See [examples/README.md](examples/README.md) for navigation of example files.

## How to Use This Documentation

### For Developers

1. **Start with the schema**: Read `claude-jsonl-schema.md` to understand the data structure
2. **Understand relationships**: Review `claude-file-relationships.md` for how files connect
3. **Consider patterns**: Study the pattern files to understand usage variations
4. **Review examples**: Look at the examples folder for concrete instances

### For Understanding Your Own Data

Each documentation file includes bash commands and scripts to explore your own Claude Code data. Look for sections titled:
- "How to Explore Your Own System"
- "How to Inspect Your System"
- "Exploring Your Claude Code Data"

### Important Notes

1. **Pattern Observations**: The patterns documented here come from analysis of sample data. Your usage may differ significantly.

2. **SDK Patterns**: The `worktree-sdk-patterns.md` file documents patterns from a specific SDK implementation and should not be considered universal.

3. **Subagent Types**: References to specific subagent types (if any remain) are examples from particular implementations, not universal Claude Code features.

4. **Statistics**: Any statistics or percentages mentioned are from sample analysis and should not be considered definitive.

## Key Concepts

### JSONL Format
Each line in a `.jsonl` file is a complete JSON object representing a message or metadata entry.

### Message Types
- **user**: User input and tool results
- **assistant**: Claude's responses and tool invocations
- **summary**: Conversation continuations or completions

### UUID Relationships
- `sessionId`: Identifies the conversation file
- `uuid`: Unique message identifier
- `parentUuid`: Links messages in conversation flow
- `leafUuid`: References previous conversation endpoint

### Sidechains
Parallel conversation threads marked with `"isSidechain": true`, often used for complex task delegation.

### Continuations
New conversation files that continue from previous sessions, beginning with a summary message.

### MCP (Model Context Protocol)
Extensibility mechanism allowing integration with external services through standardized server connections. MCP tools are prefixed with `mcp__`.

### Hooks
User-configurable shell commands that execute in response to events, enabling workflow customization and automation.

## Development Considerations

When building tools to work with Claude Code conversations:

1. **Handle file size variance**: Files can range from ~100 bytes to 15+ MB
2. **Support multiple conversation types**: Linear, continued, with sidechains
3. **Preserve UUID relationships**: Critical for conversation threading
4. **Consider visualization needs**: Complex conversations need sophisticated display
5. **Respect privacy**: Sanitize sensitive information when archiving

## Contributing

If you discover additional patterns or schema elements in your Claude Code usage, consider documenting them following the style of existing files. Remember to:
- Focus on general patterns rather than specific implementations
- Include exploration commands for readers
- Avoid system-specific paths or details
- Note when patterns are from specific implementations

## License

This documentation is provided to support the Claude Code community in building useful tools and understanding the conversation format.