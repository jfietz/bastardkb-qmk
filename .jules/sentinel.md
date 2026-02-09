## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-09 - Insecure Default Log Location
**Vulnerability:** Application logs were written to the current working directory (`cwd`) by default, potentially exposing sensitive build information in shared environments.
**Learning:** Defaulting to `cwd` for logs assumes `cwd` is private, which is a faulty assumption especially in CI/CD or shared workspaces.
**Prevention:** Use XDG Base Directory specification (e.g., `XDG_STATE_HOME`) for application logs and enforce restrictive permissions (`0700`).
