# Subagent and Sidechain Patterns in Claude Code

## Overview

This document describes the patterns and usage of subagents (via Task tool) and sidechain conversations in Claude Code based on analysis of conversation files. These features enable parallel processing and complex task delegation.

## Subagent System Architecture

### The Task Tool

The Task tool enables Claude to spawn specialized subagents for complex, focused work. These subagents run in parallel threads (sidechains) within the same conversation session.

```json
{
  "type": "tool_use",
  "name": "Task",
  "input": {
    "subagent_type": "agent-type-identifier",
    "description": "Brief task description",
    "prompt": "Detailed instructions for the subagent"
  }
}
```

### Subagent Type Parameter

The Task tool accepts a `subagent_type` parameter that determines the specialized behavior of the spawned agent. The specific types available depend on:
- Claude Code version and configuration
- Project templates or frameworks in use
- Custom configurations

**Example subagent types observed** (these are not universal):
- Architectural analysis agents
- Implementation planning agents
- Code generation agents
- General-purpose research agents

**Note**: The actual subagent types available in your system will depend on your specific setup and any templates you're using.

## Sidechain Conversation Structure

### Sidechain Message Characteristics

```json
{
  "parentUuid": null,  // Often null even in sidechains
  "isSidechain": true,  // Key identifier
  "userType": "external",
  "cwd": "/working/directory",
  "sessionId": "same-as-main-conversation",  // Critical: same session
  "version": "1.0.86",
  "gitBranch": "main",
  "type": "user",
  "message": {
    "role": "user",
    "content": "[subagent prompt content]"
  },
  "uuid": "unique-sidechain-message-id",
  "timestamp": "2025-08-21T00:46:17.230Z"
}
```

### Key Sidechain Properties

1. **Same SessionId**: Sidechains share the main conversation's sessionId
2. **Independent Threading**: parentUuid often null, creating fresh thread
3. **Parallel Execution**: Multiple sidechains can run concurrently
4. **Result Integration**: Results merged back into main conversation

## Usage Patterns

### Heavy Sidechain Usage

**Observed in complex projects**:
- Multiple conversation files with sidechains
- Large conversation files with numerous Task invocations
- Complex multi-step workflows

**Typical Workflow**:
1. User requests complex feature
2. Main thread spawns specialized subagent
3. Subagent works in sidechain
4. Results return to main thread
5. Additional subagents may be spawned
6. All results consolidated in main conversation

### Minimal or No Sidechain Usage

**Observed in simpler projects**:
- Linear conversation flow
- Direct tool usage without Task delegation
- Single-threaded execution

This suggests sidechains are primarily used for complex, multi-faceted tasks rather than routine development.

## Subagent Invocation Structure

### Task Tool Input Format

```json
{
  "subagent_type": "type-identifier",
  "description": "Brief task description",
  "prompt": "Detailed instructions for the subagent"
}
```

### Common Prompt Patterns

**Analysis Tasks**:
- Current state description
- Specific problems to investigate
- Files or areas to examine
- Expected output format

**Planning Tasks**:
- Context from previous analysis
- Goals to achieve
- Constraints to consider
- Deliverable structure

**Implementation Tasks**:
- Specific changes to make
- Files to modify
- Testing requirements
- Success criteria

## Sidechain vs Main Thread Patterns

### Main Thread Responsibilities
- User interaction
- High-level orchestration
- Result integration
- Decision making
- Context maintenance

### Sidechain Responsibilities
- Focused analysis
- Deep implementation
- Parallel research
- Specialized tasks
- Independent problem-solving

## Performance and Scalability

### Performance Observations

**In complex conversation files**:
- File sizes can grow very large (10+ MB)
- Many Task invocations possible in a single conversation
- Multiple concurrent sidechains supported
- System handles parallel processing effectively

This demonstrates Claude Code's capability to manage complex, multi-threaded conversations with extensive tool usage.

## Sidechain Detection and Visualization

### Detection Algorithm

```python
def identify_sidechains(messages):
    sidechains = []
    main_thread = []
    
    for message in messages:
        if message.get("isSidechain", False):
            sidechains.append(message)
        else:
            main_thread.append(message)
    
    return {
        "main": main_thread,
        "sidechains": group_by_task(sidechains)
    }
```

### Visualization Ideas

For proper sidechain display:
1. **Parallel Tracks**: Show sidechains as parallel swim lanes
2. **Task Grouping**: Group sidechain messages by task
3. **Result Integration**: Show where results merge to main thread
4. **Time Alignment**: Align sidechains temporally with main thread
5. **Agent Type Labels**: Clearly mark subagent types

## Use Case Patterns

### Pattern 1: Sequential Analysis
```
Main → Architecture Review → Synthesis → Implementation
```
Each stage completes before next begins.

### Pattern 2: Parallel Research
```
Main → [Research A | Research B | Research C] → Consolidation
```
Multiple subagents work simultaneously.

### Pattern 3: Iterative Refinement
```
Main → Analysis → Implementation → Testing → Analysis → Fix
```
Cyclic pattern with multiple subagent invocations.

### Pattern 4: Hierarchical Delegation
```
Main → Master Agent → [Sub-agent 1 | Sub-agent 2] → Master → Main
```
Subagents can spawn other subagents.

## Evolution and Trends

### Version Correlation
- Earlier versions (1.0.86): Subagents present
- Current versions (1.0.93): Continued support
- Pattern: Consistent subagent availability

### Usage Growth
- Complex projects increasingly use subagents
- Simple projects remain linear
- Bifurcation: Projects either use heavily or not at all

## Conclusion

Subagents and sidechains represent Claude Code's advanced capability for handling complex, multi-faceted development tasks. They enable:

1. **Parallel Processing**: Multiple analyses simultaneously
2. **Specialized Expertise**: Different agents for different tasks
3. **Scalable Architecture**: Handle complex projects efficiently
4. **Clean Separation**: Focused work in isolated contexts

For archival tools, proper handling of sidechains and subagent invocations is crucial for complex projects, while simpler projects can be displayed with traditional linear conversation views.