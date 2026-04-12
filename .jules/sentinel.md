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

## 2024-04-12 - Arbitrary File Read via Symlink
**Vulnerability:** In `copy_assets_to_output_dir`, the `Path.is_file()` check follows symlinks by default. This allows a malicious repository to include a symlink pointing to a sensitive file outside the expected directory, which is then copied to the output directory, leading to an arbitrary file read vulnerability.
**Learning:** Python's `Path.is_file()` returns `True` for symlinks that point to regular files. When processing files from an untrusted source, such as a Git repository, relying solely on `is_file()` is insufficient to prevent following malicious symlinks.
**Prevention:** When traversing and operating on files from an untrusted directory, explicitly check `not f.is_symlink()` in addition to `f.is_file()` to ensure the application only processes actual files and does not follow symlinks.
