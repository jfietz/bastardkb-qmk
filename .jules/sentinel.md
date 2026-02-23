## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-14 - Insecure Log File Permissions
**Vulnerability:** Application logs created in `os.getcwd()` with default umask (often 0644) expose potentially sensitive build information to other users on shared systems.
**Learning:** Defaulting to the current working directory for logs is risky in multi-user environments. `RotatingFileHandler` does not inherently support permission enforcement, requiring explicit `umask` manipulation.
**Prevention:** Store logs in user-private directories (e.g., `XDG_STATE_HOME`) with strict permissions (0700 for directory, 0600 for files) using `os.umask` blocks during file creation.
