## 2024-05-23 - Batch Operation Error Aggregation in CLI
**Learning:** For command-line batch operations (like compiling multiple firmwares), printing errors iteratively in a long, fast-scrolling log stream results in poor UX because users easily miss failures or have to scroll excessively to find what broke.
**Action:** When executing batch tasks, always aggregate failed items into a clear list (e.g., `failed_firmwares`) and present them explicitly in the final summary output or panel to ensure immediate visibility.
