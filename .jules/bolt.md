## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Parallelize git submodule update
**Learning:** `git submodule update` supports a `--jobs` argument to fetch submodules in parallel. In a repo with many submodules like QMK, sequential fetching is a major bottleneck.
**Action:** Always check if `git submodule update` can be parallelized, especially in CI or setup scripts. Use `--jobs` with a reasonable core count.
