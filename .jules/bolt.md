## 2026-01-26 - Enable ccache for QMK builds
**Learning:** The `bastardkb_build_releases.py` script uses `qmk compile` which supports passing environment variables via `--env`. Enabling `USE_CCACHE=yes` significantly speeds up subsequent builds by caching compilation results. This was previously commented out in the script.
**Action:** When working with QMK build scripts, check for compiler caching options like `ccache` to improve build times, especially for CI/CD pipelines or iterative development. Ensure `ccache` is installed in the environment.

## 2026-02-14 - Unit Test Pollution with sys.modules
**Learning:** Mocking dependencies like `rich` using `sys.modules` in one test file (`test_performance.py`) persists across the test run, affecting other tests (`test_ux.py`). Specifically, assigning `MagicMock` directly to `sys.modules["rich.panel"].Panel` causes `InvalidSpecError` when the mock is instantiated with arguments that are also Mocks, because `MagicMock` treats the first argument as a spec.
**Action:** When mocking classes in `sys.modules`, define a custom `MagicMock` subclass that overrides `__init__` to handle or ignore arguments appropriately, ensuring test isolation and stability.
