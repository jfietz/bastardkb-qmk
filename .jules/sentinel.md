## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-02-09 - Log Location Constraint
**Rejected Change:** Moving application logs to `XDG_STATE_HOME` was rejected by maintainers.
**Reason:** Maintainers prefer logs in the current working directory for visibility or workflow reasons, despite the potential security implication in shared environments.
**Constraint:** Do not attempt to move `bastardkb_build_releases.py.log` out of the project root.
