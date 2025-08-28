# Viewer UI Improvements Analysis

## Overview

The current viewer does a good job of basic conversation display, but with the improved parsing capabilities we've identified, there are significant opportunities to enhance the user experience. This document analyzes how manifest.json changes will affect the viewer and proposes UI improvements.

## Manifest.json Enhancements Required

### 1. Sidechain Relationship Tracking

**Current State**: No sidechain information in manifest

**Proposed Addition**:
```json
"sidechains": {
  "parent-session-id": [
    {
      "session_id": "sidechain-session-id",
      "trigger_message_uuid": "uuid-of-task-invocation",
      "subagent_type": "general-purpose",
      "task_description": "Research X and Y"
    }
  ]
},
"conversation_metadata": {
  "session-id": {
    "is_sidechain": true,
    "parent_session": "parent-id",
    "subagent_type": "general-purpose"
  }
}
```

### 2. Enhanced Message Statistics

**Current State**: Basic counts (user, assistant, system, summary)

**Proposed Enhancement**:
```json
"statistics": {
  "messages": {
    "human_input": 15,        // Actual human messages
    "assistant_response": 20,  // Assistant text responses
    "tool_results": 45,        // System-generated tool results
    "thinking_blocks": 8,      // Assistant thinking blocks
    "summary": 1
  },
  "tools": {
    "Bash": 12,
    "Read": 8,
    "Task": 3,                // Subagent invocations
    "mcp__browser-use__browser_navigate": 5  // MCP tools
  },
  "subagents": {
    "general-purpose": 2,
    "architecture-reviewer": 1
  }
}
```

### 3. Todo Integration

**Current State**: Todos collected but not displayed

**Proposed Enhancement**:
```json
"todos": {
  "session-id": {
    "file": "todos/session-id.json",
    "total_count": 8,
    "status_counts": {
      "completed": 5,
      "in_progress": 1,
      "pending": 2
    },
    "items": [  // Optionally embed for viewer
      {
        "content": "Implement feature X",
        "status": "completed",
        "activeForm": "Implementing feature X"
      }
    ]
  }
}
```

## Viewer UI Improvements

### 1. Sidechain/Agent Display

#### Conversation List Enhancement
```
[CONVERSATIONS]
├── Main Conversation (e22b2cf8...)
│   ├── 🤖 [AGENT: general-purpose] Research task (abc123...)
│   └── 🤖 [AGENT: architecture-reviewer] Review code (def456...)
└── Another Conversation (789xyz...)
```

**Implementation**:
- Indent sidechain conversations under their parent
- Use icons/emojis to indicate agent type
- Show subagent_type and task description
- Allow collapse/expand of sidechain groups
- Different color coding for sidechains

#### In-Conversation Task Links
When displaying a Task tool invocation:
```
[TOOL: Task - general-purpose]
Description: Research implementation patterns
➔ View sidechain conversation (abc123...)
```

### 2. Focused Mode Improvements

#### Current Issues
- Tool groups are partially implemented but complex
- Thinking blocks shown inline as "[Thinking]"
- Tool results shown as separate messages
- No distinction between human and system messages

#### Proposed Focused Mode Content
**SHOW**:
1. Human input messages (actual user typing)
2. Assistant text responses
3. Assistant thinking blocks (formatted distinctly)
4. Collapsed tool groups (single expandable block)
5. Summary messages (for continuations)

**HIDE**:
1. Individual tool invocations
2. Tool result details
3. System-generated user messages
4. Tool result content (unless expanded)

#### Improved Tool Grouping
```html
<div class="tool-sequence">
  <div class="tool-summary" onclick="expand()">
    ▶ Tool Sequence: 5 operations
    [Bash × 2, Read × 2, Write × 1]
    <span class="duration">~2.3s</span>
  </div>
  <div class="tool-details" style="display:none">
    <!-- Individual tool blocks -->
  </div>
</div>
```

### 3. Todo List Rendering

#### Claude Code Style Display
```html
<div class="todo-list">
  <h3>📋 Task List</h3>
  <div class="todo-item completed">
    ✅ Set up project structure
  </div>
  <div class="todo-item in-progress">
    🔄 Implement main feature
  </div>
  <div class="todo-item pending">
    ⬜ Write tests
  </div>
  <div class="todo-summary">
    Progress: 5/8 completed (62.5%)
  </div>
</div>
```

**Features**:
- Load todos from JSON files when conversation selected
- Display inline with conversation or in sidebar
- Show status with visual indicators
- Progress bar or percentage
- Collapsible section

### 4. Thinking Block Display

#### Current: Inline text
```
[ASSISTANT]
[Thinking] Internal reasoning text...
Here's my response...
```

#### Proposed: Distinct formatting
```html
<div class="message assistant">
  <div class="thinking-block collapsible">
    <div class="thinking-header" onclick="toggle()">
      💭 Assistant's Reasoning ▶
    </div>
    <div class="thinking-content" style="display:none">
      <!-- Formatted thinking content -->
    </div>
  </div>
  <div class="message-content">
    Here's my response...
  </div>
</div>
```

**Features**:
- Collapsed by default in focused mode
- Expanded in detailed mode
- Different background/border color
- Monospace font for technical reasoning
- Optional "Show all thinking" toggle

### 5. Message Type Indicators

#### Visual Differentiation
```css
.message.human-input {
  border-left: 4px solid #00ff00;  /* Green for human */
}

.message.tool-result {
  border-left: 2px dashed #666;     /* Dashed gray for system */
  opacity: 0.8;
}

.message.assistant-response {
  border-left: 4px solid #0088ff;  /* Blue for assistant */
}

.message.sidechain-result {
  border-left: 4px solid #ff00ff;  /* Purple for subagent */
  background: rgba(255, 0, 255, 0.05);
}
```

### 6. MCP Tool Recognition

#### Special Handling for MCP Tools
```html
<div class="tool-block mcp-tool">
  <div class="tool-header">
    🌐 [MCP: browser-use] Navigate to page
  </div>
  <div class="tool-content">
    <!-- Browser interaction details -->
  </div>
</div>
```

**Features**:
- Different icon for MCP tools
- Group browser sequences together
- Show browser state/screenshots if available
- Link related browser actions

### 7. Enhanced Statistics Display

#### Project Header Enhancement
```html
<div class="stats-detailed">
  <div class="stat-row">
    <span>Human Messages: 15</span>
    <span>Assistant Responses: 20</span>
    <span>Tools Used: 65</span>
  </div>
  <div class="stat-row">
    <span>Subagents: 3</span>
    <span>Thinking Blocks: 8</span>
    <span>Todos: 5/8 ✓</span>
  </div>
</div>
```

### 8. Navigation Improvements

#### Keyboard Shortcuts
- `j/k` - Navigate conversations
- `Enter` - Open selected conversation
- `f` - Toggle focused/detailed mode
- `t` - Show/hide thinking blocks
- `s` - Show/hide sidechains
- `?` - Show help

#### Search/Filter
```html
<input type="text" 
       placeholder="Search conversations..." 
       onkeyup="filterConversations(this.value)">

<div class="filters">
  <label><input type="checkbox" checked> Main</label>
  <label><input type="checkbox"> Sidechains</label>
  <label><input type="checkbox"> With Todos</label>
  <label><input type="checkbox"> With Thinking</label>
</div>
```

## Implementation Priority

### Phase 1: Core Display Improvements
1. **Fix message type classification** - Distinguish human vs system
2. **Improve tool grouping** - Single collapsed block in focused mode
3. **Add thinking block formatting** - Collapsible, distinct styling

### Phase 2: Sidechain Support
4. **Parse and display sidechains** - Parent-child relationships
5. **Add Task tool links** - Navigate to sidechain conversations
6. **Visual hierarchy** - Indent/group related conversations

### Phase 3: Enhanced Features
7. **Todo list rendering** - Claude Code style checkboxes
8. **MCP tool recognition** - Special handling for browser tools
9. **Enhanced statistics** - More detailed breakdowns

### Phase 4: Polish
10. **Keyboard navigation** - Improve accessibility
11. **Search and filters** - Find conversations quickly
12. **Export improvements** - Better markdown generation

## Technical Considerations

### 1. Performance
- Lazy load conversation content
- Virtual scrolling for long conversation lists
- Cache parsed JSONL data in memory
- Debounce search/filter operations

### 2. Data Flow
```
manifest.json → Initial conversation list
     ↓
User selects conversation
     ↓
Load JSONL file → Parse messages
     ↓
Load todos.json (if exists)
     ↓
Apply view mode filters → Render
```

### 3. Backwards Compatibility
- Support old manifest format
- Gracefully handle missing fields
- Progressive enhancement approach

### 4. Responsive Design
- Mobile-friendly conversation list
- Touch gestures for expand/collapse
- Responsive typography

## Example Focused Mode View

```
═══════════════════════════════════════════════════════
[CLAUDE CODE CONVERSATIONS]
Project: /Users/robotdad/Source/project
15 Human • 20 Assistant • 65 Tools • 3 Agents • 5/8 Todos
═══════════════════════════════════════════════════════

[USER] 10:23 AM
Can you help me implement feature X?

💭 [Assistant Reasoning - click to expand]

[ASSISTANT] 10:23 AM
I'll help you implement feature X. Let me first examine your 
existing code structure and then create the implementation.

▶ [TOOLS: 5 operations in 2.3s]
  Bash × 2, Read × 2, Write × 1

[ASSISTANT] 10:24 AM
I've successfully implemented feature X with the following:
- Created new module in src/features/
- Added configuration options
- Integrated with existing system

📋 Task Progress: 3/5 completed
✅ Analyze code structure
✅ Create feature module
✅ Add configuration
⬜ Write tests
⬜ Update documentation

[USER] 10:25 AM
Great! Can you also add error handling?

[ASSISTANT] 10:25 AM
I'll add comprehensive error handling now...

🤖 [SUBAGENT: general-purpose]
   Researching error handling patterns
   → View full conversation

[ASSISTANT] 10:28 AM  
Based on the research, I've implemented error handling with:
- Try-catch blocks for async operations
- Custom error classes
- Graceful degradation
```

## Conclusion

The viewer has a solid foundation but needs significant enhancements to properly display the rich conversation data available in JSONL files. The priority should be:

1. **Immediate**: Fix focused mode to properly hide tool details and show only human/assistant interaction
2. **High Priority**: Add sidechain/agent support for Task tool conversations
3. **Medium Priority**: Render todos and thinking blocks properly
4. **Enhancement**: Add search, filters, and keyboard navigation

These improvements will make the viewer much more useful for understanding complex Claude Code conversations, especially those involving multiple agents, extensive tool use, and detailed reasoning.