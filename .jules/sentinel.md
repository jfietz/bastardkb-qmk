## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-05-23 - Insecure Log File Location
**Vulnerability:** Build logs were written to `CWD` with default permissions.
**Learning:** Tools writing logs to `CWD` can expose sensitive build information in shared environments (e.g., `/tmp` or shared project dirs) if file permissions are not restricted.
**Prevention:** Use `XDG_STATE_HOME` (or `~/.local/state`) for application logs and enforce `0700` directory permissions and `0600` file permissions.
