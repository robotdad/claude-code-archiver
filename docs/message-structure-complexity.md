# Message Structure Complexity and Display Considerations

## Overview

Claude Code JSONL files contain a complex mix of conversational and technical messages. Understanding this structure is crucial for building effective viewers that can present conversations clearly while preserving technical context when needed.

## Message Categories

### 1. Pure Conversational Messages

**Human Input Messages**
- User-initiated requests or responses
- Contains actual human-typed content
- Should always be displayed in conversation views

**Assistant Explanatory Messages**
- Claude's responses with explanations
- Planning statements before tool use
- Synthesis after tool results
- Primary display content

### 2. Tool Orchestration Messages

**Assistant Tool Use Messages**
```json
{
  "type": "assistant",
  "message": {
    "content": [
      {
        "type": "text",
        "text": "Let me check that for you:"
      },
      {
        "type": "tool_use",
        "id": "toolu_01ABC...",
        "name": "Read",
        "input": {"file_path": "/path/to/file"}
      }
    ]
  }
}
```

**Key Characteristics:**
- Can contain both text and tool_use blocks
- Text provides context for tool usage
- Multiple tools can be called in parallel
- Tool IDs link to subsequent results

### 3. Technical Infrastructure Messages

**Pure Tool Result Messages**
```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_01ABC...",
        "content": "Tool output here...",
        "is_error": false
      }
    ]
  }
}
```

These are NOT human input but system-generated responses to tool invocations.

## Message Content Complexity

### Multi-Block Content Arrays

Assistant messages can contain multiple content blocks:

```json
"content": [
  {"type": "text", "text": "Explanation"},
  {"type": "tool_use", "name": "Tool1", ...},
  {"type": "tool_use", "name": "Tool2", ...},
  {"type": "text", "text": "Additional context"}
]
```

### Enhanced Metadata

Tool results often include rich metadata:

```json
{
  "toolUseResult": {
    "file": {
      "filePath": "/absolute/path",
      "content": "file contents",
      "numLines": 239,
      "startLine": 1,
      "totalLines": 239
    },
    "stdout": "output",
    "stderr": "",
    "interrupted": false,
    "isImage": false
  }
}
```

## System-Injected Content

### System Reminders

Automatically added to tool results:
```
<system-reminder>
Security or compliance reminder text
</system-reminder>
```

### Hook Feedback

Hook execution results embedded in messages:
```
PostToolUse:Edit [hook script] completed successfully
[Hook output...]
```

### Continuation Summaries

Special messages for context management:
```json
{
  "isCompactSummary": true,
  "message": {
    "content": "This session is being continued from..."
  }
}
```

## Message Flow Patterns

### Standard Tool Usage Flow

```
1. Human Request
   ↓
2. Assistant Planning (text + tool_use)
   ↓
3. Tool Result (system-generated user message)
   ↓
4. Assistant Synthesis (text response)
```

### Parallel Tool Execution

```
Assistant Message:
├── Text: "Checking multiple things..."
├── Tool Use 1: Read file A
├── Tool Use 2: Run command B
└── Tool Use 3: Search pattern C
   ↓
User Messages (system-generated):
├── Tool Result 1
├── Tool Result 2
└── Tool Result 3
   ↓
Assistant Message:
└── Text: "Based on the results..."
```

## Assistant Thinking Blocks

### Hidden Reasoning Content

Assistant messages can contain thinking blocks that capture internal reasoning:

```json
{
  "type": "thinking",
  "thinking": "[Internal reasoning and planning content]",
  "signature": "[Cryptographic signature]"
}
```

**Key Characteristics:**
- Not displayed to users in the interface
- Contains detailed internal reasoning and planning
- Includes cryptographic signature for integrity
- Found in assistant message content arrays
- Captures the assistant's problem-solving process

**Example thinking content:**
- Analysis of user requests
- Planning approaches to problems
- Reasoning through complex decisions
- Internal evaluation of options
- Meta-analysis of conversation context

## Identifying Message Types

### Human vs System-Generated User Messages

**Human Input:**
```json
{
  "type": "user",
  "message": {
    "content": "User typed this text"
  }
}
```

**System-Generated (Tool Result):**
```json
{
  "type": "user",
  "message": {
    "content": [
      {"type": "tool_result", ...}
    ]
  }
}
```

**Detection Algorithm:**
```python
def is_human_message(message):
    if message["type"] != "user":
        return False
    
    content = message["message"].get("content")
    if isinstance(content, str):
        return True  # Simple string = human input
    
    if isinstance(content, list):
        # Check if any block is NOT a tool_result
        for block in content:
            if block.get("type") != "tool_result":
                return True
    
    return False  # Pure tool results
```

## Message Statistics

Based on analysis of typical conversations:

| Message Type | Typical Percentage | Display Priority |
|--------------|-------------------|------------------|
| Human Input | 10-15% | Always show |
| Assistant Text | 20-30% | Always show |
| Tool Use | 25-35% | Summarize |
| Tool Results | 30-40% | Hide/Collapse |
| System Injected | 5-10% | Optional |

## Content Block Types in Assistant Messages

### Complete List of Block Types

1. **text**: Visible response to user
2. **tool_use**: Tool invocation with parameters
3. **thinking**: Hidden internal reasoning (not shown to users)

### Thinking Block Preservation

Thinking blocks contain valuable information about:
- How the assistant interpreted the request
- What approaches were considered
- Why certain decisions were made
- Internal problem-solving process

These blocks are preserved in JSONL but not shown in the Claude Code interface.

## Special Content Types

### System-Injected Tags

**System Reminders**: Added to tool results
```xml
<system-reminder>
Contextual guidance or compliance text
</system-reminder>
```

**Hook Output**: Embedded in messages
```
PostToolUse:Edit [script] completed successfully
[Output details...]
```

**Error Wrappers**: For tool failures
```xml
<tool_use_error>
Error description
</tool_use_error>
```

## Message Size Considerations

### Large Content Blocks

Tool results can be very large:
- File contents (thousands of lines)
- Command output (verbose logs)
- Search results (many matches)
- Error traces (full stack traces)

### Thinking Block Sizes

Thinking blocks can contain extensive reasoning:
- Multiple paragraphs of analysis
- Step-by-step problem solving
- Detailed planning sequences

## Complete Message Structure

### Assistant Message with All Block Types

```json
{
  "type": "assistant",
  "message": {
    "content": [
      {
        "type": "thinking",
        "thinking": "Internal reasoning...",
        "signature": "..."
      },
      {
        "type": "text",
        "text": "Visible response to user"
      },
      {
        "type": "tool_use",
        "id": "toolu_...",
        "name": "ToolName",
        "input": {...}
      }
    ]
  }
}
```

### User Message Variations

1. **Human input**: Simple string content
2. **Tool result**: Array with tool_result blocks
3. **Mixed**: Both human text and tool results (rare)

## Summary of Message Complexity

Claude Code JSONL files contain:

1. **Human conversations**: Actual user input and assistant explanations
2. **Hidden reasoning**: Thinking blocks with internal assistant reasoning
3. **Tool orchestration**: Complex chains of tool invocations and results
4. **System infrastructure**: Generated messages, reminders, and metadata

Key insights:
- Not all "user" messages are from humans (many are system-generated tool results)
- Assistant messages can contain hidden thinking blocks not shown to users
- Majority of messages (60-80%) are technical infrastructure
- Tool use creates complex ID-linked message chains
- System injects various content types (reminders, hooks, errors)