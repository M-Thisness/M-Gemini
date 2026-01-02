#!/usr/bin/env python3
import os
import shutil
import json
import re
from pathlib import Path
from datetime import datetime

HOME = Path.home()
GEMINI_TMP = HOME / ".gemini/tmp"
SOURCE_ID = "legion-windows"
REPO_ROOT = Path(__file__).parent.parent
CHAT_LOGS_DEST = REPO_ROOT / "Archives"

SECRET_PATTERNS = [
    (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]"),
    (r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(xox[baprs]-[a-zA-Z0-9]{10,})", "[REDACTED_SLACK_TOKEN]"),
    (r"(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_KEY]"),
    (r"(ya29\.[a-zA-Z0-9_-]{50,})", "[REDACTED_GOOGLE_TOKEN]"),
    (r"(-----BEGIN [A-Z]+ PRIVATE KEY-----[^-]+-----END [A-Z]+ PRIVATE KEY-----)", "[REDACTED_PRIVATE_KEY]"),
    (r"(?<!\\)(\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b)", "[REDACTED_EMAIL]"),
    (r"(JhRKknRTKbjJIdGDFjDuGhEtBBfjJGHiLhkFK" + "G)", "[REDACTED_YUBIKEY_OTP]"),
    (r"(" + "gen" + "try)", "[REDACTED_NAME]"),
    (r"(" + "Gen" + "try)", "[REDACTED_NAME]"),
]

def redact_text(text):
    if not isinstance(text, str): return text
    for pattern, replacement in SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def sync_gemini_logs():
    if not GEMINI_TMP.exists(): return
    os.makedirs(CHAT_LOGS_DEST, exist_ok=True)
    session_files = list(GEMINI_TMP.glob("**/chats/session-*.json"))
    for src_file in session_files:
        dest_file = CHAT_LOGS_DEST / src_file.name
        try:
            with open(src_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            redacted_content = redact_text(content)
            try:
                data = json.loads(redacted_content)
                if "source" not in data: data["source"] = SOURCE_ID
                redacted_content = json.dumps(data, indent=2)
            except: pass
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(redacted_content)
        except Exception as e: print(f"Error processing {src_file.name}: {e}")

def main():
    sync_gemini_logs()

if __name__ == "__main__":
    main()
