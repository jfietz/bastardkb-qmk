## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-26 - Insecure Log File Creation
**Vulnerability:** Log file created in current working directory with default permissions (world-readable).
**Learning:** Utilities often default to CWD for logs, which is insecure in shared environments. `RotatingFileHandler` respects `umask` but defaults to system umask which might be permissive.
**Prevention:** Store logs in user-specific secure directories (e.g., `XDG_STATE_HOME`) with `0o700` directory permissions and force `0o600` file permissions using `os.umask`.
