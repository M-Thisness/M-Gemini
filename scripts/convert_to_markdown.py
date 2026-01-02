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
    content = msg.get('content', '').strip()
    return f"👤: **{content}**\n\n"

def format_tool_summary(tool: Dict[str, Any]) -> str:
    name = tool.get('name')
    args = tool.get('args', {})
    
    if name in ['run_command', 'run_shell_command']:
        cmd = args.get('CommandLine') or args.get('command') or ''
        return f"Ran `{cmd.split()[0]}`" if cmd else f"Ran command"
    elif name in ['read_file', 'view_file', 'read_url_content']:
        path = args.get('file_path') or args.get('AbsolutePath') or args.get('Url') or 'file'
        return f"Read `{Path(path).name}`"
    elif name in ['write_to_file', 'replace_file_content', 'multi_replace_file_content']:
        path = args.get('TargetFile') or 'file'
        return f"Edited `{Path(path).name}`"
    elif name in ['search_web', 'google_search']:
        q = args.get('query') or 'query'
        return f"Searched `{q}`"
    else:
        return f"Called `{name}`"

def format_gemini_message(msg: Dict[str, Any]) -> str:
    output = []
    
    # Thoughts (collapsed visual using blockquote)
    thoughts = msg.get('thoughts', [])
    for t in thoughts:
        desc = t.get('description', '')
        summary = t.get('subject') or (desc[:50] + "...")
        # Use blockquote for thinking to keep it distinct but readable
        output.append(f"> 🧠 **{summary}**\n> {desc}\n")
        
    # Tools (collapsed visual using blockquote)
    for tool in msg.get('toolCalls', []):
        summary = format_tool_summary(tool)
        # Compact tool info
        output.append(f"> 🛠️ **{summary}**")
        
        # Args - summarized or full? User wanted compact.
        # Let's put args in a code block inside the quote if needed, or just keep it simple.
        # For LLM context, full args are useful. For human reading, summary is better.
        # Let's try a hybrid:
        # > 🛠️ Ran `winget search`
        # > Input: `winget search Playnite`
        # > Output: `Found Playnite...`
        
        args = tool.get('args', {})
        cmd = args.get('CommandLine') or args.get('command')
        if cmd:
            output.append(f"> ` {cmd} `")
        
        result = tool.get('resultDisplay') or tool.get('result') or 'Done'
        result_str = str(result).strip()
        if result_str:
            # Truncate long outputs for readability, LLMs can handle truncation contextually usually
            # unless we need full logs. User asked for "clean".
            preview = result_str[:200].replace('\n', ' ') + ('...' if len(result_str) > 200 else '')
            output.append(f"> -> *{preview}*")
        
        output.append("") # Spacer
        
    content = msg.get('content', '').strip()
    if content:
        output.append(f"🤖: {content}\n")

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
    chat_logs_dir, output_dir = project_root / 'chat_logs_raw', project_root / 'chat_logs_markdown'
    output_dir.mkdir(exist_ok=True)
    sessions = []
    for json_path in chat_logs_dir.glob('*.json'):
        info = convert_json_to_markdown(json_path, output_dir)
        if info: sessions.append(info)
    print(f"Converted {len(sessions)} conversations")

if __name__ == '__main__':
    main()
