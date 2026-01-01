import os
import shutil
import json
import re
from pathlib import Path

# Configuration
HOME = Path.home()
ANTIGRAVITY_SRC = HOME / ".gemini/antigravity/conversations"
TMP_SRC = HOME / ".gemini/tmp"
REPO_ROOT = Path(__file__).parent.parent

# Destinations
ANTIGRAVITY_DEST = REPO_ROOT / "antigravity-data"
TRANSCRIPTS_DEST = REPO_ROOT / "transcripts"

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
    """Syncs .pb files and readable markdown from Antigravity."""
    dest_dir = ANTIGRAVITY_DEST
    os.makedirs(dest_dir, exist_ok=True)
    
    # Sync .pb files (encrypted/binary)
    if ANTIGRAVITY_SRC.exists():
        print(f"Syncing Antigravity files from {ANTIGRAVITY_SRC}...")
        for file_path in ANTIGRAVITY_SRC.glob("*.pb"):
            shutil.copy2(file_path, dest_dir / file_path.name)
            
    # Sync Brain Task Logs (Readable MD)
    brain_dir = HOME / ".gemini/antigravity/brain"
    if brain_dir.exists():
        print(f"Syncing Brain logs from {brain_dir}...")
        for root, dirs, files in os.walk(brain_dir):
            for file in files:
                if file == "task.md":
                    # Extract UUID from parent folder name
                    uuid = Path(root).name
                    # Create destination: antigravity-data/brain/<UUID>.md
                    brain_dest = dest_dir / "brain"
                    os.makedirs(brain_dest, exist_ok=True)
                    shutil.copy2(os.path.join(root, file), brain_dest / f"{uuid}.md")

    # Sync Scratch Chat Logs (Readable MD)
    scratch_log = HOME / ".gemini/antigravity/scratch/chat_logs/chat_log.md"
    if scratch_log.exists():
        print(f"Syncing Scratch chat log...")
        scratch_dest = dest_dir / "scratch"
        os.makedirs(scratch_dest, exist_ok=True)
        shutil.copy2(scratch_log, scratch_dest / "chat_log.md")


def sync_json_logs():
    """Syncs and REDACTS .json logs from tmp directories."""
    dest_dir = TRANSCRIPTS_DEST
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
