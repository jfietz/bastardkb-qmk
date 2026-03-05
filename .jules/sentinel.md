## 2026-01-25 - Build Script Integrity
**Vulnerability:** Ignored return code from `git submodule update` in build script.
**Learning:** Build scripts often assume happy paths for external commands. Failing to check return codes can lead to builds proceeding with incomplete or outdated dependencies (integrity loss).
**Prevention:** Always check return codes of subprocess calls, especially for critical setup steps like dependency fetching.

## 2026-03-04 - Insecure Directory Permissions with os.makedirs
**Vulnerability:** Pre-existing log directory with permissive permissions was not adequately restricted, because `os.makedirs(..., mode=0o700, exist_ok=True)` only applies `mode` to newly created directories. This allowed local attackers to view potentially sensitive build logs if they could pre-create the directory.
**Learning:** Python's `os.makedirs` function does not enforce the specified `mode` on existing directories when `exist_ok=True` is provided. This is a common and dangerous anti-pattern for log and state directories.
**Prevention:** Always use `os.chmod()` immediately after `os.makedirs()` if the directory may already exist, or use a method that explicitly handles permissions on pre-existing paths.

## 2026-03-05 - Symlink Attack via shutil.copyfile
**Vulnerability:** Arbitrary file overwrite when copying files (e.g. `shutil.copyfile` or `Path.rename`) to a user-controlled output directory without checking if the destination is a symlink. `shutil.copyfile(src, dst)` will follow the symlink at `dst` and overwrite its target.
**Learning:** Functions like `shutil.copyfile` follow symlinks by default, leading to critical file overwrite vulnerabilities if the destination path is a symlink created by a malicious user in a shared output directory.
**Prevention:** Always check if the destination path exists or is a symlink (`dst.exists() or dst.is_symlink()`) and remove it before copying or renaming files to it.
