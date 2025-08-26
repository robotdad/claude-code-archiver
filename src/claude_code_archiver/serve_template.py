#!/usr/bin/env python3
"""Simple HTTP server for viewing Claude Code archives."""

import http.server
import socketserver
import webbrowser
from pathlib import Path
from typing import Any

PORT = 8000


class ViewerHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler that serves viewer.html at root path."""

    def do_GET(self):
        """Handle GET requests, serving viewer.html for root path."""
        # If requesting root path, redirect to viewer.html
        if self.path == "/" or self.path == "":
            # Read and serve viewer.html directly
            try:
                with open("viewer.html", "rb") as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                self.send_error(404, "viewer.html not found")
                return
        
        # Call the parent method to handle other requests
        super().do_GET()

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
            with socketserver.TCPServer(("", port), ViewerHTTPRequestHandler) as httpd:
                print(f"🚀 Starting server at http://localhost:{port}")
                print(f"📂 Serving files from: {script_dir}")
                print("🌐 Opening viewer in your browser...")
                print("\n✨ Press Ctrl+C to stop the server\n")

                # Open the viewer in the default browser (now just the root URL)
                webbrowser.open(f"http://localhost:{port}")

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
