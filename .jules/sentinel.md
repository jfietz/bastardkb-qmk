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

## 2026-11-21 - Arbitrary File Read via Symlink copy
**Vulnerability:** Insecure file collection resolving symlinks by default. When using `Path.is_file()` or similar methods to find files to copy from an untrusted or potentially compromised directory, symlinks are followed and copied.
**Learning:** Python's `Path.is_file()` resolves symlinks. If an attacker can introduce a symlink into a directory that is subsequently scraped for files to publish (e.g., pointing to `/etc/passwd`), the script will blindly copy the sensitive file contents into the output directory, leading to an Arbitrary File Read vulnerability.
**Prevention:** When scanning directories for files to process or copy, explicitly verify that the file is not a symlink by adding `and not f.is_symlink()` to the condition, unless resolving symlinks is an explicitly required and safe behavior.
