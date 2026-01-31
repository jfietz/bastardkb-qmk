## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Mocking dependencies for build scripts
**Learning:** `bastardkb_build_releases.py` imports `pygit2` and `rich` at the top level. These libraries are not available in the testing environment (CI). Tests importing this module must mock these dependencies in `sys.modules` *before* import to avoid `ModuleNotFoundError`.
**Action:** When writing tests for scripts with top-level heavy dependencies, check if they are installed in the test environment. If not, use `sys.modules` patching in `setUp` or before import.

## 2026-01-26 - Parallel build defaults
**Learning:** `qmk compile` defaults to single-threaded builds. Explicitly defaulting `--parallel` to `os.cpu_count()` ensures optimal resource usage on any machine without user intervention.
**Action:** Always verify default parallelism in build scripts. Default to `os.cpu_count()` or `multiprocessing.cpu_count()` where safe.
