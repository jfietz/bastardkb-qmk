## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Default to CPU count for parallel builds
**Learning:** The build script defaulted to `--parallel 1`, significantly underutilizing available hardware. Using `os.cpu_count()` allows `make` to saturate all cores, drastically reducing build times for multiple firmwares.
**Action:** Always check default parallelism settings in build scripts. Use `os.cpu_count()` (with fallback) as a sensible default instead of 1.
