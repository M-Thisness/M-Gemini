#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime
from pathlib import Path

# Configuration
REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "chat_logs"
OUTPUT_FILE = REPO_ROOT / "FULL_CHAT_LOG.md"

# Comprehensive secret and PII patterns (Matched with sync_raw_logs.py)
SECRET_PATTERNS = [
    (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]"),
    (r"(ghp_[a-zA-Z0-9]{20,})", "[REDACTED_GITHUB_TOKEN]"),
    (r"(xox[baprs]-[a-zA-Z0-9]{10,})", "[REDACTED_SLACK_TOKEN]"),
    (r"(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_KEY]"),
    (r"(ya29\.[a-zA-Z0-9_-]{50,})", "[REDACTED_GOOGLE_TOKEN]"),
    (r"(-----BEGIN [A-Z]+ PRIVATE KEY-----[^-]+-----END [A-Z]+ PRIVATE KEY-----)", "[REDACTED_PRIVATE_KEY]"),
    (r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", "[REDACTED_EMAIL]"),
    (r"(JhRKknRTKbjJIdGDFjDuGhEtBBfjJGHiLhkFK" + "G)", "[REDACTED_YUBIKEY_OTP]"),
    (r"(" + "gen" + "try)", "[REDACTED_NAME]"),
    (r"(" + "Gen" + "try)", "[REDACTED_NAME]")
]

def redact_text(text):
    if not isinstance(text, str):
        return text
    for pattern, replacement in SECRET_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def find_json_files(base_dir):
    json_files = []
    # Gemini logs in chat_logs are at the root level now
    for file in os.listdir(base_dir):
        if file.startswith("session-") and file.endswith(".json"):
            json_files.append(os.path.join(base_dir, file))
    return json_files

def format_timestamp(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return iso_str

def get_session_data(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            start_time_str = data.get("startTime", "")
            if start_time_str:
                dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                timestamp = dt.timestamp()
            else:
                timestamp = 0
            return {
                "timestamp": timestamp,
                "data": data,
                "path": Path(json_path).name
            }
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return None

def generate_session_markdown(session_data):
    data = session_data["data"]
    session_id = data.get("sessionId", "unknown")
    start_time = format_timestamp(data.get("startTime", ""))
    
    markdown = f"\n# Session: {start_time} (ID: {session_id})\n\n"
    markdown += f"**Source:** `{session_data['path']}`\n\n"
    markdown += "---\n\n"

    messages = data.get("messages", [])
    if not messages:
        return ""

    for msg in messages:
        timestamp = format_timestamp(msg.get("timestamp", ""))
        role = msg.get("type", "unknown").upper()
        content = redact_text(msg.get("content", ""))
        
        markdown += f"### {role} - {timestamp}\n\n"
        if content:
            markdown += f"{content}\n\n"
        
        if "toolCalls" in msg and msg["toolCalls"]:
            markdown += "**Tool Calls:**\n\n"
            for tool in msg["toolCalls"]:
                tool_name = tool.get("name", "unknown")
                tool_args = redact_text(json.dumps(tool.get("args", {}), indent=2))
                tool_result = redact_text(tool.get("resultDisplay", "Result received."))
                
                markdown += f"<details>\n<summary>Tool: `{tool_name}`</summary>\n\n"
                markdown += f"**Arguments:**\n```json\n{tool_args}\n```\n\n"
                markdown += f"**Result:**\n```\n{tool_result}\n```\n</details>\n\n"
        
        markdown += "---\n\n"
    
    return markdown

def main():
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory {SOURCE_DIR} not found.")
        return

    print(f"Scanning {SOURCE_DIR} for session logs...")
    files = find_json_files(SOURCE_DIR)
    
    sessions = []
    for f in files:
        session = get_session_data(f)
        if session:
            sessions.append(session)
    
    sessions.sort(key=lambda x: x["timestamp"])
    
    print(f"Found and sorted {len(sessions)} sessions.")
    
    full_log_content = "# Full Gemini Chat History\n\n"
    full_log_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    full_log_content += "Ordered chronologically.\n\n"
    
    for session in sessions:
        full_log_content += generate_session_markdown(session)
        full_log_content += "\n<br>\n<br>\n\n"
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_log_content)
        
    print(f"Successfully wrote full chat log to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()