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
## 2026-11-20 - Insecure Log Rotation Permissions
**Vulnerability:** Insecure file permissions on rotated log files. While the initial log file was created with a restricted `umask` (e.g., `0o077`), subsequent rotated log files created by Python's `logging.handlers.RotatingFileHandler` ignore this temporary setup and fall back to the system's default `umask`, exposing rotated logs to other users on the system.
**Learning:** Python's standard library `RotatingFileHandler` manages log rotation internally. Temporarily setting `os.umask()` around its instantiation only affects the *first* log file it creates. When it rotates files, the underlying `open()` call uses the system default environment.
**Prevention:** To enforce strict permissions (e.g., `0600`) on all rotated files, you must subclass `RotatingFileHandler` and override its `_open()` method to explicitly set the `umask` specifically when the file is being opened or created, restoring it immediately afterward in a `finally` block.
