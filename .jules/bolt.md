## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Enable incremental builds and optimize list flattening
**Learning:** Passing `--clean` to `qmk compile` prevents incremental builds, causing significant slowdowns. Removing it allows `make` to skip unchanged targets. Also, `itertools.chain.from_iterable` is preferred over `reduce(iconcat, ...)` for list flattening.
**Action:** Verify build flags to ensure incremental builds are possible. Use `itertools` for efficient iteration.
