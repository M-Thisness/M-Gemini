# Gemini CLI Raw Conversation Logs

This directory contains redacted raw conversation logs from Gemini CLI sessions.

**Last Sync:** 2026-01-01 15:05:43

## Format
- Files are in JSON format.
- Contains full session metadata, messages, thoughts, and tool calls.
- All sensitive data is automatically redacted before syncing.

## Redacted Information
The sync script automatically redacts:
- API keys and authentication tokens
- Email addresses
- Phone numbers
- IP addresses
- Private keys
- Database connection strings
- File paths containing usernames
- Other PII and secrets

## Syncing
To sync the latest logs:
```bash
python scripts/sync_raw_logs.py
```
