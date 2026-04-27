## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-03-04 - Insecure Directory Permissions with os.makedirs
**Vulnerability:** Pre-existing log directory with permissive permissions was not adequately restricted, because `os.makedirs(..., mode=0o700, exist_ok=True)` only applies `mode` to newly created directories. This allowed local attackers to view potentially sensitive build logs if they could pre-create the directory.
**Learning:** Python's `os.makedirs` function does not enforce the specified `mode` on existing directories when `exist_ok=True` is provided. This is a common and dangerous anti-pattern for log and state directories.
**Prevention:** Always use `os.chmod()` immediately after `os.makedirs()` if the directory may already exist, or use a method that explicitly handles permissions on pre-existing paths.

## 2026-11-09 - Arbitrary File Overwrite via Symlink with shutil.copyfile
**Vulnerability:** Insecure file copy operation with `shutil.copyfile(src, dst)`. If `dst` already exists as a symbolic link pointing to a sensitive file, `shutil.copyfile` will resolve the symlink and overwrite the target file with the source file contents.
**Learning:** Python's `shutil.copyfile` follows symlinks at the destination path by default. If the destination directory is attacker-controllable (e.g., world-writable or shared), they can pre-create symlinks pointing to sensitive files (like `/etc/passwd` or ssh keys) and the script will blindly overwrite them.
**Prevention:** Always verify if the destination path is a symlink or exists before copying. Use `if dst.exists() or dst.is_symlink(): dst.unlink()` to explicitly remove any pre-existing symlinks or files before copying into that path.

## 2026-11-20 - Insecure Log File Rotation Permissions
**Vulnerability:** When using standard `RotatingFileHandler` with a temporary umask setup, the initial log file is created with restricted permissions (e.g., `0600`), but rotated files created later by the handler inherit the process's default umask (often `022`), resulting in permissive permissions (e.g., `0644`). This could expose rotated logs to unauthorized local users.
**Learning:** Setting the `umask` around the initialization of a `RotatingFileHandler` is insufficient to protect rotated log files, as the file rotation logic happens asynchronously later during a logging event.
**Prevention:** Subclass the `RotatingFileHandler` and override the internal `_open` method to temporarily apply a restrictive `umask` (e.g., `0o077`) every time a new log file is opened or rotated, ensuring all generated log files maintain correct permissions.

## 2026-04-19 - Arbitrary File Read via Source Symlink Resolution
**Vulnerability:** Insecure file iteration using `Path.is_file()` during via.json copying in `bastardkb_build_releases.py`. Because `is_file()` follows symlinks by default, an attacker could create a symlink in the untrusted `via` directory pointing to a sensitive file outside the repository (e.g., `/etc/passwd`). The script would then read and copy the contents of the sensitive file to the output directory.
**Learning:** `Path.is_file()` follows symlinks natively. When traversing or processing files from untrusted or shared directories, relying solely on `is_file()` can lead to arbitrary file read vulnerabilities if the file is copied or read.
**Prevention:** Always explicitly check for and reject symlinks when processing files from untrusted directories, using `f.is_file() and not f.is_symlink()`.

## 2026-05-15 - Path Traversal via Unsanitized Basename in pathlib
**Vulnerability:** In `Reporter.log_file()`, passing unsanitized user inputs (like branch names containing slashes) directly to `pathlib.Path()` allows path traversal if an attacker controls the branch name. Additionally, using `Path.with_suffix(".log")` on the resulting path can incorrectly truncate parts of the original basename if it contains dots (e.g., `branch.v1.0` becomes `branch.v1.log`).
**Learning:** `pathlib.Path` concatenates paths without sanitizing directory separators. When building paths using user-controlled basenames, the basename must be explicitly sanitized. Furthermore, `Path.with_suffix()` replaces the existing suffix; if the unsanitized basename contains a dot, it acts destructively rather than just appending.
**Prevention:** Sanitize user input basenames by replacing directory separators (`/` and `\`) with safe characters like `_`. To append an extension to a string that might already contain dots, use string formatting (e.g., `f"{sanitized_name}.log"`) before passing it to `pathlib.Path`.
