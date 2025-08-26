#!/usr/bin/env python3
"""Simple HTTP server for viewing Claude Code archives."""

import http.server
import json
import socketserver
import webbrowser
import zipfile
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

    def do_POST(self):
        """Handle POST requests for API endpoints."""
        if self.path == "/api/save-manifest":
            self._handle_save_manifest()
        elif self.path == "/api/repack-archive":
            self._handle_repack_archive()
        elif self.path == "/api/save-and-repack":
            self._handle_save_and_repack()
        else:
            self.send_error(404, "API endpoint not found")

    def _handle_save_manifest(self):
        """Handle saving updated manifest."""
        try:
            # Parse form data to get manifest
            # For simplicity, we'll expect the manifest as JSON in the request body
            if self.headers.get('Content-Type', '').startswith('multipart/form-data'):
                # Handle multipart form data (from the browser)
                import cgi
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )

                if 'manifest' in form:
                    manifest_data = form['manifest'].value
                    if isinstance(manifest_data, bytes):
                        manifest_data = manifest_data.decode('utf-8')

                    # Update the manifest.json file
                    with open("manifest.json", "w", encoding="utf-8") as f:
                        f.write(manifest_data)

                    # Update viewer.html with new manifest
                    self._update_viewer_html()

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                else:
                    raise ValueError("No manifest data received")
            else:
                raise ValueError("Expected multipart/form-data")

        except Exception as e:
            print(f"Error saving manifest: {e}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _handle_repack_archive(self):
        """Handle repacking the archive with updates."""
        try:
            # Find the original archive file
            archive_files = list(Path(".").glob("*.zip"))
            if not archive_files:
                raise ValueError("No archive file found to repack")

            archive_path = archive_files[0]  # Use first found archive

            # Create new archive with current directory contents
            temp_archive = archive_path.with_suffix('.zip.new')
            with zipfile.ZipFile(temp_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in Path(".").rglob("*"):
                    if file_path.is_file() and file_path != temp_archive:
                        zipf.write(file_path, file_path)

            # Replace original archive
            archive_path.unlink()
            temp_archive.rename(archive_path)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "archive": str(archive_path)}).encode())

        except Exception as e:
            print(f"Error repacking archive: {e}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _handle_save_and_repack(self):
        """Handle saving updated manifest and repacking archive in one operation."""
        try:
            # Parse form data to get manifest
            if self.headers.get('Content-Type', '').startswith('multipart/form-data'):
                # Handle multipart form data (from the browser)
                import cgi
                import io
                
                # Create a new rfile from the request body since cgi.FieldStorage consumes it
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                form = cgi.FieldStorage(
                    fp=io.BytesIO(post_data),
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST', 'CONTENT_LENGTH': str(content_length)}
                )
                
                if 'manifest' in form:
                    manifest_data = form['manifest'].value
                    if isinstance(manifest_data, bytes):
                        manifest_data = manifest_data.decode('utf-8')
                    
                    print(f"Received manifest data: {len(manifest_data)} characters")
                    
                    # Update the manifest.json file
                    with open("manifest.json", "w", encoding="utf-8") as f:
                        f.write(manifest_data)
                    print("Updated manifest.json")
                    
                    # Update viewer.html with new manifest
                    self._update_viewer_html()
                    print("Updated viewer.html")
                    
                    # Find and repack the archive - look in current dir and parent dir
                    archive_files = list(Path(".").glob("*.zip"))
                    if not archive_files:
                        # Look in parent directory (common when extracted with Finder)
                        archive_files = list(Path("..").glob("*.zip"))
                        
                    if archive_files:
                        archive_path = archive_files[0]  # Use first found archive
                        print(f"Found archive to repack: {archive_path}")
                        
                        # Create new archive with current directory contents
                        temp_archive = archive_path.with_suffix('.zip.new')
                        with zipfile.ZipFile(temp_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for file_path in Path(".").rglob("*"):
                                if file_path.is_file() and file_path != temp_archive and not file_path.name.endswith('.zip.new'):
                                    # Use relative paths in the archive
                                    zipf.write(file_path, file_path)
                        
                        # Replace original archive
                        archive_path.unlink()
                        temp_archive.rename(archive_path)
                        print(f"Archive repacked successfully: {archive_path}")
                        
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            "success": True, 
                            "archive": str(archive_path.name),
                            "message": "Changes saved and archive repacked successfully"
                        }).encode())
                    else:
                        # Try to find archive with a name based on current directory
                        current_dir = Path.cwd().name
                        potential_archive = Path("..") / f"{current_dir}.zip"
                        if potential_archive.exists():
                            archive_path = potential_archive
                            print(f"Found archive based on directory name: {archive_path}")
                            
                            # Create new archive with current directory contents
                            temp_archive = archive_path.with_suffix('.zip.new')
                            with zipfile.ZipFile(temp_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                for file_path in Path(".").rglob("*"):
                                    if file_path.is_file() and file_path != temp_archive:
                                        zipf.write(file_path, file_path)
                            
                            # Replace original archive
                            archive_path.unlink()
                            temp_archive.rename(archive_path)
                            print(f"Archive repacked successfully: {archive_path}")
                            
                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                "success": True, 
                                "archive": str(archive_path.name),
                                "message": "Changes saved and archive repacked successfully"
                            }).encode())
                        else:
                            # No archive found, just save manifest
                            print("No archive found to repack")
                            print(f"Looked in: {Path.cwd()}, {Path.cwd().parent}")
                            print(f"Files in current dir: {list(Path('.').glob('*'))}")
                            print(f"Files in parent dir: {list(Path('..').glob('*.zip'))}")
                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                "success": True,
                                "message": "Changes saved (no archive found to repack)"
                            }).encode())
                else:
                    raise ValueError("No manifest data received")
            else:
                raise ValueError("Expected multipart/form-data")
                
        except Exception as e:
            import traceback
            print(f"Error saving and repacking: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _update_viewer_html(self):
        """Update viewer.html with the new manifest data."""
        try:
            # Read current manifest
            with open("manifest.json", encoding="utf-8") as f:
                manifest_data = json.load(f)

            # Read current viewer.html
            with open("viewer.html", encoding="utf-8") as f:
                html_content = f.read()

            # Replace the manifest data in the HTML
            manifest_json = json.dumps(manifest_data)
            old_pattern = r'let manifest = .*?;'
            new_content = f'let manifest = {manifest_json};'

            import re
            updated_html = re.sub(old_pattern, new_content, html_content, flags=re.DOTALL)

            # Write updated viewer.html
            with open("viewer.html", "w", encoding="utf-8") as f:
                f.write(updated_html)

        except Exception as e:
            print(f"Warning: Could not update viewer.html: {e}")

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
