## 2024-05-25 - Add TimeRemainingColumn to batch operations
**Learning:** Users lack visibility into how long batch processes like firmware builds will take, causing uncertainty during long-running tasks.
**Action:** Always include an estimated time remaining indicator (e.g., `TimeRemainingColumn` in `rich.progress`) to progress bars for long-running batch operations to improve user experience.
