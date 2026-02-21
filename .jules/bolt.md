## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-02-06 - Incremental Builds with QMK
**Learning:** Removing `--clean` from `qmk compile` allows for incremental builds, which significantly speeds up development cycles when using `ccache`. However, one must ensure the build system correctly tracks dependencies. The `rich` library's `Panel` class requires careful mocking (using a custom class that handles `*args`) to avoid `InvalidSpecError` when mocked with `MagicMock` in `sys.modules`.
**Action:** Always verify if `--clean` is necessary in build scripts. When mocking complex classes like `rich.panel.Panel`, use a custom mock class that consumes positional arguments correctly.
