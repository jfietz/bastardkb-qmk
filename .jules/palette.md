## 2024-05-16 - Add TimeRemainingColumn to long-running build progress
**Learning:** UX guidelines for CLI tools using `rich.progress` recommend including a `TimeRemainingColumn` alongside `TimeElapsedColumn` for long-running batch operations to provide users with an estimated completion time and reduce wait anxiety.
**Action:** Always include `TimeRemainingColumn` when configuring a `rich.progress` overall progress bar for multi-item build operations to improve the command-line UX.
