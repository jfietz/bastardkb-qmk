## 2026-01-25 - Enable ccache for QMK builds
**Learning:** The build script forces a clean build (`--clean`) for every firmware configuration to ensure correctness. This defeats the purpose of incremental builds but is perfect for `ccache`. Enabling `USE_CCACHE=yes` allows caching across clean builds, significantly reducing build time for multiple targets sharing the same core files.
**Action:** When seeing forced clean builds in C/C++ projects, always check if `ccache` is enabled.
