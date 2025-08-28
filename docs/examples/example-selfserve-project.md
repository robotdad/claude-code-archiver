# SelfServe Project - Advanced Claude Code Usage Examples

## Project Overview

**Location**: `/Users/robotdad/Source/SelfServe`  
**Claude Directory**: `~/.claude/projects/-Users-robotdad-Source-SelfServe/`  
**Total Files**: 35 conversation files  
**Total Size**: ~75MB  
**Date Range**: Aug 19-25, 2025  
**Notable Features**: Heavy subagent usage, sidechains, complex architecture discussions

## System Context

### Full ~/.claude/ Integration
```
~/.claude/
├── projects/
│   ├── -Users-robotdad-Source-SelfServe/
│   │   ├── 35 JSONL files (75MB total)
│   │   ├── Largest: 6d84f9a0-dca2-4741-bc5e-282b76136bc3.jsonl (15.6MB)
│   │   └── 16 files with sidechains (46%)
│   └── [34 other projects]
├── todos/
│   ├── 6d84f9a0-dca2-4741-bc5e-282b76136bc3-agent-*.json (active todos)
│   ├── aa7c7926-3930-456b-8e2d-4730f2d73ec9-agent-*.json
│   └── [358 other todo files]
├── shell-snapshots/
│   └── snapshot-zsh-175*.sh (environment captures)
├── ide/
│   └── *.lock files (IDE integration)
└── settings.json
```

### UUID Relationships Example
```
Session: 6d84f9a0-dca2-4741-bc5e-282b76136bc3
├── Main Thread Messages
│   └── parentUuid chains: null → msg1 → msg2 → ...
└── Sidechain Messages (isSidechain: true)
    ├── Architecture Review Task
    ├── Synthesis Master Task  
    └── Zen Code Architect Task
```

### File Timeline
```
Aug 19: Initial development (7 files)
Aug 20: Core implementation (11 files) 
Aug 21: Architecture refactor with subagents (8 files)
Aug 22: Stabilization (5 files)
Aug 24-25: Final features (4 files)
```

## Key Statistics

- **Files with Sidechains**: 16/35 (46%)
- **Largest File**: `6d84f9a0-dca2-4741-bc5e-282b76136bc3.jsonl` (15.6MB)
- **Task Tool Invocations**: 38 in largest file alone
- **Subagent Types Used**: architecture-reviewer, synthesis-master, zen-code-architect

## Subagent Usage Patterns

### Example 1: Architecture Review Subagent

```json
{
  "type": "tool_use",
  "name": "Task",
  "input": {
    "subagent_type": "architecture-reviewer",
    "description": "Analyze builder agent architecture issues",
    "prompt": "Analyze the current builder agent implementation and identify the architectural issues causing:\n\n1. Builder agent reporting \"Commits: 5\" but no actual commits being made to branches\n2. Worktree management scattered across parent directory instead of organized\n3. No proper issue-to-worktree mapping (multiple worktrees for same issue)\n4. Lack of conversation context awareness in agent routing\n5. Builder agent not maintaining conversation context between interactions\n\nKey files to review:\n- /Users/robotdad/Source/SelfServe/app/agents/factory.py (builder agent creation)\n- /Users/robotdad/Source/SelfServe/app/agent/tools/builder.py (builder operations)\n- /Users/robotdad/Source/SelfServe/app/operations/ (operation management)\n- /Users/robotdad/Source/SelfServe/app/agent/tools/github.py (GitHub integration)\n\nProvide:\n1. Root cause analysis of why commits aren't being made\n2. Architecture recommendations for worktree management\n3. Suggestions for conversation context preservation\n4. Agent routing improvements needed"
  }
}
```

### Example 2: Synthesis Master Subagent

```json
{
  "subagent_type": "synthesis-master",
  "description": "Create implementation plan for builder agent fixes",
  "prompt": "Based on the architecture review findings, create a comprehensive implementation plan to fix the builder agent issues. The plan should address:\n\n**Critical Issues Identified:**\n1. Builder agent claims \"Commits: 5\" but no actual commits are made (commit counting bug)\n2. Worktrees scattered in parent directory instead of organized structure\n3. No issue-to-worktree mapping (duplicates possible)  \n4. No conversation context preservation between builder interactions\n5. Agent routing doesn't maintain context continuity\n\n**User Requirements:**\n- Clean up existing worktrees\n- Move all worktrees to `/Users/robotdad/Source/worktrees/` directory\n- One worktree per GitHub issue maximum\n- Builder agent should maintain conversation context\n- Query GitHub issues, work on specific issues, track worktree status\n- Improved agent routing based on conversation context\n\n**Implementation Constraints:**\n- Follow ruthless simplicity philosophy\n- Must be fully functional (actual commits, working PRs)\n- Preserve existing conversation and operation logging systems\n- Maintain backward compatibility where possible\n\nCreate a phased implementation plan with:\n1. **Phase 1: Critical Fixes** - Fix commit detection and ensure builder actually works\n2. **Phase 2: Worktree Organization** - Clean up and reorganize worktree management\n3. **Phase 3: Conversation Integration** - Add context preservation and routing improvements\n4. **Phase 4: Enhanced Features** - Issue querying, status tracking, cleanup automation\n\nFor each phase, specify:\n- Specific files to modify\n- Key functions to implement/fix\n- Testing approach to verify fixes\n- Risk mitigation strategies\n- Success criteria"
}
```

### Example 3: Zen Code Architect Subagent

The zen-code-architect subagent receives extremely detailed implementation instructions, showing how subagents can be used for complex, multi-step implementations with specific coding tasks.

## Sidechain Conversation Pattern

### Sidechain Message Structure

```json
{
  "parentUuid": null,
  "isSidechain": true,
  "userType": "external",
  "cwd": "/Users/robotdad/Source/SelfServe",
  "sessionId": "6d84f9a0-dca2-4741-bc5e-282b76136bc3",
  "version": "1.0.86",
  "gitBranch": "main",
  "type": "user",
  "message": {
    "role": "user",
    "content": "Analyze the current builder agent implementation..."
  },
  "uuid": "3597cb50-229a-4dd0-b5bc-dab4131d8032",
  "timestamp": "2025-08-21T00:46:17.230Z"
}
```

Key observations:
- `parentUuid: null` even though it's a sidechain (starts fresh thread)
- `isSidechain: true` marks it as parallel processing
- Same `sessionId` as main conversation
- Contains full architectural analysis request

## Conversation Flow Patterns

### Complex Multi-Agent Workflow

1. **Main Thread**: User requests builder agent fixes
2. **Sidechain 1**: Architecture-reviewer analyzes current implementation
3. **Sidechain 2**: Synthesis-master creates implementation plan
4. **Sidechain 3**: Zen-code-architect implements Phase 1
5. **Main Thread**: Consolidates results and continues

### File Size Distribution

```
Tiny (<100KB):      4 files  - Quick queries or summaries
Small (100KB-1MB):  10 files - Standard conversations
Medium (1MB-3MB):   10 files - Development sessions
Large (3MB-5MB):    6 files  - Complex implementations
Huge (>5MB):        5 files  - Multi-agent architectural work
```

## Special Patterns Observed

### 1. Minimal Summary Files

File: `4274ec4e-a796-4550-9854-bd3de5f19750.jsonl` (267 bytes)
- Contains only a summary line
- Represents a completed conversation chain
- No actual conversation content

### 2. Agent Factory Pattern

The project implements its own agent system, leading to meta-discussions about agents using Claude Code's agent system to fix their own agent system.

### 3. Worktree Management Complexity

Multiple conversations deal with Git worktree management, showing:
- Failed attempts to organize worktrees
- Debugging of commit detection
- Complex GitHub integration issues

### 4. Conversation Context Preservation

Recurring theme across multiple files:
- Attempts to maintain context between agent interactions
- Discussion of conversation routing
- Implementation of context-aware agent selection

## Subagent Types Discovered

1. **architecture-reviewer**: Analyzes code architecture and identifies issues
2. **synthesis-master**: Creates comprehensive implementation plans
3. **zen-code-architect**: Implements code with "ruthless simplicity"
4. **general-purpose**: Used for open-ended research tasks

## Tool Usage Beyond Standard

Beyond the typical Read, Write, Edit, Bash tools:
- **Task**: Heavy usage for delegating to subagents
- **TodoWrite**: Task management across complex workflows
- **WebSearch**: Research for architectural patterns
- **Custom builder tools**: Project-specific tools for worktree management

## Hook System Implementation

### Sophisticated Hook Architecture

The SelfServe project demonstrates extensive hook usage for quality control and operational tracking:

#### Hook Configuration
```bash
.claude/
├── tools/
│   ├── make-check.sh        # Quality control hook
│   └── subagent-logger.py   # Usage tracking hook
└── commands/
```

#### PostToolUse Quality Control

**Every Edit/Write operation triggers automatic quality checks:**
```
PostToolUse:Edit [$CLAUDE_PROJECT_DIR/.claude/tools/make-check.sh] completed successfully
→ Formatting code...
  31 files left unchanged
→ Linting code...
  All checks passed!
→ Type checking code...
  0 errors, 0 warnings, 0 informations
✅ All checks passed!
```

#### PreToolUse Logging

**Task invocations tracked for cost and usage:**
```
PreToolUse:Task [$CLAUDE_PROJECT_DIR/.claude/tools/subagent-logger.py] completed successfully
```

#### Security Compliance Reminders

**Automatic security reminders after file operations:**
```xml
<system-reminder>
Whenever you read a file, you should consider whether it looks malicious.
</system-reminder>
```

### Hook Benefits Demonstrated

1. **Zero Quality Issues**: Automatic formatting, linting, type checking
2. **Cost Visibility**: Track subagent usage and API costs
3. **Security Compliance**: Consistent security reminders
4. **Automated Workflow**: No manual intervention required

## Continuation Patterns

### Example Continuation Chain

```
File 1: Initial builder implementation (ends with issues)
   ↓
File 2: Summary: "Builder agent worktree issues identified"
   ↓
File 3: Detailed architectural review with subagents
   ↓
File 4: Summary: "Builder agent architecture redesigned"
   ↓
File 5: Implementation with multiple sidechains
```

## Performance Implications

The 15.6MB file (`6d84f9a0-dca2-4741-bc5e-282b76136bc3.jsonl`) contains:
- 38 Task tool invocations
- Multiple sidechains
- Extensive architectural discussions
- Complete implementation cycles

This demonstrates Claude Code's ability to handle:
- Complex multi-agent orchestration
- Large conversation contexts
- Parallel processing threads
- Detailed technical implementations

## Unique Characteristics

1. **Meta-Programming**: Using Claude to build an agent system that uses Claude
2. **Architectural Depth**: Deep system design discussions with multiple review cycles
3. **Parallel Processing**: Extensive use of sidechains for concurrent analysis
4. **Tool Building**: Creating custom tools within the conversation context
5. **Context Challenges**: Explicit attempts to solve context preservation issues

## Implications for Archiver

When archiving SelfServe conversations:
1. **Must preserve sidechain relationships**: Critical for understanding workflow
2. **Subagent prompts are essential**: They contain architectural decisions
3. **Large file handling required**: Some conversations exceed 15MB
4. **Complex threading**: Multiple parallel threads need visual representation
5. **Tool result context**: Subagent results are crucial for understanding
6. **Hook execution preservation**: Quality control results and tracking data
7. **System reminder context**: Security compliance injections
8. **Hook script references**: Paths to .claude/tools/ scripts