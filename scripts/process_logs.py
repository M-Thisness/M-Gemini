#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

# ==========================================
# PART 1: Convert JSON to Markdown
# ==========================================

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
    
    # Thoughts
    thoughts = msg.get('thoughts', [])
    for t in thoughts:
        desc = t.get('description', '')
        summary = t.get('subject') or (desc[:50] + "...")
        output.append(f"> 🧠 **{summary}**\n> {desc}\n")
        
    # Tools
    for tool in msg.get('toolCalls', []):
        summary = format_tool_summary(tool)
        output.append(f"> 🛠️ **{summary}**")
        
        args = tool.get('args', {})
        cmd = args.get('CommandLine') or args.get('command')
        if cmd:
            output.append(f"> ` {cmd} `")
        
        result = tool.get('resultDisplay') or tool.get('result') or 'Done'
        result_str = str(result).strip()
        if result_str:
            preview = result_str[:200].replace('\n', ' ') + ('...' if len(result_str) > 200 else '')
            output.append(f"> -> *{preview}*")
        
        output.append("") 
        
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
        
    output_path = output_dir / (json_path.stem + '.md')
    with open(output_path, 'w', encoding='utf-8') as f: f.write(''.join(md_lines))
    return {'session_id': session_id}

def run_conversion(project_root: Path):
    print("--- Starting JSON to Markdown Conversion ---")
    chat_logs_dir = project_root / 'Archives'
    sessions = []
    for json_path in chat_logs_dir.glob('*.json'):
        info = convert_json_to_markdown(json_path, chat_logs_dir)
        if info: sessions.append(info)
    print(f"Converted {len(sessions)} conversations.")


# ==========================================
# PART 2: Generate Journals (Concatenation)
# ==========================================

def run_journal_generation(project_root: Path):
    print("\n--- Starting Journal Generation ---")
    chat_logs_dir = project_root / "Archives"
    journals_dir = project_root / "journals"
    journals_dir.mkdir(parents=True, exist_ok=True)

    daily_files = defaultdict(list)
    for md_file in chat_logs_dir.glob("session-*.md"):
        filename = md_file.name
        try:
            date_str = filename.split('session-')[1][:10]
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                daily_files[date_str].append(md_file)
        except IndexError: pass

    for date_str, files in daily_files.items():
        files.sort(key=lambda x: x.name)
        full_day_content = f"# Journal - {date_str}\n\n"
        for md_path in files:
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    full_day_content += f"{content.strip()}\n\n---\n\n"
            except Exception as e:
                print(f"Error reading {md_path}: {e}")

        with open(journals_dir / f"{date_str}.md", 'w', encoding='utf-8') as f:
            f.write(full_day_content)
        
    print(f"Generated {len(daily_files)} daily journals.")


# ==========================================
# PART 3: Combine Chat Logs (Full Log)
# ==========================================

def run_log_combination(project_root: Path):
    print("\n--- Combining All Chat Logs ---")
    source_dir = project_root / "Archives"
    output_file = project_root / "FULL_CHAT_LOG.md"

    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} not found.")
        return

    md_files = sorted(source_dir.glob("session-*.md"))
    print(f"Found {len(md_files)} session logs.")
    
    full_log_content = "# Full Gemini Chat History\n\n"
    full_log_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    full_log_content += "Ordered chronologically.\n\n"
    
    for md_path in md_files:
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                full_log_content += content.strip() + "\n\n<br>\n<br>\n\n"
        except Exception as e:
            print(f"Error reading {md_path}: {e}")
        
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_log_content)
        
    print(f"Successfully wrote full chat log to {output_file}")


# ==========================================
# Main Orchestrator
# ==========================================

def main():
    project_root = Path(__file__).parent.parent
    
    # 1. Convert JSON -> Markdown
    run_conversion(project_root)
    
    # 2. Generate Journals (Daily Aggregations)
    run_journal_generation(project_root)
    
    # 3. Combine All Logs (Master Record)
    run_log_combination(project_root)

if __name__ == "__main__":
    main()
