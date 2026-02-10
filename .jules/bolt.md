## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-01-26 - Avoid unnecessary list conversions
**Learning:** `len(list(sequence))` is an anti-pattern when `sequence` supports `len()` directly (like tuples or lists). It creates an unnecessary copy of the data, consuming O(N) memory and time.
**Action:** Always prefer direct `len(sequence)` where possible, especially in tight loops or reduce operations.

## 2026-01-26 - Respect user feedback on repetition
**Learning:** When a user flags a change as repetitive ("Stop proposing the same change"), immediately pivot to a different, valid optimization instead of trying to force the original proposal.
**Action:** Validate if a proposed change has been previously rejected or is causing friction, and explore alternative performance improvements.
