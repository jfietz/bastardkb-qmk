## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-25 - Insecure Log File Creation
**Vulnerability:** Log files created in `os.getcwd()` (Current Working Directory).
**Learning:** Writing files to the current working directory is risky if the directory is shared or untrusted (e.g., `/tmp`), as it enables symlink attacks or file clobbering.
**Prevention:** Always use secure temporary directories (e.g., `tempfile.mkdtemp()`) for logs and temporary artifacts, ensuring restrictive permissions.
