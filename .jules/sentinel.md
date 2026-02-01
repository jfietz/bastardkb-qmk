## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-01 - Secure Log Storage
**Vulnerability:** Application logs were written to `os.getcwd()`, posing risks in shared directories (symlink attacks) and causing permission errors.
**Learning:** Scripts often default to CWD for logs, ignoring multi-user environment risks.
**Prevention:** Use `XDG_STATE_HOME` or `~/.local/state` with 0700 permissions for persistent logs.
