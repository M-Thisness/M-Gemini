#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def get_time_of_day(hour):
    if 5 <= hour < 12: return "Morning"
    elif 12 <= hour < 18: return "Day"
    else: return "Night"

def summarize_session(messages):
    user_prompts = [msg for msg in messages if msg.get('type') == 'user']
    if not user_prompts: return "**Goal**: System maintenance and background tasks."
    
    first_prompt = user_prompts[0].get('content', '').strip()
    goal = first_prompt.split('\n')[0][:150].strip().rstrip('.')
    
    summary_lines = [f"**Goal**: {goal}"]
    
    # Heuristics for actions
    seen_actions = set()
    
    for msg in messages:
        # Check tool calls
        if 'toolCalls' in msg:
            for tool in msg['toolCalls']:
                name = tool.get('name')
                args = tool.get('args', {})
                
                # Normalize tool names and args
                if name in ['run_command', 'run_shell_command']:
                    cmd = args.get('CommandLine') or args.get('command') or ''
                    cmd_name = cmd.split()[0]
                    if cmd_name and cmd_name not in ['git', 'ls', 'cd', 'dir', 'echo']: 
                        action = f"[x] **Exec**: Run `{cmd_name}`"
                        if action not in seen_actions:
                            summary_lines.append(f"*   {action}")
                            seen_actions.add(action)
                            
                elif name in ['replace_file_content', 'multi_replace_file_content', 'write_to_file', 'edit_file']: # edit_file might be legacy
                    path = args.get('TargetFile') or args.get('file_path') or args.get('target_file') or 'file'
                    filename = os.path.basename(path)
                    action = f"[+] **Edit**: Modified `{filename}`"
                    if action not in seen_actions:
                        summary_lines.append(f"*   {action}")
                        seen_actions.add(action)
                        
                elif name in ['search_web', 'google_search']:
                    query = args.get('query') or args.get('q') or 'something'
                    action = f"[?] **Research**: Searched for '{query}'"
                    if action not in seen_actions:
                         summary_lines.append(f"*   {action}")
                         seen_actions.add(action)


    # Simple outcome guess
    summary_lines.append(f"*   **Outcome**: Completed {len(messages)} interactions.")
    
    return '\n'.join(summary_lines)

def main():
    repo_root = Path(__file__).parent.parent
    chat_logs_dir, journals_dir = repo_root / "Archives", repo_root / "journals"
    daily_data = defaultdict(lambda: defaultdict(list))
    for json_file in chat_logs_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f: data = json.load(f)
            start_time = datetime.fromisoformat(data.get('startTime').replace('Z', '+00:00'))
            date_str, period, source = start_time.strftime('%Y-%m-%d'), get_time_of_day(start_time.hour), data.get("source", "unknown")
            daily_data[date_str][period].append({'timestamp': start_time.strftime('%H:%M'), 'summary': summarize_session(data.get('messages', [])), 'source': source})
        except: continue
    for date_str, periods in daily_data.items():
        all_entries = []
        for p in ["Morning", "Day", "Night"]: all_entries.extend(periods[p])
        all_entries.sort(key=lambda x: x['timestamp'])
        content = f"# Journal - {date_str}\n\n"
        for entry in all_entries: content += f"**{entry['timestamp']} ({entry['source']})**\n{entry['summary']}\n\n"
        with open(journals_dir / f"{date_str}.md", 'w', encoding='utf-8') as f: f.write(content)
    print(f"Generated {len(daily_data)} journal entries")

if __name__ == "__main__":
    main()
