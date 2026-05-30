## 2024-05-30 - Add time remaining to progress bar
**Learning:** For long-running CLI batch operations using `rich.progress`, include an estimated time remaining indicator (e.g., `TimeRemainingColumn`) in the global progress bar to improve user experience and reduce uncertainty.
**Action:** Always add `TimeRemainingColumn` to `rich.progress.Progress` for batch processes.
