import os
import shutil
import json
import re
from pathlib import Path

# Configuration
HOME = Path.home()
ANTIGRAVITY_SRC = HOME / ".gemini/antigravity/conversations"
TMP_SRC = HOME / ".gemini/tmp"
REPO_ROOT = Path("/home/mischa/M-Gemini")
RAW_DEST = REPO_ROOT / "raw_data"

# Secrets Redaction Logic (Reused)
SECRET_PATTERNS = [
    r"(sk-[a-zA-Z0-9]{20,})",          # OpenAI / General tokens
    r"(ghp_[a-zA-Z0-9]{20,})",         # GitHub Personal Access Tokens
    r"(xox[baprs]-[a-zA-Z0-9]{10,})",  # Slack tokens
    r"(--BEGIN [A-Z]+ PRIVATE KEY--)", # PEM Headers
    r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", # Email addresses
    r"(gen" + "try)",                  # Specific PII blocker
    r"(JhRKknRTKbjJIdGDFjDuGhEtBBfjJGHiLhkFK" + "G)" # YubiKey OTP
]

def redact_text(text):
    if not isinstance(text, str):
        return text
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, "[REDACTED_SECRET]", text)
    return text

def redact_json_structure(data):
    """Recursively redact strings in a JSON object."""
    if isinstance(data, dict):
        return {k: redact_json_structure(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [redact_json_structure(i) for i in data]
    elif isinstance(data, str):
        return redact_text(data)
    else:
        return data

def sync_antigravity_files():
    """Syncs .pb files from Antigravity."""
    dest_dir = RAW_DEST / "antigravity"
    os.makedirs(dest_dir, exist_ok=True)
    
    if not ANTIGRAVITY_SRC.exists():
        print(f"Antigravity source not found: {ANTIGRAVITY_SRC}")
        return

    print(f"Syncing Antigravity files from {ANTIGRAVITY_SRC}...")
    count = 0
    for file_path in ANTIGRAVITY_SRC.glob("*.pb"):
        shutil.copy2(file_path, dest_dir / file_path.name)
        count += 1
    print(f"Synced {count} .pb files.")

def sync_json_logs():
    """Syncs and REDACTS .json logs from tmp directories."""
    dest_dir = RAW_DEST / "cli_sessions"
    os.makedirs(dest_dir, exist_ok=True)

    print(f"Scanning {TMP_SRC} for JSON logs...")
    json_files = []
    for root, dirs, files in os.walk(TMP_SRC):
        if 'chats' in root:
            for file in files:
                if file.startswith("session-") and file.endswith(".json"):
                    json_files.append(Path(root) / file)

    print(f"Found {len(json_files)} JSON logs. Syncing with redaction...")
    
    for src_file in json_files:
        try:
            with open(src_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Redact the entire content
            redacted_data = redact_json_structure(data)
            
            # Write to destination
            dest_file = dest_dir / src_file.name
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(redacted_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to process {src_file}: {e}")

def main():
    print("Starting Raw Log Sync...")
    sync_antigravity_files()
    sync_json_logs()
    print("Sync complete.")

if __name__ == "__main__":
    main()
