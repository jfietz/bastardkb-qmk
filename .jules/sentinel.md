## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-25 - Insecure Log File Location
**Vulnerability:** Application logs were written to the current working directory (`os.getcwd()`) with default permissions, potentially exposing sensitive information if run in shared directories or failing if the directory is non-writable.
**Learning:** Defaulting to CWD for logs is insecure and fragile. Always use standard user state directories (XDG_STATE_HOME) with restricted permissions (`0o700` for directory, `0o600` for file).
**Prevention:** Use `XDG_STATE_HOME` and explicitly set permissions on log directories and files.
