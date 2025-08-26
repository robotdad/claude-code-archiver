"""Generator for terminal-style HTML viewer."""

import json
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
        # Embed manifest JSON
        manifest_json = json.dumps(manifest)

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

        .conversation-item .session-id {
            color: #00ff00;
            font-weight: bold;
        }

        .conversation-item .meta {
            color: #888;
            font-size: 12px;
            margin-top: 5px;
        }

        .conversation-item .continuation-marker {
            color: #ffb000;
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

        .view-controls {
            margin-top: 10px;
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

        /* Messages */
        .messages {
            padding: 20px;
            overflow-y: auto;
            flex: 1;
        }

        .message {
            margin-bottom: 20px;
            padding: 10px;
            border-left: 3px solid #333;
        }

        .message.user {
            border-left-color: #00ff00;
            background: #0a1a0a;
        }

        .message.assistant {
            border-left-color: #0088ff;
            background: #0a0a1a;
        }

        .message.system {
            border-left-color: #666;
            background: #1a1a1a;
            color: #888;
        }

        .message.summary {
            border-left-color: #ffb000;
            background: #1a1a0a;
        }

        .message.tool_result {
            border-left-color: #888;
            background: #0f0f0f;
            color: #888;
        }

        .message-header {
            margin-bottom: 10px;
            font-weight: bold;
            color: #ffb000;
        }

        .message-content {
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        /* Tool groups - collapsed tool sequences */
        .tool-group {
            margin: 15px 0;
            border: 1px solid #333;
            background: #0a0a0a;
            border-radius: 4px;
        }

        .tool-group-header {
            padding: 10px 15px;
            background: #151515;
            color: #888;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            transition: background 0.2s;
        }

        .tool-group-header:hover {
            background: #1a1a1a;
        }

        .tool-group-header .tool-indicator {
            display: inline-block;
            width: 15px;
            transition: transform 0.2s;
        }

        .tool-group-header.expanded .tool-indicator {
            transform: rotate(90deg);
        }

        .tool-group-content {
            border-top: 1px solid #333;
            padding: 10px;
            background: #0f0f0f;
        }

        .tool-message {
            margin: 5px 0;
            border-left-width: 2px;
        }

        /* Tool blocks */
        .tool-block {
            margin: 10px 0;
            border: 1px solid #444;
            background: #1a1a1a;
        }

        .tool-header {
            padding: 5px 10px;
            background: #222;
            color: #ffb000;
            cursor: pointer;
            font-size: 12px;
        }

        .tool-header:before {
            content: "▶ ";
        }

        .tool-header.expanded:before {
            content: "▼ ";
        }

        .tool-content {
            padding: 10px;
            display: none;
            font-size: 12px;
            color: #888;
            max-height: 300px;
            overflow-y: auto;
        }

        .tool-content.expanded {
            display: block;
        }

        .tool-result {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #333;
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
                    [CONVERSATIONS]
                </div>
                <div class="conversation-items" id="conversationList">
                    <div class="loading">Loading conversations...</div>
                </div>
            </div>

            <div id="conversationView" class="conversation-view">
                <div class="view-header">
                    <div id="viewTitle">[NO CONVERSATION SELECTED]</div>
                    <div class="view-controls">
                        <button class="btn active" id="focusedModeBtn">FOCUSED MODE</button>
                        <button class="btn" id="detailedModeBtn">DETAILED MODE</button>
                    </div>
                </div>
                <div id="messages" class="messages">
                    <div style="text-align: center; color: #888; margin-top: 50px;">Select a conversation to view</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Embed manifest data directly
        let manifest = MANIFEST_DATA;
        let currentConversation = null;
        let viewMode = 'focused';

        // Initialize on startup
        function initializeViewer() {
            displayStats();
            displayConversationList();
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
                const item = document.createElement('div');
                item.className = 'conversation-item';
                item.onclick = () => loadConversation(conv);

                const continuation = conv.starts_with_summary ?
                    '<span class="continuation-marker">[CONTINUATION]</span> ' : '';

                item.innerHTML = `
                    <div class="session-id">${continuation}${conv.session_id.substring(0, 12)}...</div>
                    <div class="meta">
                        Messages: ${conv.message_count} |
                        ${conv.first_timestamp ? new Date(conv.first_timestamp).toLocaleDateString() : 'Unknown date'}
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

            // No need to add active class anymore - always visible
            document.getElementById('viewTitle').textContent =
                `[SESSION: ${convInfo.session_id}] - ${convInfo.message_count} messages`;

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

            // Process conversations to group tool interactions
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
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${entry.type}`;

            let header = '';
            let mainContent = '';

            if (entry.type === 'summary') {
                header = '[SUMMARY - Continuation from previous conversation]';
                mainContent = entry.summary || 'No summary available';
            } else if (entry.type === 'system') {
                header = '[SYSTEM]';
                mainContent = entry.content || '';
            } else if (entry.message) {
                const role = entry.message.role?.toUpperCase() || entry.type?.toUpperCase();
                const timestamp = entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : '';
                header = `[${role}] ${timestamp}`;

                // Process message content
                if (typeof entry.message.content === 'string') {
                    mainContent = entry.message.content;
                } else if (Array.isArray(entry.message.content)) {
                    const textBlocks = [];
                    entry.message.content.forEach(block => {
                        if (block.type === 'text') {
                            textBlocks.push(block.text || '');
                        } else if (block.type === 'thinking') {
                            textBlocks.push(`[Thinking] ${block.thinking || ''}`);
                        }
                    });
                    mainContent = textBlocks.join('\\n\\n');
                }
            }

            // Build the message HTML
            let messageHTML = `<div class="message-header">${header}</div>`;
            if (mainContent) {
                messageHTML += `<div class="message-content">${escapeHtml(mainContent)}</div>`;
            }

            messageDiv.innerHTML = messageHTML;
            container.appendChild(messageDiv);
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

        function createToolBlock(tool) {
            const toolDiv = document.createElement('div');
            toolDiv.className = 'tool-block';
            const shouldHide = viewMode === 'focused';

            if (tool.type === 'tool_use') {
                const toolName = tool.name || 'Unknown Tool';
                const inputStr = JSON.stringify(tool.input || {}, null, 2);

                toolDiv.innerHTML = `
                    <div class="tool-header ${shouldHide ? '' : 'expanded'}" onclick="toggleTool(this)">
                        [TOOL:${toolName}]
                    </div>
                    <div class="tool-content ${shouldHide ? '' : 'expanded'}">
                        <pre>${escapeHtml(inputStr)}</pre>
                    </div>
                `;
            } else if (tool.type === 'tool_result') {
                const content = tool.content || '';
                // Truncate very long results in focused mode
                const displayContent = shouldHide && content.length > 500
                    ? content.substring(0, 500) + '\\n... [truncated]'
                    : content;

                toolDiv.innerHTML = `
                    <div class="tool-header ${shouldHide ? '' : 'expanded'}" onclick="toggleTool(this)">
                        [RESULT${tool.id ? ` for ${tool.id.substring(0, 8)}...` : ''}]
                    </div>
                    <div class="tool-content ${shouldHide ? '' : 'expanded'}">
                        <pre>${escapeHtml(displayContent)}</pre>
                    </div>
                `;
            }

            return toolDiv;
        }

        function toggleTool(header) {
            header.classList.toggle('expanded');
            header.nextElementSibling.classList.toggle('expanded');
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

        // Start loading when page loads
        window.addEventListener('DOMContentLoaded', initializeViewer);
    </script>
</body>
</html>"""

        # Replace manifest placeholder with actual data
        html_template = html_template.replace("MANIFEST_DATA", manifest_json)

        return html_template

    def save_viewer(self, output_path: Path, manifest: dict[str, Any]) -> None:
        """Save the viewer HTML file.

        Args:
            output_path: Path to save the HTML file
            manifest: The archive manifest data
        """
        html_content = self.generate_viewer(manifest)
        output_path.write_text(html_content, encoding="utf-8")
