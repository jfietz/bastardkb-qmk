## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-05-15 - Insecure Log File Location
**Vulnerability:** Application logs were written to `CWD` with default permissions.
**Learning:** Writing logs to the current working directory is risky as it may be a shared location or have loose permissions, exposing sensitive build details.
**Prevention:** Use standard secure state directories (e.g., `XDG_STATE_HOME`) with explicit `0700` directory and `0600` file permissions for application logs.
