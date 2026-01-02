# Archives (Gemini CLI Logs)

This directory acts as the central repository for your Gemini CLI conversation history. It contains both the **Source of Truth (JSON)** and the **Human-Readable (Markdown)** versions of every session.

## 🔄 The Workflow: From CLI to Markdown

The following automated pipeline ensures your local CLI sessions are safely backed up, redacted, and converted into a readable format on GitHub.

### 1. **Unload & Redact (Local)**
*   **Script:** `scripts/sync_raw_logs.py`
*   **Action:**
    1.  Reads raw session logs from your local machine (`~/.gemini/tmp`).
    2.  **Redacts sensitive data** (API keys, PII, secrets) using `gitleaks` patterns.
    3.  Copies the safe JSON files into this `Archives/` folder.

### 2. **Push to GitHub**
*   **Action:** You commit and push the new JSON files to the repository.
*   **Safety:** `gitleaks` (via `gitleaks.toml`) scans the commit to ensure no secrets were missed.

### 3. **Automated Processing (GitHub Actions)**
*   **Workflow:** `.github/workflows/process_logs.yml`
*   **Trigger:** Pushing files to `Archives/`.
*   **Steps:**
    1.  **Parse JSON:** The workflow runs `scripts/convert_to_markdown.py`. This script reads every JSON file and generates a companion `.md` file in the same folder.
    2.  **Generate Journals:** `scripts/generate_journals.py` processes the logs to create daily engineering field logs in `journals/`.
    3.  **Combine Logs:** `scripts/combine_chat_logs.py` aggregates all markdown files into the master `FULL_CHAT_LOG.md`.
    4.  **Commit:** The workflow automatically commits the new Markdown files back to the repo.

---

## 🆚 Comparison: Raw JSON vs. Parsed Markdown

The transformation creates a clean, readable thread from the complex raw data.

### **Raw JSON (`session-....json`)**
*   **Format:** Machine-readable structure.
*   **Content:** Contains full metadata, timestamps, token usage, tool arguments, and raw API responses.
*   **Use Case:** Debugging, data analysis, programmatic access.

```json
{
  "id": "28f5a0e5-...",
  "timestamp": "2025-12-03T01:15:13.025Z",
  "type": "user",
  "content": "format the USB flashdrive named Mischa (E:) into EXT4"
},
{
  "id": "ee87004d-...",
  "timestamp": "2025-12-03T01:15:36.511Z",
  "type": "gemini",
  "toolCalls": [
    {
      "name": "run_shell_command",
      "args": {
        "command": "Get-PSDrive -Name E; wsl --status"
      },
      "resultDisplay": "Name Used (GB) Free (GB)...\nE 0.00 117.56..."
    }
  ],
  "thoughts": [
    {
      "subject": "Assessing Format Feasibility",
      "description": "I've begun evaluating available tools..."
    }
  ]
}
```

### **Parsed Markdown (`session-....md`)**
*   **Format:** Human-readable GitHub-flavored Markdown.
*   **Content:**
    *   **👤 / 🤖 Icons:** Clearly distinguish User vs. Agent.
    *   **Collapsed Context:** Thoughts (`🧠`) and Tool Calls (`🛠️`) are hidden in blockquotes to keep the thread clean, but available if needed.
    *   **Clean Output:** Focuses on the conversation flow.

```markdown
👤: **format the USB flashdrive named Mischa (E:) into EXT4**

> 🧠 **Assessing Format Feasibility**
> I've begun evaluating available tools...

> 🛠️ **Ran `Get-PSDrive`**
> ` Get-PSDrive -Name E; wsl --status `
> -> *Name Used (GB) Free (GB)...*

🤖: Windows does not natively support formatting drives to the **EXT4** file system.
```
