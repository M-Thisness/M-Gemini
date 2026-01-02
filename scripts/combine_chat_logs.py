#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path

# Configuration
REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "Archives"
OUTPUT_FILE = REPO_ROOT / "FULL_CHAT_LOG.md"

def find_markdown_files(base_dir):
    md_files = []
    for file in base_dir.glob("session-*.md"):
        md_files.append(file)
    return sorted(md_files) # Filenames session-YYYY-MM-DD sort chronologically naturally

def main():
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory {SOURCE_DIR} not found.")
        return

    print(f"Scanning {SOURCE_DIR} for markdown logs...")
    files = find_markdown_files(SOURCE_DIR)
    
    print(f"Found {len(files)} session logs.")
    
    full_log_content = "# Full Gemini Chat History\n\n"
    full_log_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    full_log_content += "Ordered chronologically.\n\n"
    
    for md_path in files:
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Ensure spacing
                full_log_content += content.strip() + "\n\n<br>\n<br>\n\n"
        except Exception as e:
            print(f"Error reading {md_path}: {e}")
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_log_content)
        
    print(f"Successfully wrote full chat log to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()