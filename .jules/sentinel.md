## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-01-26 - Insecure Log File Creation
**Vulnerability:** The build script created log files in the current working directory using a predictable name. This allowed a local attacker to overwrite arbitrary user files via a symlink attack if they could plant a symlink in the directory where the script was run.
**Learning:** Defaulting to `os.getcwd()` for output files (especially logs) is risky in shared environments.
**Prevention:** Use `tempfile.mkdtemp()` (which has 0700 permissions) to store temporary logs, or explicitly validate that the output file path is not a symlink to a sensitive location.
