## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-12 - Secure Logging Directory
**Vulnerability:** Application logs were written to the current working directory, posing a risk of information leakage in shared environments and cluttering the workspace.
**Learning:** Build tools often default to `cwd` for logs. XDG Base Directory specification (`XDG_STATE_HOME`) provides a standard, secure location (`0700` permissions) for such artifacts.
**Prevention:** Use `os.environ.get("XDG_STATE_HOME")` and ensure directory permissions are explicitly set to `0700`.
