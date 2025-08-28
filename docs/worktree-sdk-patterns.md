# Worktree and Claude Code SDK Patterns

## Overview

This document describes patterns observed when Claude Code is used with git worktrees and SDK automation. These patterns show how automated workflows can structure development tasks.

**IMPORTANT DISCLAIMER**: The patterns documented here come from analysis of conversations using a specific SDK implementation/wrapper. Different SDK implementations, automation tools, or usage patterns will likely produce different results. These observations should be considered as examples rather than universal patterns.

## How to Find SDK Patterns in Your System

```bash
# Look for worktree-related projects
ls -d ~/.claude/projects/*worktree* 2>/dev/null
# Look for projects with common worktree prefixes (varies by implementation)
ls ~/.claude/projects/ | grep -E "(worktree|issue-|feature-)" 2>/dev/null

# Check for structured prompts
grep -h "Working in git worktree" ~/.claude/projects/*/*.jsonl 2>/dev/null | head -5

# Find SDK-related references
grep -h "claude_code_sdk" ~/.claude/projects/*/*.jsonl 2>/dev/null | wc -l

# Count conversations per issue (if using issue-based naming)
for dir in ~/.claude/projects/*issue*; do
  if [ -d "$dir" ]; then
    count=$(ls "$dir"/*.jsonl 2>/dev/null | wc -l)
    echo "$(basename "$dir"): $count attempts"
  fi
done
```

## Observed Patterns

### File Count Variance

Automated workflows may show:
- Wide variance in conversation file counts per task
- Multiple attempts for complex implementations
- Iterations spanning multiple sessions

### Key Observation

High conversation counts for single tasks suggest:
- Iterative development approaches
- Automated retry mechanisms
- Complex implementation challenges

## SDK Usage Patterns

**Note**: These patterns come from specific SDK implementations and are not universal.

### 1. Structured Initial Prompts

SDK implementations may use templated prompts like:

```
Working in git worktree: [worktree_path]

Goal: [specific_implementation_goal]

[Additional instructions for implementation]
```

Prompt structures vary by SDK implementation.

### 2. Worktree Path Convention

Observed implementations may use various naming patterns:
- Issue-based: `issue-{number}-{description}`
- Feature-based: `feature-{name}`
- Custom prefixes based on project needs

Worktree locations vary:
- Sibling directory to main repository
- Centralized workspace location
- Project-specific organization

This is implementation-specific; there is no universal convention.

### 3. Git Branch Naming

Branch naming in automated workflows often follows patterns like:
- Issue tracking: `issue-{number}-{description}`
- Feature naming: `feature/{name}`
- Custom conventions per project

The relationship between worktree names and branch names is implementation-specific.

## Metadata Patterns

### 1. Working Directory Consistency

In SDK-driven conversations, the `cwd` field reflects the working directory:
```json
{
  "cwd": "[current_working_directory]",
  "gitBranch": "[current_branch_name]"
}
```

### 2. Goal Types Observed

Automated workflows may include goals such as:
- **Dependency Management**: Installing or updating project dependencies
- **Feature Implementation**: Adding new functionality to applications
- **UI Development**: Creating or modifying user interface components
- **Testing Scenarios**: Including failure cases for CI/CD validation

### 3. Version Information

Consistent version numbers across worktree projects suggest:
- Automated usage during specific time periods
- SDK integration maintaining version consistency

## Patterns in Automated Development

### 1. Multiple Attempts per Issue

Automated workflows may create multiple conversation files for the same task:
- Same issue with multiple conversation attempts
- Variations in goal wording or approach
- Retry patterns for complex implementations

### 2. Testing Patterns

Automated workflows may include:
- Test-specific tasks
- Deliberate failure testing for CI/CD validation
- Edge case and integration testing

These patterns indicate systematic testing approaches in automated development.

### 3. No Sidechains or Subagents

Worktree projects show:
- **0% sidechain usage** (checked multiple projects)
- **No Task tool invocations**
- **Pure linear development**

This contrasts with patterns seen in complex architectural projects.

## SDK Integration Patterns

### Common SDK Features

SDK implementations may include:
- Custom error handling and error types
- Builder or workflow management patterns
- Progress tracking mechanisms
- Integration with version control systems

### Structured Workflows

Automated systems often implement:
- Templated prompt generation
- Systematic retry mechanisms
- Progress monitoring
- Error recovery strategies

## Differences from Manual Usage

**Observed differences** (specific to analyzed implementation):

- **Initiation**: Automated vs user-driven
- **Prompt structure**: Templated vs variable
- **Retry patterns**: Multiple attempts common in automation
- **Sidechain usage**: May differ between manual and automated
- **Branch management**: Systematic in automation
- **Working directory**: Isolated worktrees vs project roots
- **Task definition**: Specific goals vs open-ended requests

## Observed Characteristics

### Pattern Summary

In the analyzed sample:
- Multiple conversation files per issue were common
- Linear conversation flow (no sidechains observed)
- Consistent version numbers suggesting automated usage
- Mix of feature implementation and testing tasks

**Note**: These observations are from a specific implementation and should not be considered universal patterns for all SDK usage.

## Key Observations

### Implementation-Specific Patterns

The analyzed implementation showed:
1. Structured, templated workflows
2. Worktree isolation for each task
3. Multiple retry attempts for complex issues
4. Linear conversation flow without sidechains
5. Explicit testing workflows

### Potentially General Patterns

Patterns that may apply more broadly:
1. **Iteration**: Automated systems may retry tasks multiple times
2. **Isolation**: Worktrees provide clean environments
3. **Automation characteristics**: Less interactive than manual usage
4. **Systematic approaches**: Consistent patterns within implementations

## Summary

Worktree and SDK patterns demonstrate how Claude Code can be integrated into automated development workflows. Key considerations:

- **Different paradigms**: Manual interactive use vs automated workflows
- **Structured patterns**: Automation often uses templates and conventions
- **Iteration patterns**: Automated systems may retry tasks
- **Isolation benefits**: Worktrees provide clean, isolated environments

**Important**: The patterns described here are from a specific implementation. Your experience with Claude Code SDK or automation tools may differ significantly.