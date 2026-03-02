## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-25 - Insecure Directory Permissions
**Vulnerability:** Relying on `os.makedirs(..., mode=0o700, exist_ok=True)` which does not update permissions of an existing directory.
**Learning:** When ensuring secure permissions on a directory that might already exist, explicit `os.chmod` is required because `exist_ok=True` silently ignores existing incorrect permissions.
**Prevention:** Always follow `os.makedirs(..., mode=..., exist_ok=True)` with an explicit `os.chmod` when securing sensitive directories.
