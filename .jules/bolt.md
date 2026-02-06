## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Parallelize git submodule update
**Learning:** `git submodule update` supports a `--jobs <N>` argument (since Git 2.9) to fetch submodules in parallel. This significantly speeds up initialization for repositories with many submodules like QMK.
**Action:** Always check for parallel execution options (`--jobs`, `--parallel`) when scripting subprocess calls, especially for network or build operations.
