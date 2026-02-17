## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Enable incremental QMK builds by removing --clean
**Learning:** The default `qmk compile --clean` flag forces a full rebuild for every firmware, negating the benefits of incremental compilation even with `ccache`. Removing it allows `make` to skip up-to-date targets, significantly speeding up subsequent builds and re-runs.
**Action:** For build scripts managing multiple similar targets or re-runs, avoid `clean` flags unless necessary for correctness. Trust the build system (make) and compiler cache (ccache) to handle dependencies.
