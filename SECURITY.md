# Security Policy

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

If you believe you have found a security vulnerability in this project, please report it privately.

## Data Safety

This repository is designed to store processed logs.
- **Do not commit** original `.pb` or `.json` session files containing raw tokens.
- **Do not commit** `.env` files or certificates.
- The `convert_sessions.py` script attempts to redact known secret patterns, but manual review is always recommended before pushing new transcripts.
