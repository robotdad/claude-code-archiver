#!/usr/bin/env python3
"""Simple HTTP server for viewing Claude Code archives."""

import http.server
import socketserver
import webbrowser
from pathlib import Path
from typing import Any

PORT = 8000


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with minimal logging."""

    def log_message(self, format: str, *args: Any) -> None:
        """Only log errors, not every request."""
        if args[1] != "200":
            super().log_message(format, *args)


def main():
    """Start a simple HTTP server and open the viewer."""
    # Change to the script's directory
    script_dir = Path(__file__).parent
    import os

    os.chdir(script_dir)

    # Find an available port
    port = PORT
    while port < PORT + 100:
        try:
            with socketserver.TCPServer(("", port), QuietHTTPRequestHandler) as httpd:
                print(f"🚀 Starting server at http://localhost:{port}")
                print(f"📂 Serving files from: {script_dir}")
                print("🌐 Opening viewer in your browser...")
                print("\n✨ Press Ctrl+C to stop the server\n")

                # Open the viewer in the default browser
                webbrowser.open(f"http://localhost:{port}/viewer.html")

                # Start serving
                httpd.serve_forever()
                break
        except OSError:
            port += 1
    else:
        print(f"❌ Could not find an available port between {PORT} and {PORT + 99}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
