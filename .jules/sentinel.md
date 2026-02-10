## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-25 - Secure Log Storage (REJECTED)
**Proposal:** Move application logs to `XDG_STATE_HOME` with restricted permissions.
**Constraint:** The maintainers explicitly prefer logs in the current working directory (`os.getcwd()`).
**Outcome:** Reverted changes. Do not attempt to move logs for this project again.
