## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Parallel Compilation Defaults
**Learning:** Defaulting build concurrency (`--parallel`) to 1 severely limits performance on modern multi-core machines. Python's `os.cpu_count()` provides a safe default to maximize resource utilization.
**Action:** Always verify default concurrency settings in build scripts and use `os.cpu_count()` or similar dynamic checks instead of hardcoded low values.
