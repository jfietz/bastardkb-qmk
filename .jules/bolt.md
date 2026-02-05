## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Avoid intermediate lists in QMK argument building
**Learning:** The codebase used `functools.reduce(operator.iconcat, ...)` to flatten environment variable arguments. This creates unnecessary intermediate lists. `itertools.chain.from_iterable` is more efficient and cleaner.
**Action:** When flattening iterables for command-line arguments, prefer `itertools.chain`.
