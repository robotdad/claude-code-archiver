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
    <title>Claude Code Archive</title>
    <!-- Markdown rendering and syntax highlighting -->
    <script src="https://cdn.jsdelivr.net/npm/marked@9.1.6/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/highlight.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            /* Primary colors */
            --bg-primary: #1a1a1a;        /* Main background */
            --bg-secondary: #2a2a2a;      /* Panel backgrounds */
            --bg-tertiary: #3a3a3a;       /* Interactive elements */

            /* Text colors */
            --text-primary: #e1e1e1;      /* Main text */
            --text-secondary: #a1a1a1;    /* Secondary text */
            --text-muted: #717171;        /* Muted text */

            /* Accent colors */
            --accent-green: #7dd87d;      /* Soft green accent */
            --accent-green-muted: #5bb85b; /* Darker green for borders */
            --accent-orange: #ff9f40;     /* Warning/highlight color */

            /* Border colors */
            --border-primary: #404040;    /* Main borders */
            --border-secondary: #2a2a2a;  /* Subtle borders */

            /* State colors */
            --hover-bg: #3a3a3a;         /* Hover states */
            --active-bg: #4a4a4a;        /* Active states */
        }

        body {
            font-family: system-ui, -apple-system, 'SF Pro Display', 'Segoe UI', 'Roboto', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 20px;
            line-height: 1.6;
            font-size: 14px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            height: 100vh;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        /* Unified Header */
        .unified-header {
            border: 1px solid var(--accent-green-muted);
            padding: 20px;
            margin-bottom: 20px;
            background: var(--bg-secondary);
            border-radius: 12px;
            font-family: system-ui, -apple-system, sans-serif;
        }

        .header-main {
            margin-bottom: 16px;
        }

        .project-title {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent-orange);
            margin: 0 0 6px 0;
            letter-spacing: -0.5px;
        }

        .project-path {
            color: var(--text-secondary);
            font-size: 14px;
            font-family: 'SF Mono', 'Monaco', monospace;
        }

        .statistics-inline {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .stat-group {
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 8px 12px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            min-width: 80px;
        }

        .stat-value {
            font-size: 18px;
            font-weight: 700;
            color: var(--accent-green);
            margin-bottom: 2px;
        }

        .stat-label {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .type-breakdown {
            color: var(--accent-green);
            font-size: 13px;
            line-height: 1.6;
            margin: 12px 0 0 0;
            padding: 12px;
            background: var(--bg-tertiary);
            border-radius: 8px;
        }

        .type-item {
            margin: 3px 0;
            font-family: system-ui, -apple-system, sans-serif;
        }

        .type-count {
            color: var(--text-primary);
            font-weight: 600;
        }

        .type-status {
            color: var(--text-muted);
            font-size: 11px;
        }

        .filter-controls {
            margin-top: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .filter-btn {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-primary);
            color: var(--text-secondary);
            padding: 8px 16px;
            cursor: pointer;
            font-family: inherit;
            font-size: 12px;
            transition: all 0.2s ease;
            border-radius: 6px;
            font-weight: 500;
        }

        .filter-btn:hover {
            background: var(--hover-bg);
            color: var(--text-primary);
            border-color: var(--accent-green-muted);
        }

        .filter-btn.active {
            background: var(--accent-green);
            color: var(--bg-primary);
            border-color: var(--accent-green);
            font-weight: 600;
        }

        .filter-btn.warning {
            border-color: var(--accent-orange);
            color: var(--accent-orange);
        }

        .filter-btn.warning:hover {
            background: var(--accent-orange);
            color: var(--bg-primary);
        }

        /* Main Layout */
        .main-content {
            display: flex;
            flex: 1;
            overflow: hidden;
            gap: 20px;
            min-height: 0;
        }

        /* Conversation List */
        .conversation-list {
            width: 380px;
            border: 1px solid var(--accent-green-muted);
            background: var(--bg-secondary);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border-radius: 8px;
        }

        .list-header {
            background: var(--bg-tertiary);
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-primary);
            color: var(--accent-orange);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            font-size: 13px;
        }

        .list-controls {
            display: flex;
            gap: 5px;
        }

        .small-btn {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            color: var(--text-secondary);
            padding: 4px 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            border-radius: 4px;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .small-btn:hover {
            background: var(--hover-bg);
            color: var(--text-primary);
            border-color: var(--accent-green-muted);
        }

        .small-btn.active {
            background: var(--accent-orange);
            color: var(--bg-primary);
            border-color: var(--accent-orange);
        }

        .small-btn:disabled {
            background: var(--bg-primary);
            color: var(--text-muted);
            border-color: var(--border-secondary);
            cursor: not-allowed;
            opacity: 0.6;
        }

        .conversation-items {
            overflow-y: auto;
            flex: 1;
        }

        .conversation-item {
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
            background: transparent;
        }

        .conversation-item[data-display-default="false"] {
            display: none;
        }

        .conversation-item:hover {
            background: var(--hover-bg);
        }

        .conversation-item.active {
            background: var(--active-bg);
            border-left: 4px solid var(--accent-orange);
        }

        .conversation-item .conversation-header {
            margin-bottom: 8px;
        }

        .conversation-item .session-id {
            color: var(--accent-green);
            font-weight: 600;
            font-size: 11px;
            font-family: 'SF Mono', 'Monaco', monospace;
        }

        .conversation-item .conversation-title {
            color: var(--text-primary);
            font-weight: 500;
            margin-top: 4px;
            font-size: 14px;
            line-height: 1.4;
        }

        .conversation-item .conversation-meta {
            color: var(--text-secondary);
            font-size: 12px;
        }

        .conversation-item .meta-line {
            margin-bottom: 3px;
        }

        .conversation-item .meta-label {
            color: var(--text-muted);
            font-weight: 600;
        }

        .conversation-item .continuation-marker {
            color: var(--accent-orange);
            font-size: 10px;
            font-weight: 600;
        }

        .conversation-item .snapshot-marker {
            color: var(--text-muted);
            font-size: 10px;
            font-weight: 600;
        }

        .conversation-item.hidden {
            opacity: 0.6;
            background: var(--bg-primary) !important;
        }

        .conversation-item .conversation-actions {
            margin-top: 5px;
            display: none;
        }

        .conversation-item:hover .conversation-actions {
            display: block;
        }

        .conversation-actions button {
            background: transparent;
            border: 1px solid var(--border-primary);
            color: var(--text-secondary);
            padding: 2px 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 10px;
            margin-right: 6px;
            border-radius: 3px;
            transition: all 0.2s ease;
        }

        .conversation-actions button:hover {
            color: var(--accent-orange);
            border-color: var(--accent-orange);
            background: var(--hover-bg);
        }

        /* Conversation View */
        .conversation-view {
            flex: 1;
            border: 1px solid var(--accent-green-muted);
            background: var(--bg-secondary);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border-radius: 8px;
        }

        .view-header {
            background: var(--bg-tertiary);
            padding: 15px;
            border-bottom: 1px solid var(--border-primary);
        }

        .view-title-main {
            font-size: 18px;
            color: var(--text-primary);
            margin-bottom: 6px;
            font-weight: 600;
        }

        .view-title-meta {
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 400;
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
            background: var(--bg-secondary);
            border: 1px solid var(--accent-green-muted);
            color: var(--accent-green);
            padding: 8px 16px;
            cursor: pointer;
            margin-right: 12px;
            font-family: inherit;
            font-size: 12px;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .btn:hover {
            background: var(--hover-bg);
            border-color: var(--accent-green);
        }

        .btn.active {
            background: var(--accent-green);
            color: var(--bg-primary);
            border-color: var(--accent-green);
            font-weight: 600;
        }

        /* Messages - Claude Code Style */
        .messages {
            padding: 20px;
            overflow-y: auto;
            flex: 1;
            font-family: system-ui, -apple-system, 'SF Mono', 'Monaco', 'Cascadia Code', 'Fira Code', 'Consolas', 'Liberation Mono', monospace;
            line-height: 1.6;
            background: var(--bg-primary);
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
        .message.user .message-prefix { color: var(--accent-green); }
        .message.user .message-prefix::before { content: ">"; }

        .message.assistant .message-prefix { color: var(--text-primary); }
        .message.assistant .message-prefix::before { content: "●"; }

        .message.thinking .message-prefix { color: var(--text-muted); }
        .message.thinking .message-prefix::before { content: "*"; }

        .message.tool .message-prefix { color: var(--accent-green); }
        .message.tool .message-prefix::before { content: "●"; }

        .message.system .message-prefix { color: var(--text-muted); }
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
            color: var(--text-muted);
            font-style: italic;
        }

        .message.agent {
            background: rgba(139, 92, 246, 0.05);
            border-left: 2px solid #8b5cf6;
            padding-left: 4px;
        }

        /* Thinking block special handling */
        .thinking-indicator {
            color: var(--text-muted);
            font-style: italic;
            cursor: pointer;
            user-select: none;
            transition: color 0.2s ease;
        }

        .thinking-indicator:hover {
            color: var(--text-secondary);
        }

        .thinking-content {
            color: var(--text-muted);
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
            margin: 12px 0 12px 32px;
            padding: 12px;
            border-left: 3px solid var(--accent-orange);
            background: var(--bg-secondary);
            border-radius: 6px;
        }

        .todo-header {
            color: var(--accent-orange);
            margin-bottom: 10px;
            font-weight: 600;
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

        /* Markdown Content Styles */
        .markdown-content {
            line-height: 1.6;
        }

        .markdown-content h1,
        .markdown-content h2,
        .markdown-content h3,
        .markdown-content h4,
        .markdown-content h5,
        .markdown-content h6 {
            color: var(--text-primary);
            font-weight: 600;
            margin: 16px 0 8px 0;
        }

        .markdown-content h1 { font-size: 24px; }
        .markdown-content h2 { font-size: 20px; }
        .markdown-content h3 { font-size: 18px; }
        .markdown-content h4 { font-size: 16px; }
        .markdown-content h5 { font-size: 14px; }
        .markdown-content h6 { font-size: 13px; }

        .markdown-content p {
            margin: 8px 0;
        }

        .markdown-content ul,
        .markdown-content ol {
            margin: 8px 0;
            padding-left: 24px;
        }

        .markdown-content li {
            margin: 4px 0;
        }

        .markdown-content blockquote {
            border-left: 3px solid var(--accent-green);
            padding-left: 12px;
            margin: 12px 0;
            color: var(--text-secondary);
            font-style: italic;
        }

        .markdown-content code {
            background: var(--bg-secondary);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
            font-size: 13px;
            color: var(--accent-green);
        }

        .markdown-content pre {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
            overflow-x: auto;
            font-size: 13px;
        }

        .markdown-content pre code {
            background: transparent;
            padding: 0;
            border-radius: 0;
            color: inherit;
        }

        .markdown-content a {
            color: var(--accent-green);
            text-decoration: underline;
            transition: color 0.2s ease;
        }

        .markdown-content a:hover {
            color: var(--accent-green-muted);
        }

        .markdown-content table {
            border-collapse: collapse;
            width: 100%;
            margin: 12px 0;
            background: var(--bg-secondary);
            border-radius: 6px;
            overflow: hidden;
        }

        .markdown-content th,
        .markdown-content td {
            border: 1px solid var(--border-primary);
            padding: 8px 12px;
            text-align: left;
        }

        .markdown-content th {
            background: var(--bg-tertiary);
            font-weight: 600;
            color: var(--text-primary);
        }

        .markdown-content hr {
            border: none;
            border-top: 1px solid var(--border-primary);
            margin: 20px 0;
        }

        /* Code blocks */
        .code-block {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
            overflow-x: auto;
            font-size: 13px;
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
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-primary);
            border-radius: 4px;
            transition: background 0.2s ease;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }

        /* Responsive Design */
        @media (max-width: 1200px) {
            .container {
                padding: 16px;
                max-width: 100%;
            }

            .conversation-list {
                width: 320px;
            }
        }

        @media (max-width: 768px) {
            .container {
                padding: 12px;
                gap: 16px;
            }

            .main-content {
                flex-direction: column;
                gap: 16px;
            }

            .conversation-list {
                width: 100%;
                max-height: 300px;
            }

            .unified-header {
                padding: 16px;
            }

            .project-title {
                font-size: 20px;
            }

            .stat-group {
                gap: 16px;
            }

            .stat-item {
                min-width: 60px;
                padding: 6px 10px;
            }

            .filter-controls {
                gap: 8px;
            }

            .filter-btn {
                padding: 6px 12px;
                font-size: 11px;
            }
        }

        @media (max-width: 480px) {
            body {
                padding: 8px;
            }

            .container {
                padding: 0;
                gap: 12px;
            }

            .unified-header {
                padding: 12px;
                border-radius: 8px;
            }

            .project-title {
                font-size: 18px;
            }

            .stat-group {
                gap: 12px;
            }

            .filter-btn {
                padding: 4px 8px;
                font-size: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="unified-header" id="unifiedHeader">
            <div class="header-main">
                <h1 class="project-title">Claude Code Archive</h1>
                <div class="project-path" id="projectPath">Loading archive data...</div>
            </div>
            <div class="statistics-inline" id="statisticsInline" style="display: none;">
                <div class="stat-group">
                    <span class="stat-item">
                        <span class="stat-value" id="totalCount">0</span>
                        <span class="stat-label">conversations</span>
                    </span>
                    <span class="stat-item">
                        <span class="stat-value" id="totalMessages">0</span>
                        <span class="stat-label">messages</span>
                    </span>
                    <span class="stat-item">
                        <span class="stat-value" id="dateRange">-</span>
                        <span class="stat-label">date range</span>
                    </span>
                </div>
                <div class="filter-controls" id="filterControls">
                    <button class="filter-btn" id="btnSDK" onclick="toggleConversationType('sdk_generated')">Show SDK</button>
                    <button class="filter-btn" id="btnSubagents" onclick="toggleConversationType('multi_agent_workflow')">Toggle Subagents</button>
                    <button class="filter-btn" id="btnSnapshots" onclick="toggleConversationType('snapshot')">Show Snapshots</button>
                    <button class="filter-btn" id="btnCompletions" onclick="toggleConversationType('completion_marker')">Show Completions</button>
                    <button class="filter-btn" id="btnShowAll" onclick="showAllTypes()">Show All</button>
                    <button class="filter-btn warning" id="btnHideAll" onclick="hideAllTypes()">Hide All</button>
                </div>
            </div>
            <div class="type-breakdown" id="typeBreakdown" style="display: none;">
                <!-- Type breakdown will be populated by JavaScript -->
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

        // Conversation type visibility - tracks which types are currently visible
        let visibleTypes = {
            'original': true,
            'true_continuation': true,
            'multi_agent_workflow': true,
            'sdk_generated': false,  // Hidden by default - major discovery!
            'subagent_sidechain': true,
            'context_history': false,
            'completion_marker': false,
            'snapshot': false,
            'auto_linked': true,
            'post_compaction': true
        };

        // Initialize markdown renderer
        function initializeMarkdown() {
            if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
                marked.setOptions({
                    highlight: function(code, lang) {
                        if (lang && hljs.getLanguage(lang)) {
                            try {
                                return hljs.highlight(code, { language: lang }).value;
                            } catch (err) {}
                        }
                        return hljs.highlightAuto(code).value;
                    },
                    breaks: true,
                    gfm: true
                });
            }
        }

        // Render markdown content
        function renderMarkdown(text) {
            if (typeof marked !== 'undefined') {
                try {
                    return marked.parse(text);
                } catch (error) {
                    console.warn('Markdown parsing error:', error);
                    return escapeHtml(text);
                }
            }
            return escapeHtml(text);
        }

        // Check if text appears to be markdown
        function isMarkdownContent(text) {
            if (!text || typeof text !== 'string') return false;

            // Simple heuristics to detect markdown
            const markdownIndicators = [
                /^#{1,6}\\s+/m,           // Headers
                /\\*\\*.*?\\*\\*/,           // Bold
                /\\*.*?\\*/,               // Italic
                /`.*?`/,                 // Inline code
                /^```/m,                 // Code blocks
                /^\\* /m,                 // Unordered lists
                /^\\d+\\. /m,              // Ordered lists
                /^\\> /m,                 // Blockquotes
                /\\[.*?\\]\\(.*?\\)/         // Links
            ];

            return markdownIndicators.some(regex => regex.test(text));
        }

        // Initialize on startup
        async function initializeViewer() {
            try {
                initializeMarkdown();

                // Fetch manifest.json from the same directory
                const response = await fetch('manifest.json');
                manifest = await response.json();
                hiddenConversations = new Set(manifest.hidden_conversations || []);
                displayStats();
                displayConversationStatistics();
                displayConversationList();
                updateFilterButtons();
            } catch (error) {
                console.error('Failed to load manifest:', error);
                document.getElementById('conversationList').innerHTML = '<div style="color: #ff0000;">Failed to load manifest.json</div>';
            }
        }

        function displayStats() {
            // Update project path
            const projectPath = document.getElementById('projectPath');
            projectPath.textContent = manifest.project_path;

            // Update inline statistics
            document.getElementById('totalMessages').textContent = manifest.total_messages?.toLocaleString() || 0;

            // Calculate and display date range
            if (manifest.conversations && manifest.conversations.length > 0) {
                const dates = manifest.conversations
                    .filter(c => c.first_timestamp)
                    .map(c => new Date(c.first_timestamp))
                    .sort((a, b) => a - b);

                if (dates.length > 0) {
                    const firstDate = dates[0];
                    const lastDate = dates[dates.length - 1];
                    const dateRange = firstDate.toLocaleDateString() +
                        (firstDate.getTime() !== lastDate.getTime() ? ' - ' + lastDate.toLocaleDateString() : '');
                    document.getElementById('dateRange').textContent = dateRange;
                }
            }
        }

        function displayConversationStatistics() {
            const statisticsInline = document.getElementById('statisticsInline');
            const breakdownElement = document.getElementById('typeBreakdown');

            if (!manifest.conversation_statistics) {
                return;
            }

            const stats = manifest.conversation_statistics;
            const byType = stats.by_type || {};

            // Show statistics inline section
            statisticsInline.style.display = 'flex';

            // Update summary counts
            document.getElementById('totalCount').textContent = stats.total_count || 0;

            // Create type breakdown display
            const typeDisplayNames = {
                'original': 'Original',
                'true_continuation': 'True Continuations',
                'multi_agent_workflow': 'Multi-Agent Workflows',
                'sdk_generated': 'SDK-Generated',
                'subagent_sidechain': 'Subagent Sidechains',
                'context_history': 'Context History',
                'completion_marker': 'Completion Markers',
                'snapshot': 'Snapshots',
                'auto_linked': 'Auto Linked',
                'post_compaction': 'Post Compaction'
            };

            let breakdownHTML = '';
            let linePrefix = '';
            const typeKeys = Object.keys(typeDisplayNames);

            typeKeys.forEach((typeKey, index) => {
                const count = byType[typeKey] || 0;
                if (count === 0) return;

                const isLast = index === typeKeys.length - 1 || typeKeys.slice(index + 1).every(k => (byType[k] || 0) === 0);
                linePrefix = isLast ? '└─' : '├─';

                const displayName = typeDisplayNames[typeKey];
                const isVisible = visibleTypes[typeKey];
                const statusText = isVisible ? '(shown)' : '(hidden)';
                const statusClass = isVisible ? 'shown' : 'hidden';

                // Highlight SDK-generated as major discovery
                const countDisplay = typeKey === 'sdk_generated' && count > 0 ?
                    `<span class="type-count">${count}+</span> <span style="color: #ff8800;">← Major discovery!</span>` :
                    `<span class="type-count">${count}</span>`;

                breakdownHTML += `
                    <div class="type-item">
                        ${linePrefix} ${displayName}: ${countDisplay} <span class="type-status">${statusText}</span>
                    </div>
                `;
            });

            breakdownElement.innerHTML = breakdownHTML;
            if (breakdownHTML.trim()) {
                breakdownElement.style.display = 'block';
            }
        }

        function calculateShownCount() {
            if (!manifest || !manifest.conversations) return 0;
            return manifest.conversations.filter(conv => {
                const type = conv.conversation_type || 'original';
                const isHidden = hiddenConversations.has(conv.session_id);
                const isTypeVisible = visibleTypes[type];
                return !isHidden && isTypeVisible;
            }).length;
        }

        function calculateHiddenCount() {
            if (!manifest || !manifest.conversations) return 0;
            return manifest.conversations.filter(conv => {
                const type = conv.conversation_type || 'original';
                const isHidden = hiddenConversations.has(conv.session_id);
                const isTypeVisible = visibleTypes[type];
                return isHidden || !isTypeVisible;
            }).length;
        }

        function displayConversationList() {
            const listContainer = document.getElementById('conversationList');
            listContainer.classList.remove('loading');
            listContainer.innerHTML = '';

            manifest.conversations.forEach(conv => {
                const conversationType = conv.conversation_type || 'original';

                // Skip conversations based on type visibility
                if (!visibleTypes[conversationType]) {
                    return;
                }

                // Skip hidden conversations unless showing them
                const isHidden = hiddenConversations.has(conv.session_id);
                if (isHidden && !showHidden) {
                    return;
                }

                const item = document.createElement('div');
                item.className = 'conversation-item';

                // Add data attributes for filtering
                item.setAttribute('data-type', conversationType);
                item.setAttribute('data-display-default', visibleTypes[conversationType] ? 'true' : 'false');

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

                    // Check if content should be rendered as markdown
                    const shouldRenderMarkdown = isMarkdownContent(mainContent);
                    const contentHtml = shouldRenderMarkdown ?
                        renderMarkdown(mainContent) :
                        escapeHtml(mainContent);

                    messageDiv.innerHTML = `
                        <span class="message-prefix"></span>
                        <span class="message-content ${shouldRenderMarkdown ? 'markdown-content' : ''}">${agentLabel}${contentHtml}</span>
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
            // Use the new type-based filtering system
            toggleConversationType('snapshot');
            // Keep old button behavior for backwards compatibility
            const btn = document.getElementById('showSnapshotsBtn');
            if (visibleTypes['snapshot']) {
                btn.classList.add('active');
                btn.textContent = 'All';
            } else {
                btn.classList.remove('active');
                btn.textContent = 'Snapshots';
            }
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
            displayConversationStatistics();
        }

        // Filter control functions
        function toggleConversationType(type) {
            visibleTypes[type] = !visibleTypes[type];
            displayConversationList();
            displayConversationStatistics();
            updateFilterButtons();
        }

        function showAllTypes() {
            Object.keys(visibleTypes).forEach(type => {
                visibleTypes[type] = true;
            });
            displayConversationList();
            displayConversationStatistics();
            updateFilterButtons();
        }

        function hideAllTypes() {
            Object.keys(visibleTypes).forEach(type => {
                visibleTypes[type] = false;
            });
            // Keep 'original' visible to avoid empty list
            visibleTypes['original'] = true;
            displayConversationList();
            displayConversationStatistics();
            updateFilterButtons();
        }

        function updateFilterButtons() {
            // Update button states based on visibility
            const buttons = {
                'btnSDK': 'sdk_generated',
                'btnSubagents': 'multi_agent_workflow',
                'btnSnapshots': 'snapshot',
                'btnCompletions': 'completion_marker'
            };

            Object.keys(buttons).forEach(btnId => {
                const btn = document.getElementById(btnId);
                const type = buttons[btnId];
                if (btn) {
                    if (visibleTypes[type]) {
                        btn.classList.add('active');
                        if (btnId === 'btnSDK') btn.textContent = 'Hide SDK';
                        else if (btnId === 'btnSnapshots') btn.textContent = 'Hide Snapshots';
                        else if (btnId === 'btnCompletions') btn.textContent = 'Hide Completions';
                    } else {
                        btn.classList.remove('active');
                        if (btnId === 'btnSDK') btn.textContent = 'Show SDK';
                        else if (btnId === 'btnSnapshots') btn.textContent = 'Show Snapshots';
                        else if (btnId === 'btnCompletions') btn.textContent = 'Show Completions';
                    }
                }
            });

            // Update Show All / Hide All button states
            const allVisible = Object.values(visibleTypes).every(v => v);
            const showAllBtn = document.getElementById('btnShowAll');
            if (showAllBtn) {
                if (allVisible) {
                    showAllBtn.classList.add('active');
                } else {
                    showAllBtn.classList.remove('active');
                }
            }
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
