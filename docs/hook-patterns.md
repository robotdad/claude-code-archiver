# Hook Patterns in Claude Code

## Overview

Claude Code supports a hook system that allows users to configure shell commands that execute in response to specific events during conversations. This document describes hook patterns and their representation in JSONL files.

## Hook System Architecture

Hooks are shell commands configured in Claude Code settings that trigger on specific events:
- Tool invocations
- Message submissions
- Completion events
- Error conditions

## Identifying Hook Usage

```bash
# Search for hook-related messages
grep -i "hook" ~/.claude/projects/*/*.jsonl 2>/dev/null | head -10

# Look for hook execution patterns
grep "PostToolUse" ~/.claude/projects/*/*.jsonl 2>/dev/null
grep "PreToolUse" ~/.claude/projects/*/*.jsonl 2>/dev/null

# Find hook script references
grep "\$CLAUDE_PROJECT_DIR/.claude/tools" ~/.claude/projects/*/*.jsonl 2>/dev/null

# Find blocked operations from hooks
grep -i "blocked by.*hook" ~/.claude/projects/*/*.jsonl 2>/dev/null
```

## Hook Event Types

### Common Hook Points

1. **PreToolUse Hooks**
   - Before tool execution (e.g., `PreToolUse:Task`)
   - Logging and preparation
   - Validation and checks
   - Example: `PreToolUse:Task [$CLAUDE_PROJECT_DIR/.claude/tools/subagent-logger.py]`

2. **PostToolUse Hooks**
   - After tool completion (e.g., `PostToolUse:Edit`, `PostToolUse:Write`)
   - Quality control and validation
   - Automated testing
   - Example: `PostToolUse:Edit [$CLAUDE_PROJECT_DIR/.claude/tools/make-check.sh]`

3. **System Reminder Hooks**
   - Security compliance reminders
   - Context injection
   - User guidance

## Hook Feedback in Messages

### User Message Hooks

Hooks can modify or validate user input:

```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": "Original or modified content from hook"
  },
  // Hook feedback may appear in content
}
```

### Hook Blocking Patterns

When hooks prevent operations:
- Blocked message indicators
- Hook rejection feedback
- Suggested remediations

## Hook Configuration Impact

### On Conversation Flow

Hooks can:
- Interrupt normal flow
- Inject additional context
- Modify tool parameters
- Cancel operations

### On Tool Usage

Hook interference patterns:
- Pre-tool validation
- Parameter modification
- Result transformation
- Execution prevention

## Common Hook Use Cases

### 1. Code Quality Enforcement

**Quality control hooks can:**
- Run formatting tools (black, prettier, ruff)
- Execute linters (eslint, pylint, flake8)
- Perform type checking (mypy, pyright, tsc)
- Run test suites automatically

**Typical output pattern:**
```
→ Formatting code...
  Files formatted successfully

→ Linting code...
  All checks passed!

→ Type checking code...
  0 errors, 0 warnings

✅ All checks passed!
```

### 2. Operation Logging and Tracking

**Hooks can track:**
- Tool invocation counts
- API usage and costs
- Performance metrics
- Error rates and patterns

### 3. Security and Compliance

**Security hooks may:**
- Check for sensitive data exposure
- Validate file access patterns
- Inject compliance reminders
- Audit operation logs

### 4. Workflow Automation

**Automation capabilities:**
- Code formatting on save
- Test execution before commits
- Documentation generation
- Dependency updates

## Hook Message Patterns

### Hook Execution Feedback

**Typical execution feedback structure:**
```
PostToolUse:[ToolName] [hook script path] completed successfully
[Hook output and results]
```

**Common feedback elements:**
- Execution status (success/failure)
- Working directory context
- Command output
- Result indicators (✅/❌)

### System Reminders

**System-injected messages:**
```xml
<system-reminder>
[Context-appropriate reminder or guidance]
</system-reminder>
```

These may appear after specific operations to provide:
- Security guidance
- Best practice reminders
- Compliance requirements
- Usage tips

## Error Handling

### Hook Failures

When hooks fail:
- Error messages in conversation
- Fallback behavior
- User notification
- Recovery suggestions

### Blocking Resolution

When blocked by hooks:
- Determine adjustability
- Check hook configuration
- User intervention required
- Alternative approaches

## Performance Implications

### Hook Overhead

Considerations:
- Execution time per hook
- Cumulative delay impact
- Resource consumption
- Timeout handling

### Optimization

Best practices:
- Fast hook execution
- Async where possible
- Minimal blocking operations
- Efficient scripts

## Hook Integration Patterns

### Hook Organization

**Common directory structures:**
```
project_root/
├── .claude/
│   ├── hooks/        # Hook scripts
│   ├── tools/        # Custom tools
│   └── config/       # Configuration
└── [project files]
```

### Quality Control Pipeline

**Typical quality check sequence:**
1. **Formatting**: Code style normalization
2. **Linting**: Static analysis
3. **Type Checking**: Type safety validation
4. **Test Execution**: Automated testing

### Hook Environment

**Hooks may have access to:**
- Project directory paths
- Tool execution context
- File modification details
- Environment variables

### Multi-Phase Hook System

```
Tool Invocation
    ↓
Pre-execution hooks
    ↓
Tool Execution
    ↓
Post-execution hooks
    ↓
Result integration
    ↓
Conversation Continues
```

## Security and Privacy

### Hook Access

Hooks have access to:
- Conversation context
- File system
- Environment variables
- External services

### Data Handling

Considerations:
- Hooks may log data
- External service calls
- Credential exposure risks
- Audit trail creation

## Best Practices

### For Users

1. **Organize hooks systematically**
   - Use consistent directory structure
   - Version control hook scripts
   - Document hook behavior

2. **Design for portability**
   - Use relative paths
   - Leverage environment variables
   - Avoid system-specific dependencies

3. **Implement quality gates**
   - Sequential validation steps
   - Fast failure on errors
   - Clear feedback messages

4. **Monitor and track**
   - Log hook executions
   - Track performance metrics
   - Monitor failure rates

## Evolution

### Current State

- Basic hook system
- Shell command execution
- Event-based triggers
- Simple feedback mechanism

### Potential Future

- Advanced hook types
- Complex event chains
- Conditional execution
- Rich feedback formats

## Production Hook Patterns

### Observed Capabilities

**Quality Control Integration:**
- Automatic code formatting after edits
- Linting and type checking on file changes
- Test execution before operations complete
- Build validation in CI/CD pipelines

**Operational Monitoring:**
- Tool usage tracking and analytics
- Cost monitoring for API operations
- Performance metrics collection
- Error rate tracking

**Compliance and Security:**
- Security reminder injection
- Sensitive data detection
- Access pattern validation
- Audit log generation

### Hook Execution Patterns

**Frequency observations:**
- File modification hooks: Every edit/write operation
- Validation hooks: Before critical operations
- Logging hooks: Start and end of tool invocations
- Compliance hooks: After sensitive operations

## Benefits of Hook System

### Development Workflow Enhancement

1. **Consistent Quality**: Automated enforcement of coding standards
2. **Operational Visibility**: Real-time tracking of operations
3. **Security Compliance**: Automatic security controls
4. **Workflow Automation**: Reduced manual intervention

### Integration Capabilities

- **Development tools**: Linters, formatters, type checkers
- **Build systems**: Make, npm, gradle, maven
- **Testing frameworks**: pytest, jest, mocha
- **Monitoring tools**: Custom analytics and tracking

## Conclusion

The hook system in Claude Code provides powerful customization capabilities that appear in JSONL files as:
- Hook execution feedback
- System-injected reminders
- Quality control results
- Operation tracking data

Hooks enable:
- Automated quality enforcement
- Usage and cost tracking
- Security compliance
- Workflow customization

The hook system transforms Claude Code into a customizable development environment with automated quality gates and compliance controls.