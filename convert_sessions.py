import json
import os
import re
from datetime import datetime
from pathlib import Path

# Configuration
SOURCE_DIR = Path("/home/mischa/.gemini/tmp")
OUTPUT_DIR = Path("transcripts")

# Regex for potential secrets (Basic patterns: OpenAI-like, Private Keys, etc.)
SECRET_PATTERNS = [
    r"(sk-[a-zA-Z0-9]{20,})",          # OpenAI / General tokens
    r"(ghp_[a-zA-Z0-9]{20,})",         # GitHub Personal Access Tokens
    r"(xox[baprs]-[a-zA-Z0-9]{10,})",  # Slack tokens
    r"(--BEGIN [A-Z]+ PRIVATE KEY--)", # PEM Headers
    r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", # Email addresses
    r"(gen" + "try)"                   # Specific PII blocker (obfuscated)
]

def redact_text(text):
    if not isinstance(text, str):
        return text
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, "[REDACTED_SECRET]", text)
    return text

def find_json_files(base_dir):
    json_files = []
    # Search specifically in the 'chats' subdirectories of the tmp folders
    for root, dirs, files in os.walk(base_dir):
        if 'chats' in root:
            for file in files:
                if file.startswith("session-") and file.endswith(".json"):
                    json_files.append(os.path.join(root, file))
    return json_files

def format_timestamp(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return iso_str

def convert_session_to_md(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return

    session_id = data.get("sessionId", "unknown")
    start_time = format_timestamp(data.get("startTime", ""))
    
    # Create filename based on timestamp or ID
    filename = f"{session_id}.md"
    output_path = OUTPUT_DIR / filename
    
    markdown_content = f"# Chat Session: {session_id}\n\n"
    markdown_content += f"**Start Time:** {start_time}\n"
    markdown_content += f"**Source:** `{json_path}`\n\n"
    markdown_content += "---\n\n"

    messages = data.get("messages", [])
    if not messages:
        print(f"Skipping empty session: {json_path}")
        return

    for msg in messages:
        timestamp = format_timestamp(msg.get("timestamp", ""))
        role = msg.get("type", "unknown").upper()
        content = redact_text(msg.get("content", ""))
        
        markdown_content += f"### {role} - {timestamp}\n\n"
        if content:
            markdown_content += f"{content}\n\n"
        
        # Handle tool calls
        if "toolCalls" in msg and msg["toolCalls"]:
            markdown_content += "**Tool Calls:**\n\n"
            for tool in msg["toolCalls"]:
                tool_name = tool.get("name", "unknown")
                tool_args = redact_text(json.dumps(tool.get("args", {}), indent=2))
                tool_output = redact_text(json.dumps(tool.get("result", {}), indent=2))
                
                markdown_content += f"<details>\n<summary>Tool: <code>{tool_name}</code></summary>\n\n"
                markdown_content += f"**Arguments:**\n```json\n{tool_args}\n```\n\n"
                markdown_content += f"**Result:**\n```json\n{tool_output}\n```\n</details>\n\n"
        
        markdown_content += "---\n\n"

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"Converted: {output_path}")

def main():
    print(f"Scanning {SOURCE_DIR} for session logs...")
    files = find_json_files(SOURCE_DIR)
    print(f"Found {len(files)} session files.")
    
    for json_file in files:
        convert_session_to_md(json_file)

if __name__ == "__main__":
    main()
