# Claude Code Project Examples

This directory contains detailed analyses of real Claude Code projects, demonstrating the variety of conversation patterns, file structures, and development workflows found in `~/.claude/projects/`.

## Overview

Each example file provides an in-depth analysis of a specific project, including:
- File statistics and structure
- Conversation patterns and types
- Tool usage and special features
- Development workflow insights
- Implications for archival tools

## Example Files

### 1. [claude-code-archiver-project.md](claude-code-archiver-project.md) 
**Balanced Development with Continuations**
- 14 conversation files, 19.5MB total
- Shows continuation chains and UUID relationships
- Mix of regular and continuation conversations
- Active todo tracking throughout development
- Good example of typical mid-size project

### 2. [example-selfserve-project.md](example-selfserve-project.md)
**Complex Multi-Agent Architecture**
- 35 conversation files, ~75MB total
- Heavy subagent usage (38 Task invocations in single file)
- 46% of files contain sidechains
- Shows architecture-reviewer, synthesis-master, zen-code-architect subagents
- Best example for understanding parallel processing and complex workflows

### 3. [example-viber-project.md](example-viber-project.md)
**Clean, Simple Project Lifecycle**
- 5 conversation files, ~2.1MB total
- Shows project completion with 122-byte summary file
- Minimal complexity (1 sidechain, no subagents)
- Best example for understanding simple, successful projects

### 4. [example-recipe-tool-project.md](example-recipe-tool-project.md)
**Iterative Development with Continuations**
- 16 conversation files, ~16.3MB total
- 37.5% continuation rate (6 summary files)
- No sidechains despite complexity
- Shows burst development pattern over specific days
- Best example for understanding continuation chains

### 5. [example-semantic-workbench-project.md](example-semantic-workbench-project.md)
**Minimal Quick Fix Pattern**
- 2 conversation files, 72KB total
- Completed in 7 minutes
- Smallest project examined
- Best example for understanding quick, focused tasks

## Quick Comparison of Examples

| Project | Files | Size | Sidechains | Continuations | Subagents | Key Feature |
|---------|-------|------|------------|---------------|-----------|-------------|
| **Claude-Code-Archiver** | 14 | 19.5MB | Few | Multiple | Some | Balanced mid-size development |
| **SelfServe** | 35 | 75MB | 46% | Variable | 38+ Tasks | Complex multi-agent architecture |
| **VIBER** | 5 | 2.1MB | 20% | 40% | None | Clean completion with summary |
| **Recipe-Tool** | 16 | 16.3MB | 0% | 37.5% | None | Heavy continuation chains |
| **Semantic-Workbench** | 2 | 72KB | 0% | 50% | None | Minimal quick fix pattern |

## Project Classification Summary

| Type | Files | Size | Sidechains | Subagents | Example |
|------|-------|------|------------|-----------|---------|
| **A: Quick Fix** | 1-2 | <100KB | 0% | None | Semantic-Workbench |
| **B: Simple Development** | 3-5 | <5MB | 0-20% | None | VIBER |
| **C: Iterative Development** | 10-20 | 10-20MB | 0% | None | Recipe-Tool |
| **D: Complex Architecture** | 30+ | 50MB+ | 40%+ | Heavy | SelfServe |
| **E: SDK/Automation** | 40+ | Variable | 0% | None | Worktree Projects* |

*See [worktree-sdk-patterns.md](../worktree-sdk-patterns.md) for SDK/automation patterns

## Key Patterns Across All Examples

### File Size Distribution
- **Minimum**: 122 bytes (summary-only completion markers)
- **Maximum**: 15.6MB (complex multi-agent sessions)
- **Typical**: 100KB-2MB for standard development

### Sidechain Usage
- **Range**: 0% to 46% of files
- **Correlation**: Directly correlates with architectural complexity
- **Pattern**: Always share same `sessionId` as main conversation

### Continuation Patterns
- **Rate**: 0% to 50% of files
- **Trigger**: Context limit reached
- **Marker**: Summary message with `leafUuid` reference

### Subagent Types Found
- `architecture-reviewer`: Code architecture analysis
- `synthesis-master`: Implementation planning
- `zen-code-architect`: Code implementation
- `general-purpose`: Open-ended research

## Directory Structure in ~/.claude

All examples reference this common structure:
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
└── settings.json
```

## How to Use These Examples

1. **Pick any example** based on your interest - all have complete system views
2. **Review project types** to understand the classification system
3. **Study specific patterns** relevant to your use case
4. **Compare across projects** to see the full range of possibilities

## Common Elements Across Examples

### Message Types
- `summary`: Continuation or completion markers
- `user`: User input and tool results
- `assistant`: Claude responses and tool usage

### UUID Relationships
- `sessionId`: Identifies the conversation file
- `parentUuid`: Links messages in conversation flow
- `uuid`: Unique per message
- `leafUuid`: References previous conversation endpoint

### Tool Usage Patterns
- Standard: Read, Write, Edit, Bash, Grep, Glob
- Advanced: Task (subagents), TodoWrite, WebSearch
- SDK-specific: Structured builder patterns

## Implications for Archival Tools

Based on all examples, archival tools must handle:

1. **Size Range**: 122 bytes to 15.6MB per file
2. **File Count**: 1 to 48+ files per project
3. **Complexity**: Linear to multi-dimensional with sidechains
4. **Continuations**: Both summary types (continuation and completion)
5. **Retries**: Multiple attempts at same task (SDK pattern)
6. **Visualization**: Adaptive based on project type

## Additional Resources

- [Schema Documentation](../claude-jsonl-schema.md): Complete JSONL schema
- [Relationship Documentation](../claude-file-relationships.md): File relationships and patterns
- [Subagent Patterns](../subagent-and-sidechain-patterns.md): Deep dive into parallel processing
- [Worktree Patterns](../worktree-sdk-patterns.md): SDK and automation patterns

## Contributing

When adding new examples, please include:
1. Project overview section with key statistics
2. File structure and size distribution
3. Unique patterns or features
4. Comparison with other project types
5. Implications for archival tools