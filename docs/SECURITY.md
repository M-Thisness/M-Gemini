# Security Policy

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

If you believe you have found a security vulnerability in this project, please report it privately.

## Data Safety

This repository is designed to store processed logs.
- **Do not commit** original `.pb` or unredacted `.json` session files.
- **Do not commit** `.env` files or certificates.
- The `sync_raw_logs.py` script automatically redacts sensitive data during synchronization.
- The `convert_to_markdown.py` script generates readable versions of the logs.
- Manual review is always recommended before pushing new chat logs.
