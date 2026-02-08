## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-25 - Secure Log Storage
**Vulnerability:** Application logs were written to `os.getcwd()` with default permissions.
**Learning:** Writing logs to the current working directory exposes them to unauthorized users if the directory is shared or world-writable, and relies on the user running the script from a writable location.
**Prevention:** Store logs in a user-private directory (e.g., `XDG_STATE_HOME`) with restricted permissions (`0700`).
