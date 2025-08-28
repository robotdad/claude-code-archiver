"""Generator for terminal-style HTML viewer."""

from pathlib import Path
from typing import Any


class ViewerGenerator:
    """Generates a terminal-style HTML viewer for conversations."""

    def generate_viewer(self, manifest: dict[str, Any]) -> str:
        """Generate the complete HTML viewer.

        Args:
            manifest: The archive manifest data

        Returns:
            Complete HTML content as string
        """
        # No longer embedding manifest - will fetch from manifest.json file

        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code Conversations</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Cascadia Code', 'Fira Code', 'SF Mono', 'Consolas', 'Liberation Mono', 'Courier New', monospace;
            background: #0c0c0c;
            color: #00ff00;
            padding: 20px;
            line-height: 1.4;
            font-size: 14px;
        }

        .container {
            max-width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            border: 1px solid #00ff00;
            padding: 10px;
            margin-bottom: 20px;
            background: #1a1a1a;
        }

        .header h1 {
            font-size: 16px;
            font-weight: normal;
            color: #ffb000;
        }

        .stats {
            margin-top: 10px;
            color: #888;
        }

        /* Main Layout */
        .main-content {
            display: flex;
            flex: 1;
            overflow: hidden;
            gap: 10px;
        }

        /* Conversation List */
        .conversation-list {
            width: 350px;
            border: 1px solid #00ff00;
            background: #0f0f0f;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .list-header {
            background: #1a1a1a;
            padding: 10px;
            border-bottom: 1px solid #00ff00;
            color: #ffb000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .list-controls {
            display: flex;
            gap: 5px;
        }

        .small-btn {
            background: #1a1a1a;
            border: 1px solid #666;
            color: #666;
            padding: 2px 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
        }

        .small-btn:hover {
            background: #222;
            color: #888;
        }

        .small-btn.active {
            background: #333;
            color: #ffb000;
            border-color: #ffb000;
        }

        .small-btn:disabled {
            background: #111;
            color: #444;
            border-color: #444;
            cursor: not-allowed;
        }

        .conversation-items {
            overflow-y: auto;
            flex: 1;
        }

        .conversation-item {
            padding: 10px;
            border-bottom: 1px solid #333;
            cursor: pointer;
            transition: background 0.2s;
        }

        .conversation-item:hover {
            background: #1a1a1a;
        }

        .conversation-item.active {
            background: #222;
            border-left: 3px solid #ffb000;
        }

        .conversation-item .conversation-header {
            margin-bottom: 8px;
        }

        .conversation-item .session-id {
            color: #00ff00;
            font-weight: bold;
            font-size: 11px;
        }

        .conversation-item .conversation-title {
            color: #fff;
            font-weight: normal;
            margin-top: 3px;
            font-size: 13px;
            line-height: 1.3;
        }

        .conversation-item .conversation-meta {
            color: #888;
            font-size: 11px;
        }

        .conversation-item .meta-line {
            margin-bottom: 2px;
        }

        .conversation-item .meta-label {
            color: #666;
            font-weight: bold;
        }

        .conversation-item .continuation-marker {
            color: #ffb000;
            font-size: 10px;
        }

        .conversation-item .snapshot-marker {
            color: #888;
            font-size: 10px;
        }

        .conversation-item.hidden {
            opacity: 0.5;
            background: #0a0a0a !important;
        }

        .conversation-item .conversation-actions {
            margin-top: 5px;
            display: none;
        }

        .conversation-item:hover .conversation-actions {
            display: block;
        }

        .conversation-actions button {
            background: none;
            border: 1px solid #444;
            color: #888;
            padding: 1px 4px;
            cursor: pointer;
            font-family: inherit;
            font-size: 9px;
            margin-right: 5px;
        }

        .conversation-actions button:hover {
            color: #ffb000;
            border-color: #ffb000;
        }

        /* Conversation View */
        .conversation-view {
            flex: 1;
            border: 1px solid #00ff00;
            background: #0f0f0f;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .view-header {
            background: #1a1a1a;
            padding: 10px;
            border-bottom: 1px solid #00ff00;
        }

        .view-title-main {
            font-size: 16px;
            color: #fff;
            margin-bottom: 4px;
            font-weight: bold;
        }

        .view-title-meta {
            font-size: 12px;
            color: #888;
            font-weight: normal;
        }

        .view-controls {
            margin-top: 10px;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .control-group {
            display: flex;
            gap: 5px;
            align-items: center;
        }

        .btn {
            background: #1a1a1a;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 5px 10px;
            cursor: pointer;
            margin-right: 10px;
            font-family: inherit;
            font-size: 12px;
        }

        .btn:hover {
            background: #222;
        }

        .btn.active {
            background: #00ff00;
            color: #0c0c0c;
        }

        /* Messages - Claude Code Style */
        .messages {
            padding: 20px;
            overflow-y: auto;
            flex: 1;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Fira Code', 'Consolas', 'Liberation Mono', monospace;
            line-height: 1.6;
        }

        .message {
            margin: 4px 0;
            padding: 2px 0;
            display: flex;
            align-items: flex-start;
            border: none;
            background: transparent;
        }

        .message-prefix {
            flex-shrink: 0;
            width: 24px;
            text-align: center;
            user-select: none;
            font-weight: normal;
        }

        .message-content {
            flex: 1;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin-left: 8px;
        }

        /* Claude Code message type prefixes */
        .message.user .message-prefix { color: #00ff00; }
        .message.user .message-prefix::before { content: ">"; }

        .message.assistant .message-prefix { color: #ffffff; }
        .message.assistant .message-prefix::before { content: "●"; }

        .message.thinking .message-prefix { color: #666666; }
        .message.thinking .message-prefix::before { content: "*"; }

        .message.tool .message-prefix { color: #00ff00; }
        .message.tool .message-prefix::before { content: "●"; }

        .message.system .message-prefix { color: #444444; }
        .message.system .message-prefix::before { content: "◆"; }

        .message.agent .message-prefix { color: #8b5cf6; }
        .message.agent .message-prefix::before { content: "🤖"; font-size: 1.2em; }

        .message.summary .message-prefix { color: #ffb000; }
        .message.summary .message-prefix::before { content: "📋"; }

        .message.tool_result .message-prefix { color: #666666; }
        .message.tool_result .message-prefix::before { content: "↳"; }

        /* Message content styling */
        .message.system {
            opacity: 0.7;
            font-size: 0.9em;
        }

        .message.thinking .message-content {
            color: #666666;
            font-style: italic;
        }

        .message.agent {
            background: rgba(139, 92, 246, 0.05);
            border-left: 2px solid #8b5cf6;
            padding-left: 4px;
        }

        /* Thinking block special handling */
        .thinking-indicator {
            color: #666666;
            font-style: italic;
            cursor: pointer;
            user-select: none;
        }

        .thinking-indicator:hover {
            color: #888888;
        }

        .thinking-content {
            color: #666666;
            font-style: italic;
            margin-left: 32px;
            padding: 8px 0;
            display: none;
        }

        .thinking-content.expanded {
            display: block;
        }

        /* Todo list rendering */
        .todo-list {
            margin: 10px 0 10px 32px;
            padding: 10px;
            border-left: 2px solid #666;
        }

        .todo-header {
            color: #ffb000;
            margin-bottom: 8px;
            font-weight: bold;
        }

        .todo-item {
            margin: 4px 0;
            display: flex;
            align-items: center;
        }

        .todo-checkbox {
            margin-right: 8px;
            flex-shrink: 0;
        }

        .todo-item.completed { color: #00ff00; }
        .todo-item.completed .todo-checkbox::before { content: "☑"; }

        .todo-item.in-progress { color: #ffb000; }
        .todo-item.in-progress .todo-checkbox::before { content: "⊡"; }

        .todo-item.pending { color: #888888; }
        .todo-item.pending .todo-checkbox::before { content: "☐"; }

        .todo-progress {
            margin-top: 8px;
            color: #ffb000;
            font-size: 0.9em;
        }

        /* Agent/sidechain messages */
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
            margin-left: 32px;
            display: block;
            margin-top: 4px;
        }

        /* Tool groups - Claude Code style */
        .tool-group {
            margin: 8px 0;
        }

        .tool-group-header {
            display: flex;
            align-items: center;
            cursor: pointer;
            user-select: none;
            padding: 2px 0;
        }

        .tool-group-header .message-prefix {
            color: #00ff00;
        }

        .tool-group-header .message-prefix::before {
            content: "●";
        }

        .tool-group-summary {
            color: #00ff00;
            margin-left: 8px;
        }

        .tool-group-count {
            color: #666666;
            font-size: 0.9em;
            margin-left: 8px;
        }

        .tool-group-content {
            margin-left: 32px;
            padding: 4px 0;
            border-left: 1px dashed #333;
            padding-left: 12px;
            display: none;
        }

        .tool-group.expanded .tool-group-content {
            display: block;
        }

        .tool-message {
            margin: 4px 0;
            display: flex;
            align-items: flex-start;
        }

        .tool-message .message-prefix {
            color: #00ff00;
        }

        .tool-message .message-prefix::before {
            content: "→";
        }

        /* Individual tool display in detailed mode */
        .tool-detail {
            margin: 8px 0 8px 32px;
            padding: 8px;
            background: #0a0a0a;
            border-left: 1px solid #333;
            font-size: 12px;
            color: #888;
        }

        .tool-detail-header {
            color: #00ff00;
            margin-bottom: 4px;
        }

        .tool-detail-content {
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }

        /* Code blocks */
        .code-block {
            background: #1a1a1a;
            border: 1px solid #333;
            padding: 10px;
            margin: 10px 0;
            overflow-x: auto;
            font-size: 12px;
        }

        /* Tool blocks (individual tools in groups) */
        .tool-block {
            margin: 4px 0;
            margin-left: 24px;
        }

        .tool-block .tool-header {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #888;
            font-size: 13px;
            padding: 2px 0;
        }

        .tool-block .tool-prefix {
            color: #00ff00;
        }

        .tool-block .tool-name {
            color: #888;
        }

        .tool-block .tool-details {
            margin-left: 24px;
            margin-top: 4px;
            padding: 8px;
            background: #0a0a0a;
            border-left: 1px solid #333;
            font-size: 12px;
            color: #666;
            max-height: 200px;
            overflow-y: auto;
        }

        .tool-block .tool-details pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        /* Loading */
        .loading {
            text-align: center;
            padding: 20px;
            color: #888;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #1a1a1a;
        }

        ::-webkit-scrollbar-thumb {
            background: #444;
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>▓▓▓ CLAUDE CODE CONVERSATIONS ▓▓▓</h1>
            <div class="stats" id="stats">
                Loading archive data...
            </div>
        </div>

        <div class="main-content">
            <div class="conversation-list">
                <div class="list-header">
                    <span>[CONVERSATIONS]</span>
                    <div class="list-controls">
                        <button class="small-btn" id="showSnapshotsBtn">Snapshots</button>
                        <button class="small-btn" id="showHiddenBtn">Hidden</button>
                        <button class="small-btn" id="saveChangesBtn">Save</button>
                    </div>
                </div>
                <div class="conversation-items" id="conversationList">
                    <div class="loading">Loading conversations...</div>
                </div>
            </div>

            <div id="conversationView" class="conversation-view">
                <div class="view-header">
                    <div id="viewTitle">[NO CONVERSATION SELECTED]</div>
                    <div class="view-controls">
                        <div class="control-group">
                            <button class="btn active" id="focusedModeBtn">FOCUSED MODE</button>
                            <button class="btn" id="detailedModeBtn">DETAILED MODE</button>
                        </div>
                        <div class="control-group">
                            <button class="btn" id="exportBtn">EXPORT</button>
                        </div>
                    </div>
                </div>
                <div id="messages" class="messages">
                    <div style="text-align: center; color: #888; margin-top: 50px;">Select a conversation to view</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load manifest from file instead of embedding
        let manifest = null;
        let currentConversation = null;
        let viewMode = 'focused';
        let showSnapshots = false;  // Toggle for showing snapshot files
        let showHidden = false;  // Toggle for showing hidden conversations
        let hiddenConversations = new Set();  // Track hidden conversations
        let hasUnsavedChanges = false;  // Track if there are unsaved changes

        // Initialize on startup
        async function initializeViewer() {
            try {
                // Fetch manifest.json from the same directory
                const response = await fetch('manifest.json');
                manifest = await response.json();
                hiddenConversations = new Set(manifest.hidden_conversations || []);
                displayStats();
                displayConversationList();
            } catch (error) {
                console.error('Failed to load manifest:', error);
                document.getElementById('conversationList').innerHTML = '<div style="color: #ff0000;">Failed to load manifest.json</div>';
            }
        }

        function displayStats() {
            const stats = document.getElementById('stats');
            stats.innerHTML = `
                Project: <span style="color: #ffb000">${manifest.project_path}</span> |
                Conversations: <span style="color: #ffb000">${manifest.conversation_count}</span> |
                Total Messages: <span style="color: #ffb000">${manifest.total_messages}</span> |
                Created: <span style="color: #888">${new Date(manifest.created_at).toLocaleString()}</span>
            `;
        }

        function displayConversationList() {
            const listContainer = document.getElementById('conversationList');
            listContainer.classList.remove('loading');
            listContainer.innerHTML = '';

            manifest.conversations.forEach(conv => {
                // Skip snapshots by default unless showing all
                if (!showSnapshots && conv.conversation_type === 'snapshot') {
                    return;
                }

                // Skip hidden conversations unless showing them
                const isHidden = hiddenConversations.has(conv.session_id);
                if (isHidden && !showHidden) {
                    return;
                }

                const item = document.createElement('div');
                item.className = 'conversation-item';
                if (conv.conversation_type === 'snapshot') {
                    item.className += ' snapshot';
                }
                if (isHidden) {
                    item.className += ' hidden';
                }
                item.onclick = (event) => {
                    // Don't load conversation if clicking on action buttons
                    if (!event.target.matches('button')) {
                        loadConversation(conv);
                    }
                };

                // Determine the marker based on conversation type
                let marker = '';
                if (conv.conversation_type === 'post_compaction') {
                    // Only mark true continuations
                    marker = '<span class="continuation-marker">[CONTINUATION]</span> ';
                } else if (conv.conversation_type === 'snapshot') {
                    marker = '<span class="snapshot-marker">[SNAPSHOT]</span> ';
                }
                // Note: auto_linked and auto_linked_with_internal_compaction get no marker

                // Format timestamps
                const firstDate = conv.first_timestamp ? new Date(conv.first_timestamp) : null;
                const lastDate = conv.last_timestamp ? new Date(conv.last_timestamp) : null;

                const formatDateTime = (date) => {
                    if (!date) return 'Unknown';
                    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                };

                // Create duration display if we have both dates
                let durationText = '';
                if (firstDate && lastDate && firstDate.getTime() !== lastDate.getTime()) {
                    const durationMs = lastDate.getTime() - firstDate.getTime();
                    const hours = Math.floor(durationMs / (1000 * 60 * 60));
                    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
                    if (hours > 0) {
                        durationText = ` (${hours}h ${minutes}m)`;
                    } else if (minutes > 0) {
                        durationText = ` (${minutes}m)`;
                    }
                }

                item.innerHTML = `
                    <div class="conversation-header">
                        <div class="session-id">${marker}${conv.session_id.substring(0, 12)}...</div>
                        <div class="conversation-title">${conv.title || 'Conversation'}</div>
                    </div>
                    <div class="conversation-meta">
                        <div class="meta-line">
                            <span class="meta-label">Messages:</span> ${conv.message_count}
                            ${durationText}
                        </div>
                        <div class="meta-line">
                            <span class="meta-label">Started:</span> ${formatDateTime(firstDate)}
                        </div>
                        ${lastDate && firstDate && lastDate.getTime() !== firstDate.getTime() ?
                            `<div class="meta-line"><span class="meta-label">Last:</span> ${formatDateTime(lastDate)}</div>`
                            : ''
                        }
                    </div>
                    <div class="conversation-actions">
                        <button onclick="toggleHideConversation('${conv.session_id}')">${isHidden ? 'SHOW' : 'HIDE'}</button>
                        <button onclick="exportConversation('${conv.session_id}')">EXPORT</button>
                    </div>
                `;

                listContainer.appendChild(item);
            });
        }

        async function loadConversation(convInfo) {
            // Update UI
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            event.currentTarget.classList.add('active');

            // Update view title with enhanced metadata
            const firstDate = convInfo.first_timestamp ? new Date(convInfo.first_timestamp) : null;
            const lastDate = convInfo.last_timestamp ? new Date(convInfo.last_timestamp) : null;

            const formatDateTime = (date) => {
                if (!date) return 'Unknown';
                return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            };

            let titleText = `${convInfo.title || 'Conversation'}`;
            let metaText = `${convInfo.message_count} messages`;

            if (firstDate) {
                metaText += ` • Started: ${formatDateTime(firstDate)}`;
                if (lastDate && lastDate.getTime() !== firstDate.getTime()) {
                    metaText += ` • Last: ${formatDateTime(lastDate)}`;
                }
            }

            document.getElementById('viewTitle').innerHTML = `
                <div class="view-title-main">${titleText}</div>
                <div class="view-title-meta">[${convInfo.session_id.substring(0, 12)}...] ${metaText}</div>
            `;

            const messagesContainer = document.getElementById('messages');
            messagesContainer.innerHTML = '<div class="loading">Loading conversation...</div>';

            try {
                // Load JSONL file
                const response = await fetch(`conversations/${convInfo.session_id}.jsonl`);
                const text = await response.text();
                const lines = text.trim().split('\\n').filter(line => line);

                currentConversation = lines.map(line => {
                    try {
                        return JSON.parse(line);
                    } catch (e) {
                        console.error('Failed to parse line:', e);
                        return null;
                    }
                }).filter(entry => entry !== null);

                displayMessages();
            } catch (error) {
                console.error('Failed to load conversation:', error);
                messagesContainer.innerHTML = '<div style="color: #ff4444">Error loading conversation</div>';
            }
        }

        function displayMessages() {
            const container = document.getElementById('messages');
            container.innerHTML = '';

            // Process conversations to group tool interactions and system messages
            let processedEntries = [];
            let i = 0;

            while (i < currentConversation.length) {
                const entry = currentConversation[i];

                // In focused mode, skip or collapse system messages
                if (viewMode === 'focused' && entry.type === 'system') {
                    // Skip system messages in focused mode
                    i++;
                    continue;
                }

                // Handle tool sequences: assistant tool_use -> user tool_result
                if (entry.type === 'assistant' && entry.message && Array.isArray(entry.message.content)) {
                    const hasToolUse = entry.message.content.some(b => b.type === 'tool_use');
                    const hasText = entry.message.content.some(b => b.type === 'text' && b.text && b.text.trim());
                    const hasThinking = entry.message.content.some(b => b.type === 'thinking');

                    if (hasToolUse) {
                        // Collect all tool interactions that follow
                        const toolSequence = [];
                        toolSequence.push(entry);

                        // Look ahead for tool results
                        let j = i + 1;
                        while (j < currentConversation.length) {
                            const nextEntry = currentConversation[j];
                            if (nextEntry.type === 'user' && (nextEntry.toolUseResult ||
                                (nextEntry.message && Array.isArray(nextEntry.message.content) &&
                                 nextEntry.message.content.some(b => b.type === 'tool_result')))) {
                                toolSequence.push(nextEntry);
                                j++;
                            } else {
                                break;
                            }
                        }

                        // If assistant message has text content too, split it
                        if (hasText || hasThinking) {
                            // Create a message with just text/thinking
                            const textEntry = {
                                ...entry,
                                message: {
                                    ...entry.message,
                                    content: entry.message.content.filter(b =>
                                        b.type === 'text' || b.type === 'thinking'
                                    )
                                }
                            };
                            processedEntries.push({type: 'message', data: textEntry});

                            // Create tool group with just tools
                            const toolEntry = {
                                ...entry,
                                message: {
                                    ...entry.message,
                                    content: entry.message.content.filter(b => b.type === 'tool_use')
                                }
                            };
                            processedEntries.push({
                                type: 'tool_group',
                                data: [toolEntry, ...toolSequence.slice(1)]
                            });
                        } else {
                            // Entire sequence is tools
                            processedEntries.push({type: 'tool_group', data: toolSequence});
                        }

                        i = j;
                        continue;
                    }
                }

                // Skip user messages that only contain tool results in focused mode
                if (viewMode === 'focused' && entry.type === 'user' && entry.toolUseResult && entry.message) {
                    const hasUserText = entry.message.content && (
                        typeof entry.message.content === 'string' ||
                        (Array.isArray(entry.message.content) &&
                         entry.message.content.some(b => b.type === 'text' && b.text && b.text.trim()))
                    );
                    if (!hasUserText) {
                        // This is a tool-result-only message, should have been captured above
                        i++;
                        continue;
                    }
                }

                // Regular message
                processedEntries.push({type: 'message', data: entry});
                i++;
            }

            // Render processed entries
            processedEntries.forEach((item, index) => {
                if (item.type === 'tool_group') {
                    renderToolGroup(container, item.data, index);
                } else {
                    renderMessage(container, item.data);
                }
            });
        }

        function renderToolGroup(container, toolSequence, groupIndex) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'tool-group';

            // Count tools
            let toolCount = 0;
            let toolNames = [];
            toolSequence.forEach(entry => {
                if (entry.message && Array.isArray(entry.message.content)) {
                    entry.message.content.forEach(block => {
                        if (block.type === 'tool_use') {
                            toolCount++;
                            toolNames.push(block.name || block.tool_name || 'Unknown');
                        }
                    });
                }
            });

            const isExpanded = viewMode === 'detailed';

            // Create collapsible header
            const headerDiv = document.createElement('div');
            headerDiv.className = `tool-group-header ${isExpanded ? 'expanded' : ''}`;
            headerDiv.innerHTML = `
                <span class="tool-indicator">▶</span>
                [TOOLS: ${toolCount}] ${toolNames.slice(0, 3).join(', ')}${toolNames.length > 3 ? '...' : ''}
            `;
            headerDiv.onclick = function() {
                const content = this.nextElementSibling;
                const indicator = this.querySelector('.tool-indicator');
                if (content.style.display === 'none' || !content.style.display) {
                    content.style.display = 'block';
                    indicator.textContent = '▼';
                    this.classList.add('expanded');
                } else {
                    content.style.display = 'none';
                    indicator.textContent = '▶';
                    this.classList.remove('expanded');
                }
            };

            // Create content div
            const contentDiv = document.createElement('div');
            contentDiv.className = 'tool-group-content';
            contentDiv.style.display = isExpanded ? 'block' : 'none';

            // Render each tool interaction
            toolSequence.forEach(entry => {
                const msgDiv = document.createElement('div');
                msgDiv.className = `message ${entry.type} tool-message`;

                if (entry.message && Array.isArray(entry.message.content)) {
                    entry.message.content.forEach(block => {
                        if (block.type === 'tool_use') {
                            const toolDiv = createToolBlock({
                                type: 'tool_use',
                                name: block.name || block.tool_name,
                                input: block.input || block.tool_input,
                                id: block.id
                            });
                            if (toolDiv) msgDiv.appendChild(toolDiv);
                        } else if (block.type === 'tool_result') {
                            const content = typeof block.content === 'string'
                                ? block.content
                                : JSON.stringify(block.content, null, 2);
                            const toolDiv = createToolBlock({
                                type: 'tool_result',
                                content: content,
                                id: block.tool_use_id
                            });
                            if (toolDiv) msgDiv.appendChild(toolDiv);
                        }
                    });
                }

                if (msgDiv.children.length > 0) {
                    contentDiv.appendChild(msgDiv);
                }
            });

            groupDiv.appendChild(headerDiv);
            groupDiv.appendChild(contentDiv);
            container.appendChild(groupDiv);
        }

        function renderMessage(container, entry) {
            // Classify the message type
            let isThinking = false;
            let isTodoWrite = false;
            let isAgent = entry.is_sidechain || entry.isSidechain;

            // Check for thinking blocks
            if (entry.type === 'assistant' && entry.message && Array.isArray(entry.message.content)) {
                isThinking = entry.message.content.some(block => block.type === 'thinking');
                // Check for TodoWrite tool
                isTodoWrite = entry.message.content.some(block =>
                    block.type === 'tool_use' && (block.name === 'TodoWrite' || block.tool_name === 'TodoWrite')
                );
            }

            // Process different message types
            if (entry.type === 'summary') {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message summary';
                messageDiv.innerHTML = `
                    <span class="message-prefix"></span>
                    <span class="message-content">
                        <strong>Continuation from previous conversation</strong>

${escapeHtml(entry.summary || 'No summary available')}
                    </span>
                `;
                container.appendChild(messageDiv);
            } else if (entry.message) {
                // Handle thinking blocks separately
                if (isThinking && entry.message.content) {
                    // Extract thinking content
                    const thinkingBlock = entry.message.content.find(b => b.type === 'thinking');
                    if (thinkingBlock) {
                        const thinkingDiv = document.createElement('div');
                        thinkingDiv.className = 'message thinking';
                        const isCollapsed = viewMode === 'focused';
                        thinkingDiv.innerHTML = `
                            <span class="message-prefix"></span>
                            <span class="message-content">
                                <span class="thinking-indicator" onclick="toggleThinking(this)">Thinking...</span>
                                <div class="thinking-content${!isCollapsed ? ' expanded' : ''}">${escapeHtml(thinkingBlock.thinking || '')}</div>
                            </span>
                        `;
                        container.appendChild(thinkingDiv);
                    }
                }

                // Handle main content (non-thinking, non-tool)
                const hasMainContent = entry.message.content && (
                    typeof entry.message.content === 'string' ||
                    (Array.isArray(entry.message.content) &&
                     entry.message.content.some(b => b.type === 'text' && b.text && b.text.trim()))
                );

                if (hasMainContent) {
                    const messageDiv = document.createElement('div');
                    // Determine the correct class
                    if (isAgent) {
                        messageDiv.className = 'message agent';
                    } else if (entry.type === 'system') {
                        messageDiv.className = 'message system';
                    } else {
                        messageDiv.className = `message ${entry.type}`;
                    }

                    let mainContent = '';
                    if (typeof entry.message.content === 'string') {
                        mainContent = entry.message.content;
                    } else if (Array.isArray(entry.message.content)) {
                        // Extract only text blocks
                        const textBlocks = entry.message.content
                            .filter(b => b.type === 'text')
                            .map(b => b.text || '')
                            .join('\\n\\n');
                        mainContent = textBlocks;
                    }

                    // Add agent label if it's a sidechain message
                    let agentLabel = '';
                    if (isAgent) {
                        agentLabel = '<span class="agent-label">[Agent]</span> ';
                    }

                    messageDiv.innerHTML = `
                        <span class="message-prefix"></span>
                        <span class="message-content">${agentLabel}${escapeHtml(mainContent)}</span>
                    `;
                    container.appendChild(messageDiv);
                }

                // Handle TodoWrite tool specially
                if (isTodoWrite && entry.message.content) {
                    handleTodoWrite(container, entry);
                }
            } else if (entry.type === 'system') {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message system';
                messageDiv.innerHTML = `
                    <span class="message-prefix"></span>
                    <span class="message-content">${escapeHtml(entry.content || '')}</span>
                `;
                container.appendChild(messageDiv);
            }
        }

        function toggleThinking(element) {
            const content = element.nextElementSibling;
            content.classList.toggle('expanded');
        }

        function handleTodoWrite(container, entry) {
            // Find the next tool result that contains the todo data
            let todoData = null;
            const entryIndex = currentConversation.indexOf(entry);
            for (let i = entryIndex + 1; i < currentConversation.length; i++) {
                const nextEntry = currentConversation[i];
                if (nextEntry.type === 'user' && nextEntry.message && Array.isArray(nextEntry.message.content)) {
                    const toolResult = nextEntry.message.content.find(b => b.type === 'tool_result');
                    if (toolResult && toolResult.content) {
                        try {
                            // Try to parse the todo data
                            const content = typeof toolResult.content === 'string' ?
                                toolResult.content : JSON.stringify(toolResult.content);
                            if (content.includes('todos')) {
                                // Extract todo items from the content
                                const match = content.match(/\\[\\{.*?\\}\\]/s);
                                if (match) {
                                    todoData = JSON.parse(match[0]);
                                }
                            }
                        } catch (e) {
                            console.error('Failed to parse todo data:', e);
                        }
                        break;
                    }
                }
            }

            if (todoData && Array.isArray(todoData)) {
                renderTodoList(container, todoData);
            }
        }

        function createToolBlock(tool) {
            const toolDiv = document.createElement('div');
            toolDiv.className = 'tool-block';

            let html = '';
            if (tool.type === 'tool_use') {
                const toolName = tool.name || 'Unknown Tool';
                const inputStr = JSON.stringify(tool.input || {}, null, 2);
                html = `
                    <div class="tool-header" onclick="toggleToolDetails(this)">
                        <span class="tool-prefix">●</span>
                        <span class="tool-name">${escapeHtml(toolName)}</span>
                    </div>
                    <div class="tool-details">
                        <pre>${escapeHtml(inputStr)}</pre>
                    </div>
                `;
            } else if (tool.type === 'tool_result') {
                const content = tool.content || '';
                // Truncate very long results
                const displayContent = content.length > 500
                    ? content.substring(0, 500) + '\\n... [truncated]'
                    : content;
                const resultLabel = tool.id ? ('Result for ' + tool.id.substring(0, 8) + '...') : 'Result';
                html = `
                    <div class="tool-header" onclick="toggleToolDetails(this)">
                        <span class="tool-prefix">↳</span>
                        <span class="tool-name">${resultLabel}</span>
                    </div>
                    <div class="tool-details">
                        <pre>${escapeHtml(displayContent)}</pre>
                    </div>
                `;
            }

            toolDiv.innerHTML = html;

            // Start collapsed in focused mode
            if (viewMode === 'focused') {
                const details = toolDiv.querySelector('.tool-details');
                if (details) details.style.display = 'none';
            }

            return toolDiv;
        }

        function toggleToolDetails(header) {
            const details = header.nextElementSibling;
            if (details) {
                details.classList.toggle('expanded');
                details.style.display = details.style.display === 'none' ? 'block' : 'none';
            }
        }

        function renderTodoList(container, todos) {
            const todoDiv = document.createElement('div');
            todoDiv.className = 'todo-list';

            let completed = todos.filter(t => t.status === 'completed').length;
            let inProgress = todos.filter(t => t.status === 'in_progress').length;
            let total = todos.length;
            let percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

            let html = '<div class="todo-header">📋 Task List:</div>';

            todos.forEach(todo => {
                const statusClass = todo.status.replace('_', '-');
                const displayText = todo.activeForm && todo.status === 'in_progress' ?
                    todo.activeForm : (todo.content || '');
                html += `
                    <div class="todo-item ${statusClass}">
                        <span class="todo-checkbox"></span>
                        <span>${escapeHtml(displayText)}</span>
                    </div>
                `;
            });

            html += `<div class="todo-progress">Progress: ${completed}/${total} completed (${percentage}%)</div>`;

            todoDiv.innerHTML = html;
            container.appendChild(todoDiv);
        }

        function processContentBlocks(blocks) {
            const textBlocks = blocks
                .filter(b => b.type === 'text' || b.type === 'thinking')
                .map(b => b.text || b.thinking || '')
                .join('\\n\\n');
            return textBlocks;
        }

        function processToolResultContent(content) {
            if (typeof content === 'string') {
                return content;
            } else if (Array.isArray(content)) {
                // Handle tool_result blocks in the content
                const results = content
                    .filter(b => b.type === 'tool_result')
                    .map(b => {
                        if (typeof b.content === 'string') {
                            return b.content;
                        } else if (Array.isArray(b.content)) {
                            // Handle nested content arrays
                            return b.content
                                .filter(c => c.type === 'text')
                                .map(c => c.text || '')
                                .join('\\n');
                        }
                        return '';
                    })
                    .join('\\n\\n');
                return results || processContentBlocks(content);
            }
            return '';
        }


        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // View mode toggles
        document.getElementById('focusedModeBtn').addEventListener('click', () => {
            viewMode = 'focused';
            document.getElementById('focusedModeBtn').classList.add('active');
            document.getElementById('detailedModeBtn').classList.remove('active');
            if (currentConversation) {
                displayMessages();
            }
        });

        document.getElementById('detailedModeBtn').addEventListener('click', () => {
            viewMode = 'detailed';
            document.getElementById('detailedModeBtn').classList.add('active');
            document.getElementById('focusedModeBtn').classList.remove('active');
            if (currentConversation) {
                displayMessages();
            }
        });

        // Hide/Show functionality
        function toggleHideConversation(sessionId) {
            if (hiddenConversations.has(sessionId)) {
                hiddenConversations.delete(sessionId);
            } else {
                hiddenConversations.add(sessionId);
            }
            hasUnsavedChanges = true;
            updateSaveButton();
            displayConversationList();
        }

        function toggleShowSnapshots() {
            showSnapshots = !showSnapshots;
            const btn = document.getElementById('showSnapshotsBtn');
            if (showSnapshots) {
                btn.classList.add('active');
                btn.textContent = 'All';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Snapshots';
            }
            displayConversationList();
        }

        function toggleShowHidden() {
            showHidden = !showHidden;
            const btn = document.getElementById('showHiddenBtn');
            if (showHidden) {
                btn.classList.add('active');
                btn.textContent = 'All';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Hidden';
            }
            displayConversationList();
        }

        function updateSaveButton() {
            const btn = document.getElementById('saveChangesBtn');
            if (hasUnsavedChanges) {
                btn.classList.add('active');
                btn.textContent = 'SAVE*';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Save';
            }
        }

        async function saveChanges() {
            if (!hasUnsavedChanges) return;

            try {
                // Update manifest with hidden conversations
                manifest.hidden_conversations = Array.from(hiddenConversations);
                manifest.user_metadata = manifest.user_metadata || {};
                manifest.user_metadata.last_modified = new Date().toISOString();

                // Save updated manifest and repack archive
                const manifestBlob = new Blob([JSON.stringify(manifest, null, 2)],
                    { type: 'application/json' });
                const formData = new FormData();
                formData.append('manifest', manifestBlob, 'manifest.json');

                // Show saving indicator
                const saveBtn = document.getElementById('saveChangesBtn');
                const originalText = saveBtn.textContent;
                saveBtn.textContent = 'SAVING...';
                saveBtn.disabled = true;

                const response = await fetch('/api/save-and-repack', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const result = await response.json();
                    hasUnsavedChanges = false;
                    updateSaveButton();
                    if (result.archive) {
                        alert(`Changes saved and archive repacked successfully!\\nArchive: ${result.archive}`);
                    } else {
                        alert(result.message || 'Changes saved successfully!');
                    }
                } else {
                    const errorResult = await response.json().catch(() => ({}));
                    throw new Error(errorResult.error || 'Failed to save changes');
                }
            } catch (error) {
                console.error('Save error:', error);
                alert('Failed to save changes. Changes are preserved in browser session only.');
            } finally {
                // Reset save button
                const saveBtn = document.getElementById('saveChangesBtn');
                saveBtn.disabled = false;
                updateSaveButton();
            }
        }

        function exportConversation(sessionId) {
            const conv = manifest.conversations.find(c => c.session_id === sessionId);
            if (!conv) return;

            // Create markdown export
            let markdown = `# ${conv.title || 'Conversation'}\\n\\n`;
            markdown += `**Session ID:** ${conv.session_id}\\n`;
            markdown += `**Messages:** ${conv.message_count}\\n`;
            if (conv.first_timestamp) {
                markdown += `**Started:** ${new Date(conv.first_timestamp).toLocaleString()}\\n`;
            }
            if (conv.last_timestamp && conv.last_timestamp !== conv.first_timestamp) {
                markdown += `**Last Activity:** ${new Date(conv.last_timestamp).toLocaleString()}\\n`;
            }
            markdown += `\\n---\\n\\n`;

            // Add conversation messages if currently loaded
            // Check if this is the currently loaded conversation
            const isCurrentlyLoaded = currentConversation &&
                document.querySelector('.conversation-item.active')?.querySelector('.session-id')?.textContent?.includes(conv.session_id.substring(0, 12));

            if (isCurrentlyLoaded && currentConversation) {
                // Process conversation entries similar to the viewer display logic
                let processedEntries = [];
                let i = 0;

                while (i < currentConversation.length) {
                    const entry = currentConversation[i];

                    // Handle tool sequences: assistant tool_use -> user tool_result
                    if (entry.type === 'assistant' && entry.message && Array.isArray(entry.message.content)) {
                        const hasToolUse = entry.message.content.some(b => b.type === 'tool_use');
                        const hasText = entry.message.content.some(b => b.type === 'text' && b.text && b.text.trim());
                        const hasThinking = entry.message.content.some(b => b.type === 'thinking');

                        if (hasToolUse) {
                            // Collect all tool interactions that follow
                            const toolSequence = [];
                            toolSequence.push(entry);

                            // Look ahead for tool results
                            let j = i + 1;
                            while (j < currentConversation.length) {
                                const nextEntry = currentConversation[j];
                                if (nextEntry.type === 'user' && (nextEntry.toolUseResult ||
                                    (nextEntry.message && Array.isArray(nextEntry.message.content) &&
                                     nextEntry.message.content.some(b => b.type === 'tool_result')))) {
                                    toolSequence.push(nextEntry);
                                    j++;
                                } else {
                                    break;
                                }
                            }

                            // If assistant message has text content too, split it
                            if (hasText || hasThinking) {
                                // Create a message with just text/thinking
                                const textEntry = {
                                    ...entry,
                                    message: {
                                        ...entry.message,
                                        content: entry.message.content.filter(b =>
                                            b.type === 'text' || b.type === 'thinking'
                                        )
                                    }
                                };
                                processedEntries.push({type: 'message', data: textEntry});

                                // Create tool group with just tools
                                const toolEntry = {
                                    ...entry,
                                    message: {
                                        ...entry.message,
                                        content: entry.message.content.filter(b => b.type === 'tool_use')
                                    }
                                };
                                processedEntries.push({
                                    type: 'tool_group',
                                    data: [toolEntry, ...toolSequence.slice(1)]
                                });
                            } else {
                                // Entire sequence is tools
                                processedEntries.push({type: 'tool_group', data: toolSequence});
                            }

                            i = j;
                            continue;
                        }
                    }

                    // Skip user messages that only contain tool results
                    if (entry.type === 'user' && entry.toolUseResult && entry.message) {
                        const hasUserText = entry.message.content && (
                            typeof entry.message.content === 'string' ||
                            (Array.isArray(entry.message.content) &&
                             entry.message.content.some(b => b.type === 'text' && b.text && b.text.trim()))
                        );
                        if (!hasUserText) {
                            // This is a tool-result-only message, should have been captured above
                            i++;
                            continue;
                        }
                    }

                    // Regular message
                    processedEntries.push({type: 'message', data: entry});
                    i++;
                }

                // Export based on current view mode
                processedEntries.forEach(item => {
                    if (item.type === 'tool_group') {
                        if (viewMode === 'detailed') {
                            // Include full tool details in detailed mode
                            markdown += `\\n## Tool Usage\\n\\n`;
                            item.data.forEach(entry => {
                                if (entry.message && Array.isArray(entry.message.content)) {
                                    entry.message.content.forEach(block => {
                                        if (block.type === 'tool_use') {
                                            markdown += `**Tool:** ${block.name || block.tool_name}\\n`;
                                            markdown += `\\`\\`\\`json\\n${JSON.stringify(block.input || block.tool_input, null, 2)}\\n\\`\\`\\`\\n\\n`;
                                        } else if (block.type === 'tool_result') {
                                            const content = typeof block.content === 'string'
                                                ? block.content
                                                : JSON.stringify(block.content, null, 2);
                                            markdown += `**Tool Result:**\\n`;
                                            markdown += `\\`\\`\\`\\n${content}\\n\\`\\`\\`\\n\\n`;
                                        }
                                    });
                                }
                            });
                        } else {
                            // Focused mode - just summarize tools
                            let toolCount = 0;
                            let toolNames = [];
                            item.data.forEach(entry => {
                                if (entry.message && Array.isArray(entry.message.content)) {
                                    entry.message.content.forEach(block => {
                                        if (block.type === 'tool_use') {
                                            toolCount++;
                                            toolNames.push(block.name || block.tool_name || 'Unknown');
                                        }
                                    });
                                }
                            });
                            markdown += `\\n*[Used ${toolCount} tool(s): ${toolNames.slice(0, 3).join(', ')}${toolNames.length > 3 ? '...' : ''}]*\\n\\n`;
                        }
                    } else {
                        // Regular message
                        const entry = item.data;
                        if (entry.type === 'summary') {
                            markdown += `## Summary\\n\\n${entry.summary || 'No summary available'}\\n\\n`;
                        } else if (entry.message) {
                            const role = entry.message.role || entry.type;
                            const timestamp = entry.timestamp ?
                                new Date(entry.timestamp).toLocaleTimeString() : '';
                            markdown += `### ${role.toUpperCase()} ${timestamp}\\n\\n`;

                            if (typeof entry.message.content === 'string') {
                                markdown += `${entry.message.content}\\n\\n`;
                            } else if (Array.isArray(entry.message.content)) {
                                entry.message.content.forEach(block => {
                                    if (block.type === 'text') {
                                        markdown += `${block.text || ''}\\n\\n`;
                                    } else if (block.type === 'thinking') {
                                        if (viewMode === 'detailed') {
                                            markdown += `*[Thinking] ${block.thinking || ''}*\\n\\n`;
                                        }
                                        // In focused mode, skip thinking blocks
                                    }
                                });
                            }
                        }
                    }
                });
            } else {
                markdown += `*Note: Load this conversation in the viewer to include full message content in export.*\\n\\n`;
            }

            // Create a safe filename from title and session ID
            const safeTitle = (conv.title || 'Conversation')
                .replace(/[^a-zA-Z0-9\\s-]/g, '') // Remove special characters
                .replace(/\\s+/g, '_') // Replace spaces with underscores
                .substring(0, 50); // Limit length
            const shortSessionId = conv.session_id.substring(0, 8);
            const filename = `${safeTitle}_${shortSessionId}.md`;

            // Download as file
            const blob = new Blob([markdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        // Event listeners
        document.getElementById('showSnapshotsBtn').addEventListener('click', toggleShowSnapshots);
        document.getElementById('showHiddenBtn').addEventListener('click', toggleShowHidden);
        document.getElementById('saveChangesBtn').addEventListener('click', saveChanges);
        document.getElementById('exportBtn').addEventListener('click', () => {
            const activeItem = document.querySelector('.conversation-item.active');
            if (activeItem && currentConversation) {
                // Extract session ID from the active conversation item
                const sessionIdElement = activeItem.querySelector('.session-id');
                if (sessionIdElement) {
                    const sessionIdText = sessionIdElement.textContent;
                    // Find the full session ID from manifest
                    const conv = manifest.conversations.find(c =>
                        sessionIdText.includes(c.session_id.substring(0, 12))
                    );
                    if (conv) {
                        exportConversation(conv.session_id);
                    }
                }
            } else {
                alert('Please select a conversation first');
            }
        });

        // Start loading when page loads
        window.addEventListener('DOMContentLoaded', initializeViewer);
    </script>
</body>
</html>"""

        # No longer replacing MANIFEST_DATA since we're fetching manifest.json
        return html_template

    def save_viewer(self, output_path: Path, manifest: dict[str, Any]) -> None:
        """Save the viewer HTML file.

        Args:
            output_path: Path to save the HTML file
            manifest: The archive manifest data
        """
        html_content = self.generate_viewer(manifest)
        output_path.write_text(html_content, encoding="utf-8")
