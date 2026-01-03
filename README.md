# M-Gemini ♊️

**M-Gemini** is an automated archival engine and secure knowledge base designed to capture, redact, and organize the "thought process" and execution history of the Gemini CLI agent.

Built with a **Security-First** philosophy, it transforms raw machine-readable logs into a structured, human-readable repository while ensuring that sensitive data never touches the Git history.

### 🛡️ STRICT Security Architecture
*   **3-Layer Redaction:** Automated PII and secret stripping during the synchronization process.
*   **Gitleaks-Lite:** Local pre-commit hooks that block the accidental inclusion of API keys, tokens (including YubiKey OTPs), and credentials.
*   **Audit Logging:** Integrated system security auditing and continuous monitoring via `auditd`.
*   **Integrity:** Enforcement of GPG commit signing for verified authenticity.

### 📖 Human-Centric Archival
*   **Automated Journaling:** Generates daily summaries of collaborative accomplishments.
*   **Markdown Transformation:** Converts complex JSON/Protobuf sessions into clean, searchable Markdown.
*   **Chronological Discovery:** Easy navigation through the evolution of project tasks and system configurations.

---

## 📂 Repository Structure

* **`FULL_CHAT_LOG.md`**
  A single, chronologically ordered master chat log of all recorded sessions.

* **`chat_logs/`**
  Raw JSON logs synchronized from the local Gemini temporary directory. These are redacted versions of the original logs.

* **`chat_logs_markdown/`**
  Individual Markdown files for each session, converted from the JSON chat logs.
  * Includes tool calls, arguments, and outputs.
  * Metadata such as timestamps and user roles.

* **`journals/`**
  Daily entries summarizing key utilities and milestones accomplished.

* **`antigravity-data/`**
  Raw Protocol Buffer (`.pb`) files synced from local storage.

* **`scripts/`**
  * `sync_raw_logs.py`: Syncs and redacts logs from the local filesystem to this repository.
  * `process_logs.py`: The core engine that converts JSON logs to Markdown, generates daily journal entries, and aggregates the master chat log.
  * `pre_commit_check.py`: The STRICT security enforcement engine.

* **`Docs/`**
  * `M-SECURITY_legion-windows.md`: Comprehensive system security audit and hardening guide for Windows.
  * `M-SECURITY_legion-cachy.md`: Security audit reference for CachyOS.
  * `SECURITY.md`: Core security policies and redaction details.

## 🚀 Usage

### Prerequisites
* Python 3.x
* Access to local Gemini CLI log files (typically in `~/.gemini/tmp/...`)

### Operations Workflow

1. **Sync and Redact:**
   Bring in the latest logs from your local system:
   ```bash
   python3 scripts/sync_raw_logs.py
   ```

2. **Generate Documentation:**
   Convert logs to Markdown and update journals:
   ```bash
   python3 scripts/process_logs.py
   ```

3. **Consolidate History:**
   Regenerate the master chat log:
   *(This step is also handled by `process_logs.py` automatically)*

## 🔒 Security enforcement

This repository implements automated redaction to protect sensitive information.
* **PII Redaction:** Email addresses and specific personal identifiers are automatically masked.
* **Secret Redaction:** Patterns matching API keys, tokens (GitHub, Slack, etc.), YubiKey OTPs, and Private Keys are replaced with placeholders.
* **Pre-commit Hooks:** The repository is configured to reject commits containing specific high-sensitivity strings.

## ℹ️ About Gemini CLI

Gemini CLI is an interactive command-line agent capable of performing software engineering tasks, system administration, and general assistance directly within the terminal. This archive captures the "thought process" and execution steps of the agent.

---
*Generated automatically by M-Gemini tools.*
