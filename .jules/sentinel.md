## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-25 - Secure Log Storage
**Vulnerability:** Build logs written to the current working directory with default permissions.
**Learning:** CLI tools often log to CWD for convenience, but if executed in shared directories (like `/tmp`), this exposes sensitive build information (paths, env vars) to other users.
**Prevention:** Use standard secure state directories (e.g., `XDG_STATE_HOME`, `~/.local/state`) with restricted permissions (`0o700`) for persistent application logs.
