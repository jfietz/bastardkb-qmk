## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-06 - Insecure Log File Location
**Vulnerability:** Application logs were written to the current working directory with default permissions.
**Learning:** Writing logs to CWD can expose sensitive information in shared environments and pollute the user's workspace.
**Prevention:** Use standard XDG state directories (e.g., `~/.local/state/`) with restricted permissions (0700) for application logs.
