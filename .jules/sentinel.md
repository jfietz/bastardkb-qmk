## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2025-03-01 - Directory Creation Permissions
**Vulnerability:** `os.makedirs(mode=0o700, exist_ok=True)` does not enforce permissions if the directory already exists. This can lead to sensitive application logs being readable by other users if the directory was previously created with looser permissions.
**Learning:** In Python, the `mode` parameter in `os.makedirs()` and `os.mkdir()` is only applied when creating a new directory. It will not alter the permissions of existing directories when `exist_ok=True` is used.
**Prevention:** Explicitly call `os.chmod(path, mode)` after `os.makedirs` to enforce the desired permissions regardless of whether the directory was newly created or previously existing.
