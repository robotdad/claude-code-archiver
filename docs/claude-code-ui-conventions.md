# Claude Code UI Conventions & Viewer Implementation

## Observed Claude Code Conventions

Based on the screenshot and analysis, Claude Code uses a clean, minimal approach with specific prefixes and colors:

### Message Type Indicators

1. **User Messages**: `>` prefix (appears to be in default terminal color)
   - Clean, simple prefix for human input
   - Example: `> Look at the 2025-06-25 output. What do you think?`

2. **Assistant Thinking**: `* Thinking...` prefix (appears in gray/dimmed)
   - Shows internal reasoning process
   - Collapsible/expandable in the actual interface
   - Example: `* Thinking...` followed by the thinking content

3. **Assistant Messages**: `●` solid white bullet
   - Main assistant responses to the user
   - White color distinguishes from green tool bullets

4. **Tool Calls**: `●` colored bullets (green for most tools)
   - Same bullet shape as assistant but different color
   - Quick visual scan shows tool activity
   - Example: `● List(reports/2025-06-25)`

5. **User Terminal Commands**: `!` prefix (pink/magenta - not shown but mentioned)
   - Commands entered directly by user in terminal
   - Distinguished from tool-executed commands

6. **System Messages**: `◆` diamond or `[system]` prefix (proposed)
   - Diagnostic/infrastructure messages
   - Not shown in Claude Code UI (internal only)
   - Examples: system reminders, hook outputs, error states
   - Should be collapsed in focused mode like tools

7. **Todo Lists**: `☐` `☑` `⊡` checkbox prefixes
   - Display todo status inline with conversation
   - `☐` pending, `☑` completed, `⊡` in_progress
   - Render as a formatted list, not JSON

8. **Agent/Sidechain Messages**: `🤖` robot emoji prefix
   - Messages from subagent Task invocations
   - Shows which agent type (e.g., `🤖 [general-purpose]`)
   - Links back to parent conversation
   - Different background tint to show parallel thread

## Implementing Claude Code Style in Our Viewer

### 1. Update Message Rendering

#### Current Approach (Boxing/Borders)
```css
.message.user {
    border-left: 3px solid #00ff00;
    background: #0a1a0a;
}
```

#### Claude Code Style Approach
```css
/* Minimal, prefix-based approach */
.message {
    padding: 4px 0;
    margin: 2px 0;
    border: none;
    background: transparent;
}

.message-prefix {
    display: inline-block;
    width: 20px;
    color: #888;
    font-weight: normal;
}

.message.user .message-prefix::before {
    content: ">";
    color: #00ff00;
}

.message.assistant .message-prefix::before {
    content: "●";  /* Solid white bullet */
    color: #ffffff;
}

.message.thinking .message-prefix::before {
    content: "*";
    color: #666666;
}

.message.tool .message-prefix::before {
    content: "●";  /* Filled bullet */
    color: #00ff00;  /* Green for most tools */
}

.message.user-terminal .message-prefix::before {
    content: "!";
    color: #ff00ff;  /* Pink/magenta */
}

.message.system .message-prefix::before {
    content: "◆";  /* or "[sys]" for more clarity */
    color: #444444;  /* Very dimmed, diagnostic feel */
}
```

### 2. Thinking Block Display

#### Claude Code Style
```html
<div class="message thinking">
    <span class="message-prefix"></span>
    <span class="thinking-indicator">Thinking...</span>
    <div class="thinking-content collapsible">
        <!-- Actual thinking content -->
    </div>
</div>
```

### 3. Tool Sequence Display

#### Individual Tools (Detailed Mode)
```html
<div class="message tool">
    <span class="message-prefix"></span>
    <span class="tool-name">Read</span>
    <span class="tool-params">(reports/2025-06-25/Status.md)</span>
</div>
```

#### Grouped Tools (Focused Mode)
```html
<div class="tool-group collapsed">
    <div class="message tool-summary">
        <span class="message-prefix">●</span>
        <span class="summary-text">
            List, Read × 3, Write × 2 
            <span class="tool-count">(6 operations)</span>
        </span>
    </div>
    <!-- Expandable details -->
</div>
```

### 4. System Message Handling

System messages are diagnostic/infrastructure messages that don't appear in Claude Code's UI but exist in JSONL files. They include:

- **System reminders** (e.g., security warnings, context updates)
- **Hook execution feedback** (pre/post tool hooks)
- **Error states and warnings**
- **Compaction summaries**
- **Environment notifications**

#### Proposed Display Conventions

**Focused Mode**: Collapse system messages by default
```
◆ [System: 3 diagnostic messages] (click to expand)
```

**Detailed Mode**: Show with subdued styling
```
◆ System reminder: File appears to be malicious, refusing to execute
◆ PostToolUse:Edit hook completed successfully
◆ Environment: Working directory changed to /Users/example
```

**Visual Treatment**:
- Use very dimmed color (#444444 or #555555)
- Smaller font size or reduced opacity
- Group consecutive system messages
- In focused mode, hide entirely or show as single collapsed line

### 5. Complete Message Flow Example

```
> Help me analyze the debug output

* Thinking...
  [Expandable thinking content]

○ I'll analyze the debug output for you. Let me first look at what was generated.

● List(reports/2025-06-25)
● Read(reports/2025-06-25/Status.md)

◆ [System: Security check passed]

○ I notice several issues in the debug output:

1. Debug files missing: No debug_transcripts.md was created
2. Empty References section: Line 34 shows "- " with nothing after
3. find_previous_report.json issue: Wrong path being used

Let me check the configuration:

● Read(debug_config.json)
● Bash(grep -n "debug" config.yaml)

○ The issue is with the boolean parameter handling. The debug flag needs to be passed as true/false strings rather than quoted.

> Can you fix it?

○ I'll fix the boolean parameter issue now.

● Edit(config.yaml, old_string="debug: 'true'", new_string="debug: true")

◆ PostToolUse:Edit [format_checker.sh] completed successfully

● Bash(./run_debug.sh)

○ Fixed! The debug files are now being generated correctly.
```

### 6. Todo List Display

Todo lists should render as formatted checkboxes, not raw JSON:

```
○ Let me track our progress on this feature.

📋 Task List:
☐ Set up project structure
☐ Implement authentication
☑ Create database schema
⊡ Write API endpoints (in progress)
☐ Add error handling
☐ Write tests

Progress: 1/6 completed (17%)

○ I've completed the database schema. Now working on the API endpoints.
```

**Visual Styling:**
```css
.todo-list {
    margin: 10px 0;
    padding: 10px 20px;
    border-left: 2px solid #666;
}

.todo-item {
    margin: 4px 0;
}

.todo-item.completed { color: #00ff00; }
.todo-item.in-progress { color: #ffb000; }
.todo-item.pending { color: #888888; }

.todo-progress {
    margin-top: 8px;
    color: #ffb000;
    font-size: 0.9em;
}
```

### 7. Agent/Sidechain Message Display

Messages from Task tool subagents should be visually distinct:

```
> Can you research the best authentication patterns?

○ I'll research authentication patterns for you using a specialized agent.

● Task(subagent_type="general-purpose", description="Research authentication patterns")

🤖 [Agent: general-purpose]
Starting research on authentication patterns...
[Sidechain conversation abc123... - click to view full thread]

Key findings:
1. OAuth 2.0 with PKCE for public clients
2. JWT with refresh tokens for stateless auth
3. Session-based for traditional web apps

○ Based on the research, here are the recommended authentication patterns...
```

**Implementation:**
```css
.message.agent .message-prefix::before {
    content: "🤖";
    font-size: 1.2em;
}

.message.agent {
    background: rgba(100, 50, 200, 0.05);  /* Slight purple tint */
    border-left: 2px solid #8b5cf6;
}

.agent-label {
    color: #8b5cf6;
    font-size: 0.85em;
    margin-left: 4px;
}

.sidechain-link {
    color: #8b5cf6;
    text-decoration: underline;
    cursor: pointer;
    font-size: 0.85em;
}
```

## Detecting Message Types from JSONL

### 1. User Terminal Commands (!)
Currently not captured in JSONL. Would need to detect:
- User messages that are clearly shell commands
- Messages immediately before Bash tool results
- Pattern matching for command-like content

### 2. Human Input (>)
```python
def is_human_input(entry):
    if entry.type != "user":
        return False
    
    # Check if it's a tool result
    if entry.get("toolUseResult"):
        return False
    
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return True  # Simple string = human
    
    if isinstance(content, list):
        # Check for non-tool-result blocks
        for block in content:
            if block.get("type") not in ["tool_result"]:
                return True
    
    return False
```

### 3. Assistant Thinking (*)
```python
def has_thinking(entry):
    if entry.type != "assistant":
        return False
    
    content = entry.get("message", {}).get("content", [])
    if isinstance(content, list):
        return any(block.get("type") == "thinking" for block in content)
    return False
```

### 4. Tool Calls (●)
```python
def is_tool_call(entry):
    if entry.type != "assistant":
        return False
    
    content = entry.get("message", {}).get("content", [])
    if isinstance(content, list):
        return any(block.get("type") == "tool_use" for block in content)
    return False
```

### 5. System Messages (◆)
```python
def is_system_message(entry):
    # Type-based detection
    if entry.type == "system":
        return True
    
    # Content-based detection for system-injected content
    if entry.type == "user":
        content = entry.get("message", {}).get("content")
        if isinstance(content, str):
            # Check for system tags
            if "<system-reminder>" in content:
                return True
            if "PostToolUse:" in content and "[hook" in content:
                return True
    
    return False
```

### 6. Tool Results (Handle specially)
Tool results shouldn't be displayed as messages in focused mode, but their presence should be indicated as part of tool operations.

## Color Palette

Based on Claude Code terminal appearance:

```css
:root {
    --claude-bg: #0c0c0c;           /* Very dark background */
    --claude-fg: #ffffff;           /* White text */
    --claude-user: #00ff00;         /* Green for user */
    --claude-thinking: #666666;     /* Gray for thinking */
    --claude-tool: #00ff00;         /* Green for tools */
    --claude-tool-alt: #ffb000;     /* Orange for special tools */
    --claude-terminal: #ff00ff;     /* Magenta for terminal */
    --claude-dim: #888888;          /* Dimmed text */
    --claude-error: #ff4444;        /* Red for errors */
}
```

## Implementation Priority

### Phase 1: Core Visual Updates
1. Replace bordered boxes with prefix-based indicators
2. Implement Claude Code color scheme
3. Add proper message type detection

### Phase 2: Thinking & Tool Handling
4. Format thinking blocks with * prefix and gray text
5. Group tool sequences with ● bullets
6. Collapse/expand functionality matching Claude Code

### Phase 3: Enhanced Features
7. Detect and mark user terminal commands with !
8. Add smooth animations for expand/collapse
9. Implement keyboard shortcuts matching Claude Code

## Benefits of This Approach

1. **Cleaner Visual Hierarchy**: Prefixes are less visually heavy than borders
2. **Faster Scanning**: Easy to identify message types at a glance
3. **Familiar to Users**: Matches what Claude Code users expect
4. **Space Efficient**: More content visible on screen
5. **Better Tool Grouping**: Clear distinction between conversation and operations

## CSS Implementation Example

```css
/* Claude Code Style Message Display */
.messages {
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
    font-size: 14px;
    line-height: 1.6;
    padding: 20px;
    background: #0c0c0c;
    color: #ffffff;
}

.message {
    margin: 4px 0;
    display: flex;
    align-items: flex-start;
}

.message-prefix {
    flex-shrink: 0;
    width: 24px;
    text-align: center;
    user-select: none;
}

.message-content {
    flex: 1;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Specific message types */
.message.user .message-prefix { color: #00ff00; }
.message.user .message-prefix::before { content: ">"; }

.message.assistant .message-prefix { color: #ffffff; }
.message.assistant .message-prefix::before { content: "○"; }

.message.thinking .message-prefix { color: #666666; }
.message.thinking .message-prefix::before { content: "*"; }

.message.tool .message-prefix { color: #00ff00; }
.message.tool .message-prefix::before { content: "●"; }

.message.terminal .message-prefix { color: #ff00ff; }
.message.terminal .message-prefix::before { content: "!"; }

.message.system .message-prefix { color: #444444; }
.message.system .message-prefix::before { content: "◆"; }

.message.agent .message-prefix { color: #8b5cf6; }
.message.agent .message-prefix::before { content: "🤖"; }

/* Todo list items */
.todo-item .prefix::before {
    display: inline-block;
    width: 20px;
}
.todo-item.pending .prefix::before { content: "☐"; color: #888; }
.todo-item.in-progress .prefix::before { content: "⊡"; color: #ffb000; }  
.todo-item.completed .prefix::before { content: "☑"; color: #00ff00; }

/* System messages special handling */
.message.system {
    opacity: 0.7;
    font-size: 0.9em;
}

.system-group {
    margin: 4px 0;
    border-left: 1px dashed #333;
    padding-left: 12px;
}

.system-group.collapsed .system-details {
    display: none;
}

.system-summary {
    color: #444444;
    cursor: pointer;
    font-size: 0.85em;
}

.system-summary:hover {
    color: #666666;
}

/* Thinking block special handling */
.thinking-content {
    color: #666666;
    font-style: italic;
    margin-left: 24px;
    padding: 8px 0;
}

.thinking-indicator {
    color: #666666;
    font-style: italic;
    cursor: pointer;
}

.thinking-indicator:hover {
    color: #888888;
}

/* Tool grouping */
.tool-group {
    margin: 8px 0;
    border-left: 1px solid #333;
    padding-left: 12px;
}

.tool-group.collapsed .tool-details {
    display: none;
}

.tool-summary {
    cursor: pointer;
    opacity: 0.8;
}

.tool-summary:hover {
    opacity: 1.0;
}

/* Make it feel native */
.messages ::selection {
    background: rgba(0, 255, 0, 0.2);
}

/* Smooth transitions */
.thinking-content,
.tool-details {
    transition: all 0.2s ease;
}
```

## Next Steps

1. Update parser to properly classify message types
2. Modify viewer HTML/CSS to use Claude Code conventions
3. Test with various conversation types to ensure clarity
4. Add configuration option for "Claude Code Style" vs "Classic Style"