## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-02-14 - Incremental builds with ccache
**Learning:** Removing the `--clean` flag from `qmk compile` allows `make` to skip recompilation of unchanged files, significantly speeding up incremental builds when `ccache` is enabled (`USE_CCACHE=yes`). This aligns with the codebase's performance goals.
**Action:** When optimizing build scripts, verify if cleaning is strictly necessary or if the build system handles dependency tracking correctly. Prefer incremental builds for development workflows.
