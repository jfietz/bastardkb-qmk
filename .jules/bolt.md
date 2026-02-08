## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-27 - Parallel git submodule update
**Learning:** `git submodule update` supports `--jobs N` to fetch submodules in parallel, which is significantly faster than sequential updates when many submodules exist. This option is not prominently featured in `git submodule --help` summary but exists since git 2.10.
**Action:** Check for parallel execution options in git commands (like `fetch --jobs`, `submodule update --jobs`) when dealing with large repositories or many submodules.
