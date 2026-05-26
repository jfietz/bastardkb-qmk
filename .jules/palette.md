
## 2024-05-29 - [Time Remaining Indicator]
**Learning:** For long-running CLI batch operations, users experience uncertainty without a clear sense of progress and remaining time. Adding a time remaining indicator to the global progress bar reduces anxiety and improves the perceived responsiveness of the tool.
**Action:** When using `rich.progress` for batch operations, always include a `TimeRemainingColumn` alongside `TimeElapsedColumn` to provide a complete picture of process duration.
