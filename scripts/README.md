# Automation Scripts

This directory contains the Python scripts that power the **M-Gemini** archival and documentation pipeline. These scripts are designed to start with raw, machine-generated logs and transform them into a secure, human-readable knowledge base.

## 📜 `process_logs.py`

This is the core engine of the repository. It consolidates multiple processing steps into a single execution flow to ensure data consistency.

### Key Functions

1.  **JSON to Markdown Conversion (`run_conversion`)**
    *   **Input:** Iterates through `.json` files in the `Archives/` directory.
    *   **Processing:** Parses the raw JSON structure, extracting messages, tool calls, and thoughts. It formats timestamps and constructs a clean Markdown representation.
    *   **Output:** Generates a corresponding `.md` file for each session (e.g., `session-XYZ.md`).

2.  **Journal Generation (`run_journal_generation`)**
    *   **Input:** Scans the generated `.md` session files.
    *   **Processing:** Groups sessions by their date (extracted from filenames). It concatenates all sessions from a single day into a unified entry.
    *   **Output:** Creates daily log files in the `journals/` directory (e.g., `2025-01-01.md`).

3.  **Log Aggregation (`run_log_combination`)**
    *   **Input:** All `.md` session files in `Archives/`.
    *   **Processing:** Sorts sessions chronologically and concatenates them into one massive document.
    *   **Output:** Updates the master `FULL_CHAT_LOG.md` at the repository root.

## 🔄 `sync_raw_logs.py`

This script handles the specific task of bridging the local environment to the repository while enforcing security protocols.

### Workflow

1.  **Discovery:** Locates raw Gemini session logs in the local temporary directory (`~/.gemini/tmp`).
2.  **Redaction:**
    *   Applies a set of regex patterns (`SECRET_PATTERNS`) to the raw content *before* it leaves memory.
    *   Targets: API Keys (AWS, Slack, GitHub, Google), Private Keys, Email addresses, and YubiKey OTPs.
3.  **Normalization:** Ensures every JSON log has a `source` ID attributed to the current machine.
4.  **Archival:** Writes the sanitized JSON files to the `Archives/` directory.

> [!IMPORTANT]
> This script is the primary gatekeeper for preventing sensitive data leaks. It must be run *before* committing any new logs.
