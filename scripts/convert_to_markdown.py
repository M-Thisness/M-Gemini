#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def format_timestamp(timestamp_str: str) -> str:
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M:%S %p')
    except: return timestamp_str

def format_user_message(msg: Dict[str, Any]) -> str:
    return f"**You:** {msg.get('content', '')}\n\n"

def format_gemini_message(msg: Dict[str, Any]) -> str:
    output = []
    thoughts = msg.get('thoughts', [])
    if thoughts:
        output.append("<details><summary>thought</summary>\n")
        for t in thoughts: output.append(f"- **{t.get('subject', 'Thought')}**: {t.get('description', '')}\n")
        output.append("</details>\n")
    for tool in msg.get('toolCalls', []):
        output.append(f"**Tool Call:** `{tool.get('name')}`")
        output.append(f"```json\n{json.dumps(tool.get('args', {}), indent=2)}\n```")
        output.append(f"> {tool.get('resultDisplay', 'Result received.')}\n")
    if msg.get('content'): output.append(f"**Gemini:** {msg.get('content')}\n")
    return '\n'.join(output) + '\n\n'

def convert_json_to_markdown(json_path: Path, output_dir: Path) -> Dict[str, Any]:
    try:
        with open(json_path, 'r', encoding='utf-8') as f: data = json.load(f)
    except: return None
    session_id, timestamp, messages = data.get('sessionId', json_path.stem), data.get('startTime', ''), data.get('messages', [])
    source = data.get("source", "unknown")
    if not messages: return None
    md_lines = [f"# {session_id}\n\n"]
    u_cnt = sum(1 for m in messages if m.get('type') == 'user')
    g_cnt = sum(1 for m in messages if m.get('type') == 'gemini')
    md_lines.append(f"*{format_timestamp(timestamp)} | {u_cnt} prompts, {g_cnt} responses | Source: **{source}***\n\n---\n\n")
    for m in messages:
        if m.get('type') == 'user': md_lines.append(format_user_message(m))
        elif m.get('type') == 'gemini': md_lines.append(format_gemini_message(m))
    with open(output_dir / (json_path.stem + '.md'), 'w', encoding='utf-8') as f: f.write(''.join(md_lines))
    return {'session_id': session_id, 'filename': json_path.stem + '.md', 'timestamp': timestamp, 'user_messages': u_cnt, 'gemini_messages': g_cnt}

def main():
    project_root = Path(__file__).parent.parent
    chat_logs_dir, output_dir = project_root / 'chat_logs', project_root / 'chat_logs_markdown'
    output_dir.mkdir(exist_ok=True)
    sessions = []
    for json_path in chat_logs_dir.glob('*.json'):
        info = convert_json_to_markdown(json_path, output_dir)
        if info: sessions.append(info)
    print(f"Converted {len(sessions)} conversations")

if __name__ == '__main__':
    main()
