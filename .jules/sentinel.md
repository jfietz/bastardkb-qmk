## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-06 - Log File Location Security
**Vulnerability:** Writing logs to `os.getcwd()` allows potential symlink attacks and information disclosure in shared environments.
**Learning:** CLI tools often default to writing logs in the current directory for convenience, ignoring the security implications of shared directories (e.g., `/tmp`).
**Prevention:** Follow XDG Base Directory specification (`XDG_STATE_HOME`) and explicitly set `0700` permissions on log directories.
