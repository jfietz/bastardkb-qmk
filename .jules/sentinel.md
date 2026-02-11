## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-26 - Insecure Log File Location
**Vulnerability:** `bastardkb_build_releases.py` created logs in `os.getcwd()` with default permissions.
**Learning:** Defaulting to CWD for logs allows local attackers to pre-create symlinks in shared directories (like `/tmp`), leading to arbitrary file overwrite when the script is run by a victim.
**Prevention:** Use user-specific state directories (e.g., `XDG_STATE_HOME`) with restricted permissions (0700) for application logs.
