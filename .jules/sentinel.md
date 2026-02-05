## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-05 - Secure Logging & Pre-flight Checks
**Vulnerability:** Log files were created in the current working directory, posing a symlink attack risk if run from insecure locations (e.g., /tmp). Missing dependency checks led to ugly stack traces.
**Learning:** Tools should not assume the current working directory is secure. Failing securely with a clear error message is better than crashing with a stack trace.
**Prevention:** Use XDG Base Directory specification (e.g., `XDG_STATE_HOME`) for logs/state with strict permissions (`0700`). Add pre-flight checks for required external tools.
