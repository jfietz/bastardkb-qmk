## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2024-03-01 - Secure Directory Permissions
**Vulnerability:** `os.makedirs(..., mode=0o700, exist_ok=True)` does not update permissions if the directory already exists.
**Learning:** When using XDG directories or any predictable location, pre-existing directories could have overly permissive access, leading to information disclosure.
**Prevention:** Always explicitly call `os.chmod()` after `os.makedirs()` to enforce strict permissions.
