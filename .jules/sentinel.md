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

## 2026-11-20 - Arbitrary File Read via Path.is_file Following Symlinks
**Vulnerability:** In `copy_assets_to_output_dir`, `Path.glob()` combined with `Path.is_file()` was used to find and copy `.via.json` files. If a malicious symlink pointing to a sensitive file was present in the source directory, `is_file()` would follow it and evaluate to true, resulting in the sensitive file being copied to the public build output.
**Learning:** Python's `Path.is_file()` follows symlinks by default. When handling untrusted or externally controllable source directories, relying solely on `is_file()` can lead to arbitrary file read vulnerabilities if symlinks are created.
**Prevention:** Always explicitly check for symlinks when searching for files to copy from untrusted locations. Use `not f.is_symlink()` in combination with `f.is_file()` to ensure only regular files are processed and malicious symlinks are ignored.
