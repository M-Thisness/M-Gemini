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
    user_prompts = [msg.get('content', '').strip() for msg in messages if msg.get('type') == 'user']
    if not user_prompts: return "System maintenance and background tasks."
    intent = user_prompts[0].split('\n')[0][:100].strip().rstrip('.')
    return f"{intent} across {len(user_prompts)} interactions."

def main():
    repo_root = Path(__file__).parent.parent
    chat_logs_dir, journals_dir = repo_root / "chat_logs", repo_root / "journals"
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
