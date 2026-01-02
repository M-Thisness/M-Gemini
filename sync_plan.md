# Sync Configuration Plan

## Goal
Ensure `chat_logs_raw` and `antigravity-data` are tracked by Git and synced to the repository.

## Analysis
1.  **JSON Files**: Explicitly ignored by `*.json` in `.gitignore`.
    *   *Action*: Remove `*.json` ignore rule.
2.  **Antigravity Data**: Contains `.pb` files.
    *   *Action*: Verify if ignored. If so, whitelist.

## Steps
1.  [ ] **Modify .gitignore**:
    *   Remove `*.json`.
    *   Ensure no rules block `antigravity-data` or `chat_logs_raw`.
2.  [ ] **Stage & Commit**:
    *   `git add .` (should now pick up the files).
    *   `git commit -m "Configure repo to track all logs and data"`.
3.  [ ] **Push**:
    *   `git push` to `legion-windows`.
