## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-25 - Secure Application Logging
**Vulnerability:** Writing logs to `cwd` (insecure temporary file / symlink attack risk).
**Learning:** Scripts running in shared environments must not default to writing logs in the current working directory, as it risks information disclosure or symlink attacks.
**Prevention:** Use XDG Base Directory specification (`XDG_STATE_HOME` or `~/.local/state`) with restricted permissions (`0o700`) for application logs. Fallback to `tempfile.mkdtemp()` if necessary.
