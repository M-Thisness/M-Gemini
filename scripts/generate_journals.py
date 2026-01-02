#!/usr/bin/env python3
import os
import re
from pathlib import Path
from collections import defaultdict

def main():
    repo_root = Path(__file__).parent.parent
    chat_logs_dir = repo_root / "Archives"
    journals_dir = repo_root / "journals"

    # Ensure output directory exists
    journals_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning {chat_logs_dir} for markdown logs...")

    # Group files by date
    daily_files = defaultdict(list)
    
    # Pattern to match session-YYYY-MM-DD...md
    # We want to extract YYYY-MM-DD
    # Example: session-2025-12-03T01-12-cba3c8b5.md
    for md_file in chat_logs_dir.glob("session-*.md"):
        filename = md_file.name
        # Extract date part: YYYY-MM-DD
        # It's consistently at the start after 'session-'
        # session-2025-12-03... -> 2025-12-03
        
        try:
            date_str = filename.split('session-')[1][:10]
            # specific check for format YYYY-MM-DD
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                daily_files[date_str].append(md_file)
            else:
                print(f"Skipping {filename}: Date format mismatch")
        except IndexError:
            print(f"Skipping {filename}: Unexpected format")

    print(f"Found logs for {len(daily_files)} days.")

    # Process each day
    for date_str, files in daily_files.items():
        # Sort files chronologically by filename (timestamp is in filename)
        files.sort(key=lambda x: x.name)
        
        full_day_content = f"# Journal - {date_str}\n\n"
        
        for md_path in files:
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    full_day_content += f"{content.strip()}\n\n---\n\n"
            except Exception as e:
                print(f"Error reading {md_path}: {e}")

        output_path = journals_dir / f"{date_str}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_day_content)
        
    print(f"Successfully generated {len(daily_files)} daily journals in {journals_dir}")

if __name__ == "__main__":
    main()
