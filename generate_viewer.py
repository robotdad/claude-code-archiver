#!/usr/bin/env python3
"""Generate viewer.html for testing Phase 1 changes."""

import json
from pathlib import Path
from src.claude_code_archiver.viewer.generator import ViewerGenerator

def main():
    # Read manifest
    manifest_path = Path("SelfServe/manifest.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Generate viewer
    generator = ViewerGenerator()
    html_content = generator.generate_viewer(manifest)
    
    # Write viewer.html
    output_path = Path("SelfServe/viewer.html")
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"Generated viewer.html at {output_path}")

if __name__ == "__main__":
    main()