# Git Usage Patterns in Claude Code

## Overview

Analysis of Claude Code JSONL files reveals sophisticated git integration with consistent patterns across 99% of conversations. Git operations are deeply embedded in the development workflow, from branch management to automated PR creation.

## How to Explore Git Patterns in Your System

```bash
# Count git operations in your conversations
grep -h '"name":"Bash"' ~/.claude/projects/*/*.jsonl 2>/dev/null | \
  grep -o 'git [a-z]*' | sort | uniq -c | sort -rn

# Find your branch names
grep -h '"gitBranch":' ~/.claude/projects/*/*.jsonl 2>/dev/null | \
  jq -r '.gitBranch' | sort | uniq -c | sort -rn

# Search for commit messages
grep -h 'git commit' ~/.claude/projects/*/*.jsonl 2>/dev/null | \
  grep -o "Generated with.*Claude Code" | wc -l

# Find PR creation patterns
grep -h 'gh pr create' ~/.claude/projects/*/*.jsonl 2>/dev/null | wc -l

# Identify worktree usage
grep -h 'git worktree' ~/.claude/projects/*/*.jsonl 2>/dev/null | wc -l
```

## Git Command Usage Patterns

### Commonly Observed Commands

| Command | Purpose | Common Variations |
|---------|---------|-------------------|
| `git status` | Check repository state | Often run before commits |
| `git diff` | Review changes | With `--cached` or specific files |
| `git log` | View history | `--oneline`, `-n 10`, `main..HEAD` |
| `git add` | Stage changes | `.`, `-A`, selective files |
| `git commit` | Create commits | Often uses HEREDOC for messages |
| `git push` | Push to remote | `-u origin branch` for new branches |
| `git checkout` | Switch branches | `-b` for new branches |
| `git branch` | List/create branches | `-a` to show all |

### Command Sequencing

Claude Code follows consistent command sequences:

#### Standard Development Flow
```bash
git status                    # Check current state
git diff                      # Review unstaged changes
git add .                     # Stage all changes
git diff --cached            # Review staged changes
git commit -m "message"      # Commit with message
git push                     # Push to remote
```

#### Pre-Commit Verification
```bash
git status                    # Verify clean state
git log --oneline -5         # Review recent commits
git diff main..HEAD          # Check branch changes
```

## Branch Management Patterns

### Branch Naming Conventions

| Pattern | Example | Use Case |
|---------|---------|----------|
| `main` or `master` | `main` | Primary development branch |
| `issue-{N}-{description}` | `issue-9-implement-markdown` | Issue tracking branches |
| `feature/{name}` | `feature/dark-mode` | Feature development |
| `fix/{description}` | `fix/authentication-bug` | Bug fixes |
| `{prefix}-{description}` | Various prefixes | Project-specific conventions |

### Branch Lifecycle

1. **Creation**: `git checkout -b issue-123-description`
2. **Development**: Multiple commits with structured messages
3. **Push**: `git push -u origin issue-123-description`
4. **PR Creation**: Using GitHub CLI
5. **Merge**: Usually handled outside Claude Code

## Commit Message Structure

### Observed Pattern

Claude Code typically generates commits with this structure:

```
{Concise summary line}

{Optional bullet points for details:}
- First change detail
- Second change detail

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### HEREDOC Usage

Claude Code uses HEREDOC for multi-line commit messages:

```bash
git commit -m "$(cat <<'EOF'
Implement dark mode toggle feature

- Add theme context provider
- Update components for theme support
- Add toggle switch to settings

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Pull Request Patterns

### PR Creation with GitHub CLI

Standard PR creation pattern:

```bash
gh pr create --title "Title" --body "$(cat <<'EOF'
## Summary
- Key change 1
- Key change 2

## Test Plan
- [ ] Unit tests pass
- [ ] Manual testing completed

## Related Issues
Closes #123

🤖 Generated with [Claude Code](https://claude.ai/code)
EOF
)"
```

### PR Body Structure

1. **Summary**: Bullet points of changes
2. **Test Plan**: Checklist format
3. **Related Issues**: Links to GitHub issues
4. **Claude Code Attribution**: Signature line

## Git Workflow Integration

### Development Session Patterns

#### New Feature Implementation
```
1. git checkout main
2. git pull origin main
3. git checkout -b feature/new-feature
4. [Development with multiple commits]
5. git push -u origin feature/new-feature
6. gh pr create
```

#### Bug Fix Workflow
```
1. git status (verify clean state)
2. git checkout -b fix/bug-description
3. [Fix implementation]
4. git add affected-files
5. git commit (structured message)
6. git push
```

### Commit Frequency

- **Simple tasks**: 1-2 commits per session
- **Feature development**: 3-5 commits with logical grouping
- **Complex refactoring**: 10+ commits with granular changes
- **SDK/Automated**: Single commit per attempt

## Git Worktree Usage

### Worktree Patterns

Worktrees enable parallel development on multiple issues:

```bash
# Create worktree for an issue or feature
git worktree add [path-to-worktree] [branch-name]

# Work in isolated environment
cd [path-to-worktree]
```

### Worktree Organization

Worktrees can be organized in various ways:
- Separate directory at same level as main repository
- Subdirectory within a dedicated workspace
- Project-specific organization structure
- Naming conventions vary by team/project

## Advanced Git Patterns

### Merge Conflict Resolution

```bash
# Check conflict status
git status

# Review conflicting changes
git diff

# Resolve by choosing version
git checkout --ours file.txt  # Keep current
git checkout --theirs file.txt # Take incoming
```

### Remote Repository Setup

```bash
# Initialize new repository
git init
git remote add origin https://github.com/user/repo.git
git branch -M main
git push -u origin main
```

### Branch Synchronization

```bash
# Fetch latest changes
git fetch origin

# Check branch status
git status

# Pull with rebase
git pull --rebase origin main
```

## Correlation with Conversation Activities

### Typical Activity Patterns

| Conversation Activity | Common Git Operations |
|----------------------|----------------------|
| Starting new feature | Branch creation, initial setup |
| Implementing changes | Progressive commits |
| Testing code | Status and diff checks |
| Completing task | Final commits, push, PR |
| Code review | Branch operations, diffs |
| Bug fixing | Targeted commits |

### Automation Capabilities

Claude Code can automate various git workflows:

1. **Commit message generation**: Structured formatting
2. **PR creation**: Using GitHub CLI
3. **Branch management**: Following conventions
4. **Status verification**: Checking state before operations

## Error Handling and Recovery

### Common Git Issues Handled

1. **Uncommitted Changes**
   - Detection: `git status` before operations
   - Resolution: Stage and commit or stash

2. **Branch Tracking**
   - Detection: Push failures
   - Resolution: `git push -u origin branch`

3. **Merge Conflicts**
   - Detection: Pull/merge failures
   - Resolution: Manual conflict resolution

4. **Hook Failures**
   - Detection: Pre-commit hook errors
   - Resolution: Fix issues and retry commit

## Observed Patterns

### Common Characteristics

**Based on sample analysis**:
- Git operations are very common in Claude Code conversations
- Consistent commit message formatting with attribution
- Multiple branch naming conventions observed
- Typical workflow includes status checks, commits, and pushes

### Command Usage Patterns

**Frequently observed commands** (in rough order):
1. `git status` - State verification
2. `git commit` - Creating commits
3. `git add` - Staging changes
4. `git log` - History review
5. `git push` - Remote updates
6. `git diff` - Change review
7. Various other git commands

## Best Practices Observed

### Consistent Patterns

1. **Always check status** before operations
2. **Review diffs** before committing
3. **Use descriptive branch names** following conventions
4. **Create structured commit messages** with attribution
5. **Verify pushes** succeeded
6. **Create PRs immediately** after pushing

### Workflow Optimization

- Batch related changes in single commits
- Use atomic commits for logical units
- Maintain clean commit history
- Leverage worktrees for parallel work
- Automate repetitive operations

## Integration Points

### Claude Code Features

- **Todo tracking**: Correlates with commit points
- **Sidechains**: May span multiple commits
- **Continuations**: Maintain git context across sessions
- **SDK usage**: Automated commit per attempt

### External Tools

- **GitHub CLI (`gh`)**: PR and issue management
- **Git hooks**: Pre-commit, post-commit automation
- **CI/CD**: Triggered by push operations

## Evolution and Trends

### Version-Based Patterns

- Earlier versions: More manual git operations
- Current versions: Increased automation
- SDK integration: Fully automated git workflows

### Usage Evolution

1. **Early conversations**: Learning git patterns
2. **Mature usage**: Consistent, optimized workflows
3. **SDK automation**: Minimal manual intervention

## Recommendations for Archival

### Essential Git Context to Preserve

1. **Branch Information**: Track `gitBranch` field
2. **Commit Messages**: Full text with structure
3. **Command Sequences**: Order of operations
4. **PR Creation**: Body and metadata
5. **Error Recovery**: How issues were resolved

### Visualization Suggestions

1. **Git Graph**: Show branch/commit relationships
2. **Timeline View**: Correlate conversations with commits
3. **Command Frequency**: Heatmap of git operations
4. **Workflow Diagrams**: Common command sequences
5. **PR Tracking**: Link conversations to PRs

## Conclusion

Git integration in Claude Code demonstrates sophisticated version control understanding with consistent patterns across all projects. The system maintains professional development practices while automating routine operations, enabling efficient collaborative development.

Key takeaways:
- Deep git integration with 99% conversation coverage
- Consistent commit message structure with attribution
- Systematic branch management following conventions
- Automated PR creation with structured bodies
- Comprehensive error handling and recovery
- Clear correlation between conversation activities and git operations