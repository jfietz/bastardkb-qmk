## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-26 - Pre-existing Directory Permission Integrity
**Vulnerability:** Ignored pre-existing directory permissions using `os.makedirs(..., exist_ok=True)`.
**Learning:** `os.makedirs(..., mode=0o700, exist_ok=True)` does not enforce the mode if the directory already exists. This can lead to sensitive directories (like log storage) retaining overly permissive permissions from prior creations or manual intervention.
**Prevention:** Explicitly apply `os.chmod(dir, mode)` after directory creation/verification to enforce permissions, regardless of prior existence.
