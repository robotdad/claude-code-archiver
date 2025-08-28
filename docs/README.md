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
**The JSONL Schema Reference**
- Complete schema documentation for all message types
- Field descriptions and data types
- Tool schemas and parameters
- File organization and naming conventions
- Instructions for exploring your own Claude Code data

#### 2. [claude-file-relationships.md](claude-file-relationships.md)
**Understanding File Relationships**
- Different conversation types (regular, continuation, sidechain, etc.)
- UUID relationship system and how messages connect
- File creation triggers and lifecycle
- Cross-directory relationships (projects, todos, shell-snapshots)
- Detection algorithms for different conversation patterns

### Pattern Analysis

#### 3. [message-structure-complexity.md](message-structure-complexity.md)
**Message Structure Complexity**
- Distinguishing conversational vs technical messages
- Tool orchestration and result handling
- System-injected content (reminders, hooks)
- Assistant thinking blocks (hidden reasoning)
- Content block types and metadata

#### 4. [git-usage-patterns.md](git-usage-patterns.md)
**Git Integration Patterns**
- Common git commands and workflows
- Commit message structure and conventions
- Branch management patterns
- Pull request creation with GitHub CLI
- Correlation between conversation activities and git operations

#### 5. [subagent-and-sidechain-patterns.md](subagent-and-sidechain-patterns.md)
**Parallel Processing and Task Delegation**
- Task tool and subagent system
- Sidechain conversation structure
- Usage patterns for complex workflows
- Performance observations
- Parallel conversation patterns

#### 6. [worktree-sdk-patterns.md](worktree-sdk-patterns.md)
**Automation and SDK Usage** *(Note: Patterns from specific implementation)*
- Git worktree integration patterns
- SDK-driven conversation characteristics
- Automated retry and iteration patterns
- Differences from manual usage
- **Important**: Contains observations from a specific SDK implementation

#### 7. [mcp-integration-patterns.md](mcp-integration-patterns.md)
**Model Context Protocol Integration**
- MCP server identification and naming conventions
- Tool selection priority (MCP vs built-in)
- Common MCP server types and capabilities
- Integration patterns with external services
- Security and performance considerations

#### 8. [hook-patterns.md](hook-patterns.md)
**Hook System and Event Handling**
- Hook event types and triggers
- Message modification patterns
- Blocking and validation hooks
- Integration with git, testing, and documentation
- Performance and security implications

#### 9. [consolidated-findings-update.md](consolidated-findings-update.md)
**Key Discoveries and Insights**
- Summary file dual purposes
- File size ranges and variations
- Sidechain usage patterns
- Development workflow observations

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