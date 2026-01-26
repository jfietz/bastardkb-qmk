## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-05-20 - Log Filename Sanitization
**Vulnerability:** Potential Path Traversal in log filenames.
**Learning:** Using user-controlled input (like branch names) directly in filenames can lead to directory traversal or invalid paths, even in auxiliary files like logs.
**Prevention:** Always sanitize strings used to construct filenames using a strict allowlist of characters.
