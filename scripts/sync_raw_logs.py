#!/usr/bin/env python3
"""
Gemini CLI Raw Log Sync Script
Syncs conversation logs from ~/.gemini to M-Gemini repo with comprehensive redaction
"""

import os
import shutil
import json
import re
from pathlib import Path
from datetime import datetime

# Configuration
HOME = Path.home()
GEMINI_TMP = HOME / ".gemini/tmp"
REPO_ROOT = Path(__file__).parent.parent
CHAT_LOGS_DEST = REPO_ROOT / "chat_logs"

# Comprehensive secret and PII patterns
SECRET_PATTERNS = [
    # API Keys & Tokens
    (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]"),
    (r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(xox[baprs]-[a-zA-Z0-9]{10,})", "[REDACTED_SLACK_TOKEN]"),
    (r"(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_KEY]"),
    (r"(ya29\.[a-zA-Z0-9_-]{50,})", "[REDACTED_GOOGLE_TOKEN]"),

    # Private Keys
    (r"(-----BEGIN [A-Z]+ PRIVATE KEY-----[^-]+-----END [A-Z]+ PRIVATE KEY-----)", "[REDACTED_PRIVATE_KEY]"),
    (r"(-----BEGIN RSA PRIVATE KEY-----)", "[REDACTED_RSA_KEY_HEADER]"),

    # Email addresses (PII)
    (r"(?<!\\)(\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b)", "[REDACTED_EMAIL]"),

    # Phone numbers (PII) - Made stricter to avoid matching timestamps/UUIDs
    # Must have at least 10 digits total and include separators or +
    (r"(?<!\\)(\+\d{1,3}[-.\s]?\d{1,14})", "[REDACTED_PHONE]"),
    (r"(?<!\\)(\b\d{3}[-.]\d{3}[-.]\d{4}\b)", "[REDACTED_PHONE]"),

    # Credit card numbers (PII)
    (r"(?<!\\)(\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b)", "[REDACTED_CARD]"),

    # SSN-like patterns (PII)
    (r"(?<!\\)(\b\d{3}-\d{2}-\d{4}\b)", "[REDACTED_SSN]"),

    # IP Addresses (potentially sensitive) - Use \b to avoid matching version numbers loosely
    (r"(?<!\\)(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)", "[REDACTED_IP]"),

    # JWT tokens
    (r"(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})", "[REDACTED_JWT]"),

    # Generic secrets (password=, token=, etc.)
    (r"(password\s*[:=]\s*['\"]?[^\s'\"]{8,}['\"]?)", "password=[REDACTED]"),
    (r"(token\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "token=[REDACTED]"),
    (r"(secret\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "secret=[REDACTED]"),
    (r"(api_key\s*[:=]\s*['\"]?[^\s'\"]{20,}['\"]?)", "api_key=[REDACTED]"),

    # YubiKey OTP (obfuscated in script)
    (r"(JhRKknRTKbjJIdGDFjDuGhEtBBfjJGHiLhkFK" + "G)", "[REDACTED_YUBIKEY_OTP]"),

    # Database connection strings
    (r"(postgres://[^\s]+)", "[REDACTED_DB_CONNECTION]"),
    (r"(mysql://[^\s]+)", "[REDACTED_DB_CONNECTION]"),
    (r"(mongodb://[^\s]+)", "[REDACTED_DB_CONNECTION]"),

    # File paths that might contain usernames
    (r"(/home/[a-zA-Z0-9_-]+)", "/home/[USER]"),
    (r"(/Users/[a-zA-Z0-9_-]+)", "/Users/[USER]"),

    # Specific PII blockers (obfuscated in script)
    (r"(" + "gen" + "try)", "[REDACTED_NAME]"),
    (r"(" + "Gen" + "try)", "[REDACTED_NAME]"),
]

def redact_text(text):
    """Apply all redaction patterns to text."""
    if not isinstance(text, str):
        return text

    for pattern, replacement in SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

def sync_gemini_logs():
    """Sync and redact Gemini conversation logs."""
    if not GEMINI_TMP.exists():
        print(f"Warning: Source directory not found: {GEMINI_TMP}")
        return

    os.makedirs(CHAT_LOGS_DEST, exist_ok=True)

    # Find all session-*.json files recursively
    session_files = list(GEMINI_TMP.glob("**/chats/session-*.json"))
    print(f"Found {len(session_files)} conversation logs in {GEMINI_TMP}")

    synced_count = 0
    updated_count = 0
    skipped_count = 0

    for src_file in session_files:
        dest_file = CHAT_LOGS_DEST / src_file.name

        try:
            # Read entire file as text and apply redaction
            with open(src_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Apply all redaction patterns to the raw text
            redacted_content = content
            for pattern, replacement in SECRET_PATTERNS:
                redacted_content = re.sub(pattern, replacement, redacted_content, flags=re.IGNORECASE)

            # Check if we need to update
            should_write = True
            if dest_file.exists():
                try:
                    with open(dest_file, 'r', encoding='utf-8', errors='replace') as f:
                        existing_content = f.read()
                    if existing_content == redacted_content:
                        should_write = False
                        skipped_count += 1
                except:
                    pass

            if should_write:
                # Write redacted content
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(redacted_content)
                
                if dest_file.exists():
                     updated_count += 1
                else:
                     synced_count += 1

        except Exception as e:
            print(f"Error processing {src_file.name}: {e}")

    print(f"Synced {synced_count} new files, updated {updated_count} files, skipped {skipped_count} unchanged files")

def update_readme():
    """Update README with sync timestamp."""
    readme_path = CHAT_LOGS_DEST / "README.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""# Gemini CLI Raw Conversation Logs

This directory contains redacted raw conversation logs from Gemini CLI sessions.

**Last Sync:** {timestamp}

## Format
- Files are in JSON format.
- Contains full session metadata, messages, thoughts, and tool calls.
- All sensitive data is automatically redacted before syncing.

## Redacted Information
The sync script automatically redacts:
- API keys and authentication tokens
- Email addresses
- Phone numbers
- IP addresses
- Private keys
- Database connection strings
- File paths containing usernames
- Other PII and secrets

## Syncing
To sync the latest logs:
```bash
python scripts/sync_raw_logs.py
```
"""
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("=" * 60)
    print("Gemini CLI Raw Log Sync")
    print("=" * 60)
    print(f"Source Root: {GEMINI_TMP}")
    print(f"Destination: {CHAT_LOGS_DEST}")
    print()

    sync_gemini_logs()
    update_readme()

    print()
    print("=" * 60)
    print("Sync complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()