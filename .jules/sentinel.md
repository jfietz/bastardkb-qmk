## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-30 - Insecure Log File Location
**Vulnerability:** `RotatingFileHandler` writing logs to `os.getcwd()` created a symlink vulnerability if the script was run in shared directories (e.g. `/tmp`), allowing attackers to potentially overwrite or corrupt files.
**Learning:** CLI tools should not default to writing logs to the current working directory, as it's often untrusted.
**Prevention:** Use a secure, persistent, user-specific directory (like XDG State Home) for application logs, ensuring it has 0700 permissions.
